from __future__ import annotations


# ─────────────────────────────────────────────
#  Product recommendation logic
#  Decides whether DigiStories, SmartOS, or
#  both is the right first conversation
# ─────────────────────────────────────────────
def _recommend_product(b: dict, ig: dict, site: dict, digistories_opp: float, smartos_pain: float) -> dict:
    needs_visibility = digistories_opp >= 55
    needs_ops = smartos_pain >= 55

    if needs_visibility and needs_ops:
        product = 'DigiStories + SmartOS'
        reason = (
            'Hall is both digitally invisible and operationally leaky. '
            'Families cannot find them online, and even those who do inquire often fall through the cracks.'
        )
    elif needs_visibility:
        product = 'DigiStories'
        reason = (
            'Hall is losing visibility online — weak Instagram presence, stale Google photos, or no reels. '
            'Families are discovering competitors instead.'
        )
    elif needs_ops:
        product = 'SmartOS'
        reason = (
            'Hall is known locally but losing inquiries due to manual processes — paper diaries, no follow-up system, '
            'fragmented phone numbers.'
        )
    else:
        product = 'DigiStories'
        reason = 'Hall has baseline presence but can improve content quality and booking conversion.'

    return {'recommended_product': product, 'recommendation_reason': reason}


# ─────────────────────────────────────────────
#  Key weakness summary (plain English)
#  Tells the salesperson the top 3 pain points
#  to mention in the first conversation
# ─────────────────────────────────────────────
def _key_weaknesses(b: dict, ig: dict, site: dict) -> list[str]:
    issues = []

    if b.get('review_count', 0) < 20:
        issues.append('Very few Google reviews — families judge trust by review count')
    elif b.get('review_count', 0) < 50:
        issues.append('Low Google review count — needs consistent review collection')

    if not b.get('owner_response_presence'):
        issues.append('Never replies to Google reviews — signals to families that nobody is watching')

    if ig.get('reel_consistency_score', 0) < 4:
        issues.append('No consistent Instagram reels — looks inactive to younger couples doing research')

    if ig.get('real_wedding_score', 0) < 4:
        issues.append('No real wedding photos/videos — only stock or decoration setup shots')

    if not ig.get('whatsapp_cta_presence') and not site.get('whatsapp_cta_presence'):
        issues.append('No WhatsApp CTA anywhere — inquiries have no easy entry point')

    if not site.get('inquiry_form_presence'):
        issues.append('No inquiry form on website — losing leads who visit the site')

    if b.get('photo_count', 0) < 15:
        issues.append('Very few photos on Google listing — hall looks empty and unloved')

    if site.get('website_quality_score', 0) <= 2:
        issues.append('Website is very basic or missing — first impression is poor')

    # Return top 3 most relevant issues
    return issues[:3]


def compute_dmi(b: dict, ig: dict, site: dict, market: dict, weights: dict,
                digistories_opp: float = 0.0, smartos_pain: float = 0.0) -> dict:

    google_trust = min(weights['google_trust_signals'], (b.get('review_count', 0) / 100) * 12 + (b.get('rating', 0) / 5) * 8)

    perception_signal = (
        ig.get('real_wedding_score', 0) * 0.3
        + ig.get('walkthrough_video_score', 0) * 0.25
        + ig.get('cta_quality_score', 0) * 0.25
        + ig.get('emotion_content_score', 0) * 0.2
    )
    instagram_visibility = min(weights['instagram_visibility'], (perception_signal / 10) * weights['instagram_visibility'])

    content_freshness = min(
        weights['content_freshness'],
        ((ig.get('reel_consistency_score', 0) * 0.7 + ig.get('trust_perception_score', 0) * 0.3) / 10)
        * weights['content_freshness'],
    )

    inquiry_cta = weights['inquiry_cta_structure'] if site.get('inquiry_form_presence') else 0
    whatsapp_readiness = weights['whatsapp_readiness'] if (ig.get('whatsapp_cta_presence') or site.get('whatsapp_cta_presence')) else 0
    operational_maturity = min(weights['operational_maturity'], 4 + site.get('website_quality_score', 0) + (5 if b.get('owner_response_presence') else 0))
    review_management = min(weights['review_management'], 2 + (8 if b.get('owner_response_presence') else 0))
    booking_visibility = min(weights['booking_workflow_visibility'], 5 + (5 if site.get('inquiry_form_presence') else 0))

    score = round(
        google_trust + instagram_visibility + content_freshness + inquiry_cta + whatsapp_readiness
        + operational_maturity + review_management + booking_visibility,
        2,
    )

    if score >= 80:
        cat = 'Elite'
    elif score >= 65:
        cat = 'Growth Ready'
    elif score >= 45:
        cat = 'Visibility Weak'
    elif score >= 30:
        cat = 'Operationally Chaotic'
    else:
        cat = 'Digitally Invisible'

    breakdown = {
        'google_trust_signals': round(google_trust, 2),
        'instagram_visibility': round(instagram_visibility, 2),
        'content_freshness': round(content_freshness, 2),
        'inquiry_cta_structure': round(inquiry_cta, 2),
        'whatsapp_readiness': round(whatsapp_readiness, 2),
        'operational_maturity': round(operational_maturity, 2),
        'review_management': round(review_management, 2),
        'booking_workflow_visibility': round(booking_visibility, 2),
    }

    product_rec = _recommend_product(b, ig, site, digistories_opp, smartos_pain)
    weaknesses = _key_weaknesses(b, ig, site)

    return {
        'dmi_score': score,
        'dmi_category': cat,
        'score_breakdown': breakdown,
        'recommended_product': product_rec['recommended_product'],
        'recommendation_reason': product_rec['recommendation_reason'],
        'key_weaknesses': weaknesses,
    }
