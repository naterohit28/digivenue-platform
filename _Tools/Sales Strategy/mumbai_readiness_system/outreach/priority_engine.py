from __future__ import annotations
from outreach.whatsapp_engine import whatsapp_script


def tier_label(dmi_category: str) -> str:
    if dmi_category in ('Elite', 'Growth Ready'):
        return 'Tier A'
    if dmi_category in ('Visibility Weak', 'Operationally Chaotic'):
        return 'Tier B'
    return 'Tier C'


def _priority_reason(r: dict, pain: float, silence_boost: float, relationship_boost: float) -> str:
    """Plain-English reason why this venue is high priority today."""
    reasons = []
    if r.get('digital_silence_index', 0) >= 60:
        reasons.append('severely silent online')
    if r.get('inquiry_leakage_probability', 0) >= 0.5:
        reasons.append(f"losing ~{int(r['inquiry_leakage_probability']*100)}% of inquiries")
    if r.get('digistories_opportunity_score', 0) >= 60:
        reasons.append('high DigiStories opportunity')
    if r.get('growth_hungry_signal'):
        reasons.append('shows growth hunger (human intel)')
    if r.get('operational_struggle_signal'):
        reasons.append('operational struggle flagged (human intel)')
    if not reasons:
        reasons.append('overall weak digital presence')
    return ' | '.join(reasons)


def build_priority_queue(rows: list[dict]) -> list[dict]:
    queue = []
    for r in rows:
        if r['dmi_category'] == 'Elite':
            continue
        if 'hotel' in r['business_name'].lower():
            continue

        pain = (100 - r['smartos_readiness_score']) + r['digistories_opportunity_score']
        silence_boost = r.get('digital_silence_index', 0) * 0.4
        relationship_boost = (
            float(r.get('growth_hungry_signal') or 0) * 5
            + float(r.get('operational_struggle_signal') or 0) * 5
            + float(r.get('modernization_mindset_score') or 0) * 0.5
        )
        conversion_boost = float(r.get("conversion_likelihood_score") or 0) * 0.2
        priority_score = round(pain + silence_boost + relationship_boost + conversion_boost, 2)

        # Build the full row that also carries fields needed for WhatsApp script
        outreach_row = {
            'business_name': r['business_name'],
            'data_source': r.get('data_source', 'ai_estimate'),
            'google_maps_url': r.get('google_maps_url', ''),
            'area': r['area'],
            'suburb': r['suburb'],
            'phone': r.get('phone_numbers', '—'),
            'dmi_score': r['dmi_score'],
            'dmi_category': r['dmi_category'],
            'tier': tier_label(r['dmi_category']),
            'recommended_product': r.get('recommended_product', 'DigiStories'),
            'recommendation_reason': r.get('recommendation_reason', ''),
            'key_weaknesses': r.get('key_weaknesses', []),
            'inquiry_leakage_probability': r['inquiry_leakage_probability'],
            'digital_silence_index': r.get('digital_silence_index', 0),
            'priority_score': priority_score,
            'conversion_likelihood_score': float(r.get("conversion_likelihood_score") or 0),
            'conversion_likelihood_band': r.get("conversion_likelihood_band", "Low"),
            'data_quality_grade': r.get("data_quality_grade", "C"),
            'priority_reason': _priority_reason(r, pain, silence_boost, relationship_boost),
        }

        # Generate WhatsApp script using the enriched row
        outreach_row['whatsapp_script'] = whatsapp_script(outreach_row)

        queue.append(outreach_row)

    queue.sort(key=lambda x: x['priority_score'], reverse=True)
    return queue
