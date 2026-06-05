"""
pipeline_intelligence.py — wires the 7 intelligence engines into the live pipeline.

For every processed venue it:
  1. builds a complete Venue Intelligence Record (VIR) from collected data,
  2. scores it with DMI,
  3. benchmarks it with CIE against its suburb/type cohort,
  4. estimates lost revenue with OSE,
  5. classifies maturity with VMF,
  6. tracks month-over-month history with HVT,
  7. recommends next actions with REC.

Returns a list of full intelligence records and attaches a compact summary to
each processed row. All engines degrade gracefully on missing data.
"""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import dmi_v1
import cie_v1
import ose_v1
import maturity_v1
import tracker_v1
import reco_v1


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (name or "venue").lower()).strip("_")

def _ev(value, source):
    return {"value": value, "source": source} if value is not None else None

def _put(section: dict, key: str, ev):
    if ev is not None:
        section[key] = ev

def _clamp(x, lo, hi):
    return max(lo, min(hi, x))


# ─────────────────────────────────────────────────────────────
#  Map a processed pipeline row -> Venue Intelligence Record
# ─────────────────────────────────────────────────────────────
def build_vir(row: dict) -> dict:
    ds = row.get("data_source", "ai_estimate")
    live = row.get("collection_mode") == "live"
    g_src = "google_places_api" if ds == "google_live" else "ai_estimate"
    ig_src = "instagram_scrape" if live else "ai_estimate"
    web_src = "website_crawl" if live else "ai_estimate"
    est = "pipeline_estimate"

    name = row.get("business_name", "Venue")
    suburb = row.get("suburb") or row.get("area") or "Unknown"
    cap_max = row.get("capacity_max") or 500
    cap_min = row.get("capacity_min") or 100

    # revenue estimates (flagged pipeline_estimate -> OSE confidence stays low/honest)
    avg_value = int(_clamp(cap_max * 600, 150000, 2200000))
    inquiries = int(_clamp(round(cap_max / 80), 5, 40))
    bookings = max(1, round(inquiries * 0.28))

    gb, ig, web, trust, conv, ops, rev = {}, {}, {}, {}, {}, {}, {}

    # SECTION 2 — Google Business
    _put(gb, "rating", _ev(row.get("rating"), g_src))
    _put(gb, "total_reviews", _ev(row.get("review_count"), g_src))
    _put(gb, "total_photos", _ev(row.get("photo_count"), g_src))
    _put(gb, "review_response_rate", _ev(0.8 if row.get("owner_response_presence") else 0.0, g_src))
    if row.get("latest_review_date") is not None:
        _put(gb, "last_photo_upload", _ev(row.get("latest_review_date"), g_src))

    # SECTION 3 — Instagram
    _put(ig, "followers", _ev(row.get("followers"), ig_src))
    _put(ig, "total_posts", _ev(row.get("post_count"), ig_src))
    _put(ig, "reels_count", _ev(row.get("reel_count"), ig_src))
    if row.get("reel_consistency_score") is not None:
        _put(ig, "posting_frequency", _ev(round(row["reel_consistency_score"] / 2.5, 1), ig_src))
    _put(ig, "last_post_date", _ev(row.get("last_post_date"), ig_src))
    _put(ig, "whatsapp_cta", _ev(bool(row.get("whatsapp_cta_presence")), ig_src))

    # SECTION 4 — Website
    has_site = bool(row.get("website"))
    _put(web, "exists", _ev(has_site, web_src))
    if has_site:
        _put(web, "seo_score", _ev((row.get("seo_metadata_score") or 0) * 10, web_src))
        _put(web, "mobile_friendly", _ev(bool(row.get("mobile_responsive")), web_src))
        _put(web, "whatsapp_button", _ev(bool(row.get("whatsapp_cta_presence")), web_src))
        _put(web, "inquiry_form", _ev(bool(row.get("inquiry_form_presence")), web_src))

    # SECTION 5 — Trust signals (derived from IG content scores)
    rw = row.get("real_wedding_score")
    if rw is not None:
        _put(trust, "wedding_albums", _ev(round(rw / 2), ig_src))

    # SECTION 6 — Conversion systems
    pain = row.get("smartos_pain_breakdown", {}) or {}
    _put(conv, "follow_up_system", _ev("none" if pain.get("no_structured_follow_up") else "staff", est))
    _put(conv, "lead_form", _ev(bool(row.get("inquiry_form_presence")), web_src))
    _put(conv, "inquiry_tracking", _ev("paper", est))  # prospects: manual by default

    # SECTION 7 — Operations
    _put(ops, "smartos_usage", _ev(False, est))
    _put(ops, "calendar_management", _ev("diary", est))
    _put(ops, "reporting", _ev(1, est))

    # SECTION 8 — Revenue (estimated)
    _put(rev, "inquiry_volume_monthly", _ev(inquiries, est))
    _put(rev, "booking_volume_monthly", _ev(bookings, est))
    _put(rev, "avg_booking_value", _ev(avg_value, est))

    # Leadership (internal) from relationship intelligence
    lead = 50
    if row.get("modernization_mindset_score") is not None:
        lead = int(_clamp(row["modernization_mindset_score"] * 10, 0, 100))
    if row.get("growth_hungry_signal"):
        lead = min(100, lead + 15)

    vir = {
        "schema_version": "1.0",
        "vir_id": _slug(name),
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "collection_mode": "live" if live else "estimate",
        "data_source": ds,
        "venue": {
            "name": name,
            "type": "banquet",
            "city": "Maharashtra",
            "area": suburb,
            "capacity_min": cap_min,
            "capacity_max": cap_max,
            "price_range": {"avg_event_value": avg_value, "currency": "INR"},
            "geo": {"google_place_id": row.get("external_id")},
        },
        "google_business": gb,
        "instagram": ig,
        "website": web,
        "trust_signals": trust,
        "conversion_systems": conv,
        "operations": ops,
        "revenue": rev,
        "dimensions": {"leadership": {"score": lead, "method": "manual_override"}},
    }
    return vir


