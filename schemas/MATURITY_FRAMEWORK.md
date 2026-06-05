# Venue Maturity Framework (VMF) — Specification v1

**Method id:** `maturity_v1` · **Input:** a VIR (scored by `dmi_v1`) · **Output:** an overall maturity stage + a per-dimension stage, the weakest-link gate, and an advancement roadmap.

Four stages × five business dimensions. The stages are owner-facing language; the dimensions map cleanly onto the engines already built.

| Maturity dimension | Powered by |
|---|---|
| **Marketing** | DMI Discoverability + Trust |
| **Sales** | DMI Conversion |
| **Operations** | DMI Operations |
| **Technology** | VIR tooling evidence (website, calendar, tracking, CRM/SmartOS) |
| **Leadership** | VIR Leadership (internal) |

---

## 1. Assessment criteria — the 4×5 maturity matrix

| | 🟤 Traditional (0–30) | 🟠 Semi-Digital (31–55) | 🔵 Modern (56–80) | 🟢 Intelligent (81–100) |
|---|---|---|---|---|
| **Marketing** | Unclaimed/no Google, no Instagram, pure word-of-mouth | Claimed Google, occasional posts, a few stale reviews | Weekly reels, 50+ fresh reviews, real wedding content, strong profile | Content driven by performance data; dominates local search; review-velocity engine |
| **Sales** | Calls/walk-ins only, no follow-up, owner remembers | WhatsApp inquiries, manual replies, ad-hoc follow-up | Fast response, structured follow-up, CTAs everywhere, conversion tracked | Automated nurture, lead scoring, continuously optimised funnel |
| **Operations** | Paper diary, double-booking risk, owner is the bottleneck | Excel/Sheets, limited staff access | Booking software + calendar, multi-staff, systematic payments/vendors | Integrated ops (SmartOS), real-time dashboards, automated workflows |
| **Technology** | No website, no tools, phone only | Basic listing/site, WhatsApp, spreadsheets | Mobile site + inquiry form, CRM, calendar software | Integrated stack, data pipeline, analytics, automation |
| **Leadership** | "We've always done it this way" — resistant | Curious but cautious, delegates little | Growth-focused, invests, measures results | Data-driven, experiments, builds systems, market ambition |

Each dimension is scored 0–100 from evidence (via the DMI/VIR), then mapped to a stage by the bands above.

---

## 2. Classification rules

**Per-dimension stage** = band of its 0–100 score: `0–30 Traditional · 31–55 Semi-Digital · 56–80 Modern · 81–100 Intelligent` (stage index 0–3).

**Dimension weights** (for the composite): Marketing 25 · Sales 25 · Operations 20 · Technology 15 · Leadership 15.

**Overall stage** is **not** just the composite band — it is gated by three rules so the label stays honest:
```
base   = band(weighted composite)
gate_1 = weakest_dimension_stage + 1     ← "you're at most one stage above your weakest pillar"
gate_2 = highest stage L reached by a majority (≥ 60%) of dimensions
overall = min(base, gate_1, gate_2)
```
- **gate_1 (weakest-link)** is the core consulting principle: a venue with brilliant marketing but a paper diary is **not** "Modern" — its operations will break the moment marketing works. You can lead with one pillar, but you can't *be* a stage your foundation can't support.
- **gate_2 (majority)** stops a single strong pillar from inflating the label.

The report always names the **weakest link** — the pillar holding the overall stage down — because that's the single highest-leverage thing to fix.

---

## 3. Advancement roadmap

To advance from stage `N` to `N+1`, every dimension currently below `N+1` must clear that band. The framework auto-lists the concrete unlock per lagging dimension:

**Traditional → Semi-Digital** — *get on the map*
- Marketing: claim Google, post weekly · Sales: route inquiries to WhatsApp, reply same-day · Operations: move the diary to a shared sheet · Technology: a basic listing/site + WhatsApp · Leadership: agree to try one channel for 90 days.

**Semi-Digital → Modern** — *build the system*
- Marketing: 50+ fresh reviews + weekly reels of real functions · Sales: <1hr response + a written follow-up sequence · Operations: booking software, multi-staff access · Technology: mobile site + inquiry form + CRM · Leadership: start measuring conversion monthly.

**Modern → Intelligent** — *let data drive*
- Marketing: schedule content by what converts; review-velocity engine · Sales: automated nurture + lead scoring · Operations: SmartOS dashboards + automated workflows · Technology: integrated stack + analytics pipeline · Leadership: run experiments, decide by data.

---

## 4. Visual scorecard (text render)
```
  VENUE MATURITY SCORECARD — Swayambhu Ganesh Sabhagruh
  ─────────────────────────────────────────────────────────
  Marketing   [██░░] Traditional   21/100
  Sales       [██░░] Traditional   29/100
  Operations  [█░░░] Traditional    9/100   ◀ weakest link
  Technology  [█░░░] Traditional    5/100
  Leadership  [███░] Modern        65/100
  ─────────────────────────────────────────────────────────
  OVERALL STAGE:  🟤 TRADITIONAL        next ▶ Semi-Digital
  Holding you back: Operations, Technology
```
The four-cell track `[██░░]` shows the stage; the overall badge plus the "holding you back" line make the next move obvious at a glance.

---

## 5. Automated classification algorithm
`maturity_v1.py` (tested reference):
1. Score the VIR with `dmi_v1` → Discoverability, Trust, Conversion, Operations.
2. Derive the five maturity dimensions (Marketing = 0.55·Disc + 0.45·Trust; Sales = Conversion; Operations = Operations; Technology from VIR tooling evidence; Leadership from VIR).
3. Band each dimension → stage 0–3.
4. Apply the composite + weakest-link + majority gates → overall stage.
5. Emit per-dimension stages, weakest link, the advancement roadmap to the next stage, and the scorecard.

Deterministic, versioned (`maturity_v1`), and fully traceable back to evidence — same scalability profile as the rest of the stack (vectorisable bands, config-driven weights, re-classify history on version bump).

---

*VMF is the human-readable summit of the stack: **VIR** (facts) → **DMI** (maturity score) → **CIE** (rank) → **OSE** (₹ at stake) → **VMF** (the one-word stage + the next move).* 
