# Venue Intelligence Record (VIR) — Field Reference

**Files:** `vir.schema.json` (JSON Schema, Draft 2020-12) · `vir.example.json` (validated sample)

## The core idea: evidence before scores

The old VIR stored only scores (`visibility: 45`). Those are *opinions*. This schema stores the **raw facts that justify a score**, each tagged with **where it came from, when, and how reliable it is** — then derives the score from those facts. That is what makes a score "evidence-based."

Every measured fact uses an **evidence wrapper**:

```json
"total_reviews": { "value": 34, "source": "google_places_api", "observed_at": "2026-06-05T09:00:00Z", "confidence": 1.0 }
```

- `value` — the observation (number, boolean, string, or date)
- `source` — provenance enum (API, scrape, manual, owner-reported, estimate…)
- `observed_at` — when it was captured (so stale data can be detected)
- `confidence` — 0–1 reliability (1 = verified API call, 0.6 = owner's memory)

Pillar scores live under `dimensions.*` and carry `evidence_refs` — JSON-pointer paths back to the exact facts that produced them, plus the `method` (`rule_v3`, `manual_override`, `model_v1`) and a score `confidence` driven by how complete the evidence is.

---

## Top-level fields

| Field | Req? | Description |
|---|---|---|
| `schema_version` | **Required** | Schema version (`"1.0"`). Bump on breaking changes. |
| `vir_id` | **Required** | Unique record id (slug). |
| `generated_at` | Optional | When this record was assembled. |
| `collection_mode` | Optional | `live` / `mixed` / `manual` / `estimate`. |
| `data_completeness` | Optional | 0–1, fraction of expected evidence populated. **Drives score confidence.** |
| `venue` | **Required** | Section 1 identity. |
| `google_business` … `revenue` | Optional | Sections 2–8 evidence. |
| `dimensions` | Optional (derived) | Six pillar scores. |
| `recommendation` | Optional (derived) | Product fit + path + maturity. |
| `lifecycle` | Optional | Command Center pipeline state. |

> **Required vs optional philosophy:** only identity (`schema_version`, `vir_id`, `venue.name/type/city`) is mandatory, so a *partial* audit is still a valid VIR. Every evidence section is optional — but when a metric **is** present it **must** carry `value` + `source`. You're never forced to have data, but you're never allowed to have data without provenance.

---

## Section-by-section

**S1 `venue`** — name, type (enum), city, area, capacity_min/max, price_range (catering_from, avg_event_value), contact (owner/phone/whatsapp/email), geo (lat/lng/google_place_id). *Required: name, type, city.*

**S2 `google_business`** — claimed, rating, total_reviews, review_velocity (per month), review_response_rate (0–1), total_photos, last_photo_upload (date), posts_published, qa_activity.

**S3 `instagram`** — followers, following, total_posts, reels_count, avg_engagement (0–1), posting_frequency (per week), last_post_date, bio_optimization_score (0–100), link_present, whatsapp_cta.

**S4 `website`** — exists, url, mobile_friendly, whatsapp_button, inquiry_form, loading_speed_sec, seo_score (0–100).

**S5 `trust_signals`** — testimonials, video_testimonials, wedding_albums, media_mentions, influencer_mentions (all counts).

**S6 `conversion_systems`** — whatsapp_automation (bool), lead_form (bool), crm (string/none), follow_up_system (`none|owner_memory|staff|spreadsheet|crm_automated`), inquiry_tracking (`memory|paper|diary|excel|gsheet|crm`).

**S7 `operations`** — smartos_usage (bool), calendar_management (`diary|wall|excel|gcal|software`), inquiry_logging, booking_tracking, reporting (count 0–7 of live metrics owner can see).

**S8 `revenue`** — booking_volume_monthly, inquiry_volume_monthly, conversion_rate (0–1), avg_booking_value (INR), peak_occupancy (%), off_season_occupancy (%).

**Derived `dimensions`** — `visibility, trust, conversion, operations, revenue, leadership` (leadership internal-only). Each: `score` (0–100), `band`, `method`, `confidence`, `evidence_refs[]`, `computed_at`, optional `override_reason`.

**Derived `recommendation`** — digistories_fit / smartos_fit (`none|beneficial|critical`), recommended_path (`DigiStories|SmartOS|Both|Neither`), why, confidence, maturity_score, priority_order[].

---

## Scalability recommendations

1. **Separate raw from derived (done).** Collectors only ever write evidence sections; the scoring engine only ever writes `dimensions`/`recommendation`. They can be rebuilt independently — re-score the whole database without re-collecting.
2. **Version everything.** `schema_version` on the record, `method` on each score. When the formula changes you can re-score historical records and A/B old vs new without data loss.
3. **Confidence-weighted, not all-or-nothing.** `data_completeness` + per-score `confidence` let the UI show "Visibility 28/100 (low confidence — Instagram not yet verified)" instead of pretending precision you don't have.
4. **Stable JSON-pointer `evidence_refs`.** Keep field paths stable across versions so a score can always point back at its evidence; deprecate, don't rename.
5. **One record per venue, append snapshots elsewhere.** Store the *current* VIR in your primary table; write each `generated_at` snapshot to a history table/object store so you get time-series (review velocity, momentum) without bloating the live record.
6. **Storage path:** start as JSON files / a document store keyed by `vir_id`; the flat sections map cleanly to SQL columns or a `JSONB` column later with zero reshaping.
7. **Source-of-truth precedence:** when the same fact arrives from two sources, keep the higher-`confidence` one and log the other — never silently overwrite.

## Future AI-readiness recommendations

1. **Feature-ready by design.** Every evidence `value` is already a clean numeric/boolean/enum feature. A model can train directly on the flattened evidence vector — no scraping of free text required.
2. **Labels are built in.** `lifecycle.status` (Completed/Archived) + `recommendation.recommended_path` + outcome feedback give you supervised labels: "given this evidence, did Both/SmartOS/Neither actually succeed?" That's how `rule_v3` eventually becomes `model_v1` — and `method` already lets both coexist.
3. **Confidence + provenance enable trustworthy AI.** Models can down-weight low-confidence/stale evidence, and `evidence_refs` give you explainability ("score is low *because* Google is unclaimed and last photo was 14 months ago") — essential for a consultant-facing tool.
4. **Don't free-text what can be enumerated.** Keep `follow_up_system`, `inquiry_tracking`, etc. as controlled enums so they're directly model-consumable; reserve free text for `recommendation.why` and `override_reason`.
5. **Embeddings-friendly later.** Add an optional `narrative` block (raw review text, owner quotes) in a future minor version for LLM summarisation/sentiment — additive, non-breaking.
6. **Drift monitoring.** Because every fact has `observed_at` and `source`, you can detect data drift (e.g. Instagram scrape reliability dropping) and trigger re-collection automatically.

---

*Schema v1.0 · backward-compatible with the legacy `dimensions` block used by the Sales Tool ↔ Command Center ↔ Growth Bible bridge.*
