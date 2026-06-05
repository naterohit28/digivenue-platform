# DigiVenue Validation Framework — "Designed → Proven"

**Goal:** validate VIR, DMI, CIE, OSE, VMF, REC against **20 real Mumbai venues** in **30 days**, producing a per-engine pass/fail certification with a measured confidence level.

**Ground truth:** the founder (Rohit, 13-yr operator) is the expert labeller, **kept blind to engine outputs** during labelling to prevent anchoring. For data facts, a manual audit of each venue's live Google/Instagram/website is the truth.

**The 20-venue sample (stratified):** 4–5 suburbs × venue types × a spread of apparent maturity (some strong, some weak) so every score band and cohort is represented. Avoids validating only on easy cases.

---

## Per-engine validation

### VIR — *did we capture reality correctly?* (data accuracy)
1. **Methodology:** Manually audit each venue's live profiles; record true values for the key fields (reviews, rating, photos, IG followers/activity, website exists/quality). Compare field-by-field to the generated VIR.
2. **Success criteria:** ≥ **90%** of *factual* fields match (within tolerance: counts ±10%, booleans exact); ≥ 80% field coverage; provenance tags correct.
3. **Accuracy metrics:** per-field accuracy %, mean absolute % error for counts, coverage %, provenance-correctness %.
4. **Calibration:** fix any systematic mapping error (e.g., posting-frequency proxy biased low); recalibrate the estimate heuristics for fields we can't yet collect live.
5. **Feedback:** one manual-audit row per venue in the ground-truth sheet.
6. **Confidence scoring:** verify low-`confidence` flags actually coincide with the wrong/missing fields (a confidence tag that lies is worse than no tag).

### DMI — *does the score match expert judgment?* (score validity)
1. **Methodology:** Rohit rates each venue's digital maturity 0–100 (and per pillar) **blind**; compare to DMI.
2. **Success criteria:** **Pearson r ≥ 0.80**, **MAE ≤ 10** points, **RAG-band agreement ≥ 80%**.
3. **Accuracy metrics:** Pearson & Spearman correlation, MAE, RMSE, band confusion matrix, systematic bias (mean signed error).
4. **Calibration:** if a consistent offset/bias appears, retune dimension weights and normaliser `x90` anchors; re-score; re-measure.
5. **Feedback:** expert 0–100 ratings sheet.
6. **Confidence scoring:** confirm DMI `confidence` correlates with data completeness and with absolute error (low confidence → larger errors expected).

### CIE — *is the competitive ranking real?* (rank validity)
1. **Methodology:** Within 2–3 cohorts (e.g. Vashi banquets), Rohit ranks "who's winning online" blind; spot-check absolute numbers (leader reviews, area average) against live Google.
2. **Success criteria:** **Spearman ρ ≥ 0.75** within cohort; **leader correctly identified ≥ 80%**; percentile error ≤ 10 points vs recomputed truth.
3. **Accuracy metrics:** Spearman ρ per cohort, top-1 / top-3 leader hit rate, mean percentile error.
4. **Calibration:** adjust the composite metric weights if a metric is over/under-driving rank.
5. **Feedback:** per-cohort expert ranking sheet.
6. **Confidence scoring:** check cohort-size confidence vs ranking stability (small cohorts should flag lower).

### OSE — *is the ₹ figure believable?* (plausibility now, realised later)
1. **Methodology — two stages.** *Stage 1 (30 days):* Rohit (operator expertise) rates each conservative range **Plausible / Too high / Too low**; sanity-check it never exceeds a realistic ceiling vs the venue's actual scale. *Stage 2 (longitudinal):* for pilot venues entering SmartOS, compare predicted recoverable revenue to **realised** booking lift over the following months (via HVT).
2. **Success criteria:** ≥ **80% rated Plausible**; **0 absurd outputs** (e.g. > current revenue); directional correctness (weaker venues → larger opportunity) ≥ 90%.
3. **Accuracy metrics:** % plausible, % absurd, directional-correctness %, and (Stage 2) MAPE of predicted vs realised recovered revenue.
4. **Calibration:** tune `uplift_max` and the realism `cap` from expert feedback first, then from realised outcomes (the real calibration).
5. **Feedback:** expert plausibility sheet; later, realised booking data from pilots.
6. **Confidence scoring:** confirm `conservative_only` advisory fires whenever inputs are estimated (it must, until SmartOS supplies real volumes).

