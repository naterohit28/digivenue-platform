from __future__ import annotations

import math
from datetime import datetime


def _parse_coords(raw: str | None) -> tuple[float, float] | None:
    if not raw or "," not in raw:
        return None
    try:
        lat_s, lng_s = raw.split(",", 1)
        return float(lat_s.strip()), float(lng_s.strip())
    except Exception:
        return None


def _haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    r = 6371.0
    lat1, lon1 = math.radians(a[0]), math.radians(a[1])
    lat2, lon2 = math.radians(b[0]), math.radians(b[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def build_territory_clusters(rows: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        suburb = row.get("suburb") or "Unknown"
        grouped.setdefault(suburb, []).append(row)

    clusters = []
    for suburb, items in grouped.items():
        total = len(items)
        avg_dmi = sum(x.get("dmi_score", 0) for x in items) / total if total else 0
        avg_reviews = sum(x.get("review_count", 0) for x in items) / total if total else 0
        ig_active = sum(1 for x in items if x.get("username"))
        avg_ops = sum(x.get("smartos_readiness_score", 0) for x in items) / total if total else 0
        fresh_reviews = sum(1 for x in items if x.get("latest_review_date"))
        clusters.append(
            {
                "suburb": suburb,
                "total_businesses": total,
                "avg_dmi_score": round(avg_dmi, 2),
                "avg_review_count": round(avg_reviews, 2),
                "instagram_activity_pct": round((ig_active / total) * 100, 2) if total else 0,
                "review_freshness_pct": round((fresh_reviews / total) * 100, 2) if total else 0,
                "avg_operational_maturity": round(avg_ops, 2),
                "updated_at": datetime.utcnow().isoformat(timespec="seconds"),
            }
        )
    clusters.sort(key=lambda x: x["avg_dmi_score"], reverse=True)
    return clusters


def build_competitor_radius_map(rows: list[dict], radius_km: float = 3.0) -> list[dict]:
    points = []
    for row in rows:
        coords = _parse_coords(row.get("coordinates"))
        if not coords:
            continue
        points.append((row, coords))

    out = []
    for base_row, base_coords in points:
        nearby = []
        for other_row, other_coords in points:
            if base_row["business_name"] == other_row["business_name"]:
                continue
            distance = _haversine_km(base_coords, other_coords)
            if distance <= radius_km:
                nearby.append(
                    {
                        "business_name": other_row["business_name"],
                        "suburb": other_row.get("suburb"),
                        "distance_km": round(distance, 2),
                        "dmi_score": other_row.get("dmi_score"),
                        "dmi_category": other_row.get("dmi_category"),
                    }
                )
        nearby.sort(key=lambda x: x["distance_km"])
        out.append(
            {
                "business_name": base_row["business_name"],
                "suburb": base_row.get("suburb"),
                "radius_km": radius_km,
                "competitor_count": len(nearby),
                "competitors": nearby,
                "sales_angle": (
                    f"{len(nearby)} nearby competitors within {radius_km} km are competing for the same inquiry pool."
                ),
            }
        )
    return out
