"""
reco_v1.py — AI Recommendation Engine reference.

For each applicable action, simulates the fix on the VIR, re-runs dmi_v1 and
ose_v1, and reads off the expected DMI improvement + recovered annual revenue.
Ranks by ICE (Impact x Confidence / Effort).

Spec: RECO_SPEC.md   ·   Method id: "reco_v1"
"""
from __future__ import annotations
import copy, json, pathlib
import dmi_v1, ose_v1

METHOD = "reco_v1"

# ── historical success rates (history_factor) ────────────────────
def _load_confidence():
    for p in ["recommendations_confidence.json", "../Sales Strategy/recommendations_confidence.json", "Sales Strategy/recommendations_confidence.json"]:
        fp = pathlib.Path(__file__).parent / p
        if fp.exists():
            try:
                return {r["rule_id"]: r.get("success_rate", 70) / 100.0 for r in json.loads(fp.read_text(encoding="utf-8"))}
            except Exception:
                pass
    return {}
SUCCESS = _load_confidence()


def _get(vir, path):
    return dmi_v1._v(vir, path)

def _set(vir, path, value, source="projected"):
    node = vir
    keys = path.split(".")
    for k in keys[:-1]:
        node = node.setdefault(k, {})
    leaf = keys[-1]
    cur = node.get(leaf)
    if isinstance(cur, dict) and "value" in cur:
        cur["value"] = value
    else:
        node[leaf] = {"value": value, "source": source}
    return vir


# ── Action catalog ───────────────────────────────────────────────
def _reviews(v): return _get(v, "google_business.total_reviews") or 0
def _vel(v):     return _get(v, "google_business.review_velocity") or 0
def _freq(v):    return _get(v, "instagram.posting_frequency") or 0

ACTIONS = [
    {"id": "gmb_setup", "title": "Claim & optimise Google Business", "pillar": "Discoverability", "effort": 1,
     "applies": lambda v: not _get(v, "google_business.claimed"),
     "apply": lambda v: [_set(v, "google_business.claimed", True),
                          _set(v, "google_business.total_photos", max(30, _get(v, "google_business.total_photos") or 0)),
                          _set(v, "google_business.posts_published", 4)] and v},
    {"id": "review_engine", "title": "Google Reviews Campaign", "pillar": "Trust", "effort": 2,
     "applies": lambda v: _reviews(v) < 50 or _vel(v) < 2,
     "apply": lambda v: [_set(v, "google_business.total_reviews", max(60, _reviews(v) + 40)),
                          _set(v, "google_business.review_velocity", 4),
                          _set(v, "google_business.review_response_rate", 0.8)] and v},
    {"id": "reply_speed", "title": "Reply to inquiries in minutes", "pillar": "Conversion", "effort": 1,
     "applies": lambda v: _get(v, "conversion_systems.response_time") not in ("5min", "1hr"),
     "apply": lambda v: _set(v, "conversion_systems.response_time", "5min")},
    {"id": "followup_system", "title": "Set up a follow-up sequence", "pillar": "Conversion", "effort": 2,
     "applies": lambda v: _get(v, "conversion_systems.follow_up_system") in (None, "none", "owner_memory", "staff"),
     "apply": lambda v: _set(v, "conversion_systems.follow_up_system", "spreadsheet")},
    {"id": "content_engine", "title": "Weekly reels of real functions", "pillar": "Discoverability", "effort": 3,
     "applies": lambda v: _freq(v) < 2,
     "apply": lambda v: [_set(v, "instagram.posting_frequency", 3),
                          _set(v, "instagram.reels_count", (_get(v, "instagram.reels_count") or 0) + 8),
                          _set(v, "trust_signals.wedding_albums", (_get(v, "trust_signals.wedding_albums") or 0) + 6)] and v},
    {"id": "website_build", "title": "Build a mobile inquiry site", "pillar": "Discoverability", "effort": 4,
     "applies": lambda v: not _get(v, "website.exists"),
     "apply": lambda v: [_set(v, "website.exists", True), _set(v, "website.seo_score", 70),
                          _set(v, "website.inquiry_form", True), _set(v, "website.whatsapp_button", True)] and v},
    {"id": "whatsapp_cta", "title": "Add WhatsApp CTA everywhere", "pillar": "Conversion", "effort": 1,
     "applies": lambda v: not (_get(v, "instagram.whatsapp_cta") and _get(v, "conversion_systems.lead_form")),
     "apply": lambda v: [_set(v, "instagram.whatsapp_cta", True), _set(v, "conversion_systems.lead_form", True)] and v},
    {"id": "smartos_ops", "title": "Move bookings to SmartOS", "pillar": "Operations", "effort": 4,
     "applies": lambda v: _get(v, "operations.calendar_management") in (None, "diary", "wall", "excel"),
     "apply": lambda v: [_set(v, "operations.calendar_management", "software"),
                          _set(v, "conversion_systems.inquiry_tracking", "crm"),
                          _set(v, "operations.smartos_usage", True), _set(v, "operations.reporting", 6)] and v},
    {"id": "tracking_start", "title": "Track every inquiry & source", "pillar": "Intelligence", "effort": 2,
     "applies": lambda v: (_get(v, "operations.reporting") or 0) < 3,
     "apply": lambda v: [_set(v, "operations.reporting", 5), _set(v, "intelligence.tracks_sources", True)] and v},
]


