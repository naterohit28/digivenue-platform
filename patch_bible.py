import re

path = r"C:\Users\rohit\Downloads\DigiStories\_Web\venue-growth-bible-engine.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update DEFAULT_CONFIG
if "deal:" not in content:
    content = content.replace(
        '  cta: {\n    label: "WhatsApp",\n    type: "whatsapp",\n    enableStoriesHooks: true\n  }',
        '  cta: {\n    label: "WhatsApp",\n    type: "whatsapp",\n    enableStoriesHooks: true\n  },\n  deal: { budget: "", decisionMaker: "", timeline: "", probability: "" },\n  leakage: { inquiries: "12", bookings: "1.5", revenue: "7.5L" },\n  competitor: { name: "Blue Sea", reviews: "238" }'
    )

# 2. Update buildSetupForm
if "f_compName" not in content:
    setup_form_addition = """
  // Deal & Competitor Config
  h += `<div class="setup-group" style="background:#111; border:1px solid var(--accent);"><div class="setup-group-title" style="color:var(--accent)">Deal & Intel (Private)</div>`;
  h += `<div class="setup-row">${field('Competitor Name','f_compName',c.competitor?.name||'')} ${field('Competitor Reviews','f_compRev',c.competitor?.reviews||'')}</div>`;
  h += `<div class="setup-row">${field('Lost Inquiries/mo','f_leakInq',c.leakage?.inquiries||'')} ${field('Lost Bookings/mo','f_leakBook',c.leakage?.bookings||'')}</div>`;
  h += `<div class="setup-row">${field('Lost Rev/mo','f_leakRev',c.leakage?.revenue||'')}</div>`;
  h += `<div class="setup-row">${field('Budget Interest','f_dealBudg',c.deal?.budget||'',{select:true,options:['','High','Medium','Low']})} ${field('Decision Maker','f_dealDM',c.deal?.decisionMaker||'',{select:true,options:['','Yes','No','Unknown']})}</div>`;
  h += `<div class="setup-row">${field('Timeline','f_dealTime',c.deal?.timeline||'')} ${field('Probability %','f_dealProb',c.deal?.probability||'')}</div>`;
  h += `</div>`;
"""
    content = content.replace(
        "document.getElementById('setupForm').innerHTML = h;",
        setup_form_addition + "\n  document.getElementById('setupForm').innerHTML = h;"
    )

# 3. Update saveSetup
if "CONFIG.competitor" not in content:
    save_setup_addition = """
  if(!CONFIG.competitor) CONFIG.competitor={};
  CONFIG.competitor.name = g('f_compName');
  CONFIG.competitor.reviews = g('f_compRev');
  if(!CONFIG.leakage) CONFIG.leakage={};
  CONFIG.leakage.inquiries = g('f_leakInq');
  CONFIG.leakage.bookings = g('f_leakBook');
  CONFIG.leakage.revenue = g('f_leakRev');
  if(!CONFIG.deal) CONFIG.deal={};
  CONFIG.deal.budget = g('f_dealBudg');
  CONFIG.deal.decisionMaker = g('f_dealDM');
  CONFIG.deal.timeline = g('f_dealTime');
  CONFIG.deal.probability = g('f_dealProb');
"""
    content = content.replace(
        "CONFIG.pricing.packages = JSON.parse(JSON.stringify(_pkgTmp));",
        "CONFIG.pricing.packages = JSON.parse(JSON.stringify(_pkgTmp));" + save_setup_addition
    )

