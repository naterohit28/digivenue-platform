# Mumbai Catering & Banquet Digital Readiness System

Production-ready modular pipeline for DigiVenue intelligence, scoring, outreach prioritization, and BCA modernization reporting.

## Quick Start

1. `cd "C:\Users\rohit\Downloads\DigiStories\_Tools\Sales Strategy\mumbai_readiness_system"`
2. `python -m venv .venv`
3. `.\.venv\Scripts\activate`
4. `pip install -r requirements.txt`
5. `python run_pipeline.py`

## Outputs

Primary persistence now lives in:

- `database/mumbai_readiness.db`

The CSV/JSON files below are compatibility exports for sharing, dashboard loading, and manual review. They should not be treated as the system of record.

- `exports/bcda_extracted_leads.json`
- `exports/bcda_extracted_leads.csv`
- `exports/bcda_maturity_index_tracker.json`
- `exports/leads_audit_tracker.json`
- `exports/bcda_statistics.json`
- `exports/daily_outreach_queue.csv`

## Central Database Tables

- `ingestion_runs`: every pipeline execution with status, mode, counts, and config snapshot.
- `processed_snapshots`: full scored business profile for every business in every run.
- `vir_snapshots`: Venue Intelligence Record payloads by run and business.
- `dmi_history`: time-series DMI and dimension scores.
- `competitor_benchmarks`: cohort and 3km radius competitor intelligence.
- `recommendations`: engine recommendations and daily outreach queue scripts.
- `outcome_summaries`: aggregated reply, meeting, and win rates.
- `outcome_events`: raw outreach outcomes imported from feedback CSVs.

This keeps history queryable without passing JSON files between engines.

## Scheduler

- Run daily pipeline scheduler: `python scheduler.py`
- Default jobs:
  - Daily 8:00 AM IST full run
  - Monday 9:00 AM IST weekly strategy refresh

## Dashboard

- `streamlit run dashboard/app.py`

## Notes

- Raw and processed datasets are stored separately (`raw/`, `processed/`).
- Historical intelligence is append-only in SQLite. JSON files in `historical/` are retained only as human-readable audit mirrors.
- Current collectors are mock-safe and structured for swapping in real API/browser collectors.

## Live Collector Mode

1. Set collection_mode to live in configs/settings.json.
2. Set env var GOOGLE_MAPS_API_KEY before run.
3. Run python run_pipeline.py.

If API/network fails, collectors gracefully fall back to mock mode for continuity.


## Google Maps Depth Intelligence
- exports/territory_clusters.json + .csv: suburb-level DMI, review freshness, Instagram activity, operational maturity.
- exports/competitor_radius_map.json: 3km competitor map per venue for sales psychology-led outreach angles.

