"""
ose_v1.py — Opportunity Score Engine reference.

Estimates monthly business lost to weak digital presence as a conservative-
aggressive range, with a confidence score. Anchors to the venue's MEASURED
conversion and caps upside at a realistic ceiling so it never over-promises.

Spec: OSE_SPEC.md   ·   Method id: "ose_v1"
"""
from __future__ import annotations
import math

METHOD = "ose_v1"

PARAMS = {
    "conservative": {
        "uplift": {"reviews": 0.10, "ig": 0.08, "website": 0.06, "capture": 0.05},
        "dv": 0.05, "db": 0.05, "cap": 0.30,
    },
    "aggressive": {
        "uplift": {"reviews": 0.25, "ig": 0.22, "website": 0.18, "capture": 0.15},
        "dv": 0.15, "db": 0.15, "cap": 0.60,
    },
}
ORD_RESPONSE = {"5min": 0.0, "1hr": 0.2, "4hr": 0.45, "sameday": 0.65, "nextday": 0.85, "inconsistent": 0.9}
ORD_FOLLOWUP = {"crm_automated": 0.0, "spreadsheet": 0.25, "staff": 0.5, "owner_memory": 0.7, "none": 1.0}


def _v(vir, path):
    node = vir
    for k in path.split("."):
        if not isinstance(node, dict) or k not in node:
            return None
        node = node[k]
    return node["value"] if isinstance(node, dict) and "value" in node else node

def _src(vir, path):
    node = vir
    for k in path.split("."):
        if not isinstance(node, dict) or k not in node:
            return None
        node = node[k]
    return node.get("source") if isinstance(node, dict) else None

def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def _severities(vir, benchmark_reviews=100):
    reviews = _v(vir, "google_business.total_reviews")
    freq = _v(vir, "instagram.posting_frequency")
    web_exists = _v(vir, "website.exists")
    web_q = _v(vir, "website.seo_score")
    ctas = [_v(vir, "instagram.whatsapp_cta"), _v(vir, "conversion_systems.lead_form"), _v(vir, "website.inquiry_form")]
    resp = _v(vir, "conversion_systems.response_time")
    fup = _v(vir, "conversion_systems.follow_up_system")

    s, present = {}, {}
    s["reviews"] = _clamp(1 - (reviews / benchmark_reviews)) if reviews is not None else 0.6
    present["reviews"] = reviews is not None
    s["ig"] = _clamp(1 - (freq / 3.0)) if freq is not None else 0.6
    present["ig"] = freq is not None
    if web_exists is None:
        s["website"], present["website"] = 0.6, False
    elif not web_exists:
        s["website"], present["website"] = 1.0, True
    else:
        s["website"], present["website"] = (0.4 if (web_q or 0) < 60 else 0.1), True
    cta_known = [c for c in ctas if c is not None]
    s["capture"] = (sum(1 for c in cta_known if not c) / len(cta_known)) if cta_known else 0.6
    present["capture"] = len(cta_known) > 0
    s["response"] = ORD_RESPONSE.get(resp, 0.55); present["response"] = resp in ORD_RESPONSE
    s["followup"] = ORD_FOLLOWUP.get(fup, 0.6); present["followup"] = fup in ORD_FOLLOWUP
    return s, present


def _scenario(name, I, B, AV, conv0, sev):
    p = PARAMS[name]
    v0 = b0 = math.sqrt(conv0)
    per_cause = {c: round(I * p["uplift"][c] * sev[c], 1) for c in p["uplift"]}
    dI = sum(per_cause.values())
    v_star = min(0.85, v0 + p["dv"] * sev["response"])
    b_star = min(0.85, b0 + p["db"] * sev["followup"])
    B_star = (I + dI) * v_star * b_star
    dB_raw = max(0.0, B_star - B)
    dB = min(dB_raw, p["cap"] * B)          # realism ceiling
    dV = dB / b_star if b_star else 0.0
    dR = dB * AV
    return {
        "missed_inquiries": round(dI, 1),
        "missed_inquiries_by_cause": per_cause,
        "missed_site_visits": round(dV, 1),
        "missed_bookings": round(dB, 1),
        "missed_revenue": round(dR),
        "capped": dB < dB_raw - 0.01,
    }


def _confidence(vir, present):
    conf = 1.0
    if _src(vir, "revenue.inquiry_volume_monthly") in (None, "pipeline_estimate", "owner_reported"):
        conf *= 0.70
    if _src(vir, "revenue.avg_booking_value") in (None, "pipeline_estimate"):
        conf *= 0.80
    if _v(vir, "revenue.booking_volume_monthly") is None:
        conf *= 0.85
    coverage = sum(1 for k in present if present[k]) / len(present)
    conf *= coverage
    return round(_clamp(conf), 2)


def compute_opportunity(vir: dict, benchmark_reviews: int = 100) -> dict:
    I = _v(vir, "revenue.inquiry_volume_monthly")
    if not I:
        return {"method": METHOD, "error": "inquiry_volume_monthly required to estimate opportunity"}
    B = _v(vir, "revenue.booking_volume_monthly")
    AV = _v(vir, "revenue.avg_booking_value") or 0
    conv0 = _v(vir, "revenue.conversion_rate") or (B / I if B else 0.16)
    conv0 = _clamp(conv0, 0.02, 0.9)
    if not B:
        B = I * conv0

    sev, present = _severities(vir, benchmark_reviews)
    conf = _confidence(vir, present)
    cons = _scenario("conservative", I, B, AV, conv0, sev)
    agg = _scenario("aggressive", I, B, AV, conv0, sev)

    advisory = ("full_range" if conf >= 0.7 else "lead_conservative" if conf >= 0.5 else "conservative_only")
    return {
        "method": METHOD,
        "inputs": {"inquiries": I, "bookings": round(B, 1), "avg_value": AV, "current_conversion": round(conv0, 3)},
        "confidence": conf, "advisory": advisory,
        "conservative": cons, "aggressive": agg,
        "headline_revenue_range": [cons["missed_revenue"], agg["missed_revenue"]],
    }


def _inr(n):
    return f"Rs {n/100000:.1f}L" if n >= 100000 else f"Rs {n:,.0f}"

if __name__ == "__main__":
    import json, pathlib, sys
    path = sys.argv[1] if len(sys.argv) > 1 else str(pathlib.Path(__file__).parent / "vir.example.json")
    vir = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    r = compute_opportunity(vir)
    print(json.dumps(r, indent=2))
    if "headline_revenue_range" in r:
        lo, hi = r["headline_revenue_range"]
        print(f"\nMISSED REVENUE: {_inr(lo)} - {_inr(hi)} per month  (confidence {r['confidence']}, {r['advisory']})")
        print("Cause breakdown (conservative missed inquiries):")
        for c, n in r["conservative"]["missed_inquiries_by_cause"].items():
            print(f"  {c:9} -> {n} missed inquiries/mo")
