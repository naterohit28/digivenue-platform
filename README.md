# DigiVenue

**India's first hospitality-native operating ecosystem for banquet halls, wedding venues, caterers, and decorators.**

Banquet halls are operationally strong but digitally invisible. Families discover venues on Instagram and Google *before* they ever call — and most halls lose bookings silently during that discovery phase because they look inactive online. DigiVenue fixes that, end to end.

Founded by **Rohit Nate** — 13+ years of real banquet & catering operations in Maharashtra.

---

## The ecosystem (5 connected products)

| Product | What it does |
|---|---|
| **DigiStories** | The visible layer — Google presence, Instagram reels, real wedding photography, review collection |
| **SmartOS** | The operational backend — inquiry tracking, bookings, GST invoicing, vendor royalties, calendar |
| **DigiNetwork** | Relationship infrastructure connecting venues with trusted caterers, decorators, planners |
| **DigiMarket** | Future marketplace for decor vendors & hospitality suppliers |
| **DigiShaadi** | Future consumer wedding-discovery layer — families find halls directly, no middleman |

---

## What's in this repository

### 🌐 Marketing website — `claude DigiVenue/`
A no-framework HTML/CSS/JS site (warm-ivory hospitality design system). Homepage, DigiStories product page, results/transparency page, ecosystem, about, and a free-audit page.

### 🧠 Sales Intelligence Pipeline — `_Tools/Sales Strategy/mumbai_readiness_system/`
A Python system that scores Mumbai banquet halls and builds a daily outreach queue.

**Pipeline:** collect → score → detect pain → prioritize outreach → track over time

- **Collectors** — Google Maps, Instagram, website, marketplace signals (live or mock mode)
- **Scoring engines** — Digital Maturity Index (DMI), Digital Silence, SmartOS readiness, DigiStories opportunity
- **5 intelligence panels** — Territory Rank, Digital Silence, SmartOS Opportunity, Growth Momentum, Relationship intel
- **Outputs** — daily outreach queue with per-venue WhatsApp scripts, territory clusters, 3km competitor maps
- **Dashboard** — a Streamlit app for DMI rankings, the outreach queue, and territory intelligence
- **Honesty layer** — every venue is tagged `google_live` (real) or `ai_estimate`, so no fake number is ever quoted

Quick start:
```bash
cd "_Tools/Sales Strategy/mumbai_readiness_system"
pip install -r requirements.txt
python run_pipeline.py            # generates exports/
streamlit run dashboard/app.py    # opens the dashboard
```
To switch on real Google data, add a key (see `configs/secrets.example.json`) and run `python check_live_setup.py`.

### 🤝 Internal sales & delivery tools — `_Web/`
- **`digistories-sales-tool-v2.html`** — a 10-step, six-pillar **Venue Growth Diagnostic** a consultant runs live with a hall owner (Visibility · Trust · Conversion · Operations · Revenue · Leadership), with a Recommendation Engine (DigiStories / SmartOS / Both / Neither) and a printable customer Health Report.
- **`venue-growth-bible-engine.html`** — a configurable 27-chapter internal growth operating manual, organised around the six pillars.

> These are **internal team tools** — they read pipeline data via `intelligence_data.js` and are not meant to be shared with prospects.

### 📋 Strategy & playbooks — `_Playbooks/`, `Sales Strategy/`
The brand manifesto, approved site copy, operational playbooks, the 106-venue prospect database, and BCA partnership material.

---

## Tech stack
- **Website & tools:** HTML5, CSS3, vanilla JavaScript (no frameworks)
- **Pipeline:** Python 3.10+, SQLite, pandas, Streamlit, Plotly
- **Fonts/design:** Playfair Display + Inter, warm-ivory hospitality design system

---

## Repository layout
```
claude DigiVenue/      Marketing website (production)
_Web/                  Internal sales tool + growth bible
_Tools/                Sales intelligence pipeline (Python)
_Playbooks/            Brand & strategy documents
Sales Strategy/        Prospect database + outreach material
_Leads/                Lead data
GoogleDigiVenue/       Alternate site variant
```

---

*Internal project. Private repository — not for public distribution.*
