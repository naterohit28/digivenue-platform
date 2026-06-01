from __future__ import annotations

from datetime import datetime, timezone


def _days_since(date_str: str | None) -> int | None:
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", ""))
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return (now - dt).days
    except Exception:
        return None


def digital_silence_index(business: dict, ig: dict, site: dict) -> dict:
    post_days = _days_since(ig.get("last_post_date"))
    review_days = _days_since(business.get("latest_review_date"))

    no_post_60 = 1 if (post_days is None or post_days >= 60) else 0
    no_recent_reviews = 1 if (review_days is None or review_days >= 60) else 0
    no_recent_photo_signal = 1 if business.get("photo_count", 0) < 10 else 0
    outdated_branding = 1 if ig.get("trust_perception_score", 0) < 5 else 0
    dead_website = 1 if (not business.get("website") or site.get("website_quality_score", 0) <= 2) else 0

    score = min(
        100,
        no_post_60 * 25
        + no_recent_reviews * 25
        + no_recent_photo_signal * 15
        + outdated_branding * 20
        + dead_website * 15,
    )
    label = "Severe Silence" if score >= 70 else "At Risk" if score >= 40 else "Active Pulse"
    return {
        "digital_silence_index": round(score, 2),
        "digital_silence_label": label,
        "digital_silence_breakdown": {
            "no_post_60_plus_days": no_post_60,
            "no_recent_google_reviews": no_recent_reviews,
            "no_recent_google_photos_signal": no_recent_photo_signal,
            "outdated_branding_signal": outdated_branding,
            "dead_website_signal": dead_website,
        },
    }
