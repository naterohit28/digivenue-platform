import re

path = r"C:\Users\rohit\Downloads\DigiStories\_Web\digistories-sales-tool-v2.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the notes extraction and inject the grabbers
target_grabbers = """    const notesText = document.getElementById('fn_text') ? document.getElementById('fn_text').value.trim() : document.querySelector('.fn-textarea').value.trim();

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

content = content.replace("    const notesText = document.querySelector('.fn-textarea').value.trim();", target_grabbers)

# Replace the intake object creation
target_obj = """      founderNotes: notesText,
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
      
content = content.replace("      founderNotes: notesText,", target_obj)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Export logic patched.")
