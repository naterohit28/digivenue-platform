# Mumbai Catering & Banquet Digital Readiness System

Production-ready modular pipeline for DigiVenue intelligence, scoring, outreach prioritization, and BCA modernization reporting.

## Quick Start

1. `cd "C:\Users\rohit\Downloads\DigiStories\Sales Strategy\mumbai_readiness_system"`
2. `python -m venv .venv`
3. `.\.venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. `python run_pipeline.py`

## Outputs

- `exports/bcda_extracted_leads.json`
- `exports/bcda_extracted_leads.csv`
- `exports/bcda_maturity_index_tracker.json`
- `exports/leads_audit_tracker.json`
- `exports/bcda_statistics.json`
- `exports/daily_outreach_queue.csv`

## Scheduler

- Run daily pipeline scheduler: `python scheduler.py`
- Default jobs:
  - Daily 8:00 AM IST full run
  - Monday 9:00 AM IST weekly strategy refresh

## Dashboard

- `streamlit run dashboard/app.py`

## Notes

- Raw and processed datasets are stored separately (`raw/`, `processed/`).
- Historical snapshots are append-only (`historical/`).
- Current collectors are mock-safe and structured for swapping in real API/browser collectors.

## Live Collector Mode

1. Set collection_mode to live in configs/settings.json.
2. Set env var GOOGLE_MAPS_API_KEY before run.
3. Run python run_pipeline.py.

If API/network fails, collectors gracefully fall back to mock mode for continuity.


## Google Maps Depth Intelligence
- exports/territory_clusters.json + .csv: suburb-level DMI, review freshness, Instagram activity, operational maturity.
- exports/competitor_radius_map.json: 3km competitor map per venue for sales psychology-led outreach angles.

