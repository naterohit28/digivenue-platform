# Digital Maturity Index (DMI) — Scoring Specification v1

**Method id:** `dmi_v1` · **Input:** a Venue Intelligence Record (VIR) · **Output:** 0–100 DMI + 5 dimension scores + RAG bands + confidence.

> Design principle: **every dimension score is a weighted average of normalised, evidence-backed variables.** No variable is a raw opinion — each maps to a VIR field with a defined normalisation curve and threshold. Missing data lowers *confidence*, it does not silently score 0.

---

## 0. Normalisation primitives (raw value → 0–100 sub-score)

| Type | Use for | Formula |
|---|---|---|
| **SAT(x90)** | unbounded counts (reviews, photos, followers) | `S = 100 · (1 − e^(−2.3026 · x / x90))`, clamp 0–100. *(x90 = the value that scores 90.)* |
| **BAND(anchors)** | ratings, rates with known breakpoints | piecewise lookup (tables below) |
| **ORD(map)** | ordinal enums (follow-up system, calendar) | direct enum→score lookup |
| **BOOL** | yes/no signals | `value ? 100 : 0` |
| **RATE** | 0–1 fractions (response rate) | `min(100, value · 100)` |
| **LIN(min,max)** | bounded counts (reporting 0–7) | `100 · (x − min)/(max − min)`, clamp |
| **MEAN_BOOL** | a set of booleans (CTAs) | `100 · (#true / #total)` |

SAT is the workhorse: smooth, saturating, vectorisable, and impossible to game past 100.

---

## 1. Complete scoring matrix

### Dimension 1 — Discoverability *(can customers find them?)*
| Variable | VIR field | Weight | Normaliser |
|---|---|---|---|
| Google reviews (count) | `google_business.total_reviews` | 18 | SAT(100) |
| Google rating | `google_business.rating` | 10 | BAND_RATING |
| Google photos | `google_business.total_photos` | 14 | SAT(50) |
| Google claimed | `google_business.claimed` | 8 | BOOL |
| Google posts (90d) | `google_business.posts_published` | 6 | SAT(8) |
| Instagram posting frequency | `instagram.posting_frequency` (/wk) | 16 | SAT(3) |
| Instagram reels | `instagram.reels_count` | 8 | SAT(12) |
| Instagram reach | `instagram.followers` | 6 | SAT(2000) |
| Website presence | `website.exists` + `website.seo_score` | 14 | `exists?60:0 + 0.4·seo_score` |
| **Total** | | **100** | |

### Dimension 2 — Trust *(do they trust it once found?)*
| Variable | VIR field | Weight | Normaliser |
|---|---|---|---|
| Rating quality | `google_business.rating` | 18 | BAND_RATING |
| Review volume credibility | `google_business.total_reviews` | 14 | SAT(80) |
| Review freshness | `google_business.review_velocity` (/mo) | 16 | SAT(4) |
| Owner response rate | `google_business.review_response_rate` | 16 | RATE |
| Real wedding content | `trust_signals.wedding_albums + video_testimonials` | 20 | SAT(8) |
| Social proof | `trust_signals.testimonials + media_mentions + influencer_mentions` | 16 | SAT(10) |
| **Total** | | **100** | |

### Dimension 3 — Conversion *(inquiries → bookings?)*
| Variable | VIR field | Weight | Normaliser |
|---|---|---|---|
| Response speed | `conversion_systems.response_time`* | 20 | ORD_RESPONSE |
| Follow-up system | `conversion_systems.follow_up_system` | 20 | ORD_FOLLOWUP |
| Inquiry-capture CTAs | `instagram.whatsapp_cta`, `conversion_systems.lead_form`, `website.inquiry_form` | 18 | MEAN_BOOL |
| Conversion rate | `revenue.conversion_rate` | 20 | BAND_CONV |
| WhatsApp automation | `conversion_systems.whatsapp_automation` | 12 | BOOL |
| Lost-inquiry awareness | `conversion_systems.lost_inquiry_awareness`* | 10 | BOOL |
| **Total** | | **100** | |

### Dimension 4 — Operations *(can they manage growth?)*
| Variable | VIR field | Weight | Normaliser |
|---|---|---|---|
| Inquiry tracking | `conversion_systems.inquiry_tracking` | 25 | ORD_TRACKING |
| Booking calendar | `operations.calendar_management` | 25 | ORD_CALENDAR |
| Reporting visibility | `operations.reporting` (0–7) | 20 | LIN(0,7) |
| SmartOS / CRM usage | `operations.smartos_usage` | 15 | BOOL |
| Payment / vendor systematisation | `operations.payment_systematised`* | 15 | MEAN_BOOL |
| **Total** | | **100** | |

### Dimension 5 — Intelligence *(do they measure & use data?)*
| Variable | VIR field | Weight | Normaliser |
|---|---|---|---|
| Conversion-rate tracking | `revenue.conversion_rate.source ≠ estimate` | 30 | BOOL |
| Inquiry-source tracking | `intelligence.tracks_sources`* | 25 | BOOL |
| Reporting depth | `operations.reporting` (0–7) | 25 | LIN(0,7) |
| Data-driven cadence | `intelligence.reviews_metrics`* | 20 | ORD_CADENCE |
| **Total** | | **100** | |

\* fields marked with `*` are optional VIR extensions; when absent they simply drop out of the weighted average (see §3).

