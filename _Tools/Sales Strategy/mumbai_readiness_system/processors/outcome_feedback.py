from __future__ import annotations

import csv
from pathlib import Path


def load_outreach_outcomes(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    by_name: dict[str, list[dict]] = {}
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("business_name") or "").strip().lower()
            if not name:
                continue
            by_name.setdefault(name, []).append(row)

    summary: dict[str, dict] = {}
    for name, rows in by_name.items():
        contacted = len(rows)
        replies = sum(1 for r in rows if (r.get("outcome") or "").strip().lower() in {"replied", "meeting_booked", "won"})
        meetings = sum(1 for r in rows if (r.get("outcome") or "").strip().lower() in {"meeting_booked", "won"})
        wins = sum(1 for r in rows if (r.get("outcome") or "").strip().lower() == "won")
        summary[name] = {
            "past_contact_count": contacted,
            "past_reply_count": replies,
            "past_meeting_count": meetings,
            "past_win_count": wins,
            "reply_rate": round((replies / contacted) * 100, 2) if contacted else 0.0,
            "meeting_rate": round((meetings / contacted) * 100, 2) if contacted else 0.0,
            "win_rate": round((wins / contacted) * 100, 2) if contacted else 0.0,
        }
    return summary