### VMF — *is the maturity stage right?* (classification accuracy)
1. **Methodology:** Rohit labels each venue Traditional / Semi-Digital / Modern / Intelligent **blind**; compare to VMF, including the weakest-link call.
2. **Success criteria:** **exact-stage agreement ≥ 75%**, **within-one-stage ≥ 95%**, weakest-link agreement ≥ 70%.
3. **Accuracy metrics:** classification accuracy, off-by-one rate, Cohen's κ (chance-corrected), confusion matrix.
4. **Calibration:** adjust stage band thresholds and the Technology/Leadership mapping if misclassifications cluster.
5. **Feedback:** stage-label sheet.
6. **Confidence scoring:** validate the gating logic (a venue with a Modern pillar but Traditional foundation should stay Traditional — confirm experts agree with the gate).

### REC — *are the recommendations what an expert would do?* (relevance now, lift later)
1. **Methodology — two stages.** *Stage 1:* Rohit independently writes his top-3 "fix first" actions per venue **blind**; compare to REC's top-3. *Stage 2:* for executed actions on pilots, measure realised ΔDMI / Δbookings via the Growth Bible 👍/👎 loop + HVT.
2. **Success criteria:** **precision@3 ≥ 0.70** (≥ 2 of 3 REC actions in the expert's set); **#1-action agreement ≥ 60%**; 0 nonsensical actions.
3. **Accuracy metrics:** precision@3, recall vs expert list, #1-match rate, relevance %, and (Stage 2) realised-uplift accuracy.
4. **Calibration:** adjust action applicability/effort priors; then replace the simulated uplift with a model trained on realised outcomes.
5. **Feedback:** expert top-3 sheet; executed-action outcomes.
6. **Confidence scoring:** recompute each action's `history_factor` from realised success once outcomes accrue (the engine self-calibrates).

---

## The 30-day validation plan

| Week | Phase | Activities | Output |
|---|---|---|---|
| **1** | **Set up & generate** | Select the stratified 20; build the blind ground-truth instruments (audit sheet + expert rating/label/ranking/top-3 forms); run the pipeline to generate VIR→REC for all 20; freeze outputs (`method_version` tagged) | 20 frozen intelligence records + empty ground-truth sheets |
| **2** | **Collect ground truth (blind)** | Manual field audits (VIR truth); Rohit's 0–100 ratings (DMI), stage labels (VMF), cohort rankings (CIE), plausibility ratings (OSE), top-3 fixes (REC). A 2nd auditor double-labels ~5 venues to measure inter-rater reliability | Completed ground-truth dataset |
| **3** | **Measure & calibrate** | Run the validation harness → per-engine scorecard vs success criteria; identify systematic biases; retune weights/anchors/thresholds; re-score; re-measure (calibration loop, 1–2 iterations) | Calibrated `*_v1.1` configs + before/after scorecard |
| **4** | **Re-validate, certify, seed longitudinal** | Confirm criteria met post-calibration; lock certified configs; write the **Validation Report** (pass/fail + confidence per engine); enrol ~5 venues into SmartOS to begin **realised-outcome** validation of OSE & REC over the following months | "Proven" certification + longitudinal pilot live |

```
Wk1 Generate     [██░░░░░░]
Wk2 Ground truth [░░██░░░░]
Wk3 Calibrate    [░░░░██░░]
Wk4 Certify      [░░░░░░██] ──▶ longitudinal (months) validates OSE & REC on realised outcomes
```

---

## Instruments (kept blind)
- **Manual audit sheet** (VIR truth): venue → true reviews, rating, photos, IG followers, IG posts/wk, website exists/quality.
- **Expert rating sheet** (DMI/VMF): venue → 0–100 maturity, per-pillar, stage label.
- **Cohort ranking sheet** (CIE): per cohort → ranked list + named leader.
- **Plausibility sheet** (OSE): venue → Plausible / Too high / Too low.
- **Top-3 fixes sheet** (REC): venue → expert's first three actions.

---

## "Proven" certification bar
An engine is **certified** only when it meets *all* its success criteria on the 20-venue set after at most two calibration passes. System-level KPI: **all six engines certified** → DigiVenue is a *proven* intelligence system, with a published confidence level per engine and a documented calibration history.

> **What stays open after 30 days (and that's correct):** OSE and REC have a *predictive* component that only **time + realised SmartOS outcomes** can fully validate. The 30-day plan proves *plausibility and expert-agreement* now, and *seeds* the longitudinal proof that closes over the following months via HVT — turning the validation itself into the first turn of the learning flywheel.