### Lookup tables
```
BAND_RATING : rating <4.0 → 20 · 4.0–4.2 → 55 · 4.3–4.5 → 80 · ≥4.5 → 100
BAND_CONV   : conv  <0.10 → 20 · 0.10–0.20 → 45 · 0.20–0.35 → 70 · ≥0.35 → 100
ORD_RESPONSE: 5min 100 · 1hr 80 · 4hr 55 · sameday 35 · nextday 15 · inconsistent 10
ORD_FOLLOWUP: none 0 · owner_memory 30 · staff 50 · spreadsheet 75 · crm_automated 100
ORD_TRACKING: memory 0 · paper 20 · diary 35 · excel 60 · gsheet 80 · crm 100
ORD_CALENDAR: diary 0 · wall 25 · excel 55 · gcal 80 · software 100
ORD_CADENCE : never 0 · ad_hoc 40 · monthly 75 · weekly 100
```

---

## 2. Weightage table (dimension level)

| Dimension | Weight | Rationale |
|---|---|---|
| Discoverability | **25%** | No discovery = no inquiries; biggest top-of-funnel lever |
| Trust | **20%** | Converts discovery into a shortlist |
| Conversion | **25%** | Where most venues bleed; biggest revenue lever |
| Operations | **20%** | Caps how much growth they can absorb |
| Intelligence | **10%** | Leading indicator; small weight, high future value |
| **Total** | **100%** | |

---

## 3. Formula

**Step 1 — variable sub-score:** `s_i = normalise_i(raw_i)` → 0–100.

**Step 2 — dimension score (missing-data-safe):**
```
Dim_d = Σ_i∈present (w_i · s_i) / Σ_i∈present w_i
Conf_d = Σ_i∈present w_i / Σ_i∈all w_i        (0–1, data completeness for the dimension)
```
Re-normalising over *present* variables means a venue is never punished for data you simply haven't collected yet — the uncertainty shows up in `Conf_d`, not the score.

**Step 3 — final DMI (two supported modes):**
```
Plain (default):       DMI = Σ_d (W_d · Dim_d) / Σ_d W_d
Confidence-weighted:   DMI = Σ_d (W_d · Conf_d · Dim_d) / Σ_d (W_d · Conf_d)
Overall confidence:    DMI_conf = Σ_d (W_d · Conf_d) / Σ_d W_d
```
Use **plain** for customer-facing reports (stable, explainable); use **confidence-weighted** for internal ranking of 100k venues so well-measured venues aren't out-ranked by thinly-measured ones.

---

## 4. 0–100 score logic
- Every sub-score, every dimension, and the final DMI live on the **same 0–100 scale** — directly comparable.
- Counts use **saturating** curves so an outlier (e.g. 5,000 reviews) can't blow past 100 or dominate.
- A venue with literally no digital footprint scores ~0; a fully systematised, highly-visible, well-reviewed, data-driven venue approaches 100.

---

## 5. Red / Amber / Green thresholds
Applied identically to each **dimension** and to the **overall DMI**:

| Band | Range | Meaning |
|---|---|---|
| 🔴 **Red** | 0–39 | Critical gap — losing business now |
| 🟠 **Amber** | 40–69 | Functional but leaking; clear upside |
| 🟢 **Green** | 70–100 | Strong; optimise & scale |

Optional finer maturity labels (overall DMI): Foundational 0–30 · Emerging 31–55 · Established 56–75 · Strong 76–90 · Dominant 91+.

A dimension with `Conf_d < 0.4` should render its band greyed/"low confidence" rather than coloured — never show a confident colour on thin data.

---

## 6. Final DMI calculation (worked logic)
```
DMI = 0.25·Discoverability + 0.20·Trust + 0.25·Conversion + 0.20·Operations + 0.10·Intelligence
```
(weights already sum to 1.0, so no division needed in plain mode).

**Worked example** — actual output of `dmi_v1.py` on the Swayambhu VIR:
Discoverability 25.3, Trust 16.3, Conversion 28.6, Operations 9.2, Intelligence 6.5
→ `0.25·25.3 + 0.20·16.3 + 0.25·28.6 + 0.20·9.2 + 0.10·6.5` → **DMI = 19.2 (🔴 Red)**, overall confidence 0.83.
A synthetic fully-modern venue scores **98.9 (🟢 Green)** — confirming the index spans the full range.

---

## Robustness for 100,000 venues
1. **Vectorisable maths only.** SAT/BAND/ORD/LIN all map to numpy/SQL `CASE`/`np.select` — score the whole table in one pass, no per-venue Python loop required.
2. **Deterministic & versioned.** `dmi_v1` is pure (same input → same output); bump the version to re-score history and A/B old vs new without data loss.
3. **Missing-data-safe by construction.** Re-normalised weights + per-dimension confidence mean partial records score sensibly; you can launch on Google-only data and enrich later.
4. **Saturating curves prevent gaming & outliers.** No single mega-metric can dominate the index.
5. **Config-driven, not hard-coded.** Weights, x90 anchors, and lookup tables live in one config block — tune them centrally, recompute everyone.
6. **Confidence-weighted ranking mode** keeps thinly-measured venues from polluting the top of a 100k leaderboard.
7. **Auditable.** Each dimension exposes its contributing variables and weights, so any score can be explained to a consultant or an owner.

*DMI v1 consumes the VIR schema (`vir.schema.json`). Dimension scores write back into the VIR `dimensions` block with `method: "dmi_v1"` and `evidence_refs` to the fields above.*
