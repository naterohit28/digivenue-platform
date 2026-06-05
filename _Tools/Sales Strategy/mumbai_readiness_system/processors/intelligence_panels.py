"""
intelligence_panels.py
───────────────────────
Builds the 5 sales-intelligence panels for every venue:

  1. Territory Rank          (#X in suburb, #Y across all venues)
  2. Digital Silence Index   (no reel / no review / no photo signals)
  3. SmartOS Opportunity     (inquiry leakage / manual / WhatsApp risk)
  4. Growth Momentum         (reviews up / IG active / website fresh) -> buying signal
  5. Relationship Intel      (BCA member / 2nd gen / growth mindset / agency user)

Logic lives here ONCE. Both the Streamlit dashboard and the Sales Tool
HTML read the output, so the numbers always match.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


# ─────────────────────────────────────────────
#  helpers
# ─────────────────────────────────────────────
def _days_since(date_str: str | None) -> int | None:
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(str(date_str).replace("Z", ""))
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return (now - dt).days
    except Exception:
        return None


def _truthy(val) -> bool:
    """Treat 1/'1'/'yes'/'true'/'y' as True."""
    if val is None:
        return False
    s = str(val).strip().lower()
    return s in ("1", "yes", "true", "y", "high")


# ─────────────────────────────────────────────
#  PANEL 1 — Territory Rank
# ─────────────────────────────────────────────
def _territory_rank(row: dict, suburb_ranked: dict, global_ranked: list) -> dict:
    name = row["business_name"]
    suburb = row.get("suburb", "Unknown")

    # rank within suburb (1 = strongest DMI)
    s_list = suburb_ranked.get(suburb, [])
    s_rank = next((i + 1 for i, r in enumerate(s_list) if r["business_name"] == name), None)
    s_total = len(s_list)

    # rank across all venues
    g_rank = next((i + 1 for i, r in enumerate(global_ranked) if r["business_name"] == name), None)
    g_total = len(global_ranked)

    return {
        "suburb": suburb,
        "suburb_rank": s_rank,
        "suburb_total": s_total,
        "global_rank": g_rank,
        "global_total": g_total,
        "lines": [
            f"{suburb} Rank: #{s_rank} of {s_total} venues",
            f"Overall Rank: #{g_rank} of {g_total} venues",
        ],
    }


# ─────────────────────────────────────────────
#  PANEL 2 — Digital Silence Index
# ─────────────────────────────────────────────
def _digital_silence(row: dict) -> dict:
    reel_days = _days_since(row.get("last_reel_date") or row.get("last_post_date"))
    post_days = _days_since(row.get("last_post_date"))
    review_days = _days_since(row.get("latest_review_date"))
    photo_count = row.get("photo_count", 0) or 0

    no_reel_90 = reel_days is None or reel_days >= 90
    no_review_60 = review_days is None or review_days >= 60
    low_photos = photo_count < 12  # proxy for "no recent photo uploads"

    # reuse existing silence score if present, else estimate
    score = row.get("digital_silence_index")
    if score is None:
        score = no_reel_90 * 35 + no_review_60 * 30 + low_photos * 20 + (post_days is None) * 15
        score = min(100, score)

    label = "Severe Silence" if score >= 70 else "At Risk" if score >= 40 else "Active Pulse"

    lines = []
    lines.append(f"No reel in {reel_days} days" if reel_days is not None else "No reels found at all")
    lines.append(f"No review in {review_days} days" if review_days is not None else "No recent reviews")
    lines.append(f"Only {photo_count} photos on Google" if low_photos else f"{photo_count} photos on Google")

    return {
        "score": round(float(score), 1),
        "label": label,
        "is_strong_digistories_signal": bool(score >= 60),
        "lines": lines,
    }


# ─────────────────────────────────────────────
#  PANEL 3 — SmartOS Opportunity Index
# ─────────────────────────────────────────────
def _smartos_opportunity(row: dict) -> dict:
    leakage = row.get("inquiry_leakage_probability", 0) or 0
    pain = row.get("smartos_pain_breakdown", {}) or {}

    inquiry_risk = "High" if leakage >= 0.5 else "Medium" if leakage >= 0.35 else "Low"
    manual_risk = "High" if pain.get("no_booking_system_visibility") else "Low"
    whatsapp_risk = "High" if pain.get("no_structured_follow_up") else "Low"

    opportunity = round(min(100, leakage * 100 + sum(1 for v in pain.values() if v) * 4), 1)

    return {
        "opportunity_score": opportunity,
        "inquiry_leakage_risk": inquiry_risk,
        "manual_workflow_risk": manual_risk,
        "whatsapp_dependency_risk": whatsapp_risk,
        "lines": [
            f"Inquiry leakage risk: {inquiry_risk} (~{int(leakage * 100)}%)",
            f"Manual workflow risk: {manual_risk}",
            f"WhatsApp dependency risk: {whatsapp_risk}",
        ],
    }


# ─────────────────────────────────────────────
#  PANEL 4 — Growth Momentum Score (buying signal)
# ─────────────────────────────────────────────
def _growth_momentum(row: dict, prev: dict | None) -> dict:
    review_days = _days_since(row.get("latest_review_date"))
    post_days = _days_since(row.get("last_post_date"))

    # Compare to previous run if we have history
    reviews_up = False
    if prev:
        reviews_up = (row.get("review_count", 0) - prev.get("review_count", 0)) > 0
    # Without history, treat fresh reviews (<30d) as "reviews increasing"
    reviews_increasing = reviews_up or (review_days is not None and review_days <= 30)
    instagram_active = post_days is not None and post_days <= 30
    website_updated = bool(row.get("website")) and (row.get("website_quality_score", 0) or 0) >= 6

    score = reviews_increasing * 40 + instagram_active * 35 + website_updated * 25
    label = "Heating Up" if score >= 65 else "Some Movement" if score >= 30 else "Dormant"

    return {
        "score": int(score),
        "label": label,
        "reviews_increasing": bool(reviews_increasing),
        "instagram_active": bool(instagram_active),
        "website_updated": bool(website_updated),
        "is_buying_signal": bool(score >= 65),
        "lines": [
            ("✓" if reviews_increasing else "✗") + " Reviews increasing",
            ("✓" if instagram_active else "✗") + " Instagram active",
            ("✓" if website_updated else "✗") + " Website updated",
        ],
    }


# ─────────────────────────────────────────────
#  PANEL 5 — Relationship Intelligence Layer
# ─────────────────────────────────────────────
def _relationship(row: dict) -> dict:
    bca = _truthy(row.get("bca_regular_presence"))
    second_gen = _truthy(row.get("second_generation_involvement"))
    growth_mind = _truthy(row.get("growth_hungry_signal")) or (
        float(row.get("modernization_mindset_score") or 0) >= 6
    )
    agency_user = _truthy(row.get("agency_user")) or _truthy(row.get("branding_spend_signal"))

    tags = []
    if bca:
        tags.append("BCA Member")
    if second_gen:
        tags.append("2nd Generation")
    if growth_mind:
        tags.append("Growth Mindset")
    if agency_user:
        tags.append("Agency User")

    has_intel = bool(tags) or bool(row.get("notes"))

    return {
        "bca_member": bca,
        "second_generation": second_gen,
        "growth_mindset": growth_mind,
        "agency_user": agency_user,
        "tags": tags,
        "notes": row.get("notes") or "",
        "has_human_intel": has_intel,
        "lines": tags if tags else ["No field intel captured yet"],
    }


# ─────────────────────────────────────────────
#  Assemble all panels for every venue
# ─────────────────────────────────────────────
def build_intelligence_panels(rows: list[dict], previous_path: Path | list[dict] | None = None) -> dict:
    # previous run (for momentum)
    prev_map = {}
    if isinstance(previous_path, list):
        prev_map = {x["business_name"]: x for x in previous_path if x.get("business_name")}
    elif previous_path and Path(previous_path).exists():
        try:
            prev_data = json.loads(Path(previous_path).read_text(encoding="utf-8"))
            prev_map = {x["business_name"]: x for x in prev_data}
        except Exception:
            prev_map = {}

    # global ranking by DMI (strongest first)
    global_ranked = sorted(rows, key=lambda r: r.get("dmi_score", 0), reverse=True)

    # per-suburb ranking
    suburb_ranked: dict[str, list] = {}
    for r in global_ranked:
        suburb_ranked.setdefault(r.get("suburb", "Unknown"), []).append(r)

    panels = {}
    for row in rows:
        name = row["business_name"]
        panels[name] = {
            "business_name": name,
            "area": row.get("area"),
            "suburb": row.get("suburb"),
            "dmi_score": row.get("dmi_score"),
            "dmi_category": row.get("dmi_category"),
            "data_source": row.get("data_source", "ai_estimate"),
            "territory_rank": _territory_rank(row, suburb_ranked, global_ranked),
            "digital_silence": _digital_silence(row),
            "smartos_opportunity": _smartos_opportunity(row),
            "growth_momentum": _growth_momentum(row, prev_map.get(name)),
            "relationship": _relationship(row),
        }
    return panels
