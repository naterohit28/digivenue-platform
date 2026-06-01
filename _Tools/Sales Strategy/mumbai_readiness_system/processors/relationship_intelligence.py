from __future__ import annotations

import csv
from pathlib import Path


def load_relationship_intelligence(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    out: dict[str, dict] = {}
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("business_name") or "").strip().lower()
            if not name:
                continue
            out[name] = row
    return out