def _venue_metric(vir: dict) -> dict:
    g = lambda p: dmi_v1._v(vir, p)
    return {
        "venue_id": vir["vir_id"],
        "city": vir["venue"]["city"],
        "area": vir["venue"]["area"],
        "venue_type": vir["venue"]["type"],
        "reviews": g("google_business.total_reviews") or 0,
        "rating": g("google_business.rating") or 0,
        "photos": g("google_business.total_photos") or 0,
        "ig_followers": g("instagram.followers") or 0,
        "ig_activity": g("instagram.posting_frequency") or 0,
        "website_quality": (g("website.seo_score") or 0) if g("website.exists") else 0,
        "trust_signals": g("trust_signals.wedding_albums") or 0,
    }


# ─────────────────────────────────────────────────────────────
#  Main entry — enrich processed rows with full intelligence
# ─────────────────────────────────────────────────────────────
def enrich_with_intelligence(processed: list[dict], root: Path, history: dict | None = None, persist_history: bool = False) -> list[dict]:
    period = datetime.now(timezone.utc).strftime("%Y-%m")

    # Build VIRs + the CIE metric projection
    virs, metrics = [], []
    for row in processed:
        vir = build_vir(row)
        virs.append(vir)
        metrics.append(_venue_metric(vir))

    # HVT history is supplied by the central persistence layer. The legacy
    # file fallback exists only for old standalone runs.
    snap_dir = root / "historical" / "intelligence_snapshots"
    history = history or {}
    if not history and snap_dir.exists():
        for f in sorted(snap_dir.glob("*.json")):
            try:
                for vid, snap in json.loads(f.read_text(encoding="utf-8")).items():
                    history.setdefault(vid, []).append(snap)
            except Exception:
                pass

    records = []
    this_month_snap = {}
    for row, vir, metric in zip(processed, virs, metrics):
        dmi = dmi_v1.compute_dmi(vir)
        cie = cie_v1.compare(metric, metrics)
        ose = ose_v1.compute_opportunity(vir)
        vmf = maturity_v1.classify(vir)
        rec = reco_v1.recommend(vir)

        # write VIR-derived dimension scores back into the VIR (evidence-traceable)
        for dname, dval in dmi["dimensions"].items():
            vir["dimensions"][dname] = {"score": dval["score"], "band": dval["band"],
                                        "method": "dmi_v1", "confidence": dval["confidence"]}
        vir["dimensions"]["overall_dmi"] = {"score": dmi["dmi"], "band": dmi["band"], "method": "dmi_v1"}

        # HVT — append this month, compute trends against prior months
        snap = {"period": period, "maturity_stage": vmf["overall_stage"],
                **{k: dmi["dimensions"][k]["score"] for k in ["discoverability", "trust", "conversion", "operations", "intelligence"]},
                "dmi": dmi["dmi"]}
        this_month_snap[vir["vir_id"]] = snap
        series = [s for s in history.get(vir["vir_id"], []) if s.get("period") != period] + [snap]
        series.sort(key=lambda s: s["period"])
        hvt = tracker_v1.report(series) if len(series) >= 1 else None

        record = {
            "vir": vir,
            "dmi": {"score": dmi["dmi"], "band": dmi["band"], "confidence": dmi["confidence"],
                    "dimensions": {k: v["score"] for k, v in dmi["dimensions"].items()}},
            "competitive": {"index": cie["competitive_index"], "position": cie["position"],
                            "cohort_size": cie["cohort"]["size"], "biggest_gap": cie["biggest_gap"],
                            "reviews": cie["metrics"].get("reviews")},
            "opportunity": {"range": ose.get("headline_revenue_range"), "confidence": ose.get("confidence"),
                            "advisory": ose.get("advisory")},
            "maturity": {"stage": vmf["overall_stage"], "weakest_link": vmf["weakest_link"],
                         "next_stage": vmf["next_stage"]},
            "tracking": (hvt["summary"] if hvt else None),
            "recommendations": rec["top_actions"],
            "highest_impact_action": rec["highest_impact_action"],
        }
        records.append(record)

        # attach a compact summary onto the processed row (for existing exports/dashboard)
        row["intelligence"] = {
            "dmi": dmi["dmi"], "dmi_band": dmi["band"],
            "maturity_stage": vmf["overall_stage"],
            "competitive_position": cie["position"],
            "opportunity_range": ose.get("headline_revenue_range"),
            "top_action": rec["top_actions"][0]["action"] if rec["top_actions"] else None,
        }

    if persist_history:
        snap_dir.mkdir(parents=True, exist_ok=True)
        (snap_dir / f"{period}.json").write_text(json.dumps(this_month_snap, indent=2), encoding="utf-8")

    return records
