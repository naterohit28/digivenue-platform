from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def compute_delta(current_rows: list[dict], previous_path: Path) -> dict:
    prev = {}
    if previous_path.exists():
        prev_data = json.loads(previous_path.read_text(encoding='utf-8'))
        prev = {x['business_name']: x for x in prev_data}

    alerts = []
    for row in current_rows:
        old = prev.get(row['business_name'])
        if not old:
            alerts.append({'business_name': row['business_name'], 'alert': 'New venue discovered'})
            continue
        move = row['dmi_score'] - old.get('dmi_score', 0)
        if move >= 10:
            alerts.append({'business_name': row['business_name'], 'alert': 'Modernization movement +10 DMI'})
        if row.get('review_count', 0) - old.get('review_count', 0) >= 20:
            alerts.append({'business_name': row['business_name'], 'alert': 'Review spike detected'})

    return {'run_at': datetime.utcnow().isoformat(timespec='seconds'), 'alerts': alerts}
