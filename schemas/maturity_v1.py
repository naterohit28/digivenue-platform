"""
maturity_v1.py — Venue Maturity Framework classifier.

Maps a VIR (scored by dmi_v1) onto a 4-stage maturity model across 5 business
dimensions, applies the weakest-link + majority gates, and emits the overall
stage, weakest link, advancement roadmap, and a text scorecard.

Spec: MATURITY_FRAMEWORK.md   ·   Method id: "maturity_v1"
"""
from __future__ import annotations
import dmi_v1

METHOD = "maturity_v1"
STAGES = ["Traditional", "Semi-Digital", "Modern", "Intelligent"]
BADGE = {"Traditional": "🟤", "Semi-Digital": "🟠", "Modern": "🔵", "Intelligent": "🟢"}
WEIGHTS = {"Marketing": 25, "Sales": 25, "Operations": 20, "Technology": 15, "Leadership": 15}

ROADMAP = {
    "Semi-Digital": {
        "Marketing": "Claim Google & post weekly",
        "Sales": "Route inquiries to WhatsApp, reply same-day",
        "Operations": "Move the diary to a shared sheet",
        "Technology": "Basic listing/site + WhatsApp",
        "Leadership": "Commit to one channel for 90 days",
    },
    "Modern": {
        "Marketing": "50+ fresh reviews + weekly real-function reels",
        "Sales": "Under-1hr response + written follow-up sequence",
        "Operations": "Booking software + multi-staff access",
        "Technology": "Mobile site + inquiry form + CRM",
        "Leadership": "Measure conversion monthly",
    },
    "Intelligent": {
        "Marketing": "Schedule content by what converts; review-velocity engine",
        "Sales": "Automated nurture + lead scoring",
        "Operations": "SmartOS dashboards + automated workflows",
        "Technology": "Integrated stack + analytics pipeline",
        "Leadership": "Run experiments, decide by data",
    },
}


def _stage_idx(score):
    if score is None:
        return None
    return 0 if score <= 30 else 1 if score <= 55 else 2 if score <= 80 else 3


def _technology_score(vir):
    v = dmi_v1._v
    parts = []
    web = v(vir, "website.exists")
    if web is not None:
        parts.append(40 + 0.6 * (v(vir, "website.seo_score") or 0) if web else 0.0)
    cal = v(vir, "operations.calendar_management")
    if cal is not None:
        parts.append(dmi_v1.ORD(cal, dmi_v1.ORD_CALENDAR))
    trk = v(vir, "conversion_systems.inquiry_tracking")
    if trk is not None:
        parts.append(dmi_v1.ORD(trk, dmi_v1.ORD_TRACKING))
    crm = v(vir, "conversion_systems.crm")
    sos = v(vir, "operations.smartos_usage")
    if crm is not None or sos is not None:
        parts.append(100.0 if (sos or (crm not in (None, "none", "None"))) else 0.0)
    return round(sum(parts) / len(parts), 1) if parts else None


def classify(vir: dict) -> dict:
    d = dmi_v1.compute_dmi(vir)["dimensions"]
    disc = d["discoverability"]["score"] or 0
    trust = d["trust"]["score"] or 0
    dims = {
        "Marketing": round(0.55 * disc + 0.45 * trust, 1),
        "Sales": d["conversion"]["score"],
        "Operations": d["operations"]["score"],
        "Technology": _technology_score(vir),
        "Leadership": dmi_v1._v(vir, "dimensions.leadership.score"),
    }
    stages = {k: _stage_idx(s) for k, s in dims.items()}
    present = {k: lv for k, lv in stages.items() if lv is not None}

    wsum = sum(WEIGHTS[k] for k in present)
    composite = sum(WEIGHTS[k] * dims[k] for k in present) / wsum if wsum else 0
    base = _stage_idx(composite)

    weakest_stage = min(present.values())
    gate_1 = weakest_stage + 1
    # gate_2: highest stage reached by >=60% of present dimensions
    n = len(present)
    gate_2 = 0
    for L in range(3, -1, -1):
        if sum(1 for lv in present.values() if lv >= L) >= max(1, round(0.6 * n)):
            gate_2 = L
            break
    overall_idx = max(0, min(base, gate_1, gate_2))
    overall = STAGES[overall_idx]

    weakest = [k for k, lv in present.items() if lv == weakest_stage]
    next_stage = STAGES[overall_idx + 1] if overall_idx < 3 else None
    roadmap = {}
    if next_stage:
        for k, lv in present.items():
            if lv <= overall_idx:
                roadmap[k] = ROADMAP[next_stage][k]

    return {
        "method": METHOD,
        "overall_stage": overall,
        "overall_badge": BADGE[overall],
        "composite": round(composite, 1),
        "next_stage": next_stage,
        "weakest_link": weakest,
        "dimensions": {k: {"score": dims[k], "stage": STAGES[lv]} for k, lv in stages.items() if lv is not None},
        "advancement_roadmap": roadmap,
    }


def scorecard(vir: dict, venue_name="Venue") -> str:
    r = classify(vir)
    bars = {0: "█░░░", 1: "██░░", 2: "███░", 3: "████"}
    lines = [f"  VENUE MATURITY SCORECARD — {venue_name}", "  " + "─" * 55]
    for k in WEIGHTS:
        if k in r["dimensions"]:
            info = r["dimensions"][k]
            idx = STAGES.index(info["stage"])
            mark = "   ◀ weakest link" if k in r["weakest_link"] and len(r["weakest_link"]) <= 2 else ""
            lines.append(f"  {k:11} [{bars[idx]}] {info['stage']:13} {str(info['score']):>4}/100{mark}")
    lines.append("  " + "─" * 55)
    nxt = f"        next ▶ {r['next_stage']}" if r["next_stage"] else ""
    lines.append(f"  OVERALL STAGE:  {r['overall_badge']} {r['overall_stage'].upper()}{nxt}")
    if r["weakest_link"]:
        lines.append(f"  Holding you back: {', '.join(r['weakest_link'])}")
    return "\n".join(lines)


if __name__ == "__main__":
    import json, pathlib, sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    path = sys.argv[1] if len(sys.argv) > 1 else str(pathlib.Path(__file__).parent / "vir.example.json")
    vir = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    name = dmi_v1._v(vir, "venue.name") or "Venue"
    print(json.dumps(classify(vir), indent=2, ensure_ascii=False))
    print()
    print(scorecard(vir, name))
