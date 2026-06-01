# Claude Code Task — DigiVenue Website Refinement

You are working on the **DigiVenue** marketing website — a multi-page static site for a service that manages Google, Instagram and reviews for **banquet halls in Mumbai, Navi Mumbai and Thane**. The audience is **banquet hall owners in India** (often 45–65, family-business operators, English is a second language, frequently reading on a mid-range Android phone).

The site already exists and looks visually elegant. **Do not rebuild it. Do not change the architecture, file structure, or design framework.** Your job is to fix six specific, concrete problems. Work surgically.

---

## FIRST: Read before you touch anything

1. Read every file in the project, but especially:
   - `styles/main.css` (the design system — contains the `--space-*`, `--text-*`, `--font-*`, `--gap-*`, `--ls-*` CSS custom properties that control EVERYTHING)
   - `styles/pages/home.css` and `styles/pages/home-refined.css` (homepage "movement" layout)
   - `styles/pages/shared.css` (inner pages)
   - `js/main.js`
   - All 6 HTML pages: `index.html`, `pages/about.html`, `pages/what-we-do.html`, `pages/results.html`, `pages/ecosystem.html`, `pages/audit.html`
2. Build a quick map of: which CSS variables control section padding, the type scale, and the font sizes used by small-but-important text (eyebrows, captions, outcomes, attributions).
3. **Most fixes below should be made in the CSS variables / shared classes, NOT by hand-editing every section inline.** Change the token once, let it cascade. Only go inline when a specific element overrides the token.

---

## PROBLEM 1 — The language is too "AI / consultant-speak"

The copy reads like a Western SaaS pitch written by an AI. It must sound like **a real person from Mumbai who understands banquet halls talking plainly to another banquet owner.** Warm, direct, concrete, a little informal. Hinglish-friendly phrasing is welcome where natural (e.g. "booking", "function", "season", "enquiry" — words owners actually use).

**Find and rewrite these phrases everywhere they appear** (this is not exhaustive — fix the whole site in this spirit):

| Replace this AI-speak | With plain owner-language (examples — vary naturally) |
|---|---|
| "operational trust infrastructure" | "we keep your hall looking active and trusted online" |
| "operational trust systems" | "we run your Google, Instagram and reviews" |
| "trust diagnostic" / "trust audit" | "free check of how your hall looks online" |
| "trust gaps" | "what's making families skip your hall" |
| "Constitutional Pillars" | "How we work" |
| "Operational Realism" | "We're at your hall on event days" |
| "Micro-Local Authority" | "We only do Mumbai halls" |
| "Diagnostics Over Sales" | "We show you the problem first — no pressure" |
| "The Insider Doctrine" | "Why we started this" |
| "Run Free Trust Audit" | "Check my hall's online presence — free" |
| "Talk to a Strategist" | "Talk to us on WhatsApp" |
| "impressions and likes" | "likes that don't bring bookings" |

**Rules for the rewrite:**
- Short sentences. Cut every word that doesn't earn its place.
- Use rupees, real localities (Chembur, Ghatkopar, Dadar, Thane, Vashi), and real situations (winter wedding season, Saturday functions, WhatsApp enquiries).
- Replace abstract nouns ("infrastructure", "ecosystem", "diagnostics") with verbs and plain nouns ("we post photos", "we reply to reviews", "we send you a weekly update").
- Keep the founder/About story's emotional truth (50-year catering family, losing bookings to newer halls) — just say it like a human, not a brand manifesto.
- Do NOT introduce new fake claims, stats, or testimonials. Keep all existing numbers as-is.
- The placeholder `91XXXXXXXXXX` in WhatsApp links — leave as-is but add a clear `<!-- TODO: replace with real number -->` comment beside each.

---

## PROBLEM 2 — Images are missing

The HTML references image files that don't exist on disk, so the pages render with broken/empty image areas. References found include:
- `assets/images/hero-banquet.jpg`
- `assets/images/banquet-founder.jpg`
- `assets/images/transformation.jpg`
- `assets/images/banquet-catering.jpg`
- (and a CSS background `assets/indian_banquet_hero.png`)

**There is a folder of real, usable banquet/wedding photos provided** (JPG/PNG/WEBP — large hall shots, decor, catering, mandap, event photos). Do this:

