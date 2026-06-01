from __future__ import annotations


def analyze_marketplaces(name: str) -> dict:
    seed = sum(ord(c) for c in name) % 7
    return {
        'wedmegood_presence': 1 if seed % 2 == 0 else 0,
        'weddingwire_presence': 1 if seed % 3 == 0 else 0,
        'venuelook_presence': 1 if seed % 4 == 0 else 0,
        'facebook_activity': 1 if seed > 2 else 0,
        'pricing_transparency': 1 if seed in (1, 5, 6) else 0,
        'listing_freshness': 6 + seed,
        'marketplace_dependency_score': max(0, 10 - seed),
    }