def recommend(vir: dict, top_n: int = 3) -> dict:
    base_dmi = dmi_v1.compute_dmi(vir)
    base_rev = ose_v1.compute_opportunity(vir)
    # Total achievable revenue opportunity (conservative, annual). The OSE cap binds on the
    # whole-funnel total, so we attribute that total across actions by their DMI contribution
    # rather than differencing OSE per action (which the cap would zero out).
    monthly_missed = base_rev.get("conservative", {}).get("missed_revenue", 0) if "conservative" in base_rev else 0
    opp_annual = monthly_missed * 12
    data_conf = base_dmi["confidence"]

    # Pass 1 — simulate DMI delta + confidence for every applicable action
    cands = []
    for a in ACTIONS:
        try:
            if not a["applies"](vir):
                continue
        except Exception:
            continue
        fixed = a["apply"](copy.deepcopy(vir))
        ddmi = round(dmi_v1.compute_dmi(fixed)["dmi"] - base_dmi["dmi"], 1)
        history = SUCCESS.get(a["id"], 0.70)
        sim = 0.9 if data_conf >= 0.7 else 0.75
        conf = round((0.6 + 0.4 * data_conf) * history * sim, 2)
        cands.append({"id": a["id"], "action": a["title"], "pillar": a["pillar"],
                      "effort": a["effort"], "expected_dmi_improvement": ddmi, "confidence": conf})

    # Pass 2 — attribute the revenue opportunity proportional to DMI gain
    total_pos = sum(c["expected_dmi_improvement"] for c in cands if c["expected_dmi_improvement"] > 0) or 1
    for c in cands:
        share = max(0, c["expected_dmi_improvement"]) / total_pos
        c["expected_annual_revenue"] = round(opp_annual * share)
        impact = c["expected_dmi_improvement"] + c["expected_annual_revenue"] / 100000.0
        c["priority"] = round(impact * c["confidence"] / c["effort"], 2)

    by_priority = sorted(cands, key=lambda x: x["priority"], reverse=True)
    highest_impact = max(cands, key=lambda x: x["expected_annual_revenue"], default=None)
    return {
        "method": METHOD,
        "current_dmi": base_dmi["dmi"],
        "revenue_opportunity_annual": opp_annual,
        "top_actions": by_priority[:top_n],
        "highest_impact_action": highest_impact,
        "considered": len(cands),
    }


def _inr(n):
    return f"Rs {n/100000:.1f}L/yr" if n >= 100000 else f"Rs {n:,.0f}/yr"

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else str(pathlib.Path(__file__).parent / "vir.example.json")
    vir = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    r = recommend(vir)
    print(f"Current DMI: {r['current_dmi']}   (considered {r['considered']} applicable actions)\n")
    print("TOP 3 NEXT ACTIONS (by priority):")
    for i, a in enumerate(r["top_actions"], 1):
        print(f"  {i}. {a['action']:34} +{a['expected_dmi_improvement']} DMI | {_inr(a['expected_annual_revenue'])} | {int(a['confidence']*100)}% | effort {a['effort']}")
    h = r["highest_impact_action"]
    print(f"\nHIGHEST-IMPACT ACTION: {h['action']} -> +{h['expected_dmi_improvement']} DMI, {_inr(h['expected_annual_revenue'])}, {int(h['confidence']*100)}% confidence")
