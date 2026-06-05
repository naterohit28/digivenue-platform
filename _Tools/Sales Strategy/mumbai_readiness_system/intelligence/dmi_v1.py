"""
dmi_v1.py — Digital Maturity Index reference scorer.

Consumes a Venue Intelligence Record (VIR) and produces a 0-100 DMI plus five
evidence-backed dimension scores, each with a confidence (data completeness).

Pure-Python, config-driven, deterministic. Every formula is vectorisable to
numpy/SQL for 100k+ venues; this reference keeps it readable.

Spec: DMI_SCORING_SPEC.md   ·   Method id: "dmi_v1"
"""
from __future__ import annotations
import math
from typing import Any

METHOD = "dmi_v1"

# ── Normalisers (raw value -> 0..100) ─────────────────────────────
def SAT(x, x90):
    if x is None:
        return None
    return max(0.0, min(100.0, 100.0 * (1 - math.exp(-2.3026 * x / x90))))

def BOOL(x):
    if x is None:
        return None
    return 100.0 if x else 0.0

def RATE(x):  # 0..1 -> 0..100
    if x is None:
        return None
    return max(0.0, min(100.0, x * 100.0))

def LIN(x, lo, hi):
    if x is None:
        return None
    return max(0.0, min(100.0, 100.0 * (x - lo) / (hi - lo)))

def BAND(x, anchors):  # anchors: list of (threshold, score) ascending; first match by upper bound
    if x is None:
        return None
    for hi, sc in anchors:
        if x < hi:
            return float(sc)
    return float(anchors[-1][1])

def ORD(x, mapping):
    if x is None:
        return None
    return float(mapping.get(x, 0))

BAND_RATING = [(4.0, 20), (4.3, 55), (4.5, 80), (float("inf"), 100)]
BAND_CONV   = [(0.10, 20), (0.20, 45), (0.35, 70), (float("inf"), 100)]
ORD_FOLLOWUP = {"none": 0, "owner_memory": 30, "staff": 50, "spreadsheet": 75, "crm_automated": 100}
ORD_TRACKING = {"memory": 0, "paper": 20, "diary": 35, "excel": 60, "gsheet": 80, "crm": 100}
ORD_CALENDAR = {"diary": 0, "wall": 25, "excel": 55, "gcal": 80, "software": 100}
ORD_RESPONSE = {"5min": 100, "1hr": 80, "4hr": 55, "sameday": 35, "nextday": 15, "inconsistent": 10}
ORD_CADENCE  = {"never": 0, "ad_hoc": 40, "monthly": 75, "weekly": 100}


# ── VIR helpers ───────────────────────────────────────────────────
def _v(vir, path):
    """Read a VIR field. Evidence-wrapped values return their .value; plain values pass through."""
    node = vir
    for key in path.split("."):
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    if isinstance(node, dict) and "value" in node:
        return node["value"]
    return node

def _src(vir, path):
    node = vir
    for key in path.split("."):
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node.get("source") if isinstance(node, dict) else None

def _mean_bool(vals):
    present = [1.0 if v else 0.0 for v in vals if v is not None]
    return (100.0 * sum(present) / len(present)) if present else None


# ── Dimension variable builders: each returns list of (weight, subscore) ──
def _discoverability(vir):
    seo = _v(vir, "website.seo_score")
    web = None
    if _v(vir, "website.exists") is not None:
        web = (60.0 if _v(vir, "website.exists") else 0.0) + 0.4 * (seo or 0)
        web = min(100.0, web)
    return [
        (18, SAT(_v(vir, "google_business.total_reviews"), 100)),
        (10, BAND(_v(vir, "google_business.rating"), BAND_RATING)),
        (14, SAT(_v(vir, "google_business.total_photos"), 50)),
        (8,  BOOL(_v(vir, "google_business.claimed"))),
        (6,  SAT(_v(vir, "google_business.posts_published"), 8)),
        (16, SAT(_v(vir, "instagram.posting_frequency"), 3)),
        (8,  SAT(_v(vir, "instagram.reels_count"), 12)),
        (6,  SAT(_v(vir, "instagram.followers"), 2000)),
        (14, web),
    ]

