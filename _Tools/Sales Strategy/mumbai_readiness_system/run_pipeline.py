from __future__ import annotations

import argparse
import csv
import json
import logging
import os
from pathlib import Path

import pandas as pd

from collectors.google_maps_collector import CollectorConfig, GoogleMapsCollector
from collectors.instagram_engine import collect_instagram_profile
from collectors.marketplace_engine import analyze_marketplaces
from collectors.website_analyzer import analyze_website
from database.db import DB, load_settings, load_google_api_key
from historical.delta_engine import compute_delta
from outreach.priority_engine import build_priority_queue
from outreach.whatsapp_engine import whatsapp_script
from processors.relationship_intelligence import load_relationship_intelligence
from processors.outcome_feedback import load_outreach_outcomes
from processors.intelligence_panels import build_intelligence_panels
from reports.statistics_report import build_statistics
from reports.territory_intelligence import build_competitor_radius_map, build_territory_clusters
from scoring.digital_silence_engine import digital_silence_index
from scoring.digistories_engine import digistories_score
from scoring.dmi_engine import compute_dmi
from scoring.quality_engine import conversion_likelihood, data_quality_grade
from scoring.smartos_engine import smartos_scores


def setup_logger(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def export_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')


def export_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def run_all(root: Path) -> None:
    settings = load_settings(root)
    setup_logger(root / settings['logs_dir'] / 'pipeline.log')

    db = DB(root / settings['database_path'])
    db.init_schema(root / 'database' / 'schema.sql')

    runtime = settings.get('collector_runtime', {})
    api_key = load_google_api_key(root, runtime.get('google_api_key_env', 'GOOGLE_MAPS_API_KEY'))
    mode = settings.get('collection_mode', 'mock')

    # Auto-upgrade to live mode if a real key is present (unless explicitly forced to mock)
    if api_key and settings.get('collection_mode') == 'auto':
        mode = 'live'
    if mode == 'live' and not api_key:
        logging.warning('collection_mode=live but no API key found — falling back to estimates (mock).')
        mode = 'mock'
    collector = GoogleMapsCollector(settings['suburbs'], settings['queries'], CollectorConfig(mode=mode, google_api_key=api_key, max_results_per_query=runtime.get('max_results_per_query', 20), request_timeout_sec=runtime.get('request_timeout_sec', 12), pause_between_calls_sec=runtime.get('pause_between_calls_sec', 0.2)))
    raw_rows = collector.collect()
    export_json(root / settings['raw_dir'] / 'google_maps_snapshot.json', raw_rows)
    relationship_map = load_relationship_intelligence(root / "raw" / "relationship_intelligence.csv")
    outcomes_map = load_outreach_outcomes(root / "raw" / "outreach_outcomes.csv")

    processed = []
    for r in raw_rows:
        business_id = db.upsert_business(r)
        site = analyze_website(r.get('website'), timeout_sec=runtime.get('request_timeout_sec', 12), mode=mode)
        ig = collect_instagram_profile(
            r['business_name'],
            website_hint=r.get('website'),
            mode=mode,
            timeout_sec=runtime.get('request_timeout_sec', 12),
            pitch_strategy=r.get('pitch_strategy', ''),
        )
        market = analyze_marketplaces(r['business_name'])
        db.insert_website_analysis(business_id, site)
        db.insert_social(business_id, ig)

        smart = smartos_scores(site, ig, r)
        silence = digital_silence_index(r, ig, site)
        digi_opp = digistories_score(ig, market)
        digi = {'digistories_opportunity_score': digi_opp}
        # Pass digistories + smartos scores into DMI so it can recommend the right product
        dmi = compute_dmi(
            r, ig, site, market, settings['weights'],
            digistories_opp=digi_opp,
            smartos_pain=(100 - smart['smartos_readiness_score']),
        )
        scored = {**dmi, **smart, **silence, **digi}
        db.insert_score(business_id, scored)

        rel = relationship_map.get(r["business_name"].strip().lower(), {})
        outcomes = outcomes_map.get(r["business_name"].strip().lower(), {})
        merged = {**r, **ig, **site, **market, **scored, **rel, **outcomes, 'collection_mode': mode}
        merged.update(data_quality_grade(merged))
        merged.update(conversion_likelihood(merged))
        processed.append(merged)

    current_processed = root / settings['processed_dir'] / 'current_run_scored.json'
    previous_processed = root / settings['historical_dir'] / 'latest_scored_snapshot.json'
    export_json(current_processed, processed)

    delta = compute_delta(processed, previous_processed)
    export_json(root / settings['exports_dir'] / 'leads_audit_tracker.json', delta)

    # ── 5 Sales-Intelligence Panels (Territory / Silence / SmartOS / Momentum / Relationship)
    # Computed BEFORE we overwrite latest_scored_snapshot, so momentum can compare to the previous run.
    panels = build_intelligence_panels(processed, previous_processed)
    export_json(root / settings['exports_dir'] / 'intelligence_panels.json', panels)
    # Also publish a JS file the standalone Sales Tool HTML can read under file://
    try:
        web_dir = root.parents[2] / '_Web'
        if web_dir.exists():
            (web_dir / 'intelligence_data.js').write_text(
                'window.PANELS = ' + json.dumps(panels, ensure_ascii=False, indent=2) + ';',
                encoding='utf-8',
            )
    except Exception as e:
        logging.warning('Could not write intelligence_data.js for web tool: %s', e)

    # priority_engine now generates whatsapp_script internally per DMI category
    queue = build_priority_queue(processed)

    stats = build_statistics(processed)
    territory_clusters = build_territory_clusters(processed)
    competitor_map = build_competitor_radius_map(processed, radius_km=3.0)

    leads_export = [
        {
            'name': p['business_name'],
            'address': p['address'],
            'rating': p['rating'],
            'reviews_count': p['review_count'],
            'website': p['website'],
            'phones': p['phone_numbers'],
            'instagram': p.get('username') or 'None',
            'whatsapp_link': 'Present' if p.get('whatsapp_cta_presence') else 'None',
            'dmi_score': p['dmi_score'],
            'dmi_status': p['dmi_category'],
            'data_source': p.get('data_source', 'ai_estimate'),
            'digital_silence_index': p.get('digital_silence_index', 0),
            'digital_silence_label': p.get('digital_silence_label', ''),
            'smartos_readiness_score': p.get('smartos_readiness_score', 0),
            'inquiry_leakage_probability': p.get('inquiry_leakage_probability', 0),
            'digistories_opportunity_score': p.get('digistories_opportunity_score', 0),
            'recommended_product': p.get('recommended_product', ''),
            'conversion_likelihood_band': p.get('conversion_likelihood_band', 'Low'),
            'collection_mode': p.get('collection_mode', 'mock'),
            'data_quality_grade': p.get('data_quality_grade', 'C'),
            'conversion_likelihood_score': p.get('conversion_likelihood_score', 0),
            'google_confidence_score': p.get('google_confidence_score', 0),
            'website_confidence_score': p.get('confidence_score', 0),
            'instagram_confidence_score': p.get('instagram_confidence_score', 0),
        }
        for p in processed
    ]
    entity_profiles = []
    for p in processed:
        entity_profiles.append(
            {
                "business_name": p["business_name"],
                "data_source": p.get("data_source", "ai_estimate"),
                "identity": {
                    "category": p.get("category"),
                    "suburb": p.get("suburb"),
                    "address": p.get("address"),
                    "phone_numbers": p.get("phone_numbers"),
                    "website": p.get("website"),
                },
                "digital_state": {
                    "dmi_score": p.get("dmi_score"),
                    "dmi_category": p.get("dmi_category"),
                    "score_breakdown": p.get("score_breakdown"),
                    "digital_silence_index": p.get("digital_silence_index"),
                    "digital_silence_label": p.get("digital_silence_label"),
                    "digital_silence_breakdown": p.get("digital_silence_breakdown"),
                    "trust_perception_score": p.get("trust_perception_score"),
                    "recommended_product": p.get("recommended_product"),
                    "recommendation_reason": p.get("recommendation_reason"),
                    "key_weaknesses": p.get("key_weaknesses"),
                },
                "operational_state": {
                    "smartos_readiness_score": p.get("smartos_readiness_score"),
                    "inquiry_leakage_probability": p.get("inquiry_leakage_probability"),
                    "smartos_pain_breakdown": p.get("smartos_pain_breakdown"),
                    "digistories_opportunity_score": p.get("digistories_opportunity_score"),
                },
                "model_intelligence": {
                    "data_quality_score": p.get("data_quality_score"),
                    "data_quality_grade": p.get("data_quality_grade"),
                    "conversion_likelihood_score": p.get("conversion_likelihood_score"),
                    "conversion_likelihood_band": p.get("conversion_likelihood_band"),
                    "google_confidence_score": p.get("google_confidence_score"),
                    "website_confidence_score": p.get("confidence_score"),
                    "instagram_confidence_score": p.get("instagram_confidence_score"),
                },
                "feedback_intelligence": {
                    "past_contact_count": p.get("past_contact_count"),
                    "past_reply_count": p.get("past_reply_count"),
                    "past_meeting_count": p.get("past_meeting_count"),
                    "past_win_count": p.get("past_win_count"),
                    "reply_rate": p.get("reply_rate"),
                    "meeting_rate": p.get("meeting_rate"),
                    "win_rate": p.get("win_rate"),
                },
                "relationship_intelligence": {
                    "second_generation_involvement": p.get("second_generation_involvement"),
                    "bca_regular_presence": p.get("bca_regular_presence"),
                    "modernization_mindset_score": p.get("modernization_mindset_score"),
                    "recently_renovated": p.get("recently_renovated"),
                    "portal_complaint_signal": p.get("portal_complaint_signal"),
                    "operational_struggle_signal": p.get("operational_struggle_signal"),
                    "branding_spend_signal": p.get("branding_spend_signal"),
                    "growth_hungry_signal": p.get("growth_hungry_signal"),
                    "notes": p.get("notes"),
                },
            }
        )

    export_json(root / settings['exports_dir'] / 'bcda_extracted_leads.json', leads_export)
    export_csv(root / settings['exports_dir'] / 'bcda_extracted_leads.csv', leads_export)
    export_json(root / settings['exports_dir'] / 'bcda_maturity_index_tracker.json', processed)
    export_json(root / settings['exports_dir'] / 'business_entity_profiles.json', entity_profiles)
    export_json(root / settings['exports_dir'] / 'bcda_statistics.json', stats)
    export_json(root / settings['exports_dir'] / 'territory_clusters.json', territory_clusters)
    export_json(root / settings['exports_dir'] / 'competitor_radius_map.json', competitor_map)
    export_csv(root / settings['exports_dir'] / 'territory_clusters.csv', territory_clusters)
    export_csv(root / settings['exports_dir'] / 'daily_outreach_queue.csv', queue)

    # preserve history without overwrite
    stamp = pd.Timestamp.now('UTC').strftime('%Y%m%d_%H%M%S')
    export_json(root / settings['historical_dir'] / f'scored_snapshot_{stamp}.json', processed)
    export_json(previous_processed, processed)

    logging.info('Run complete. Processed=%s Queue=%s', len(processed), len(queue))


def main() -> None:
    parser = argparse.ArgumentParser(description='Mumbai Digital Readiness Pipeline')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    run_all(args.root)


if __name__ == '__main__':
    main()

