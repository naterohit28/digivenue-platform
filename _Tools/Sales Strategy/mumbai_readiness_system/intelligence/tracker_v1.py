"""
tracker_v1.py — Historical Venue Health Tracking reference.

Given a venue's monthly DMI snapshots, computes per-metric trends (MoM delta,
growth %, rolling avg, least-squares slope, trajectory, growth-since-baseline)
and raises improvement / decline / milestone / stall alerts.

Spec: TRACKER_SPEC.md   ·   Method id: "tracker_v1"
"""
from __future__ import annotations
import statistics

METHOD = "tracker_v1"
METRICS = ["discoverability", "trust", "conversion", "operations", "intelligence", "dmi"]
EPS = 1e-9


def band(dmi):
    if dmi is None:
        return "unknown"
    return "green" if dmi >= 70 else "amber" if dmi >= 40 else "red"

def _slope(values):
    pts = [(i, v) for i, v in enumerate(values) if v is not None]
    n = len(pts)
    if n < 2:
        return 0.0
    xbar = sum(x for x, _ in pts) / n
    ybar = sum(y for _, y in pts) / n
    denom = sum((x - xbar) ** 2 for x, _ in pts)
    if denom == 0:
        return 0.0
    return sum((x - xbar) * (y - ybar) for x, y in pts) / denom

def _trajectory(m):
    return "improving" if m >= 1.0 else "declining" if m <= -1.0 else "stable"


def compute_trends(snapshots: list[dict]) -> dict:
    """snapshots: list sorted by period, each {period, <metric>:value,...}."""
    out = {"method": METHOD, "periods": [s["period"] for s in snapshots], "metrics": {}}
    for m in METRICS:
        series = [s.get(m) for s in snapshots]
        rows = []
        for i, v in enumerate(series):
            prev = series[i - 1] if i > 0 else None
            mom = round(v - prev, 1) if (v is not None and prev is not None) else None
            pct = round((v - prev) / max(EPS, abs(prev)) * 100, 1) if (v is not None and prev not in (None, 0)) else None
            window = [x for x in series[max(0, i - 2):i + 1] if x is not None]
            roll = round(statistics.mean(window), 1) if window else None
            rows.append({"period": snapshots[i]["period"], "value": v, "mom_delta": mom, "mom_pct": pct, "rolling_3m": roll})
        last_k = series[-3:] if len(series) >= 3 else series
        m_slope = round(_slope(last_k), 2)
        first = next((x for x in series if x is not None), None)
        last = next((x for x in reversed(series) if x is not None), None)
        out["metrics"][m] = {
            "points": rows,
            "slope_3m": m_slope,
            "trajectory": _trajectory(m_slope),
            "growth_since_baseline_pct": round((last / first - 1) * 100, 1) if (first not in (None, 0) and last is not None) else None,
            "total_change": round(last - first, 1) if (first is not None and last is not None) else None,
        }
    return out


def detect_alerts(snapshots: list[dict]) -> list[dict]:
    alerts = []

    def add(period, metric, typ, sev, delta, msg):
        alerts.append({"period": period, "metric": metric, "type": typ, "severity": sev, "delta": delta, "message": msg})

    for m in METRICS:
        series = [s.get(m) for s in snapshots]
        consecutive_down = 0
        for i in range(1, len(snapshots)):
            v, prev = series[i], series[i - 1]
            per = snapshots[i]["period"]
            if v is None or prev is None:
                continue
            d = round(v - prev, 1)
            # band / stage transitions (DMI only for band)
            if m == "dmi":
                if band(v) != band(prev):
                    up = ["red", "amber", "green"].index(band(v)) > ["red", "amber", "green"].index(band(prev))
                    if up:
                        add(per, m, "milestone", "info", d, f"DMI crossed into {band(v).upper()} band")
                    else:
                        add(per, m, "band_drop", "critical", d, f"DMI dropped to {band(v).upper()} band")
            if d >= 5:
                add(per, m, "improvement", "info", d, f"{m} up +{d}")
            elif d <= -5:
                add(per, m, "decline", "warn", d, f"{m} down {d}")
            consecutive_down = consecutive_down + 1 if d < 0 else 0
            if consecutive_down >= 2:
                add(per, m, "sustained_decline", "critical", d, f"{m} declining {consecutive_down} months straight")
        # stall: flat slope while DMI below target
        if m == "dmi" and len(series) >= 3:
            recent = [x for x in series[-3:] if x is not None]
            if recent and abs(_slope(recent)) < 1.0 and recent[-1] < 55:
                add(snapshots[-1]["period"], m, "stall", "warn", 0.0, "DMI flat for 3 months and still below 55")

    # maturity stage transitions
    for i in range(1, len(snapshots)):
        a, b = snapshots[i - 1].get("maturity_stage"), snapshots[i].get("maturity_stage")
        if a and b and a != b:
            order = ["Traditional", "Semi-Digital", "Modern", "Intelligent"]
            up = order.index(b) > order.index(a)
            add(snapshots[i]["period"], "maturity", "milestone" if up else "band_drop",
                "info" if up else "critical", 0.0, f"Maturity {a} -> {b}")
    return alerts


def report(snapshots):
    t = compute_trends(snapshots)
    a = detect_alerts(snapshots)
    dmi = t["metrics"]["dmi"]
    return {"trends": t, "alerts": a,
            "summary": {"dmi_trajectory": dmi["trajectory"], "dmi_growth_pct": dmi["growth_since_baseline_pct"],
                        "dmi_total_change": dmi["total_change"], "alert_count": len(a)}}


if __name__ == "__main__":
    import json
    # synthetic DigiStories pilot improving over 6 months
    series = [
        {"period": "2026-01", "discoverability": 25, "trust": 16, "conversion": 29, "operations": 9,  "intelligence": 6,  "dmi": 19, "maturity_stage": "Traditional"},
        {"period": "2026-02", "discoverability": 31, "trust": 22, "conversion": 30, "operations": 12, "intelligence": 8,  "dmi": 24, "maturity_stage": "Traditional"},
        {"period": "2026-03", "discoverability": 42, "trust": 34, "conversion": 33, "operations": 14, "intelligence": 10, "dmi": 31, "maturity_stage": "Traditional"},
        {"period": "2026-04", "discoverability": 55, "trust": 46, "conversion": 41, "operations": 20, "intelligence": 14, "dmi": 41, "maturity_stage": "Semi-Digital"},
        {"period": "2026-05", "discoverability": 63, "trust": 54, "conversion": 48, "operations": 24, "intelligence": 18, "dmi": 47, "maturity_stage": "Semi-Digital"},
        {"period": "2026-06", "discoverability": 68, "trust": 60, "conversion": 52, "operations": 26, "intelligence": 22, "dmi": 52, "maturity_stage": "Semi-Digital"},
    ]
    r = report(series)
    s = r["summary"]
    print(f"DMI trajectory: {s['dmi_trajectory']} | total change {s['dmi_total_change']} ({s['dmi_growth_pct']}%) | {s['alert_count']} alerts\n")
    print("Alerts:")
    for al in r["alerts"]:
        if al["metric"] in ("dmi", "maturity"):
            print(f"  [{al['severity']:8}] {al['period']} {al['type']:18} {al['message']}")