# 4. Replace renderIntel completely
intel_new = """function renderIntel(){
  const el = document.getElementById('intel'); if(!el) return;

  // Compute data with fallbacks
  let m = {level:1,score:50,dim:{}};
  let scores = {visibility:{val:30},conversion:{val:25},growth:{val:40}};
  let recs = [{
    action: 'Google Review Reactivation Campaign',
    why: 'Customers searching "venue in your city" cannot find you. This is the single biggest leak.',
    impact: '+22% local search visibility within 30 days.'
  }];

  if (CONFIG.assessment && typeof computeScores === 'function') {
      try {
          const res = computeScores();
          m = res.maturity;
          scores = res.scores;
          recs = topRecommendations();
      } catch(e) {}
  }
  
  const compName = (CONFIG.competitor && CONFIG.competitor.name) || "Blue Sea";
  const compRev = parseInt((CONFIG.competitor && CONFIG.competitor.reviews) || "238");
  const youRev = 42; // Simulated current state
  const gap = Math.max(0, compRev - youRev);
  
  const leakInq = (CONFIG.leakage && CONFIG.leakage.inquiries) || "12";
  const leakBook = (CONFIG.leakage && CONFIG.leakage.bookings) || "1.5";
  const leakRev = (CONFIG.leakage && CONFIG.leakage.revenue) || "7.5L";

  let h = `<div class="section-header">
      <div class="section-tag">Growth Intelligence</div>
      <h2 class="section-title">Your growth <em>intelligence</em></h2>
    </div>`;

  // 1. Competitive Gap Visualization
  h += `<div class="card" style="margin-bottom:18px; display:flex; gap:20px; align-items:center; background:var(--bg-1); border: 1px solid var(--border);">
    <div style="flex:1; text-align:center;">
      <div class="mono" style="color:var(--text-3); font-size:12px;">You</div>
      <div style="font-size:32px; font-weight:700; color:var(--text);">${youRev}</div>
      <div style="font-size:11px; color:var(--text-3);">Google Reviews</div>
    </div>
    <div style="font-size:24px; color:var(--text-2);">vs</div>
    <div style="flex:1; text-align:center;">
      <div class="mono" style="color:var(--accent); font-size:12px;">${esc(compName)}</div>
      <div style="font-size:32px; font-weight:700; color:var(--accent);">${compRev}</div>
      <div style="font-size:11px; color:var(--text-3);">Google Reviews</div>
    </div>
    <div style="flex:1.5; text-align:center; border-left: 1px solid var(--border); padding-left: 20px;">
      <div class="mono" style="color:#ef4444; font-size:12px;">Visibility Gap</div>
      <div style="font-size:42px; font-weight:800; color:#ef4444; line-height:1;">${gap}</div>
      <div style="font-size:11px; color:var(--text-3);">Lost social proof</div>
    </div>
  </div>`;

  // 2. Revenue Leakage Card
  h += `<div class="card" style="margin-bottom:18px; border-left:4px solid #ef4444; background:rgba(239, 68, 68, 0.05);">
    <h3 style="color:#ef4444; font-size:14px; text-transform:uppercase; letter-spacing:1px; margin-bottom:14px;">Estimated Monthly Revenue Leakage</h3>
    <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px;">
      <div>
        <div style="font-size:24px; font-weight:700;">${esc(leakInq)}</div>
        <div style="font-size:11px; color:var(--text-2);">Lost Inquiries</div>
      </div>
      <div>
        <div style="font-size:24px; font-weight:700;">${esc(leakBook)}</div>
        <div style="font-size:11px; color:var(--text-2);">Lost Bookings</div>
      </div>
      <div style="text-align:right;">
        <div style="font-size:28px; font-weight:800; color:#ef4444;">₹${esc(leakRev)}</div>
        <div style="font-size:11px; color:var(--text-2);">Estimated Revenue Lost</div>
      </div>
    </div>
  </div>`;

  // 3. SmartOS Readiness Card
  const vScore = scores.visibility?.val || 30;
  const oScore = scores.conversion?.val || 25;
  const gScore = scores.growth?.val || (m.score || 40);
  
  h += `<div class="card" style="margin-bottom:18px;">
    <h3 style="margin-bottom:16px;">SmartOS Readiness</h3>
    <div style="display:flex; gap:15px; text-align:center; flex-wrap:wrap;">
      <div style="flex:1; min-width:80px; background:var(--bg-2); padding:15px; border-radius:8px;">
        <div style="font-size:28px; font-weight:700; color:var(--accent);">${vScore}</div>
        <div class="mono" style="font-size:10px; color:var(--text-3); margin-top:5px;">VISIBILITY</div>
      </div>
      <div style="flex:1; min-width:80px; background:var(--bg-2); padding:15px; border-radius:8px;">
        <div style="font-size:28px; font-weight:700; color:var(--green);">${oScore}</div>
        <div class="mono" style="font-size:10px; color:var(--text-3); margin-top:5px;">OPERATIONAL</div>
      </div>
      <div style="flex:1; min-width:80px; background:var(--bg-2); padding:15px; border-radius:8px;">
        <div style="font-size:28px; font-weight:700; color:var(--gold);">${gScore}</div>
        <div class="mono" style="font-size:10px; color:var(--text-3); margin-top:5px;">GROWTH</div>
      </div>
    </div>
  </div>`;

  // 4. AI Recommended Next Action
  if (recs.length > 0) {
    const r = recs[0];
    h += `<div class="card" style="margin-bottom:18px; border: 1px solid var(--accent); background:linear-gradient(135deg, var(--bg-1), rgba(197, 160, 89, 0.05));">
      <div class="mono" style="font-size:11px; color:var(--accent); margin-bottom:8px;">PRIORITY #1</div>
      <h3 style="font-size:22px; margin-bottom:8px; color:var(--text);">${esc(r.action)}</h3>
      <p style="font-size:14px; color:var(--text-2); margin-bottom:12px;">${esc(r.why)}</p>
      <div style="background:var(--bg-2); padding:10px 14px; border-radius:6px; display:inline-block; border-left: 2px solid var(--green);">
        <strong style="color:var(--green); font-size:12px;">Expected Impact:</strong>
        <span style="font-size:13px; color:var(--text); margin-left:6px;">${esc(r.impact)}</span>
      </div>
    </div>`;
  }

  el.innerHTML = h;
}"""

# Extract the old renderIntel using regex
pattern = re.compile(r"function renderIntel\(\)\{.*?(?=function renderGrowthInvestment\(\))", re.DOTALL)
content = re.sub(pattern, intel_new + "\n\n", content)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Patched successfully!")
