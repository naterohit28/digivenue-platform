from __future__ import annotations


def build_statistics(rows: list[dict]) -> dict:
    total = len(rows)
    invisible = len([r for r in rows if r['dmi_category'] == 'Digitally Invisible'])
    weak = len([r for r in rows if r['dmi_category'] in ('Visibility Weak', 'Operationally Chaotic')])
    active = len([r for r in rows if r['dmi_category'] in ('Growth Ready', 'Elite')])
    avg_reviews = round(sum(r.get('review_count', 0) for r in rows) / total, 2) if total else 0
    avg_rating = round(sum(float(r.get('rating', 0) or 0) for r in rows) / total, 2) if total else 0
    return {
        'total_audited': total,
        'invisible_count': invisible,
        'invisible_pct': round((invisible / total) * 100, 2) if total else 0,
        'weak_count': weak,
        'weak_pct': round((weak / total) * 100, 2) if total else 0,
        'active_count': active,
        'active_pct': round((active / total) * 100, 2) if total else 0,
        'pct_needing_modernization': round(((invisible + weak) / total) * 100, 2) if total else 0,
        'average_reviews': avg_reviews,
        'average_rating': avg_rating,
    }
