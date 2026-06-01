import os

path = r"_Web/digistories-sales-tool-v2.html"

code = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>DigiVenue — Growth Consultation Suite</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400;1,500;1,600&family=Inter:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  /* ─── TOKENS & TYPOGRAPHY (Warm Ivory, Hospitality Native) ─── */
  :root {
    --color-bg:           #FAF7F2;
    --color-bg-deep:      #F5EFE6;
    --color-surface:      #F3EEE5;
    --color-surface-mid:  #EBE4D8;
    --color-surface-high: #E2D9C9;
    --color-border:       #E5DFD3;
    --color-border-light: #D5CEBF;
    --color-border-gold:  rgba(197, 160, 89, 0.3);
    
    --color-text-primary:   #1F1D1C;
    --color-text-secondary: #4A4644;
    --color-text-muted:     #6F6864;
    --color-text-inverse:   #FAF7F2;
    
    --color-accent:         #D94822;
    --color-accent-hover:   #B83615;
    --color-accent-subtle:  rgba(217, 72, 34, 0.08);
    --color-gold:           #C5A059;
    --color-gold-hover:     #D4B06A;
    --color-gold-subtle:    rgba(197, 160, 89, 0.06);
    --color-green:          #16a34a;
    --color-green-subtle:   rgba(22, 163, 74, 0.08);
    --color-red:            #dc2626;
    --color-red-subtle:     rgba(220, 38, 38, 0.08);

    --font-serif:    'Playfair Display', Georgia, serif;
    --font-sans:     'Inter', system-ui, sans-serif;
    --font-mono:     'DM Mono', monospace;

    --radius-sm: 4px;
    --radius-md: 0px; /* Architectural, 0px border radius */
    --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { 
    font-family: var(--font-sans); 
    background-color: var(--color-bg); 
    color: var(--color-text-secondary);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }

  /* ─── TYPOGRAPHY CLASSES ─── */
  .text-display { font-family: var(--font-serif); font-size: clamp(34px, 5vw, 56px); font-weight: 500; color: var(--color-text-primary); line-height: 1.1; letter-spacing: -0.02em; }
  .text-display em { font-style: italic; font-weight: 400; color: var(--color-accent); }
  .text-h1 { font-family: var(--font-serif); font-size: clamp(26px, 4vw, 40px); font-weight: 500; color: var(--color-text-primary); line-height: 1.2; letter-spacing: -0.02em; margin-bottom: 20px;}
  .text-h2 { font-family: var(--font-serif); font-size: clamp(20px, 3vw, 30px); font-weight: 500; color: var(--color-text-primary); line-height: 1.25; margin-bottom: 16px;}
  .text-h3 { font-family: var(--font-serif); font-size: 20px; font-weight: 500; color: var(--color-text-primary); }
  .text-lead { font-size: 16px; font-weight: 300; color: var(--color-text-secondary); line-height: 1.6; margin-bottom: 28px; }
  .text-label { font-family: var(--font-sans); font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: var(--color-text-muted); }
  .text-label.accent { color: var(--color-accent); }
  .text-label.green { color: var(--color-green); }

  /* ─── LAYOUT ─── */
  .topbar { position: sticky; top: 0; z-index: 100; background: rgba(250, 247, 242, 0.95); backdrop-filter: blur(12px); border-bottom: 1px solid var(--color-border); padding: 14px 24px; display: flex; justify-content: space-between; align-items: center; }
  .brand { font-family: var(--font-serif); font-size: 18px; font-weight: 600; color: var(--color-text-primary); letter-spacing: -0.01em; display:flex; align-items:center; gap: 10px; }
  .brand-badge { background: var(--color-bg-deep); border: 1px solid var(--color-border); padding: 3px 8px; font-size: 9px; font-family: var(--font-sans); text-transform: uppercase; letter-spacing: 0.1em; color: var(--color-text-muted); }
  
  .nav { position: sticky; top: 57px; z-index: 90; background: var(--color-bg); border-bottom: 1px solid var(--color-border); overflow-x: auto; scrollbar-width: none; }
  .nav::-webkit-scrollbar { display: none; }
  .nav-inner { display: flex; padding: 10px 24px; gap: 24px; min-width: max-content; }
  .nav-item { font-family: var(--font-sans); font-size: 12px; font-weight: 500; color: var(--color-text-muted); cursor: pointer; transition: color 0.3s var(--ease-out); display: flex; align-items: center; gap: 6px; }
  .nav-item:hover { color: var(--color-text-primary); }
  .nav-item.active { color: var(--color-accent); }
  .nav-num { font-size: 10px; opacity: 0.6; }

  .main { max-width: 900px; margin: 0 auto; padding: 40px 24px 120px; }
  .stage { display: none; animation: fadeIn 0.4s var(--ease-out); }
  .stage.active { display: block; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }

  /* ─── UI COMPONENTS ─── */
  .card { background: var(--color-surface); border: 1px solid var(--color-border); padding: 32px; margin-bottom: 20px; transition: border-color 0.3s; }
  .card.gold { background: linear-gradient(145deg, var(--color-surface), var(--color-gold-subtle)); border-color: var(--color-border-gold); }
  .card.red { background: var(--color-red-subtle); border-color: var(--color-red); }
  
  .field { margin-bottom: 20px; }
  .field label { display: block; margin-bottom: 6px; }
  .input { width: 100%; background: var(--color-bg); border: 1px solid var(--color-border-light); padding: 14px; font-family: var(--font-sans); font-size: 15px; color: var(--color-text-primary); transition: all 0.3s var(--ease-out); outline: none; }
  .input:focus { border-color: var(--color-text-primary); background: #fff; }
  select.input { appearance: none; cursor: pointer; }
  
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }

  .btn { display: inline-flex; align-items: center; justify-content: center; padding: 14px 28px; background: var(--color-text-primary); color: var(--color-text-inverse); font-family: var(--font-sans); font-size: 13px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; border: none; cursor: pointer; transition: background 0.3s var(--ease-out); }
  .btn:hover { background: var(--color-accent); }
  .btn.outline { background: transparent; border: 1px solid var(--color-text-primary); color: var(--color-text-primary); }
  .btn.outline:hover { background: var(--color-surface-mid); border-color: var(--color-text-primary); }
  
  /* ─── AUDIT CARDS ─── */
  .audit-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 32px; }
  .audit-card { border: 1px solid var(--color-border); background: var(--color-surface); padding: 20px; display: flex; align-items: flex-start; gap: 14px; cursor: pointer; transition: all 0.2s var(--ease-out); }
  .audit-card:hover { border-color: var(--color-border-light); background: var(--color-surface-mid); }
  .audit-card.active { border-color: var(--color-accent); background: var(--color-accent-subtle); }
  .audit-check { width: 20px; height: 20px; border: 1px solid var(--color-border-light); background: var(--color-bg); display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2px; }
  .audit-card.active .audit-check { border-color: var(--color-accent); background: var(--color-accent); color: #fff; }
  .audit-card.active .audit-check::after { content: '✓'; font-size: 12px; }
  .audit-content h4 { font-family: var(--font-sans); font-size: 15px; font-weight: 500; color: var(--color-text-primary); margin-bottom: 2px; }
  .audit-content p { font-size: 13px; color: var(--color-text-secondary); }

  /* ─── NEXT BEST ACTION ─── */
  .nba { background: var(--color-accent-subtle); border-left: 4px solid var(--color-accent); padding: 20px; margin-top: 24px; }
  .nba-title { font-family: var(--font-sans); font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: var(--color-accent); margin-bottom: 6px; }
  .nba-text { font-family: var(--font-serif); font-size: 18px; color: var(--color-text-primary); }

  /* ─── SCORE METER ─── */
  .score-wrap { text-align: center; margin: 30px 0; }
  .score-circle { width: 140px; height: 140px; border-radius: 50%; border: 2px solid var(--color-border-light); margin: 0 auto 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; }
  .score-num { font-family: var(--font-serif); font-size: 48px; line-height: 1; color: var(--color-text-primary); }
  .score-label { font-family: var(--font-sans); font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--color-text-muted); margin-top: 3px; }
  
  /* ─── FOUNDER NOTES ─── */
  .founder-notes { position: fixed; bottom: 0; right: 40px; width: 360px; background: var(--color-text-primary); color: var(--color-bg); z-index: 200; transform: translateY(calc(100% - 48px)); transition: transform 0.4s var(--ease-out); border-top: 1px solid #333; border-left: 1px solid #333; border-right: 1px solid #333; }
  .founder-notes.open { transform: translateY(0); }
  .fn-header { padding: 14px 20px; font-family: var(--font-sans); font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; cursor: pointer; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; }
  .fn-header:hover { background: rgba(255,255,255,0.05); }
  .fn-body { padding: 20px; }
  .fn-textarea { width: 100%; height: 140px; background: transparent; border: none; color: #fff; font-family: var(--font-sans); font-size: 13px; line-height: 1.6; resize: none; outline: none; }
  .fn-textarea::placeholder { color: rgba(255,255,255,0.3); }

  /* ─── CONTROLS ─── */
  .controls { position: fixed; bottom: 0; left: 0; right: 0; background: var(--color-bg); border-top: 1px solid var(--color-border); padding: 20px 24px; display: flex; justify-content: space-between; z-index: 90; }

  /* ─── PRINT MODE (BRIEF) ─── */
  @media print {
    body { background: #fff; color: #000; }
    .topbar, .nav, .founder-notes, .controls, .main { display: none !important; }
    .print-brief { display: block !important; padding: 20px; border: 1px solid #000; }
    .print-brief h1 { font-size: 28px; border-bottom: 2px solid #000; padding-bottom: 12px; margin-bottom: 24px; }
    .print-section { margin-bottom: 24px; }
    .print-section h3 { font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em; border-bottom: 1px solid #ddd; padding-bottom: 6px; margin-bottom: 12px; font-family: var(--font-sans); }
    .print-row { display: flex; justify-content: space-between; margin-bottom: 6px; font-family: var(--font-sans); font-size: 13px; }
    .print-label { font-weight: 600; }
  }
  
  @media (max-width: 768px) {
    .main { padding: 30px 16px 120px; }
    .grid-2, .grid-3 { grid-template-columns: 1fr; }
    .audit-grid { grid-template-columns: 1fr; }
    .founder-notes { width: 100%; right: 0; }
  }
</style>
</head>
<body>

<!-- TOPBAR -->
<div class="topbar">
  <div class="brand">
    <img src="logo.svg" alt="DigiVenue" style="height: 22px; width: auto; display: block;">
    <span class="brand-badge">Growth Consultation</span>
  </div>
  <a href="#" id="toggleIntelBtn" style="display:none; font-size:11px; color:var(--color-text-muted); text-decoration:none;">Internal · Toggle Intelligence</a>
</div>

<!-- NAV -->
<div class="nav">
  <div class="nav-inner" id="navBar">
    <!-- Generated by JS -->
  </div>
</div>

<!-- ════════ LIVE VENUE INTELLIGENCE (data-driven, from pipeline) ════════ -->
<div class="main" id="intelCardWrap" style="padding-top: 16px; display:none;">
  <div class="card" id="intelCard" style="display:none; border: 1px solid var(--color-border-gold);">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:16px;">
      <div>
        <div class="text-label accent">Live Intelligence</div>
        <h2 class="text-h3" style="margin-top:4px;">Venue Intelligence Card</h2>
        <div style="font-size:10px; color:#b91c1c; margin-top:2px;">Internal use only. Do not show this panel during a live customer consultation.</div>
      </div>
      <div style="min-width:240px;">
        <label class="text-label">Pick a venue from your database</label>
        <select class="input" id="intel_select" onchange="renderIntel()">
          <option value="">— Select a venue —</option>
        </select>
      </div>
    </div>

    <div id="intel_empty" style="color:var(--color-text-muted); font-size:13px; padding:6px 0;">
      Pick a venue above to load its 5 live intelligence panels. (Run the pipeline to refresh the data.)
    </div>

    <div id="intel_body" style="display:none;">
      <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:16px;">
        <h3 class="text-h3" id="intel_name" style="margin:0;"></h3>
        <span id="intel_meta" class="text-body" style="color:var(--color-text-muted); font-size:13px;"></span>
        <span id="intel_source" style="font-size:11px; font-weight:600; padding:2px 8px; border-radius:4px;"></span>
      </div>

      <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:14px;">
        <!-- Panel 1 -->
        <div class="card" style="margin:0; padding:20px; background:var(--color-surface);">
          <div class="text-label" style="margin-bottom:8px;">📍 Territory Rank</div>
          <div id="intel_territory" style="font-size:13px; line-height:1.8;"></div>
        </div>
        <!-- Panel 2 -->
        <div class="card" style="margin:0; padding:20px; background:var(--color-surface);">
          <div class="text-label" style="margin-bottom:8px;">🔇 Digital Silence</div>
          <div style="font-family:var(--font-serif); font-size:28px; color:var(--color-accent);" id="intel_silence_score"></div>
          <div id="intel_silence" style="font-size:12px; line-height:1.7; margin-top:4px;"></div>
        </div>
        <!-- Panel 3 -->
        <div class="card" style="margin:0; padding:20px; background:var(--color-surface);">
          <div class="text-label" style="margin-bottom:8px;">⚙️ SmartOS Opportunity</div>
          <div style="font-family:var(--font-serif); font-size:28px; color:var(--color-accent);" id="intel_smartos_score"></div>
          <div id="intel_smartos" style="font-size:12px; line-height:1.7; margin-top:4px;"></div>
        </div>
        <!-- Panel 4 -->
        <div class="card" style="margin:0; padding:20px; background:var(--color-surface);">
          <div class="text-label" style="margin-bottom:8px;">📈 Growth Momentum</div>
          <div style="font-family:var(--font-serif); font-size:28px; color:var(--color-gold);" id="intel_momentum_score"></div>
          <div id="intel_momentum" style="font-size:12px; line-height:1.7; margin-top:4px;"></div>
        </div>
        <!-- Panel 5 -->
        <div class="card" style="margin:0; padding:20px; background:var(--color-surface);">
          <div class="text-label" style="margin-bottom:8px;">🤝 Relationship Intel</div>
          <div id="intel_relationship" style="font-size:12px; line-height:1.8; margin-top:4px;"></div>
        </div>
      </div>

      <div style="margin-top:14px;">
        <button class="btn outline" onclick="loadIntelIntoConsultation()">Use this venue in the consultation ↓</button>
      </div>
    </div>
  </div>
</div>

<!-- MAIN STAGES -->
<div class="main" id="stages">

  <!-- STEP 1: VENUE BASELINE -->
  <div class="stage active" id="st-0">
    <div class="text-label accent" style="margin-bottom: 12px;">Step 1</div>
    <h1 class="text-display">Venue <em>Baseline</em></h1>
    <p class="text-lead">Establish the baseline. Who are we talking to and what is their current scale?</p>

    <div class="card">
      <div class="grid-2">
        <div class="field">
          <label class="text-label">Venue Name</label>
          <input type="text" class="input" id="v_name" placeholder="e.g. The Grand Palace">
        </div>
        <div class="field">
          <label class="text-label">City / Location</label>
          <input type="text" class="input" id="v_loc" placeholder="e.g. Mumbai, Andheri">
        </div>
      </div>
      <div class="grid-2">
        <div class="field">
          <label class="text-label">Owner / Point of Contact</label>
          <input type="text" class="input" id="v_owner" placeholder="e.g. Rajesh Mehta">
        </div>
        <div class="field">
          <label class="text-label">WhatsApp / Phone Number</label>
          <input type="tel" class="input" id="v_phone" placeholder="e.g. 9819576256">
        </div>
      </div>
      <div class="grid-2">
        <div class="field">
          <label class="text-label">Venue Type</label>
          <select class="input" id="v_type">
            <option value="banquet">Banquet Hall</option>
            <option value="lawn">Wedding Lawn</option>
            <option value="hotel">Hotel / Resort</option>
            <option value="convention">Convention Center</option>
          </select>
        </div>
        <div class="field">
          <label class="text-label">Current Monthly Inquiries</label>
          <select class="input" id="v_inq">
            <option value="Under 20">Under 20 (Invisible)</option>
            <option value="20-50">20 - 50 (Surviving)</option>
            <option value="50-100">50 - 100 (Growing)</option>
            <option value="100+">100+ (Scaling)</option>
          </select>
        </div>
      </div>
      <div class="grid-2">
        <div class="field">
          <label class="text-label">Min Guest Capacity</label>
          <input type="number" class="input" id="v_cap_min" placeholder="e.g. 300" value="300">
        </div>
        <div class="field">
          <label class="text-label">Max Guest Capacity</label>
          <input type="number" class="input" id="v_cap_max" placeholder="e.g. 800" value="800">
        </div>
      </div>
      <div class="grid-2">
        <div class="field">
          <label class="text-label">Catering Rate (Starting ₹ / plate)</label>
          <input type="text" class="input" id="v_catering" placeholder="e.g. 1200">
        </div>
        <div class="field">
          <label class="text-label">Instagram Handle</label>
          <input type="text" class="input" id="v_instagram" placeholder="e.g. @grandcelebration">
        </div>
      </div>
      <div class="grid-2">
        <div class="field">
          <label class="text-label">Website URL</label>
          <input type="url" class="input" id="v_website" placeholder="e.g. grandcelebration.in">
        </div>
        <div class="field">
          <label class="text-label">Email Address</label>
          <input type="email" class="input" id="v_email" placeholder="e.g. contact@venue.com">
        </div>
      </div>
    </div>
  </div>

  <!-- STEP 2: DIGITAL PRESENCE AUDIT -->
  <div class="stage" id="st-1">
    <div class="text-label accent" style="margin-bottom: 12px;">Step 2</div>
    <h1 class="text-display">Presence <em>Audit</em></h1>
    <p class="text-lead">Evaluate their online profiles during the call. Tap the signals they currently have.</p>

    <h2 class="text-h3" style="margin-bottom: 16px;">Instagram Presence</h2>
    <div class="audit-grid">
      <div class="audit-card" onclick="toggleAudit(this)" id="audit_ig_exists">
        <div class="audit-check"></div>
        <div class="audit-content">
          <h4>Instagram Profile Live</h4>
          <p>The venue has an active Instagram account.</p>
        </div>
      </div>
      <div class="audit-card" onclick="toggleAudit(this)" id="audit_ig_reels">
        <div class="audit-check"></div>
        <div class="audit-content">
          <h4>Weekly Event Reels</h4>
          <p>They post video walkthroughs or decorations at least weekly.</p>
        </div>
      </div>
      <div class="audit-card" onclick="toggleAudit(this)" id="audit_ig_bio">
        <div class="audit-check"></div>
        <div class="audit-content">
          <h4>Clear Booking CTA in Bio</h4>
          <p>Bio has location, capacity, and direct WhatsApp contact link.</p>
        </div>
      </div>
    </div>

    <h2 class="text-h3" style="margin-bottom: 16px; margin-top: 32px;">Google Maps & Search</h2>
    <div class="audit-grid">
      <div class="audit-card" onclick="toggleAudit(this)" id="audit_gmb_opt">
        <div class="audit-check"></div>
        <div class="audit-content">
          <h4>Listing Claimed & Optimized</h4>
          <p>GMB listing exists, claimed, with correct hours and name.</p>
        </div>
      </div>
      <div class="audit-card" onclick="toggleAudit(this)" id="audit_gmb_reviews">
        <div class="audit-check"></div>
        <div class="audit-content">
          <h4>50+ High Quality Reviews</h4>
          <p>Strong recent Google reviews with replies.</p>
        </div>
      </div>
      <div class="audit-card" onclick="toggleAudit(this)" id="audit_gmb_photos">
        <div class="audit-check"></div>
        <div class="audit-content">
          <h4>Premium Photography</h4>
          <p>Listing has professional empty/full venue setup photos.</p>
        </div>
      </div>
    </div>

    <h2 class="text-h3" style="margin-bottom: 16px; margin-top: 32px;">Web Conversion</h2>
    <div class="audit-grid">
      <div class="audit-card" onclick="toggleAudit(this)" id="audit_web_mobile">
        <div class="audit-check"></div>
        <div class="audit-content">
          <h4>Mobile Optimized Web</h4>
          <p>Website loads fast on phone and is easy to read.</p>
        </div>
      </div>
      <div class="audit-card" onclick="toggleAudit(this)" id="audit_web_whatsapp">
        <div class="audit-check"></div>
        <div class="audit-content">
          <h4>WhatsApp Floating CTA</h4>
          <p>Website features a floating chat widget to reduce lead friction.</p>
        </div>
      </div>
    </div>
  </div>

  <!-- STEP 3: COMPETITIVE POSITION -->
  <div class="stage" id="st-2">
    <div class="text-label accent" style="margin-bottom: 12px;">Step 3</div>
    <h1 class="text-display">Competitive <em>Position</em></h1>
    <p class="text-lead">Compare GMB review count against local rivals and select competitor advantages.</p>

    <div class="card">
      <div class="grid-2">
        <div class="field">
          <label class="text-label">Competitor Name</label>
          <input type="text" class="input" id="c_name" placeholder="e.g. Blue Sea Banquets">
        </div>
        <div class="field">
          <label class="text-label">Competitor Google Reviews</label>
          <input type="number" class="input" id="c_reviews" placeholder="e.g. 238" value="238" oninput="calcReviewsGap()">
        </div>
      </div>
      <div class="grid-2">
        <div class="field">
          <label class="text-label">Our Google Reviews</label>
          <input type="number" class="input" id="v_reviews" placeholder="e.g. 42" value="42" oninput="calcReviewsGap()">
        </div>
        <div class="field">
          <label class="text-label">Calculated Google Review Gap</label>
          <div id="c_gap_display" style="font-family: var(--font-serif); font-size: 28px; color: var(--color-accent); padding: 10px 0;">196 reviews</div>
        </div>
      </div>

      <h3 class="text-h3" style="margin-top: 24px; margin-bottom: 16px;">Their Strategic Gaps</h3>
      <div class="audit-grid">
        <div class="audit-card" onclick="toggleAudit(this)" id="c_gap_rank">
          <div class="audit-check"></div>
          <div class="audit-content">
            <h4>Higher GMB Rankings</h4>
            <p>They rank top 3 in local maps search results.</p>
          </div>
        </div>
        <div class="audit-card" onclick="toggleAudit(this)" id="c_gap_reels">
          <div class="audit-check"></div>
          <div class="audit-content">
            <h4>Consistent Premium Reels</h4>
            <p>They post weekly reels of setups attracting prospects.</p>
          </div>
        </div>
        <div class="audit-card" onclick="toggleAudit(this)" id="c_gap_decor">
          <div class="audit-check"></div>
          <div class="audit-content">
            <h4>Visual Walkthroughs</h4>
            <p>Their posts highlight decorated vs empty setups.</p>
          </div>
        </div>
        <div class="audit-card" onclick="toggleAudit(this)" id="c_gap_pricing">
          <div class="audit-check"></div>
          <div class="audit-content">
            <h4>Lower Package Friction</h4>
            <p>They prominently display catering and hall starting rates.</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- STEP 4: OPERATIONAL HEALTH CHECK -->
  <div class="stage" id="st-3">
    <div class="text-label accent" style="margin-bottom: 12px;">Step 4</div>
    <h1 class="text-display">Operational <em>Health</em></h1>
    <p class="text-lead">Assess inquiry response time, registers, and operational bottlenecks (SmartOS fit).</p>

    <div class="card">
      <div class="grid-3">
        <div class="field">
          <label class="text-label">Response Speed</label>
          <select class="input" id="ops_speed">
            <option value="immediate">Immediate (&lt; 5 min)</option>
            <option value="fast">Fast (&lt; 1 hour)</option>
            <option value="medium">Medium (Same day)</option>
            <option value="slow">Slow (Next day)</option>
          </select>
        </div>
        <div class="field">
          <label class="text-label">Inquiry Register Type</label>
          <select class="input" id="ops_register">
            <option value="paper">Traditional Paper Register</option>
            <option value="sheets">Manual Excel/Google Sheets</option>
            <option value="crm">Digital CRM Platform</option>
          </select>
        </div>
        <div class="field">
          <label class="text-label">Follow-up Sequence</label>
          <select class="input" id="ops_followup">
            <option value="none">No follow-up (Leads die)</option>
            <option value="manual">Manual spreadsheet track</option>
            <option value="automated">Automated software triggers</option>
          </select>
        </div>
      </div>

      <h3 class="text-h3" style="margin-top: 24px; margin-bottom: 16px;">Key Operational Gaps</h3>
      <div class="audit-grid">
        <div class="audit-card" onclick="toggleAudit(this)" id="ops_bottleneck_double">
          <div class="audit-check"></div>
          <div class="audit-content">
            <h4>Double Booking Risk</h4>
            <p>Traditional calendar diary causes scheduling errors.</p>
          </div>
        </div>
        <div class="audit-card" onclick="toggleAudit(this)" id="ops_bottleneck_vendor">
          <div class="audit-check"></div>
          <div class="audit-content">
            <h4>Decorator Royalty Disputes</h4>
            <p>Manual calculation of planner and decorator commissions.</p>
          </div>
        </div>
        <div class="audit-card" onclick="toggleAudit(this)" id="ops_bottleneck_staff">
          <div class="audit-check"></div>
          <div class="audit-content">
            <h4>Staff Calendar Access</h4>
            <p>Sales staff cannot check date occupancy remotely.</p>
          </div>
        </div>
        <div class="audit-card" onclick="toggleAudit(this)" id="ops_bottleneck_owner">
          <div class="audit-check"></div>
          <div class="audit-content">
            <h4>Owner Visibility Gaps</h4>
            <p>Founder has zero real-time dashboard of pipeline values.</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- STEP 5: REVENUE REALITY CHECK -->
  <div class="stage" id="st-4">
    <div class="text-label accent" style="margin-bottom: 12px;">Step 5</div>
    <h1 class="text-display">Revenue <em>Reality</em></h1>
    <p class="text-lead">Compute monthly lost bookings and annual bleeding revenue to drive closing urgency.</p>

    <div class="card red">
      <h2 class="text-h2" style="color: var(--color-red); margin-bottom: 24px; text-align: center;">Estimated Monthly Revenue Leakage</h2>
      
      <div class="grid-3">
        <div class="field">
          <label class="text-label">Estimated Lost Inquiries / mo</label>
          <input type="number" class="input" id="leak_inquiries" value="12" oninput="calcLeakage()">
        </div>
        <div class="field">
          <label class="text-label">Conversion Rate (%)</label>
          <input type="number" class="input" id="leak_conv" value="10" oninput="calcLeakage()">
        </div>
        <div class="field">
          <label class="text-label">Avg Event Booking Value (₹)</label>
          <input type="number" class="input" id="leak_value" value="500000" oninput="calcLeakage()">
        </div>
      </div>

      <div style="border-top: 1px solid var(--color-border-light); margin-top: 24px; padding-top: 24px; display:flex; justify-content:space-between; flex-wrap:wrap; gap:16px; text-align:center;">
        <div style="flex:1;">
          <div class="text-label">Lost Bookings / Month</div>
          <div id="leak_res_bookings" style="font-family: var(--font-serif); font-size: 28px; color: var(--color-red); font-weight:700;">1.2</div>
        </div>
        <div style="flex:1;">
          <div class="text-label">Lost Revenue / Month</div>
          <div id="leak_res_rev" style="font-family: var(--font-serif); font-size: 28px; color: var(--color-red); font-weight:700;">₹6,00,000</div>
        </div>
        <div style="flex:1.5; border-left:1px solid var(--color-border-light); padding-left: 20px;">
          <div class="text-label" style="color:var(--color-red)">Annual Revenue Bleeding</div>
          <div id="leak_res_annual" style="font-family: var(--font-serif); font-size: 36px; color: var(--color-red); font-weight:800; line-height:1;">₹72,00,000</div>
        </div>
      </div>
    </div>
  </div>

  <!-- STEP 6: HEALTH DASHBOARD -->
  <div class="stage" id="st-5">
    <div class="text-label accent" style="margin-bottom: 12px;">Step 6</div>
    <h1 class="text-display">Growth <em>Dashboard</em></h1>
    <p class="text-lead">Multi-score dashboard detailing diagnostic index values across pillars.</p>

    <div class="card">
      <div class="score-wrap" style="margin-bottom:32px;">
        <div class="score-circle">
          <div class="score-num" id="diag_score">0</div>
          <div class="score-label">Maturity Score</div>
        </div>
        <h2 class="text-h2" id="diag_title">Invisible</h2>
        <p class="text-body" id="diag_desc" style="max-width: 440px; margin: 0 auto; font-size: 14px; color: var(--color-text-secondary);"></p>
      </div>

      <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:16px; margin-bottom: 24px;">
        <div style="background:var(--color-bg-deep); padding:16px; text-align:center;">
          <div style="font-size:24px; font-weight:700; color:var(--color-accent);" id="score_vis">0</div>
          <div class="text-label" style="font-size:9px; margin-top:4px;">Visibility</div>
        </div>
        <div style="background:var(--color-bg-deep); padding:16px; text-align:center;">
          <div style="font-size:24px; font-weight:700; color:var(--color-gold);" id="score_trust">0</div>
          <div class="text-label" style="font-size:9px; margin-top:4px;">Trust</div>
        </div>
        <div style="background:var(--color-bg-deep); padding:16px; text-align:center;">
          <div style="font-size:24px; font-weight:700; color:var(--color-green);" id="score_conv">0</div>
          <div class="text-label" style="font-size:9px; margin-top:4px;">Conversion</div>
        </div>
        <div style="background:var(--color-bg-deep); padding:16px; text-align:center;">
          <div style="font-size:24px; font-weight:700; color:var(--color-text-primary);" id="score_cons">0</div>
          <div class="text-label" style="font-size:9px; margin-top:4px;">Consistency</div>
        </div>
        <div style="background:var(--color-bg-deep); padding:16px; text-align:center;">
          <div style="font-size:24px; font-weight:700; color:var(--color-accent);" id="score_ops">0</div>
          <div class="text-label" style="font-size:9px; margin-top:4px;">Operations</div>
        </div>
        <div style="background:var(--color-bg-deep); padding:16px; text-align:center;">
          <div style="font-size:24px; font-weight:700; color:var(--color-red);" id="score_rev">0</div>
          <div class="text-label" style="font-size:9px; margin-top:4px;">Revenue Control</div>
        </div>
      </div>

      <div class="nba">
        <div class="nba-title">AI Recommended Next Action</div>
        <div class="nba-text" id="nba_text">Update Google Photos and start posting Weekly Reels.</div>
        <div style="font-size:12px; margin-top:8px;" id="nba_impact"></div>
      </div>
    </div>
  </div>

  <!-- STEP 7: GROWTH ROADMAP -->
  <div class="stage" id="st-6">
    <div class="text-label accent" style="margin-bottom: 12px;">Step 7</div>
    <h1 class="text-display">The <em>Roadmap</em></h1>
    <p class="text-lead">Dual modernization tracks combining organic visibility with operational tools.</p>

    <div class="grid-2">
      <div class="card" style="padding:0;">
        <div style="padding:24px; background:var(--color-accent); color:#fff;">
          <h3 class="text-h3" style="color:#fff;">Track A: DigiStories (Visibility)</h3>
          <p style="font-size:12px; opacity:0.8; margin-top:4px;">Organic & paid marketing execution</p>
        </div>
        <div style="padding:24px;">
          <div style="margin-bottom: 16px;">
            <strong style="display:block; font-size:14px; color:var(--color-text-primary);">Phase 1: Asset Foundation (Days 1-14)</strong>
            <span style="font-size:13px; color:var(--color-text-secondary);">Shoot professional interior design reels and optimize Google Maps photos.</span>
          </div>
          <div style="margin-bottom: 16px;">
            <strong style="display:block; font-size:14px; color:var(--color-text-primary);">Phase 2: Content Distribution (Days 15-45)</strong>
            <span style="font-size:13px; color:var(--color-text-secondary);">3 reels per week + post-event review generation scripts launched.</span>
          </div>
          <div>
            <strong style="display:block; font-size:14px; color:var(--color-text-primary);">Phase 3: Search Dominance (Days 45+)</strong>
            <span style="font-size:13px; color:var(--color-text-secondary);">Meta lead-gen ads to target local engaged couples directly.</span>
          </div>
        </div>
      </div>

      <div class="card" style="padding:0;">
        <div style="padding:24px; background:var(--color-gold); color:#fff;">
          <h3 class="text-h3" style="color:#fff;">Track B: SmartOS (Operations)</h3>
          <p style="font-size:12px; opacity:0.8; margin-top:4px;">Software transition & controls pilot</p>
        </div>
        <div style="padding:24px;">
          <div style="margin-bottom: 16px;">
            <strong style="display:block; font-size:14px; color:var(--color-text-primary);">Phase 1: Digital Register (Days 1-7)</strong>
            <span style="font-size:13px; color:var(--color-text-secondary);">Import traditional paper diary records into SmartOS digital register.</span>
          </div>
          <div style="margin-bottom: 16px;">
            <strong style="display:block; font-size:14px; color:var(--color-text-primary);">Phase 2: WhatsApp Automation (Days 8-14)</strong>
            <span style="font-size:13px; color:var(--color-text-secondary);">Set up automated inquiry templates, routing, and quick reply triggers.</span>
          </div>
          <div>
            <strong style="display:block; font-size:14px; color:var(--color-text-primary);">Phase 3: Pipeline Control (Days 15+)</strong>
            <span style="font-size:13px; color:var(--color-text-secondary);">Establish coordinator and decorator royalty payout dashboards.</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- STEP 8: INVESTMENT & PLAN -->
  <div class="stage" id="st-7">
    <div class="text-label accent" style="margin-bottom: 12px;">Step 8</div>
    <h1 class="text-display">The <em>Plan</em></h1>
    <p class="text-lead">ROI-oriented packages with Meta ad spend transparency and SmartOS pilot options.</p>

    <div class="grid-3" style="margin-bottom: 24px;">
      <!-- Tier 1 -->
      <div class="card" style="padding: 24px; display:flex; flex-direction:column; justify-content:space-between; border-top: 4px solid var(--color-text-muted);">
        <div>
          <div class="text-label">Starter</div>
          <div style="font-family: var(--font-serif); font-size: 32px; color:var(--color-text-primary); margin-top: 8px; margin-bottom: 12px;">₹10,000<span style="font-size:14px; color:var(--color-text-muted);">/mo</span></div>
          <ul style="font-size:12px; line-height:1.8; color:var(--color-text-secondary); margin-left: 14px;">
            <li>GMB optimization & audit</li>
            <li>Weekly caption copywriting</li>
            <li>Basic local SEO listings</li>
          </ul>
        </div>
        <button class="btn outline" style="margin-top: 20px; padding:10px;" onclick="selectPlan('Starter')">Select</button>
      </div>

      <!-- Tier 2 -->
      <div class="card gold" style="padding: 24px; display:flex; flex-direction:column; justify-content:space-between; border-top: 4px solid var(--color-gold);">
        <div>
          <div class="text-label accent">Growth</div>
          <div style="font-family: var(--font-serif); font-size: 32px; color:var(--color-text-primary); margin-top: 8px; margin-bottom: 12px;">₹15,000<span style="font-size:14px; color:var(--color-text-muted);">/mo</span></div>
          <ul style="font-size:12px; line-height:1.8; color:var(--color-text-secondary); margin-left: 14px;">
            <li>Google maps photos sync</li>
            <li>4 event reels/mo + setup scripts</li>
            <li>Meta leads campaign integration</li>
          </ul>
        </div>
        <button class="btn" style="margin-top: 20px; padding:10px;" onclick="selectPlan('Growth')">Select Plan</button>
      </div>

      <!-- Tier 3 -->
      <div class="card" style="padding: 24px; display:flex; flex-direction:column; justify-content:space-between; border-top: 4px solid var(--color-accent);">
        <div>
          <div class="text-label">Unified Engine</div>
          <div style="font-family: var(--font-serif); font-size: 32px; color:var(--color-text-primary); margin-top: 8px; margin-bottom: 12px;">₹22,000<span style="font-size:14px; color:var(--color-text-muted);">/mo</span></div>
          <ul style="font-size:12px; line-height:1.8; color:var(--color-text-secondary); margin-left: 14px;">
            <li>DigiStories social setup</li>
            <li>SmartOS software access</li>
            <li>Auto contracts & commission logs</li>
          </ul>
        </div>
        <button class="btn outline" style="margin-top: 20px; padding:10px;" onclick="selectPlan('Unified Engine')">Select</button>
      </div>
    </div>

    <div class="card" style="padding: 20px; border-left: 4px solid var(--color-green); background: var(--color-green-subtle);">
      <label style="display:flex; align-items:center; gap:12px; cursor:pointer;">
        <input type="checkbox" id="plan_smartos_pilot" style="width:18px; height:18px; accent-color:var(--color-green);" checked>
        <span style="font-size:14px; font-weight:500; color:var(--color-text-primary);">Include SmartOS 14-day free pilot for registry modernization</span>
      </label>
    </div>

    <div style="font-size:11px; text-align:center; color:var(--color-text-muted); margin-top: 16px;">
      ⚠️ Ad Spend Disclosure: 100% of Meta ad budgets are billed directly to your business card. DigiVenue charges 0% markup on media budgets.
    </div>
  </div>

  <!-- STEP 9: DECISION MAKER INTELLIGENCE (CRM panel, internal only) -->
  <div class="stage" id="st-8">
    <div class="text-label accent" style="margin-bottom: 12px;">Step 9 (Internal Only)</div>
    <h1 class="text-display">CRM <em>Intelligence</em></h1>
    <p class="text-lead">Private founder notes to log deal dynamics, decision makers, and probability before brief generation.</p>

    <div class="card">
      <div class="field">
        <label class="text-label">Internal Deal Strategy Notes</label>
        <textarea class="input" id="fn_text" placeholder="Log budget concerns, competitor pressure, family ownership structure, decorator friction, or follow-up plans. Hidden on customer output." style="height: 120px; resize:none;"></textarea>
      </div>

      <div class="grid-3">
        <div class="field">
          <label class="text-label">Decision Maker Present</label>
          <select id="deal_dm" class="input">
            <option value="Unknown">— Select —</option>
            <option value="Yes">Yes (Direct deal)</option>
            <option value="No">No (Gatekeeper)</option>
            <option value="Joint">Joint Family Decision</option>
          </select>
        </div>
        <div class="field">
          <label class="text-label">Budget Interest</label>
          <select id="deal_budget" class="input">
            <option value="Medium">— Select —</option>
            <option value="High">High (Ready to buy)</option>
            <option value="Medium">Medium (Checking prices)</option>
            <option value="Low">Low (Friction/Hesitant)</option>
          </select>
        </div>
        <div class="field">
          <label class="text-label">Deal Timeline</label>
          <select id="deal_timeline" class="input">
            <option value="Casual">— Select —</option>
            <option value="Urgent">Urgent (&lt; 14 days)</option>
            <option value="Casual">Casual (Checking dates)</option>
            <option value="Longterm">Long-term (Off-season)</option>
          </select>
        </div>
      </div>

      <div style="display:flex; align-items:center; gap:20px; margin-top:20px;">
        <span class="text-label">Gut Close Probability:</span>
        <input type="range" id="deal_prob" min="0" max="100" value="50" style="flex:1; accent-color:var(--color-accent);" oninput="document.getElementById('prob_val').textContent = this.value + '%'">
        <span id="prob_val" style="font-family:var(--font-mono); font-size:16px; color:var(--color-accent); font-weight:bold;">50%</span>
      </div>
    </div>
  </div>

  <!-- STEP 10: PROPOSAL BRIEF GENERATION -->
  <div class="stage" id="st-9">
    <div class="text-label accent" style="margin-bottom: 12px;">Step 10</div>
    <h1 class="text-display">Meeting <em>Summary</em></h1>
    <p class="text-lead">Print the customized one-page growth brief for the owner or export the raw intake playbook data.</p>

    <div class="card" style="text-align:center; padding: 48px;">
      <h3 class="text-h3" style="margin-bottom:12px;">Modernization Brief Ready</h3>
      <p style="font-size:14px; color:var(--color-text-secondary); max-width: 440px; margin: 0 auto 24px;">The Venue Health Brief is structured respectfully to anchor the closing conversations. Review is complete.</p>
      
      <div style="display:flex; gap:16px; justify-content:center;">
        <button class="btn" onclick="generateBrief()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px; display: inline-block; vertical-align: middle;"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
          Print Brief
        </button>
        <button class="btn outline" onclick="exportIntakeJSON()">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right: 6px; display: inline-block; vertical-align: middle;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          Export JSON Data
        </button>
      </div>
    </div>
  </div>

</div>

<!-- Printable Brief Structure (Hidden normally) -->
<div class="print-brief" id="printBrief" style="display:none; margin-top: 48px; background: #fff; color: #000; padding: 40px;">
  <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #000; padding-bottom: 16px; margin-bottom: 24px;">
    <img src="logo.svg" alt="DigiVenue" style="height: 24px; width: auto; display: block; filter: brightness(0); max-width: 130px;">
    <h1 style="font-family: var(--font-serif); font-size: 22px; font-weight: 500; margin: 0; padding: 0; border: none; line-height: 1;">Digital Modernization Brief</h1>
  </div>
  
  <div class="print-section">
    <h3>Venue Profile</h3>
    <div class="print-row"><span class="print-label">Venue Name:</span> <span id="p_vname"></span></div>
    <div class="print-row"><span class="print-label">Territory / Area:</span> <span id="p_vloc"></span></div>
    <div class="print-row"><span class="print-label">Primary Owner Contact:</span> <span id="p_vowner"></span></div>
    <div class="print-row"><span class="print-label">Monthly Scale Baseline:</span> <span id="p_vinq"></span></div>
    <div class="print-row"><span class="print-label">Capacity Limits:</span> <span><span id="p_vcap_min">300</span> - <span id="p_vcap_max">800</span> guests</span></div>
    <div class="print-row"><span class="print-label">Catering Rate (Plate):</span> <span id="p_vcatering">N/A</span></div>
    <div class="print-row"><span class="print-label">Instagram Handle:</span> <span id="p_vinstagram">N/A</span></div>
  </div>

  <div class="print-section">
    <h3>Digital Presence Diagnosis</h3>
    <div style="font-family: var(--font-serif); font-size: 20px; margin-bottom: 6px;">Growth Maturity Score: <span id="p_score"></span>/100</div>
    <p style="font-size: 13px; line-height: 1.6; color: #333;" id="p_diag"></p>
  </div>

  <div class="print-section">
    <h3>Market Competitive Position</h3>
    <div class="print-row"><span class="print-label">Primary Competitor Name:</span> <span id="p_cname"></span></div>
    <div class="print-row"><span class="print-label">Competitor Review Gaps:</span> <span id="p_cgap"></span></div>
    <div class="print-row"><span class="print-label">Their Digital Advantage:</span> <span id="p_cadv"></span></div>
  </div>

  <div class="print-section">
    <h3>Actionable Next Steps</h3>
    <p style="font-size: 14px; font-weight: 600; color: #000;" id="p_nba"></p>
    <p style="font-size: 12px; color: #333; margin-top: 4px;" id="p_nba_impact"></p>
  </div>

  <div class="print-section">
    <h3>Modernization Pilot Plan</h3>
    <div class="print-row"><span class="print-label">Plan Recommendation:</span> <span id="p_plan_name">Growth Plan</span></div>
    <div class="print-row"><span class="print-label">Operational Pilot Track:</span> <span id="p_plan_pilot">SmartOS 14-Day Free Pilot Included</span></div>
    <div class="print-row"><span class="print-label">Monthly Investment:</span> <span id="p_plan_inv">₹15,000/mo</span></div>
  </div>
  
  <p style="font-size: 11px; color: #999; text-align: center; margin-top: 48px;">Generated by DigiVenue growth Consultation System. Internal copy reserved.</p>
</div>

<!-- CONTROLS -->
<div class="controls">
  <button class="btn outline" id="btnPrev" onclick="navStep(-1)" style="visibility: hidden;">Previous</button>
  <button class="btn" id="btnNext" onclick="navStep(1)">Continue</button>
</div>

<!-- Live data published by the pipeline (run_pipeline.py writes this file) -->
<script src="intelligence_data.js" onerror="window.PANELS=window.PANELS||null;"></script>
<script>
  let selectedPlanName = "Growth Plan";
  let selectedPlanPrice = "₹15,000";

  // ═══════ LIVE VENUE INTELLIGENCE ═══════
  function initIntel() {
    const sel = document.getElementById('intel_select');
    if (!sel) return;
    if (typeof window.PANELS !== 'object' || !window.PANELS) {
      document.getElementById('intel_empty').textContent =
        'No live data file found (intelligence_data.js). Run python run_pipeline.py to generate it, then refresh this page.';
      return;
    }
    // Sort venues weakest DMI first (best opportunity at top)
    const names = Object.keys(window.PANELS).sort(
      (a, b) => (window.PANELS[a].dmi_score || 0) - (window.PANELS[b].dmi_score || 0)
    );
    names.forEach(n => {
      const o = document.createElement('option');
      o.value = n;
      const v = window.PANELS[n];
      o.textContent = `${n} — ${v.suburb || ''} (DMI ${v.dmi_score})`;
      sel.appendChild(o);
    });
  }

  function initIntelToggle() {
    const btn = document.getElementById('toggleIntelBtn');
    const wrap = document.getElementById('intelCardWrap') || document.getElementById('intelCard');
    const card = document.getElementById('intelCard');
    if (!btn || !wrap) return;

    const isInternal = new URLSearchParams(location.search).get('internal') === '1';
    btn.style.display = isInternal ? 'inline-block' : 'none';

    const visible = sessionStorage.getItem('intelVisible') === '1';
    wrap.style.display = visible ? 'block' : 'none';
    if (card) card.style.display = visible ? 'block' : 'none';

    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const isHidden = wrap.style.display === 'none' || !wrap.style.display;
      wrap.style.display = isHidden ? 'block' : 'none';
      if (card) card.style.display = isHidden ? 'block' : 'none';
      sessionStorage.setItem('intelVisible', isHidden ? '1' : '0');
    });
  }

  function bullets(arr) {
    return (arr || []).map(l => `• ${l}`).join('<br>');
  }

  function renderIntel() {
    const name = document.getElementById('intel_select').value;
    const body = document.getElementById('intel_body');
    const empty = document.getElementById('intel_empty');
    if (!name || !window.PANELS || !window.PANELS[name]) {
      body.style.display = 'none';
      empty.style.display = 'block';
      return;
    }
    const v = window.PANELS[name];
    empty.style.display = 'none';
    body.style.display = 'block';

    document.getElementById('intel_name').textContent = name;
    document.getElementById('intel_meta').textContent =
      `${v.suburb || ''} · DMI ${v.dmi_score} (${v.dmi_category})`;

    const src = document.getElementById('intel_source');
    if (v.data_source === 'google_live') {
      src.textContent = '✅ Real Google data';
      src.style.background = '#E3F1E8'; src.style.color = '#1a7a4a';
    } else {
      src.textContent = '🤖 AI estimate';
      src.style.background = '#FBEFE9'; src.style.color = '#B83615';
    }

    // Panel 1 — Territory
    document.getElementById('intel_territory').innerHTML = bullets(v.territory_rank.lines);
    // Panel 2 — Silence
    document.getElementById('intel_silence_score').textContent = v.digital_silence.score + '/100';
    document.getElementById('intel_silence').innerHTML =
      `<b>${v.digital_silence.label}</b><br>` + bullets(v.digital_silence.lines);
    // Panel 3 — SmartOS
    document.getElementById('intel_smartos_score').textContent = v.smartos_opportunity.opportunity_score + '/100';
    document.getElementById('intel_smartos').innerHTML = bullets(v.smartos_opportunity.lines);
    // Panel 4 — Momentum
    document.getElementById('intel_momentum_score').textContent = v.growth_momentum.score + '/100';
    document.getElementById('intel_momentum').innerHTML =
      `<b>${v.growth_momentum.label}</b><br>` + bullets(v.growth_momentum.lines) +
      (v.growth_momentum.is_buying_signal ? '<br><b style="color:#1a7a4a;">🔥 Buying signal</b>' : '');
    // Panel 5 — Relationship
    const rel = v.relationship;
    document.getElementById('intel_relationship').innerHTML =
      (rel.tags && rel.tags.length
        ? rel.tags.map(t => `<span style="display:inline-block;background:var(--color-gold-subtle);border:1px solid var(--color-border-gold);padding:2px 8px;border-radius:4px;margin:2px;font-size:12px;">${t}</span>`).join(' ')
        : '• No field intel captured yet') +
      (rel.notes ? `<br><span style="color:var(--color-text-muted);">${rel.notes}</span>` : '');
  }

  function loadIntelIntoConsultation() {
    const name = document.getElementById('intel_select').value;
    if (!name || !window.PANELS[name]) return;
    const v = window.PANELS[name];
    
    // Set venue inputs
    document.getElementById('v_name').value = name;
    document.getElementById('v_loc').value = v.suburb || '';
    
    // Sync review inputs in Step 3
    document.getElementById('v_reviews').value = v.territory_rank ? (window.PANELS[name].google_reviews_count || 42) : 42;
    calcReviewsGap();
    
    goToStep(0);
  }

  const STEPS = [
    { id: 'venue_info', label: 'Venue' },
    { id: 'audit', label: 'Audit' },
    { id: 'competitor', label: 'Competitor' },
    { id: 'operations', label: 'Operations' },
    { id: 'revenue', label: 'Revenue' },
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'roadmap', label: 'Roadmap' },
    { id: 'package', label: 'Plan' },
    { id: 'deal', label: 'CRM' },
    { id: 'proposal', label: 'Brief' }
  ];

  let currentStep = 0;
  
  function initNav() {
    const navBar = document.getElementById('navBar');
    let html = '';
    STEPS.forEach((s, i) => {
      html += `<div class="nav-item ${i === 0 ? 'active' : ''}" id="nav-item-${i}" onclick="goToStep(${i})">
                 <span class="nav-num">0${i+1}</span> ${s.label}
               </div>`;
    });
    navBar.innerHTML = html;
  }

  function goToStep(index) {
    if (index < 0 || index >= STEPS.length) return;
    
    // Auto calculations before switching panels
    if (index === 2) calcReviewsGap();
    if (index === 4) calcLeakage();
    if (index === 5) calculateDiagnosis();

    // Hide all
    document.querySelectorAll('.stage').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    
    // Show current
    document.getElementById(`st-${index}`).classList.add('active');
    document.getElementById(`nav-item-${index}`).classList.add('active');
    
    currentStep = index;
    
    // Controls
    document.getElementById('btnPrev').style.visibility = index === 0 ? 'hidden' : 'visible';
    const nextBtn = document.getElementById('btnNext');
    if (index === STEPS.length - 1) {
      nextBtn.style.display = 'none';
    } else {
      nextBtn.style.display = 'inline-flex';
    }
    
    // Scroll nav
    const navItem = document.getElementById(`nav-item-${index}`);
    if (navItem) {
      navItem.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function navStep(dir) {
    goToStep(currentStep + dir);
  }

  // Audit Toggles
  function toggleAudit(el) {
    el.classList.toggle('active');
    calculateDiagnosis();
  }

  // Competitor Review Gap
  function calcReviewsGap() {
    const cReviews = parseInt(document.getElementById('c_reviews').value) || 0;
    const vReviews = parseInt(document.getElementById('v_reviews').value) || 0;
    const gap = Math.max(0, cReviews - vReviews);
    document.getElementById('c_gap_display').textContent = gap + " reviews";
  }

  // Revenue Leakage Calculator
  function calcLeakage() {
    const inq = parseFloat(document.getElementById('leak_inquiries').value) || 0;
    const conv = parseFloat(document.getElementById('leak_conv').value) || 0;
    const val = parseFloat(document.getElementById('leak_value').value) || 0;
    
    const bookings = inq * (conv / 100);
    const rev = bookings * val;
    const annual = rev * 12;
    
    document.getElementById('leak_res_bookings').textContent = bookings.toFixed(1);
    document.getElementById('leak_res_rev').textContent = "₹" + rev.toLocaleString('en-IN');
    document.getElementById('leak_res_annual').textContent = "₹" + annual.toLocaleString('en-IN');
  }

  // Plan Selection
  function selectPlan(name) {
    selectedPlanName = name;
    if (name === "Starter") {
      selectedPlanPrice = "₹10,000/mo";
    } else if (name === "Growth") {
      selectedPlanPrice = "₹15,000/mo";
    } else {
      selectedPlanPrice = "₹22,000/mo";
    }
    alert("Selected plan: " + name + " (" + selectedPlanPrice + ")");
    navStep(1);
  }

  // Diagnosis Score Calculation
  function calculateDiagnosis() {
    // Audit Score variables
    const check_ig_exists = document.getElementById('audit_ig_exists').classList.contains('active');
    const check_ig_reels = document.getElementById('audit_ig_reels').classList.contains('active');
    const check_ig_bio = document.getElementById('audit_ig_bio').classList.contains('active');
    const check_gmb_opt = document.getElementById('audit_gmb_opt').classList.contains('active');
    const check_gmb_reviews = document.getElementById('audit_gmb_reviews').classList.contains('active');
    const check_gmb_photos = document.getElementById('audit_gmb_photos').classList.contains('active');
    const check_web_mobile = document.getElementById('audit_web_mobile').classList.contains('active');
    const check_web_whatsapp = document.getElementById('audit_web_whatsapp').classList.contains('active');

    // 6 Pillars calculations
    // 1. Visibility Score (IG exists/reels + GMB Listing/Photos)
    let score_visibility = 0;
    if (check_ig_exists) score_visibility += 25;
    if (check_ig_reels) score_visibility += 25;
    if (check_gmb_opt) score_visibility += 25;
    if (check_gmb_photos) score_visibility += 25;

    // 2. Trust Score (Reviews + Photos)
    let score_trust = 0;
    if (check_gmb_reviews) score_trust += 50;
    if (check_gmb_photos) score_trust += 50;

    // 3. Conversion Score (Website mobile + Website WhatsApp + IG bio)
    let score_conversion = 0;
    if (check_web_mobile) score_conversion += 40;
    if (check_web_whatsapp) score_conversion += 40;
    if (check_ig_bio) score_conversion += 20;

    // 4. Consistency Score (Instagram reels + Bio CTA)
    let score_consistency = 0;
    if (check_ig_reels) score_consistency += 60;
    if (check_ig_bio) score_consistency += 40;

    // 5. Operations Score (Register type + Response speed)
    const register_type = document.getElementById('ops_register').value;
    const response_speed = document.getElementById('ops_speed').value;
    let score_operations = 30; // base line
    if (register_type === 'crm') score_operations += 40;
    else if (register_type === 'sheets') score_operations += 20;
    if (response_speed === 'immediate') score_operations += 30;
    else if (response_speed === 'fast') score_operations += 15;

    // 6. Revenue Control Score (inverse of operational bottleneck checks)
    const bot_double = document.getElementById('ops_bottleneck_double').classList.contains('active');
    const bot_vendor = document.getElementById('ops_bottleneck_vendor').classList.contains('active');
    const bot_staff = document.getElementById('ops_bottleneck_staff').classList.contains('active');
    const bot_owner = document.getElementById('ops_bottleneck_owner').classList.contains('active');
    let score_revenue = 100;
    if (bot_double) score_revenue -= 25;
    if (bot_vendor) score_revenue -= 25;
    if (bot_staff) score_revenue -= 25;
    if (bot_owner) score_revenue -= 25;

    // Map to grid HTML elements
    document.getElementById('score_vis').textContent = score_visibility;
    document.getElementById('score_trust').textContent = score_trust;
    document.getElementById('score_conv').textContent = score_conversion;
    document.getElementById('score_cons').textContent = score_consistency;
    document.getElementById('score_ops').textContent = score_operations;
    document.getElementById('score_rev').textContent = score_revenue;

    // Weighted Overall Maturity Score
    const total_weighted = Math.round(
      (score_visibility * 0.25) + 
      (score_trust * 0.20) + 
      (score_conversion * 0.20) + 
      (score_consistency * 0.15) + 
      (score_operations * 0.10) + 
      (score_revenue * 0.10)
    );

    document.getElementById('diag_score').textContent = total_weighted;

    // Classification
    let title = "Invisible";
    let desc = "Right now, the venue lacks digital foundation. Families checking online cannot find or verify you, leading to inquiry loss.";
    let nba = "Reclaim Google maps presence & launch visual reels distribution.";
    let impact = "Expected Impact: +22% maps search visibility in 30 days.";

    if (total_weighted >= 90) {
      title = "Market Leader";
      desc = "The venue is fully systemized. High visibility, high trust, and automated SmartOS operations.";
      nba = "Implement machine learning ads scaling.";
      impact = "Expected Impact: +8-12 bookings monthly.";
    } else if (total_weighted >= 65) {
      title = "Active";
      desc = "You have the foundation, but gaps in operations and consistency are leaking inquiries to competitors.";
      nba = "Plug lead leakage with SmartOS automated WhatsApp replies.";
      impact = "Expected Impact: Reduce inquiry response time under 5 minutes.";
    } else if (total_weighted >= 35) {
      title = "Present but Weak";
      desc = "The venue exists online but looks traditional. You are losing high-value clients to modernized rivals.";
      nba = "Launch post-wedding review loops and shoot empty-to-decorated walkthroughs.";
      impact = "Expected Impact: Establish trust with 40+ Google reviews.";
    }

    document.getElementById('diag_title').textContent = title;
    document.getElementById('diag_desc').textContent = desc;
    document.getElementById('nba_text').textContent = nba;
    document.getElementById('nba_impact').textContent = impact;
  }

  function generateBrief() {
    // Populate printable elements
    document.getElementById('p_vname').textContent = document.getElementById('v_name').value || 'Unnamed Venue';
    document.getElementById('p_vloc').textContent = document.getElementById('v_loc').value || 'N/A';
    document.getElementById('p_vowner').textContent = document.getElementById('v_owner').value || 'Owner';
    document.getElementById('p_vinq').textContent = document.getElementById('v_inq').value || 'N/A';
    document.getElementById('p_vcap_min').textContent = document.getElementById('v_cap_min').value || '300';
    document.getElementById('p_vcap_max').textContent = document.getElementById('v_cap_max').value || '800';
    document.getElementById('p_vcatering').textContent = document.getElementById('v_catering').value || 'N/A';
    document.getElementById('p_vinstagram').textContent = document.getElementById('v_instagram').value || 'N/A';
    
    document.getElementById('p_score').textContent = document.getElementById('diag_score').textContent;
    document.getElementById('p_diag').textContent = document.getElementById('diag_desc').textContent;
    document.getElementById('p_cname').textContent = document.getElementById('c_name').value || 'N/A';
    document.getElementById('p_cgap').textContent = document.getElementById('c_gap_display').textContent;
    
    // Competitor advantage description
    let advs = [];
    if (document.getElementById('c_gap_rank').classList.contains('active')) advs.push("Higher GMB ranking");
    if (document.getElementById('c_gap_reels').classList.contains('active')) advs.push("Instagram Reels consistency");
    if (document.getElementById('c_gap_decor').classList.contains('active')) advs.push("Walkthrough videos");
    document.getElementById('p_cadv').textContent = advs.join(", ") || "General visibility supremacy";
    
    document.getElementById('p_nba').textContent = document.getElementById('nba_text').textContent;
    document.getElementById('p_nba_impact').textContent = document.getElementById('nba_impact').textContent;
    
    document.getElementById('p_plan_name').textContent = selectedPlanName;
    document.getElementById('p_plan_inv').textContent = selectedPlanPrice + "/mo";
    
    const pilot_checked = document.getElementById('plan_smartos_pilot').checked;
    document.getElementById('p_plan_pilot').textContent = pilot_checked ? "SmartOS 14-Day Free Pilot Included" : "Pilot Declined";

    document.getElementById('printBrief').style.display = 'block';
    
    setTimeout(() => {
      window.print();
      document.getElementById('printBrief').style.display = 'none';
    }, 150);
  }

  function exportIntakeJSON() {
    const vName = document.getElementById('v_name').value.trim();
    if (!vName) {
      alert("Please enter a Venue Name in Step 1 before exporting.");
      goToStep(0);
      return;
    }

    const vLoc = document.getElementById('v_loc').value.trim();
    const vOwner = document.getElementById('v_owner').value.trim();
    const vPhone = document.getElementById('v_phone').value.trim();
    const vType = document.getElementById('v_type').value;
    const vInq = document.getElementById('v_inq').value;
    const vCapMin = parseInt(document.getElementById('v_cap_min').value) || 300;
    const vCapMax = parseInt(document.getElementById('v_cap_max').value) || 800;
    const vCatering = document.getElementById('v_catering').value.trim();
    const vInstagram = document.getElementById('v_instagram').value.trim();
    const vWebsite = document.getElementById('v_website').value.trim();
    const vEmail = document.getElementById('v_email').value.trim();

    // Checkboxes from Step 2
    const hasIgExists = document.getElementById('audit_ig_exists').classList.contains('active');
    const hasIgReels = document.getElementById('audit_ig_reels').classList.contains('active');
    const hasIgBio = document.getElementById('audit_ig_bio').classList.contains('active');
    const hasGmbOpt = document.getElementById('audit_gmb_opt').classList.contains('active');
    const hasGmbReviews = document.getElementById('audit_gmb_reviews').classList.contains('active');
    const hasGmbPhotos = document.getElementById('audit_gmb_photos').classList.contains('active');
    const hasWebMobile = document.getElementById('audit_web_mobile').classList.contains('active');
    const hasWebWhatsapp = document.getElementById('audit_web_whatsapp').classList.contains('active');

    // Competitor inputs from Step 3
    const cName = document.getElementById('c_name').value.trim();
    const cReviews = parseInt(document.getElementById('c_reviews').value) || 0;
    const vReviews = parseInt(document.getElementById('v_reviews').value) || 0;

    // Operational from Step 4
    const opsSpeed = document.getElementById('ops_speed').value;
    const opsRegister = document.getElementById('ops_register').value;
    const opsFollowup = document.getElementById('ops_followup').value;
    const botDouble = document.getElementById('ops_bottleneck_double').classList.contains('active');
    const botVendor = document.getElementById('ops_bottleneck_vendor').classList.contains('active');
    const botStaff = document.getElementById('ops_bottleneck_staff').classList.contains('active');
    const botOwner = document.getElementById('ops_bottleneck_owner').classList.contains('active');

    // Revenue Leakage from Step 5
    const leakInq = document.getElementById('leak_inquiries').value;
    const leakBook = document.getElementById('leak_res_bookings').textContent;
    const leakRev = document.getElementById('leak_res_rev').textContent;

    // Private Notes & Deal Info from Step 9
    const notesText = document.getElementById('fn_text').value.trim();
    const dealDM = document.getElementById('deal_dm').value;
    const dealBudget = document.getElementById('deal_budget').value;
    const dealTime = document.getElementById('deal_timeline').value;
    const dealProb = document.getElementById('deal_prob').value;

    const igExists = vInstagram !== '' && vInstagram.toLowerCase() !== 'none';
    const webExists = vWebsite !== '' && vWebsite.toLowerCase() !== 'none';

    // Build the audit flags object
    const auditObj = {
      gmb_missing: !hasGmbOpt,
      gmb_exists: hasGmbOpt,
      gmb_reviews: hasGmbReviews,
      gmb_photos: hasGmbPhotos,
      gmb_recent_rev: hasGmbReviews,
      gmb_responds: hasGmbReviews,
      ig_exists: igExists,
      ig_dead: igExists ? !hasIgReels : true,
      ig_reels: hasIgReels,
      ig_recent: hasIgReels,
      ig_realevents: hasIgReels,
      ig_consistent: hasIgReels && hasIgBio,
      ig_cta: hasIgBio,
      web_exists: webExists,
      web_none: !webExists,
      web_mobile: hasWebMobile,
      web_inquiry: hasWebWhatsapp,
      web_whatsapp: hasWebWhatsapp,
      web_visuals: hasWebMobile,
      trust_proof: hasGmbReviews,
      trust_response: hasWebWhatsapp,
      trust_unique: true,
      trust_invisible: !hasGmbOpt
    };

    // Build pain points list
    let painPoints = [];
    if (!hasGmbReviews) painPoints.push("losing trust due to few Google reviews");
    if (!hasIgReels) painPoints.push("poor Instagram visibility and reels engagement");
    if (!hasWebWhatsapp) painPoints.push("losing digital leads due to friction on the web");
    if (cName) painPoints.push(`losing bookings to competitor ${cName} (gap: ${cReviews - vReviews} reviews)`);
    if (opsRegister === 'paper') painPoints.push("operational double booking risk from traditional registers");
    const painText = painPoints.join(", ") || "needs general online visibility and booking workflow modernization";

    // Setup the final intake payload
    const intake = {
      business: {
        name: vName,
        owner: vOwner,
        phone: vPhone,
        city: vLoc,
        area: vLoc,
        type: vType,
        capacityMin: vCapMin,
        capacityMax: vCapMax,
        email: vEmail,
        tagline: `${vName} — Premium ${vType.charAt(0).toUpperCase() + vType.slice(1)} in ${vLoc}`
      },
      online: {
        website: vWebsite,
        instagram: vInstagram,
        socialState: hasIgReels ? 'active' : 'dormant',
        inquiries: vInq
      },
      pricing: {
        cateringFrom: vCatering,
        packages: selectedPlanName,
        usp: cName ? `Differentiation from ${cName}` : "Hospitality excellence"
      },
      discovery: {
        pain: painText
      },
      audit: auditObj,
      auditScore: parseInt(document.getElementById('diag_score').textContent) || 0,
      assetsMissing: [],
      accessPending: [],
      notes: notesText,
      founderNotes: notesText,
      deal: {
        decisionMaker: dealDM,
        budget: dealBudget,
        timeline: dealTime,
        probability: dealProb
      },
      leakage: {
        inquiries: leakInq,
        bookings: leakBook,
        revenue: leakRev
      },
      competitor: {
        name: cName,
        reviews: cReviews
      },
      plan: {
        name: selectedPlanName,
        price: selectedPlanPrice,
        smartosPilot: document.getElementById('plan_smartos_pilot').checked
      }
    };

    // Trigger download
    const blob = new Blob([JSON.stringify(intake, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${vName.toLowerCase().replace(/[^a-z0-9]+/g, '_')}_intake.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  // Init
  initNav();
  initIntel();
  initIntelToggle();
</script>
</body>
</html>
"""

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Restructured HTML Sales Tool successfully!")
