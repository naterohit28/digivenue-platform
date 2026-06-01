from __future__ import annotations


def digistories_score(ig: dict, market: dict) -> float:
    stale = 1 if not ig.get('username') else 0
    low_reels = 1 if ig.get('reel_consistency_score', 0) < 6 else 0
    weak_engagement = 1 if ig.get('emotion_content_score', 0) < 5 else 0
    weak_cta = 1 if ig.get('cta_quality_score', 0) < 6 else 0
    weak_walkthrough = 1 if ig.get('walkthrough_video_score', 0) < 6 else 0
    weak_vendor_ecosystem = 1 if ig.get('vendor_ecosystem_score', 0) < 5 else 0
    portal_dependence = 1 if market.get('marketplace_dependency_score', 0) > 7 else 0
    return round(
        min(
            100,
            (
                stale * 20
                + low_reels * 20
                + weak_engagement * 15
                + weak_cta * 20
                + weak_walkthrough * 15
                + weak_vendor_ecosystem * 10
                + portal_dependence * 10
            ),
        ),
        2,
    )
