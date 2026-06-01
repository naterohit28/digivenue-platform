import re

path = r"C:\Users\rohit\Downloads\DigiStories\_Web\digistories-sales-tool-v2.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Step 3 (Competitor) to add Reviews
if 'id="c_reviews"' not in content:
    comp_inputs = """
        <div class="input-group">
          <label class="text-label">Competitor Name</label>
          <input type="text" id="c_name1" class="input-text" placeholder="e.g. Blue Sea Banquets">
        </div>
        <div class="input-group">
          <label class="text-label">Their Unfair Advantage</label>
          <select id="c_adv1" class="input-text">
            <option value="Better visual presence">Better visual presence</option>
            <option value="Higher review count">Higher review count</option>
            <option value="More modern decor">More modern decor</option>
            <option value="Lower price">Lower price</option>
          </select>
        </div>
        <div class="input-group">
          <label class="text-label">Competitor Google Reviews</label>
          <input type="number" id="c_reviews" class="input-text" placeholder="e.g. 250">
        </div>
        <div class="input-group">
          <label class="text-label">Our Google Reviews</label>
          <input type="number" id="v_reviews" class="input-text" placeholder="e.g. 45">
        </div>
    """
    content = re.sub(
        r'<div class="input-group">\s*<label class="text-label">Competitor Name</label>.*?</div>\s*</div>',
        comp_inputs,
        content,
        flags=re.DOTALL
    )

# 2. Update Step 5 (The Gap) to add Revenue Reality
if 'id="leak_inquiries"' not in content:
    gap_new = """
    <div class="card" style="border:1px solid #ef4444; background:rgba(239, 68, 68, 0.02);">
      <h2 class="text-h2" style="text-align: center; color:#ef4444; margin-bottom: 32px;">Revenue Leakage Calculator</h2>
      
      <div class="grid-2" style="margin-bottom: 24px;">
        <div class="input-group">
          <label class="text-label">Lost Inquiries / Month</label>
          <input type="number" id="leak_inquiries" class="input-text" placeholder="e.g. 15" oninput="calcLeakage()">
        </div>
        <div class="input-group">
          <label class="text-label">Avg Conversion Rate (%)</label>
          <input type="number" id="leak_conv" class="input-text" placeholder="e.g. 10" value="10" oninput="calcLeakage()">
        </div>
      </div>
      <div class="input-group" style="margin-bottom: 24px;">
        <label class="text-label">Avg Booking Value (₹)</label>
        <input type="number" id="leak_value" class="input-text" placeholder="e.g. 500000" oninput="calcLeakage()">
      </div>

      <div class="grid-2" style="border-top:1px solid #ef4444; padding-top:24px;">
        <div style="text-align: center;">
          <div class="text-label">Lost Bookings</div>
          <div id="leak_res_bookings" style="font-family: var(--font-serif); font-size: 32px; color: #ef4444;">0</div>
        </div>
        <div style="text-align: center;">
          <div class="text-label">Lost Revenue (₹)</div>
          <div id="leak_res_rev" style="font-family: var(--font-serif); font-size: 32px; font-weight:bold; color: #ef4444;">0</div>
        </div>
      </div>
    </div>
    <script>
      function calcLeakage() {
        const inq = parseFloat(document.getElementById('leak_inquiries').value) || 0;
        const conv = parseFloat(document.getElementById('leak_conv').value) || 0;
        const val = parseFloat(document.getElementById('leak_value').value) || 0;
        const bookings = inq * (conv / 100);
        const rev = bookings * val;
        document.getElementById('leak_res_bookings').textContent = bookings.toFixed(1);
        document.getElementById('leak_res_rev').textContent = rev.toLocaleString('en-IN');
      }
    </script>
    """
    content = re.sub(
        r'<div class="card gold">.*?</div>\s*</div>',
        gap_new + '\n  </div>',
        content,
        flags=re.DOTALL
    )

