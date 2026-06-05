# Historical Venue Health Tracking System (HVT) — Specification v1

**Method id:** `tracker_v1` · **Input:** monthly DMI snapshots per venue · **Output:** trends, growth rates, trajectories, and improvement/decline alerts.

Tracks the six metrics over time — **Discoverability, Trust, Conversion, Operations, Intelligence, and Overall DMI** — so you can prove progress to a pilot venue and catch decline before it churns. Builds on the pipeline's existing append-only `historical/` snapshots.

---

## 1. Database structure

```sql
-- Append-only, one immutable row per venue per month
CREATE TABLE venue_snapshots (
  venue_id        TEXT NOT NULL,
  period          TEXT NOT NULL,        -- 'YYYY-MM' (month key)
  captured_at     TIMESTAMP NOT NULL,
  discoverability REAL, trust REAL, conversion REAL,
  operations REAL, intelligence REAL, dmi REAL,
  maturity_stage  TEXT,                 -- Traditional|Semi-Digital|Modern|Intelligent
  data_completeness REAL,               -- confidence of this snapshot
  method_version  TEXT NOT NULL,        -- 'dmi_v1' — so re-scoring never corrupts history
  vir_ref         TEXT,                 -- pointer to the VIR snapshot that produced this
  PRIMARY KEY (venue_id, period, method_version)
);
CREATE INDEX idx_snap_venue ON venue_snapshots(venue_id, period);

-- Derived trend row per venue/metric/period (recomputed on each new snapshot)
CREATE TABLE venue_trends (
  venue_id TEXT, metric TEXT, period TEXT,
  value REAL, mom_delta REAL, mom_pct REAL,
  rolling_3m REAL, slope_3m REAL, trajectory TEXT,  -- improving|stable|declining
  vs_baseline_pct REAL,
  PRIMARY KEY (venue_id, metric, period)
);

-- Alert feed
CREATE TABLE venue_alerts (
  alert_id TEXT PRIMARY KEY, venue_id TEXT, metric TEXT, period TEXT,
  type TEXT,        -- improvement|decline|sustained_decline|stall|milestone
  severity TEXT,    -- info|warn|critical
  delta REAL, message TEXT, created_at TIMESTAMP,
  acknowledged BOOLEAN DEFAULT 0
);
```

---

## 2. Snapshot architecture
- **Cadence:** one snapshot per venue per calendar month (`period = YYYY-MM`). The monthly job freezes the latest DMI computed from that venue's current VIR.
- **Immutable & keyed by `(venue_id, period, method_version)`** — re-running mid-month upserts *that month* only; history is never overwritten.
- **Method-versioned:** every snapshot records `method_version`. When scoring changes (`dmi_v1`→`dmi_v2`), you re-score historical VIRs into a **parallel series** rather than mutating the old one — so a trend is always apples-to-apples.
- **Provenance:** `vir_ref` points to the exact VIR that produced the snapshot → full time-travel ("why was Trust 24 in March?").
- **Gap handling:** a missing month is left null (not back-filled); trend math skips nulls and flags `data_completeness`. A snapshot with low completeness is marked low-confidence so a data dropout isn't misread as a real decline.

---

## 3. Trend formulas
For each metric series `v₀…vₜ` (x = month index):
```
Month-over-month delta   ΔvₜΩ  = vₜ − vₜ₋₁
MoM growth %             gₜ    = (vₜ − vₜ₋₁) / max(ε, vₜ₋₁) · 100
Rolling 3-month average  R₃ₜ   = mean(vₜ₋₂, vₜ₋₁, vₜ)
Trajectory slope         m     = Σ(xᵢ−x̄)(vᵢ−v̄) / Σ(xᵢ−x̄)²   over last k months (least squares, points/month)
Growth since baseline    Gₜ    = (vₜ / v₀ − 1) · 100
Volatility               s     = stdev(Δvₜ)   (steady vs noisy)
```
**Trajectory label** from slope `m`: `improving` if m ≥ +1.0/mo · `declining` if m ≤ −1.0/mo · else `stable`. Using the *slope* (not just last MoM) smooths one-month noise.

---

## 4. Alert system
Evaluated each new snapshot, per metric **and** overall DMI:

| Alert | Trigger | Severity |
|---|---|---|
| **improvement** | MoM delta ≥ +5 | info |
| **milestone** | band up (red→amber→green) or maturity stage up | info → celebrate with the venue |
| **decline** | MoM delta ≤ −5 | warn |
| **sustained_decline** | ≥ 2 consecutive months declining | critical |
| **stall** | |slope| < 1 for ≥ 3 months **while** DMI < 55 | warn — "paying us, not moving" |
| **band_drop** | band down (green→amber→red) or stage down | critical |

Guardrails: suppress alerts when the snapshot's `data_completeness` is low (avoid false decline from a data gap); **cooldown/dedup** so the same alert doesn't re-fire monthly; `critical` decline/band_drop on an **Active Pilot** flags churn risk to Rohit immediately.

---

## 5. Dashboard structure

**Per-venue (client-facing progress):**
- Line charts: each of the 6 metrics over time + a bold Overall DMI line.
- Growth cards: "DMI +33 since onboarding (+174%)", trajectory badge (↗ Improving).
- Maturity timeline: Traditional → Semi-Digital milestone markers.
- Alert feed (this venue): improvements highlighted to show ROI; declines flagged.
- Before/after sparkline next to each metric.

**Portfolio (Rohit / founder view):**
- Average DMI trend across all active venues.
- **Top improvers** (proof for case studies) and **decliners needing attention** (churn watch).
- Active-pilot board with trajectory arrows; `critical` alerts surfaced first.
- Cohort comparison: how DigiStories pilots trend vs untouched venues (impact evidence).

---

*HVT closes the loop: VIR → DMI → CIE → OSE → VMF give the snapshot; HVT makes it a movie. The improvement signal also feeds the OSE/Strategy LearningEngine — proving which interventions actually move the needle over time.*
