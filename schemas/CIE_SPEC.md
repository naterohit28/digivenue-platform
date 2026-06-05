# Competitive Intelligence Engine (CIE) — Specification v1

**Method id:** `cie_v1` · **Input:** a target venue + the VIR/metric store · **Output:** per-metric `{venue, area_avg, area_leader, percentile}` + a composite Competitive Index, for any of 500k venues.

> Core idea: a number is meaningless alone. **112 reviews is great in a sleepy suburb and terrible on Link Road.** The CIE answers "compared to *who*?" by defining the right peer cohort, then ranking the venue inside it.

---

## 1. Complete architecture

```
                 ┌─────────────┐     ETL      ┌──────────────────┐
   VIR store ───▶│  venue_     │────────────▶ │  cohort_stats     │  (nightly batch)
  (per venue)    │  metrics    │   aggregate  │  precomputed      │
                 └─────────────┘              │  distributions    │
                        │                     │  + quantile sketch│
                        │                     └──────────────────┘
                        ▼                              │
        on-demand compare(target_venue)  ◀────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────────────┐
        │  Competitive Report                            │
        │  per metric: venue · area_avg · leader · pctl  │
        │  composite: Competitive Index + position band  │
        └───────────────────────────────────────────────┘
```

**Two-phase by design (the scalability key):**
1. **Batch (heavy, infrequent):** roll every venue's metrics up into **precomputed cohort distributions** — one row per `(cohort, metric)` holding mean/median/p25/p75/p90/max/leader and a quantile sketch.
2. **Serve (light, frequent):** comparing one venue is then `O(metrics)` lookups against the stored distribution — **never a live scan of the cohort.** A 500k-venue compare costs the same as a 50-venue compare.

**Cohort definition with fallback** (so sparse areas still get a meaningful peer set):
```
L0: (city, area, venue_type)      ← ideal
L1: (city, venue_type)            ← if L0 has < MIN_N (e.g. 8)
L2: (city)                        ← if L1 still sparse
L3: (venue_type, region)          ← last resort
```
The report always states which cohort level + size was used, and a `cohort_confidence` (rises with N).

---

## 2. Database schema

```sql
-- One denormalised row per venue (fed from the VIR store)
CREATE TABLE venue_metrics (
  venue_id        TEXT PRIMARY KEY,
  city            TEXT NOT NULL,
  area            TEXT NOT NULL,
  venue_type      TEXT NOT NULL,
  reviews         INTEGER,      -- google_business.total_reviews
  rating          REAL,         -- google_business.rating
  photos          INTEGER,      -- google_business.total_photos
  ig_followers    INTEGER,      -- instagram.followers
  ig_activity     REAL,         -- instagram.posting_frequency (posts/wk)
  website_quality REAL,         -- 0-100 (website.seo_score + presence)
  trust_signals   INTEGER,      -- testimonials+albums+mentions
  updated_at      TIMESTAMP
);
CREATE INDEX idx_vm_cohort ON venue_metrics(city, area, venue_type);

-- Precomputed cohort distributions (the materialised heart of the engine)
CREATE TABLE cohort_stats (
  cohort_key      TEXT NOT NULL,   -- e.g. 'mumbai|andheri|banquet'
  cohort_level    TEXT NOT NULL,   -- L0|L1|L2|L3
  metric          TEXT NOT NULL,
  n               INTEGER,
  mean            REAL,
  p25             REAL,
  p50             REAL,            -- median
  p75             REAL,
  p90             REAL,
  max             REAL,
  leader_venue_id TEXT,
  sketch          BLOB,            -- t-digest / KLL quantile sketch for exact-ish percentiles
  updated_at      TIMESTAMP,
  PRIMARY KEY (cohort_key, metric)
);

-- Optional: cached per-venue competitive snapshot for dashboards
CREATE TABLE competitive_snapshots (
  venue_id     TEXT, cohort_key TEXT, metric TEXT,
  value        REAL, percentile REAL, vs_avg_ratio REAL,
  gap_to_leader REAL, band TEXT, computed_at TIMESTAMP,
  PRIMARY KEY (venue_id, metric)
);
```