# 3. Add Operational Audits to Step 2
if 'data-id="ops_speed"' not in content:
    ops_audit = """
    <h2 class="text-h3" style="margin-top: 32px; margin-bottom: 24px;">Inquiry Handling (Ops)</h2>
    <div class="grid-2">
      <div class="audit-card" data-id="ops_speed" onclick="toggleAudit(this)">
        <div class="audit-title">Response &lt; 1 Hour</div>
        <div class="text-body">Do they reply to leads immediately?</div>
      </div>
      <div class="audit-card" data-id="ops_crm" onclick="toggleAudit(this)">
        <div class="audit-title">Uses CRM / Tracker</div>
        <div class="text-body">Or are they relying on paper diaries?</div>
      </div>
      <div class="audit-card" data-id="ops_followup" onclick="toggleAudit(this)">
        <div class="audit-title">Automated Follow-ups</div>
        <div class="text-body">Do they nurture cold leads?</div>
      </div>
    </div>
    """
    content = content.replace('</div>\n  </div>\n\n  <!-- STEP 3 -->', '</div>\n' + ops_audit + '\n  </div>\n\n  <!-- STEP 3 -->')

# 4. Add Deal Tracking to Founder Notes
if 'id="deal_prob"' not in content:
    fn_body = """
  <div class="fn-body">
    <textarea class="fn-textarea" id="fn_text" placeholder="Log emotional resistance, budget hesitation, operational issues, or family politics here. This is internal only." style="height: 100px; margin-bottom:16px; border-bottom:1px solid #444;"></textarea>
    
    <div style="display:flex; gap:10px; margin-bottom:10px;">
      <select id="deal_dm" style="flex:1; background:#222; color:#fff; border:none; padding:8px; font-size:12px;">
        <option value="">Decision Maker?</option>
        <option value="Yes">Yes</option>
        <option value="No">No (Gatekeeper)</option>
        <option value="Unknown">Unknown</option>
      </select>
      <select id="deal_budget" style="flex:1; background:#222; color:#fff; border:none; padding:8px; font-size:12px;">
        <option value="">Budget Interest</option>
        <option value="High">High</option>
        <option value="Medium">Medium</option>
        <option value="Low">Low</option>
      </select>
      <select id="deal_timeline" style="flex:1; background:#222; color:#fff; border:none; padding:8px; font-size:12px;">
        <option value="">Timeline</option>
        <option value="Urgent">Urgent</option>
        <option value="Casual">Casual</option>
      </select>
    </div>
    
    <div style="display:flex; align-items:center; gap:15px; margin-top:15px;">
      <span style="font-size:12px; color:#aaa;">Probability to Close:</span>
      <input type="range" id="deal_prob" min="0" max="100" value="50" style="flex:1;" oninput="document.getElementById('prob_val').textContent = this.value + '%'">
      <span id="prob_val" style="font-size:14px; color:var(--color-gold); font-weight:bold;">50%</span>
    </div>
  </div>
    """
    content = re.sub(
        r'<div class="fn-body">.*?</div>',
        fn_body,
        content,
        flags=re.DOTALL
    )

# 5. Export JSON modifications
if 'deal_dm' not in content:
    export_mods = """
    // Grab deal metrics
    const dealDM = document.getElementById('deal_dm') ? document.getElementById('deal_dm').value : '';
    const dealBudget = document.getElementById('deal_budget') ? document.getElementById('deal_budget').value : '';
    const dealTime = document.getElementById('deal_timeline') ? document.getElementById('deal_timeline').value : '';
    const dealProb = document.getElementById('deal_prob') ? document.getElementById('deal_prob').value : '';

    // Grab Leakage metrics
    const leakInq = document.getElementById('leak_inquiries') ? document.getElementById('leak_inquiries').value : '';
    const leakBook = document.getElementById('leak_res_bookings') ? document.getElementById('leak_res_bookings').textContent : '';
    const leakRev = document.getElementById('leak_res_rev') ? document.getElementById('leak_res_rev').textContent : '';

    // Grab Competitor metrics
    const cReviews = document.getElementById('c_reviews') ? document.getElementById('c_reviews').value : '';
    const vReviews = document.getElementById('v_reviews') ? document.getElementById('v_reviews').value : '';
"""
    content = content.replace("const notesText = document.querySelector('.fn-textarea').value.trim();", 
                              "const notesText = document.getElementById('fn_text') ? document.getElementById('fn_text').value.trim() : '';\n" + export_mods)

    # Inject into the output JSON
    content = content.replace(
        "founderNotes: notesText,",
        """founderNotes: notesText,
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
        name: cName1,
        reviews: cReviews
      },"""
    )


with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Sales Tool UI Patched Successfully.")
