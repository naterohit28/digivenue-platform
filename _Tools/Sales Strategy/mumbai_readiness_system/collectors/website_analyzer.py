from __future__ import annotations

import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


WA_PATTERNS = ('wa.me', 'api.whatsapp.com', 'whatsapp://send')
FORM_HINTS = ('book', 'enquiry', 'inquiry', 'quote', 'contact')
GALLERY_HINTS = ('gallery', 'wedding', 'events', 'decor', 'banquet')
SERVICE_HINTS = ('hall', 'catering', 'decor', 'package', 'menu', 'capacity')


def _safe_get(url: str, timeout_sec: int) -> tuple[str, float]:
    r = requests.get(url, timeout=timeout_sec, headers={'User-Agent': 'Mozilla/5.0'})
    r.raise_for_status()
    return r.text, r.elapsed.total_seconds()


def analyze_website(url: str | None, timeout_sec: int = 10, mode: str = 'mock') -> dict:
    if not url:
        return {
            'mobile_responsive': 0,
            'page_speed_score': 0,
            'whatsapp_cta_presence': 0,
            'inquiry_form_presence': 0,
            'gallery_freshness_score': 0,
            'seo_metadata_score': 0,
            'https_usage': 0,
            'social_links_count': 0,
            'services_count': 0,
            'website_quality_score': 0,
            'confidence_score': 0.3,
        }

    if mode != 'live':
        https = 1 if url.startswith('https://') else 0
        return {
            'mobile_responsive': 1,
            'page_speed_score': 68,
            'whatsapp_cta_presence': 1,
            'inquiry_form_presence': 1,
            'gallery_freshness_score': 6,
            'seo_metadata_score': 6,
            'https_usage': https,
            'social_links_count': 3,
            'services_count': 4,
            'website_quality_score': 8 if https else 4,
            'confidence_score': 0.65,
        }

    try:
        html, elapsed = _safe_get(url, timeout_sec)
        soup = BeautifulSoup(html, 'html.parser')
        html_lower = html.lower()

        has_viewport = 1 if soup.find('meta', attrs={'name': re.compile('viewport', re.I)}) else 0
        https_usage = 1 if urlparse(url).scheme == 'https' else 0

        links = [a.get('href', '').lower() for a in soup.find_all('a', href=True)]
        whatsapp_cta = 1 if any(any(p in l for p in WA_PATTERNS) for l in links) else 0

        forms = soup.find_all('form')
        form_text = ' '.join(f.get_text(' ', strip=True).lower() for f in forms)
        inquiry_form = 1 if forms and any(h in form_text for h in FORM_HINTS) else (1 if forms else 0)

        social_links = sum(1 for l in links if any(x in l for x in ('instagram.com', 'facebook.com', 'youtube.com')))

        gallery_signals = sum(1 for hint in GALLERY_HINTS if hint in html_lower)
        services_signals = sum(1 for hint in SERVICE_HINTS if hint in html_lower)

        title = soup.title.string.strip() if soup.title and soup.title.string else ''
        has_meta_desc = 1 if soup.find('meta', attrs={'name': re.compile('description', re.I)}) else 0
        seo = min(10, (4 if title else 0) + (4 if has_meta_desc else 0) + (2 if social_links > 0 else 0))

        speed_score = max(10, min(100, int(100 - elapsed * 18)))

        website_quality = 0
        website_quality += 2 if has_viewport else 0
        website_quality += 2 if inquiry_form else 0
        website_quality += 2 if whatsapp_cta else 0
        website_quality += 2 if seo >= 6 else 0
        website_quality += 2 if speed_score >= 60 else 0

        confidence = 0.85
        return {
            'mobile_responsive': has_viewport,
            'page_speed_score': speed_score,
            'whatsapp_cta_presence': whatsapp_cta,
            'inquiry_form_presence': inquiry_form,
            'gallery_freshness_score': min(10, gallery_signals),
            'seo_metadata_score': seo,
            'https_usage': https_usage,
            'social_links_count': social_links,
            'services_count': services_signals,
            'website_quality_score': website_quality,
            'confidence_score': confidence,
        }
    except Exception:
        return {
            'mobile_responsive': 0,
            'page_speed_score': 0,
            'whatsapp_cta_presence': 0,
            'inquiry_form_presence': 0,
            'gallery_freshness_score': 0,
            'seo_metadata_score': 0,
            'https_usage': 0,
            'social_links_count': 0,
            'services_count': 0,
            'website_quality_score': 0,
            'confidence_score': 0.2,
        }