---

## 3. Ranking methodology
For each metric (all "higher is better" here):
- **Area average** = cohort `mean` (report median too — robust to a single 2,100-review outlier).
- **Area leader** = cohort `max` (+ `leader_venue_id` so the rep can name them).
- **vs-average ratio** = `value / mean` (e.g. 0.34× = a third of the field).
- **gap to leader** = `max − value`.
- **Percentile** = the venue's standing in the distribution (§4).
- **Per-metric band:** 🔴 percentile < 33 · 🟠 33–66 · 🟢 > 66.

**Composite Competitive Index** (0–100) = weighted average of per-metric **percentiles**:
| Metric | Weight |
|---|---|
| Reviews | 20 |
| Rating | 15 |
| Photos | 12 |
| Instagram followers | 13 |
| Instagram activity | 15 |
| Website quality | 12 |
| Trust signals | 13 |

`Competitive Index = Σ(wᵢ · percentileᵢ) / Σwᵢ` (over metrics with data).
Position band: **Leader** 80–100 · **Strong** 60–79 · **Average** 40–59 · **Weak** 20–39 · **Laggard** 0–19.

---

## 4. Percentile calculations
**Definition (midrank, handles ties):**
```
percentile(v) = 100 · ( (#peers with value < v) + 0.5·(#peers with value = v) ) / N
```
- Robust to ties (two venues with identical reviews share a fair rank).
- At 500k scale, computed against the cohort's **quantile sketch** (t-digest) instead of re-sorting — O(1) lookup, ~1% error, mergeable across shards.
- **Small-cohort guard:** if `N < MIN_N`, fall back one cohort level and tag `cohort_confidence` lower; never report a confident percentile from 3 peers.

*Worked example (Reviews):* Venue = 112, Area Avg = 325, Leader = 2100, and 112 sits above ~18% of the cohort → **Percentile 18% (🔴)** — "you're in the bottom fifth of your area on reviews; the leader has ~19× yours."

---

## 5. Benchmarking logic
For the consultation, each metric renders as one honest line:
```
Reviews     112  │  area avg 325  │  leader 2100  │  18th percentile  🔴
Rating      3.8  │  area avg 4.3  │  leader 4.9   │  21st percentile  🔴
IG activity 0.2  │  area avg 1.8  │  leader 5.0   │  12th percentile  🔴
```
Plus three roll-ups:
- **Biggest competitive gap** = metric with the lowest percentile (where they're losing most ground).
- **Closest to parity** = highest percentile (a strength to protect).
- **Catch-up target** = the cohort `p50`/`p75` value per weak metric ("get to 325 reviews to reach the middle of your area") — concrete, never "do more marketing."

---

## 6. Scalability for 500,000 venues
1. **Precompute, don't scan.** Cohort distributions are materialised nightly; a compare is `O(#metrics)` lookups regardless of cohort size.
2. **Quantile sketches (t-digest / KLL).** Store a small mergeable sketch per `(cohort, metric)` → exact-ish percentiles without holding every value; sketches **merge across shards**, so cohorts can be aggregated in parallel.
3. **Partition by city.** `venue_metrics` and the batch job shard cleanly by city; Mumbai never blocks Pune.
4. **Incremental refresh.** Only recompute cohorts whose members changed since last run (dirty-flagging), not all 500k nightly.
5. **Cohort fallback hierarchy** keeps long-tail/sparse areas meaningful instead of erroring on N=2.
6. **Deterministic & versioned** (`cie_v1`) — re-rank history when weights/curves change, A/B old vs new.
7. **Read-path cache.** `competitive_snapshots` caches dashboard reports; invalidated only when the venue or its cohort stats change.

*CIE consumes the same VIR evidence as the DMI; `venue_metrics` is a thin projection of the VIR, and the Competitive Index slots beside the DMI as the venue's **relative** maturity (DMI = absolute, CIE = vs peers).*
