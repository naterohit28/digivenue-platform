from __future__ import annotations


def data_quality_grade(row: dict) -> dict:
    g = float(row.get("google_confidence_score", 0))
    w = float(row.get("confidence_score", 0))
    i = float(row.get("instagram_confidence_score", 0))
    avg = (g + w + i) / 3
    if avg >= 0.75:
        grade = "A"
    elif avg >= 0.5:
        grade = "B"
    else:
        grade = "C"
    return {"data_quality_score": round(avg, 2), "data_quality_grade": grade}


def conversion_likelihood(row: dict) -> dict:
    # Outcome feedback has top weight, then pain/opportunity fit.
    reply_rate = float(row.get("reply_rate", 0))
    meeting_rate = float(row.get("meeting_rate", 0))
    pain_fit = min(100.0, float(row.get("digistories_opportunity_score", 0)) * 0.5 + (100 - float(row.get("smartos_readiness_score", 0))) * 0.5)
    relationship_fit = (
        float(row.get("growth_hungry_signal") or 0) * 20
        + float(row.get("modernization_mindset_score") or 0) * 4
        + float(row.get("bca_regular_presence") or 0) * 10
    )
    score = min(100.0, reply_rate * 0.35 + meeting_rate * 0.25 + pain_fit * 0.3 + relationship_fit * 0.1)
    band = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
    return {"conversion_likelihood_score": round(score, 2), "conversion_likelihood_band": band}

