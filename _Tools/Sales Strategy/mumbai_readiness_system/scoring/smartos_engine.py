from __future__ import annotations


def smartos_scores(site: dict, ig: dict, business: dict) -> dict:
    phones = str(business.get("phone_numbers") or "")
    multi_phone = 1 if any(sep in phones for sep in [",", "/", "|", ";"]) else 0
    weak_cta = 1 if not (site.get("inquiry_form_presence") or ig.get("whatsapp_cta_presence")) else 0
    no_booking_visibility = 1 if not site.get("inquiry_form_presence") else 0
    no_structured_follow_up = 1 if not site.get("whatsapp_cta_presence") else 0
    inconsistent_response = 1 if business.get("owner_response_presence") == 0 else 0

    leakage = min(
        0.98,
        0.25
        + 0.18 * multi_phone
        + 0.2 * weak_cta
        + 0.16 * no_booking_visibility
        + 0.12 * no_structured_follow_up
        + 0.15 * inconsistent_response,
    )
    readiness = round((1 - leakage) * 100, 2)
    return {
        "smartos_readiness_score": readiness,
        "inquiry_leakage_probability": round(leakage, 2),
        "smartos_pain_breakdown": {
            "multiple_phone_numbers_fragmentation": multi_phone,
            "weak_cta_lead_flow_gap": weak_cta,
            "no_booking_system_visibility": no_booking_visibility,
            "no_structured_follow_up": no_structured_follow_up,
            "inconsistent_response_pattern": inconsistent_response,
        },
    }