def _trust(vir):
    albums = (_v(vir, "trust_signals.wedding_albums") or 0) + (_v(vir, "trust_signals.video_testimonials") or 0) \
             if (_v(vir, "trust_signals.wedding_albums") is not None or _v(vir, "trust_signals.video_testimonials") is not None) else None
    proof = None
    parts = [_v(vir, "trust_signals.testimonials"), _v(vir, "trust_signals.media_mentions"), _v(vir, "trust_signals.influencer_mentions")]
    if any(p is not None for p in parts):
        proof = sum(p or 0 for p in parts)
    return [
        (18, BAND(_v(vir, "google_business.rating"), BAND_RATING)),
        (14, SAT(_v(vir, "google_business.total_reviews"), 80)),
        (16, SAT(_v(vir, "google_business.review_velocity"), 4)),
        (16, RATE(_v(vir, "google_business.review_response_rate"))),
        (20, SAT(albums, 8)),
        (16, SAT(proof, 10)),
    ]

def _conversion(vir):
    ctas = _mean_bool([_v(vir, "instagram.whatsapp_cta"), _v(vir, "conversion_systems.lead_form"), _v(vir, "website.inquiry_form")])
    return [
        (20, ORD(_v(vir, "conversion_systems.response_time"), ORD_RESPONSE)),
        (20, ORD(_v(vir, "conversion_systems.follow_up_system"), ORD_FOLLOWUP)),
        (18, ctas),
        (20, BAND(_v(vir, "revenue.conversion_rate"), BAND_CONV)),
        (12, BOOL(_v(vir, "conversion_systems.whatsapp_automation"))),
        (10, BOOL(_v(vir, "conversion_systems.lost_inquiry_awareness"))),
    ]

def _operations(vir):
    return [
        (25, ORD(_v(vir, "conversion_systems.inquiry_tracking"), ORD_TRACKING)),
        (25, ORD(_v(vir, "operations.calendar_management"), ORD_CALENDAR)),
        (20, LIN(_v(vir, "operations.reporting"), 0, 7)),
        (15, BOOL(_v(vir, "operations.smartos_usage"))),
        (15, BOOL(_v(vir, "operations.payment_systematised"))),
    ]

def _intelligence(vir):
    tracks_conv = None
    if _v(vir, "revenue.conversion_rate") is not None:
        tracks_conv = _src(vir, "revenue.conversion_rate") not in (None, "pipeline_estimate", "unknown")
    return [
        (30, BOOL(tracks_conv)),
        (25, BOOL(_v(vir, "intelligence.tracks_sources"))),
        (25, LIN(_v(vir, "operations.reporting"), 0, 7)),
        (20, ORD(_v(vir, "intelligence.reviews_metrics"), ORD_CADENCE)),
    ]

DIMENSIONS = {
    "discoverability": (_discoverability, 0.25),
    "trust":           (_trust,          0.20),
    "conversion":      (_conversion,     0.25),
    "operations":      (_operations,     0.20),
    "intelligence":    (_intelligence,   0.10),
}

def band(score):
    if score is None:
        return "unknown"
    return "green" if score >= 70 else "amber" if score >= 40 else "red"


def compute_dmi(vir: dict, mode: str = "plain") -> dict:
    """Return {dmi, band, confidence, dimensions:{...}} for one VIR. mode: 'plain' or 'confidence'."""
    dims = {}
    for name, (builder, _w) in DIMENSIONS.items():
        rows = builder(vir)
        present = [(w, s) for (w, s) in rows if s is not None]
        wsum = sum(w for w, _ in present)
        score = round(sum(w * s for w, s in present) / wsum, 1) if wsum else None
        conf = round(wsum / sum(w for w, _ in rows), 2) if rows else 0.0
        dims[name] = {"score": score, "band": band(score), "confidence": conf}

    W = {k: w for k, (_b, w) in DIMENSIONS.items()}
    if mode == "confidence":
        num = sum(W[k] * dims[k]["confidence"] * (dims[k]["score"] or 0) for k in dims)
        den = sum(W[k] * dims[k]["confidence"] for k in dims) or 1
        dmi = num / den
    else:  # plain
        num = sum(W[k] * (dims[k]["score"] or 0) for k in dims if dims[k]["score"] is not None)
        den = sum(W[k] for k in dims if dims[k]["score"] is not None) or 1
        dmi = num / den
    dmi = round(dmi, 1)
    overall_conf = round(sum(W[k] * dims[k]["confidence"] for k in dims) / sum(W.values()), 2)
    return {"method": METHOD, "dmi": dmi, "band": band(dmi), "confidence": overall_conf, "dimensions": dims}


if __name__ == "__main__":
    import json, sys, pathlib
    path = sys.argv[1] if len(sys.argv) > 1 else str(pathlib.Path(__file__).parent / "vir.example.json")
    vir = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    out = compute_dmi(vir)
    print(json.dumps(out, indent=2))
