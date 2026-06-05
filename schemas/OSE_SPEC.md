# Opportunity Score Engine (OSE) — Specification v1

**Method id:** `ose_v1` · **Input:** a VIR (+ optional cohort benchmark) · **Output:** estimated missed inquiries / site-visits / bookings / revenue per month, as a **conservative–aggressive range** with a confidence score.

> Discipline: this estimates *lost business*, which is inherently uncertain. So it (a) always returns a **range**, never a single number; (b) caps the upside at a **realistic first-year ceiling** so a severely under-digitised venue can't show a fantasy figure; (c) lowers **confidence** when the inputs are owner-recalled rather than measured. Honest beats impressive.

---

## 1. Mathematical framework — a leaky funnel

```
        DISCOVERY                  CAPTURE            VISIT            BOOK
   reviews · IG · website  ──▶   inquiries   ──▶   site visits  ──▶  bookings ──▶ ₹
        (top of funnel)        lead capture      response speed    follow-up
```

Each weak input leaks demand at a specific stage:

| Input | Stage it leaks | Effect |
|---|---|---|
| Google reviews | Discovery | fewer people shortlist you → **missed inquiries** |
| Instagram activity | Discovery | fewer discover you → **missed inquiries** |
| Website presence | Discovery→Inquiry | weaker trust/info → **missed inquiries** |
| Lead capture (WhatsApp/form) | Inquiry | interested people bounce → **missed inquiries** |
| Response speed | Inquiry→Visit | slow reply loses the visit → **missed site visits** |
| Follow-up | Visit→Booking | no nudge, they go elsewhere → **missed bookings** |

**Variables** (from the VIR):
- `I` = current monthly inquiries (`revenue.inquiry_volume_monthly`)
- `B` = current monthly bookings (`revenue.booking_volume_monthly`)
- `AV` = average booking value (`revenue.avg_booking_value`)
- `conv₀ = B / I` — the venue's **actual** current conversion (anchors the model to reality)
- `v₀ = b₀ = √conv₀` — implied current visit-rate and book-rate (so `v₀·b₀ = conv₀`)

**Severities** `σ ∈ [0,1]` (0 = fine, 1 = worst) — each derived from evidence:
```
σ_reviews  = clamp(1 − reviews / benchmark_reviews)         (benchmark from CIE cohort, default 100)
σ_ig       = clamp(1 − posting_freq / 3)                     (3 posts/wk = healthy)
σ_website  = 1 if no website ; 0.4 if exists but weak ; 0.1 if strong
σ_capture  = fraction of {whatsapp_cta, lead_form, inquiry_form} missing
σ_response = ORD(response_time): 5min .0 · 1hr .2 · 4hr .45 · sameday .65 · nextday .85 · inconsistent .9
σ_followup = ORD(follow_up):   crm_automated 0 · spreadsheet .25 · staff .5 · owner_memory .7 · none 1
```

**Stage equations:**
```
Missed inquiries (per cause c):  ΔIᶜ = I · uplift_maxᶜ · σᶜ        c ∈ {reviews, ig, website, capture}
Missed inquiries (total):        ΔI  = Σ ΔIᶜ
Improved rates:                  v* = min(0.85, v₀ + Δv_max·σ_response)
                                 b* = min(0.85, b₀ + Δb_max·σ_followup)
Potential bookings:              B* = (I + ΔI) · v* · b*
Missed bookings (raw):           ΔB_raw = max(0, B* − B)
Realism ceiling:                 ΔB = min(ΔB_raw, cap · B)
Missed site visits:              ΔV = ΔB / b*
Missed revenue:                  ΔR = ΔB · AV
```
Anchoring `v₀,b₀` to the venue's *measured* conversion is what stops the model from claiming a venue already converting well is "losing everything."

---

## 2. Conservative model (defensible floor)
| Parameter | Value |
|---|---|
| uplift_max — reviews / ig / website / capture | 0.10 / 0.08 / 0.06 / 0.05 |
| Δv_max (response) / Δb_max (follow-up) | 0.05 / 0.05 |
| Realism ceiling `cap` (× current bookings) | **0.30** |
Interpretation: "even on cautious assumptions, you're realistically leaving *at least* this much on the table." Use this number in the printed customer report.

## 3. Aggressive model (upper plausible)
| Parameter | Value |
|---|---|
| uplift_max — reviews / ig / website / capture | 0.25 / 0.22 / 0.18 / 0.15 |
| Δv_max (response) / Δb_max (follow-up) | 0.15 / 0.15 |
| Realism ceiling `cap` (× current bookings) | **0.60** |
Interpretation: "if the turnaround lands well, the upside could be this much." Use internally / as the top of the range — never as a promise.

The two models share identical structure; only the parameters change, so the gap between them *is* the honest uncertainty band.

---

## 4. Confidence score (0–1)
```
conf = base 1.0
     × (0.70 if I is owner-estimated, 1.0 if tracked)
     × (0.80 if AV is estimated)
     × (0.85 if B not measured)
     × input_coverage          (fraction of the 6 severity inputs actually present)
```
- `conf ≥ 0.7` → show the full conservative–aggressive range.
- `0.5 ≤ conf < 0.7` → widen the band, lead with conservative.
- `conf < 0.5` → **present the conservative figure only**, labelled "rough estimate — needs tracked data to sharpen."

Confidence is shown next to the ₹ figure so nobody mistakes an estimate for a measurement.

---

## 5. AI prediction methodology (rules → learned uplift)
**Phase 1 — transparent rules (now).** The `uplift_max` / `cap` parameters above are expert priors. Fully explainable to a consultant; every ₹ traces to a cause.

**Phase 2 — calibrate from outcomes.** SmartOS already tracks real inquiries/bookings. For every venue that fixes a weakness, log the **before→after** lift. That gives `(VIR features at t0) → (realised inquiry/booking lift)` — supervised training data the rule priors get replaced by.

**Phase 3 — causal uplift modelling.** Lost business is a *counterfactual* ("bookings if fixed" − "bookings now"), so use **uplift / treatment-effect models** (T-learner or causal forest): treatment = the intervention, outcome = bookings. This estimates the true incremental effect, not just correlation — and naturally yields the conservative/aggressive band as a prediction interval.

**Phase 4 — Bayesian shrinkage + continuous learning.** Shrink each venue's predicted uplift toward its **CIE cohort prior** when its own history is thin (avoids over-fitting a single venue). Feed the Growth Bible's existing 👍/👎 outcome feedback (the LearningEngine) straight back into the parameters so the engine self-calibrates over time. `method` versioning (`ose_v1` → `ose_v2_model`) lets rule-based and learned models run side by side during validation.

**Guardrails that survive every phase:** the realism `cap`, the conservative-only fallback at low confidence, and "ranges never point estimates" — so even a confident model stays honest.

---

*OSE consumes the VIR; its conservative ₹ figure is what powers the Sales Tool's "What this can become" and the Health Report's revenue opportunity. DMI says how mature, CIE says how you rank, **OSE says what it's costing you.**
