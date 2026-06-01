from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup


def _mock_profile(name: str, pitch_strategy: str = '') -> dict:
    seed = sum(ord(c) for c in name) % 10
    var = seed  # 0-9 for variety

    # ── Pitch-aware scoring ───────────────────────────────────────
    # DigiStories → bad Instagram (that's the problem we're solving)
    # SmartOS     → decent Instagram, bad operations
    # Both        → bad Instagram AND bad operations
    if 'digistories' in pitch_strategy.lower() and 'smartos' not in pitch_strategy.lower():
        # Has some presence but content is weak / stale
        has_profile = True
        real_wedding    = max(1, 2 + var % 3)       # 1-4 (bad)
        reels           = max(1, 1 + var % 3)       # 1-3 (very bad)
        cta_quality     = max(1, 2 + var % 3)       # 1-4
        walkthrough     = max(1, 2 + var % 3)       # 1-4
        emotion         = max(1, 2 + var % 4)       # 1-4
        vendor          = max(1, 2 + var % 4)       # 1-4
        whatsapp        = 0
        followers       = 80 + var * 30             # 80-350 (small)
        post_count      = 8 + var * 2               # few posts
        reel_count      = var % 3                   # 0-2 reels only
        last_post_days  = 45 + var * 8              # stale
    elif 'smartos' in pitch_strategy.lower() and 'digistories' not in pitch_strategy.lower():
        # Has decent Instagram, just needs operations
        has_profile = True
        real_wedding    = 6 + var % 3               # 6-8
        reels           = 5 + var % 4               # 5-8
        cta_quality     = 5 + var % 4               # 5-8
        walkthrough     = 5 + var % 3               # 5-7
        emotion         = 6 + var % 3               # 6-8
        vendor          = 5 + var % 4               # 5-8
        whatsapp        = 1 if var % 2 == 0 else 0
        followers       = 400 + var * 120           # 400-1480
        post_count      = 55 + var * 8
        reel_count      = 8 + var
        last_post_days  = 5 + var * 3               # recent
    else:
        # Both — worst of all worlds
        has_profile = var % 4 != 0                  # some don't even have a profile
        real_wedding    = max(0, 1 + var % 2)       # 0-2
        reels           = max(0, var % 2)           # 0-1
        cta_quality     = max(0, 1 + var % 2)       # 0-2
        walkthrough     = max(0, var % 2)           # 0-1
        emotion         = max(0, 1 + var % 2)       # 0-2
        vendor          = max(0, 1 + var % 3)       # 0-3
        whatsapp        = 0
        followers       = max(0, 50 + var * 20)
        post_count      = max(0, 4 + var)
        reel_count      = 0
        last_post_days  = 80 + var * 5              # very stale

    if not has_profile:
        return {
            'platform': 'instagram', 'username': None, 'followers': 0,
            'following': 0, 'post_count': 0, 'reel_count': 0,
            'last_post_date': None, 'last_reel_date': None,
            'avg_views': 0, 'avg_engagement': 0, 'highlight_count': 0,
            'whatsapp_cta_presence': 0, 'bio_quality': 0, 'tagged_vendors': 0,
            'instagram_confidence_score': 0.35,
            'real_wedding_score': 0, 'reel_consistency_score': 0,
            'cta_quality_score': 0, 'walkthrough_video_score': 0,
            'emotion_content_score': 0, 'vendor_ecosystem_score': 0,
            'trust_perception_score': 0,
        }

    from datetime import date, timedelta
    last_post = (date.today() - timedelta(days=last_post_days)).isoformat()
    trust = round((real_wedding + cta_quality + walkthrough + emotion) / 4, 2)

    return {
        'platform': 'instagram',
        'username': name.lower().replace(' ', '')[:20],
        'followers': followers,
        'following': 250,
        'post_count': post_count,
        'reel_count': reel_count,
        'last_post_date': last_post,
        'last_reel_date': last_post,
        'avg_views': max(0, 200 + var * 50),
        'avg_engagement': round(max(0.5, 1.0 + var * 0.15), 2),
        'highlight_count': max(0, var % 4),
        'whatsapp_cta_presence': whatsapp,
        'bio_quality': max(1, 3 + var % 4),
        'tagged_vendors': max(0, var % 5),
        'instagram_confidence_score': 0.45,
        'real_wedding_score': real_wedding,
        'reel_consistency_score': reels,
        'cta_quality_score': cta_quality,
        'walkthrough_video_score': walkthrough,
        'emotion_content_score': emotion,
        'vendor_ecosystem_score': vendor,
        'trust_perception_score': trust,
    }


def collect_instagram_profile(name: str, website_hint: str | None = None, mode: str = 'mock',
                               timeout_sec: int = 12, pitch_strategy: str = '') -> dict:
    if mode != 'live':
        return _mock_profile(name, pitch_strategy=pitch_strategy)

    handle = name.lower().replace(' ', '').replace('&', '')
    if len(handle) < 3:
        return _mock_profile(name)

    url = f'https://www.instagram.com/{handle}/'
    try:
        r = requests.get(url, timeout=timeout_sec, headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code >= 400:
            return _mock_profile(name)
        soup = BeautifulSoup(r.text, 'html.parser')

        desc = soup.find('meta', attrs={'name': 'description'})
        desc_text = desc.get('content', '') if desc else ''

        followers = 0
        following = 0
        post_count = 0
        m = re.search(r'([\d,.]+)\sFollowers,\s([\d,.]+)\sFollowing,\s([\d,.]+)\sPosts', desc_text)
        if m:
            followers = int(float(m.group(1).replace(',', '')))
            following = int(float(m.group(2).replace(',', '')))
            post_count = int(float(m.group(3).replace(',', '')))

        bio_quality = 7 if len(desc_text) > 80 else 4 if len(desc_text) > 30 else 2
        page_text = r.text.lower()
        whatsapp_cta = 1 if 'whatsapp' in page_text or 'wa.me' in page_text else 0

        real_wedding = 8 if any(k in page_text for k in ('wedding', 'bride', 'groom', 'shaadi')) else 3
        reel_consistency = 8 if '/reel/' in page_text else 4
        cta_quality = 8 if whatsapp_cta else (5 if 'book' in page_text or 'enquiry' in page_text else 2)
        walkthrough = 8 if any(k in page_text for k in ('walkthrough', 'venue tour', 'hall tour')) else 4
        emotion = 7 if any(k in page_text for k in ('happy', 'celebration', 'love', 'family')) else 4
        vendor = 7 if any(k in page_text for k in ('decor', 'makeup', 'photography', 'planner')) else 3
        trust = round((real_wedding + cta_quality + walkthrough + emotion) / 4, 2)

        return {
            'platform': 'instagram',
            'username': handle,
            'followers': followers,
            'following': following,
            'post_count': post_count,
            'reel_count': max(0, min(post_count, int(post_count * 0.3))),
            'last_post_date': None,
            'last_reel_date': None,
            'avg_views': 0,
            'avg_engagement': 0,
            'highlight_count': 0,
            'whatsapp_cta_presence': whatsapp_cta,
            'bio_quality': bio_quality,
            'tagged_vendors': 0,
            'instagram_confidence_score': 0.6,
            'real_wedding_score': real_wedding,
            'reel_consistency_score': reel_consistency,
            'cta_quality_score': cta_quality,
            'walkthrough_video_score': walkthrough,
            'emotion_content_score': emotion,
            'vendor_ecosystem_score': vendor,
            'trust_perception_score': trust,
        }
    except Exception:
        return _mock_profile(name)
