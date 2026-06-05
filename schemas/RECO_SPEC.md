# AI Recommendation Engine (REC) — Specification v1

**Method id:** `reco_v1` · **Input:** a VIR · **Output:** Top-3 actions, the highest-impact action, each with expected DMI improvement, expected annual revenue, and a confidence score.

> The core idea: don't *guess* what an action is worth — **simulate it.** Each candidate action is a defined "fix" applied to the VIR; the engine re-runs `dmi_v1` and `ose_v1` on the fixed VIR and reads off the deltas. So "Google Reviews Campaign → +14 DMI, ₹3.2L/yr" is a *computed* counterfactual, not a number someone typed.

---

## 1. Recommendation logic — counterfactual simulation

```
for each action A whose precondition matches this venue:
    fixed_VIR = apply(A, VIR)                 # A sets the specific fields it would improve
    ΔDMI      = DMI(fixed_VIR) − DMI(VIR)      # re-run dmi_v1
    Δrevenue  = OSE(VIR) − OSE(fixed_VIR)      # recovered = the drop in 'missed revenue'
    conf      = confidence(A, VIR)
    priority  = (impact of ΔDMI, Δrevenue) × conf / effort(A)
rank by priority → Top 3 ;  highest-impact = max Δrevenue
```
Because impact is measured *through the same scoring engines the rest of the product uses*, recommendations are automatically consistent with the diagnosis the venue was shown — no second, conflicting model.

---

## 2. Rule engine design

An **action catalog** — each action is a small, declarative object:

```python
{
  "id": "review_engine",                 # matches recommendations_confidence.json rule_id
  "title": "Google Reviews Campaign",
  "pillar": "Trust",
  "effort": 2,                           # 1 (trivial) .. 5 (heavy)
  "applies": lambda vir: reviews(vir) < 50 or velocity(vir) < 2,
  "apply":   lambda vir: set(vir, {       # the counterfactual 'fixed' state
                "google_business.total_reviews": max(60, reviews+40),
                "google_business.review_velocity": 4,
                "google_business.review_response_rate": 0.8 })
}
```

- `applies` keeps the catalog **self-filtering** — a venue that already has 200 fresh reviews never sees a reviews campaign.
- `apply` is the only place "what good looks like" is encoded, and it's data, not code branches — new actions are added by appending to the list.
- Catalog covers the funnel: `gmb_claim, review_engine, reply_speed, followup_system, content_engine, website_build, whatsapp_cta, smartos_ops, tracking_start`.

---

## 3. ML-ready architecture

The rule engine is the **v1 placeholder for a learned model** — same interface, swappable internals:

| Layer | v1 (now) | v2 (learned) |
|---|---|---|
| Candidate generation | `applies` predicates | same (cheap pre-filter) |
| Impact estimate | simulate via `dmi_v1` / `ose_v1` | **uplift model** trained on real before→after outcomes (SmartOS + HVT history) |
| Confidence | data completeness × historical success rate | model prediction interval + Bayesian shrinkage to cohort prior |
| Ranking | ICE formula | learning-to-rank on realised ROI |

Because every input is the clean, typed VIR and every action has a stable `id`, the training data writes itself: `(VIR_t0 features, action_taken) → (ΔDMI, Δbookings realised)` from the HVT snapshots. `method` versioning lets `reco_v1` (rules) and `reco_v2` (model) run side-by-side for A/B before cutover. The existing **Growth Bible LearningEngine 👍/👎 feedback** and `recommendations_confidence.json` are already the first labels.

---

## 4. Prioritization framework (ICE, tuned for venues)

```
ImpactIndex = ΔDMI  +  (Δannual_revenue / ₹1L)        # DMI points + lakhs, comparable magnitudes
Priority    = ImpactIndex × Confidence / Effort        # classic Impact·Confidence / Effort
```
- **Top 3** = highest `Priority` (best bang-per-effort — what to do *first*).
- **Highest-impact action** = max `Δrevenue` (biggest prize regardless of effort — what's worth *most*).
- These can differ on purpose: a quick WhatsApp-CTA fix may top *Priority* while a website build tops *Impact*. The consultant gets both lenses.
- Effort divisor stops the engine from always recommending the heaviest project; confidence multiplier stops it from betting on thin data.

---

## 5. Confidence scoring (0–1)
```
conf = data_factor × history_factor × sim_factor
  data_factor    = 0.6 + 0.4 · completeness_of_fields_the_action_touches   (don't recommend on blind data)
  history_factor = success_rate(action.id) from recommendations_confidence.json   (e.g. 0.90 for gmb_setup)
  sim_factor     = 0.9 if the simulated ΔDMI is well-supported by present evidence, else 0.75
```
Reported as a % next to each action. Low confidence demotes an action in ranking (via the Priority multiplier) and is shown honestly — "₹3.2L/yr · 87% confidence" — so a recommendation is never mistaken for a promise. As real outcomes accumulate, `history_factor` is recomputed per action, and the whole engine self-calibrates.

---

*REC is where the stack pays off: **VIR** (facts) → **DMI/CIE/OSE/VMF** (diagnosis) → **HVT** (movement) → **REC** (the next best 3 moves, each with a simulated DMI lift, a ₹ value, and a confidence). It is the brain that turns intelligence into action.*