1. Locate the provided source images (ask me for the folder path if you can't find them, or check an `uploads/` or `source-images/` directory).
2. Create `assets/images/` if it doesn't exist.
3. **Map the best-fitting real photo to each referenced filename** and copy/rename it into place so every `src` resolves. Match by content:
   - Hero → the most atmospheric wide hall/venue shot
   - Founder → a candid catering/operations/people shot (not a posed portrait if none exists — pick the most "behind the scenes" one)
   - Transformation/results → before/after-friendly venue or decor shots
   - Catering → a food/buffet/plating shot
4. **Optimise every image for web**: resize so the longest edge is ≤2000px, compress to reasonable quality (JPG q≈80), keep file sizes ideally under ~300KB each. Convert oversized multi-MB files down. Owners view on mobile data — heavy images will kill the experience.
5. Add proper `width`/`height` attributes (or aspect-ratio CSS) to every `<img>` so the layout doesn't jump while loading, add `loading="lazy"` to below-the-fold images, and keep `fetchpriority="high"` only on the hero.
6. Write genuinely descriptive `alt` text for each in plain English ("Decorated mandap at a Chembur banquet hall before a wedding"), not keyword stuffing.
7. If a referenced image genuinely has no good match, use the closest available and leave a `<!-- TODO: replace with better-matched photo -->` comment — never leave a broken `src`.

---

## PROBLEM 3 — The page feels too long / too much vertical gap between sections

The homepage uses a deliberately spacious "movement" editorial system and the inner pages use `.content-section`. The spacing is currently **too generous for this audience** — it makes the page feel endless and forces excessive scrolling, especially on mobile.

1. Find the section-padding tokens (likely `--space-10`, `--space-9`, or the `padding` on `.movement`, `.content-section`, `.pause`, `.truth`, `.invitation`).
2. **Reduce vertical section padding by roughly 30–40%** — tune by eye, don't just slash. The goal: still elegant and breathable, but noticeably tighter. Desktop section padding that's currently ~160px should land around ~96–110px; mobile should be tighter still (~56–72px).
3. The near-empty "held moment" sections on the homepage (`.pause`, `.truth`, `.places`) eat enormous screen height for one line of text. **Reduce their min-height / padding significantly** so each is impactful but not a full empty screen. On mobile especially, these should not each occupy a whole viewport.
4. Add a clear responsive step-down: section spacing at `≤768px` and `≤480px` should be tighter than desktop. If media queries for this don't exist, add them.
5. After changing tokens, scroll the whole site (every page, desktop + mobile widths) and confirm nothing collides or overlaps.

---

## PROBLEM 4 — Important text is too small

Several genuinely important elements are set at tiny sizes (captions, eyebrows, "Outcome" lines, testimonial attributions, the `--text-micro` / `--text-caption` tokens). On a phone these are hard to read for a 50-year-old owner — the exact person who must understand them.

1. Identify the small-text tokens (`--text-micro`, `--text-caption`, eyebrow/label sizes) and the classes using them (`.eyebrow`, `.text-label`, `.what__item__result`, `.proof__attr`, `.hero__still`, `.quote-attribution`, `.pillar-card__desc`, `.places__label`, `.invitation__note`).
2. **Raise the floor for body-level important text to a minimum of 16px on mobile** (never below 15px for anything a customer needs to read). Eyebrows/labels can stay smaller (they're decorative) but bump them up if they carry real meaning.
3. Specifically increase:
   - The "Outcome ·" result lines on the homepage (`.what__item__body` / `__result`) — these are the actual value prop, currently understated.
   - Testimonial body and attribution (`.proof__quote`, `.proof__attr`).
   - Card descriptions on inner pages (`.pillar-card__desc` and equivalents).
   - Sub-headers / supporting paragraphs that are currently muted grey AND small — improve either size or contrast (see Problem 5).
4. Keep the large display type as-is (it's working). This is about lifting the small-but-important tier, not flattening the hierarchy.
5. Re-check line-length and line-height after bumping sizes so nothing gets cramped.

---

## PROBLEM 5 — (do this alongside 4) Contrast of muted text

Much supporting text uses `--color-text-muted` / `--color-text-secondary` on dark backgrounds and is hard to read. Nudge these muted greys lighter for better legibility on phones in daylight — without losing the hierarchy. Adjust the token, verify across all pages.

---

## PROBLEM 6 — Mobile experience pass (the priority device)

Most owners will see this first on a mid-range Android. After the above, do a focused mobile pass at 360px, 390px and 768px widths:
- Confirm the tightened spacing feels right (not cramped, not endless).
- Confirm all bumped-up fonts are comfortably readable.
- Confirm every image loads, is correctly sized, and doesn't overflow.
- Confirm the mobile nav drawer, hero, and all CTAs work and are thumb-reachable.
- Confirm no horizontal scroll anywhere.

---

## CONSTRAINTS (do not violate)

- **Do not** change the overall visual identity: keep Playfair Display + Inter, the dark palette, the gold/accent colour, the editorial feel.
- **Do not** add frameworks, build tools, or dependencies. It stays vanilla HTML/CSS/JS.
- **Do not** invent new statistics, testimonials, or client names.
- **Do not** rename files or break internal links between pages.
- **Prefer** editing shared CSS tokens over per-element inline styles. When you must go inline, keep it minimal.
- Keep all existing structured-data / SEO / meta tags intact (and update any copy inside them to match the new plain language).

---

## DELIVERABLE

When done, give me:
1. A short summary of exactly what you changed, grouped by the 6 problems.
2. The list of CSS variables you adjusted and their before → after values.
3. The image mapping table (which source photo became which `assets/images/*` file).
4. Any remaining `TODO` items I need to handle (real WhatsApp number, any unmatched images).

Work through the problems in order. Show me the diffs as you go. Test by opening each page at desktop and mobile widths before declaring done.
