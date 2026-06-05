"""
cie_v1.py — Competitive Intelligence Engine reference.

Given a target venue and a store of venue_metrics, builds the right peer cohort
(with sparse-area fallback), benchmarks every metric (venue vs area avg vs leader
+ midrank percentile), and returns a composite Competitive Index.

Pure-Python reference. The percentile + aggregate maths map directly to SQL /
t-digest sketches for 500k venues (see CIE_SPEC.md).
"""
from __future__ import annotations
import statistics

METHOD = "cie_v1"
MIN_N = 8  # minimum cohort size before falling back a level

# metric -> weight for the composite Competitive Index
METRICS = {
    "reviews": 20, "rating": 15, "photos": 12,
    "ig_followers": 13, "ig_activity": 15, "website_quality": 12, "trust_signals": 13,
}


# ── Cohort selection with fallback ────────────────────────────────
def _key(*parts):
    return "|".join(str(p).strip().lower() for p in parts)

def build_cohort(venues, target, min_n=MIN_N):
    """Return (cohort_list, level, cohort_key). Falls back L0->L1->L2->L3 until min_n met."""
    levels = [
        ("L0", _key(target["city"], target["area"], target["venue_type"]),
         lambda v: v["city"] == target["city"] and v["area"] == target["area"] and v["venue_type"] == target["venue_type"]),
        ("L1", _key(target["city"], target["venue_type"]),
         lambda v: v["city"] == target["city"] and v["venue_type"] == target["venue_type"]),
        ("L2", _key(target["city"]),
         lambda v: v["city"] == target["city"]),
        ("L3", _key(target["venue_type"]),
         lambda v: v["venue_type"] == target["venue_type"]),
    ]
    chosen = None
    for level, ckey, pred in levels:
        cohort = [v for v in venues if pred(v)]
        chosen = (cohort, level, ckey)
        if len(cohort) >= min_n:
            break
    return chosen


# ── Percentile (midrank, tie-safe) ────────────────────────────────
def percentile(value, values):
    if value is None or not values:
        return None
    below = sum(1 for x in values if x is not None and x < value)
    equal = sum(1 for x in values if x is not None and x == value)
    n = sum(1 for x in values if x is not None)
    return round(100.0 * (below + 0.5 * equal) / n, 1) if n else None


def band(pct):
    if pct is None:
        return "unknown"
    return "green" if pct > 66 else "amber" if pct >= 33 else "red"


def _agg(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return {
        "n": len(vals),
        "mean": round(statistics.mean(vals), 1),
        "median": round(statistics.median(vals), 1),
        "p75": round(_quantile(vals, 0.75), 1),
        "max": max(vals),
    }

def _quantile(vals, q):
    s = sorted(vals)
    if len(s) == 1:
        return s[0]
    pos = q * (len(s) - 1)
    lo = int(pos)
    frac = pos - lo
    return s[lo] + frac * (s[min(lo + 1, len(s) - 1)] - s[lo])


def compare(target, venues):
    cohort, level, ckey = build_cohort(venues, target)
    # include the target in its own cohort distribution
    ids = {v["venue_id"] for v in cohort}
    if target["venue_id"] not in ids:
        cohort = cohort + [target]
    cohort_conf = round(min(1.0, len(cohort) / 25.0), 2)

    out_metrics = {}
    weighted, wsum = 0.0, 0.0
    for m, w in METRICS.items():
        values = [v.get(m) for v in cohort]
        a = _agg(values)
        if not a:
            continue
        v = target.get(m)
        pct = percentile(v, values)
        leader_id = None
        for c in cohort:
            if c.get(m) == a["max"]:
                leader_id = c["venue_id"]; break
        out_metrics[m] = {
            "venue": v, "area_avg": a["mean"], "area_median": a["median"],
            "area_leader": a["max"], "leader_venue_id": leader_id,
            "catch_up_target": a["median"],
            "vs_avg_ratio": round(v / a["mean"], 2) if (v is not None and a["mean"]) else None,
            "gap_to_leader": round(a["max"] - v, 1) if v is not None else None,
            "percentile": pct, "band": band(pct),
        }
        if pct is not None:
            weighted += w * pct; wsum += w

    cidx = round(weighted / wsum, 1) if wsum else None
    pos = ("Leader" if cidx >= 80 else "Strong" if cidx >= 60 else "Average"
           if cidx >= 40 else "Weak" if cidx >= 20 else "Laggard") if cidx is not None else "Unknown"
    scored = [(m, d["percentile"]) for m, d in out_metrics.items() if d["percentile"] is not None]
    biggest_gap = min(scored, key=lambda x: x[1])[0] if scored else None
    strength = max(scored, key=lambda x: x[1])[0] if scored else None

    return {
        "method": METHOD, "venue_id": target["venue_id"],
        "cohort": {"key": ckey, "level": level, "size": len(cohort), "confidence": cohort_conf},
        "competitive_index": cidx, "position": pos,
        "biggest_gap": biggest_gap, "strength": strength,
        "metrics": out_metrics,
    }


if __name__ == "__main__":
    import json, random
    random.seed(7)
    # synthetic Andheri banquet cohort
    venues = []
    for i in range(14):
        venues.append({
            "venue_id": f"andheri_banquet_{i}", "city": "Mumbai", "area": "Andheri", "venue_type": "banquet",
            "reviews": random.choice([90, 150, 260, 300, 420, 600, 900, 2100, 180, 240, 330, 510, 70, 130]),
            "rating": round(random.uniform(3.6, 4.9), 1),
            "photos": random.randint(20, 300), "ig_followers": random.randint(200, 9000),
            "ig_activity": round(random.uniform(0.2, 5.0), 1), "website_quality": random.randint(0, 95),
            "trust_signals": random.randint(0, 30),
        })
    target = {"venue_id": "target_hall", "city": "Mumbai", "area": "Andheri", "venue_type": "banquet",
              "reviews": 112, "rating": 3.8, "photos": 30, "ig_followers": 280,
              "ig_activity": 0.3, "website_quality": 0, "trust_signals": 1}
    print(json.dumps(compare(target, venues), indent=2))
