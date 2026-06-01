path = r"C:\Users\rohit\Downloads\DigiStories\_Web\venue-growth-bible-engine.html"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Original line count:", len(lines))

part1 = lines[:589]

nav_groups_code = """/* ---------- NAV ---------- */
const NAV_GROUPS = [
  { title:'Onboarding', items:[
    ['assess','▼','Assessment'],
    ['intel','◆','Growth Intelligence'],
    ['audit','🔍','Deep Audit'],
    ['investment','★','Growth Investment'],
  ]},
  { title:'Pillar 1 · Visibility', items:[
    ['ch01','01','Brand Identity'],['ch02','02','Image Brief Prompts'],['ch07','07','Poster Brief Prompts'],
    ['ch09','09','Google Business'],['ch20','20','Carousels & Local Search'],
  ]},
  { title:'Pillar 2 · Conversion', items:[
    ['ch08','08','Messaging Scripts'],['ch13','13','Journey to Booking'],['ch16','16','Where Inquiries Come From'],
    ['ch21','21','Inquiry & Follow-up System'],['ch22','22','Customer Journey to Booking'],
  ]},
  { title:'Pillar 3 · Operations', items:[
    ['ch23','23','Inquiry Leakage & SmartOS Readiness'],['ch24','24','Operational Maturity Patterns'],['ch12','12','Execution Checklist'],
  ]},
  { title:'Pillar 4 · Revenue', items:[
    ['ch14','14','Seasonal Timing'],['ch25','25','Off-Season Revenue Activation'],['ch17','17','Paid Ads'],
  ]},
  { title:'Content & Rhythm', items:[
    ['ch03','03','Social Strategy'],['ch04','04','30-Day Calendar'],['ch05','05','Caption Prompts'],
    ['ch10','10','Reel Concepts & Scripts'],['ch19','19','Reels Mastery'],['ch15','15','Instagram Algorithm Rules'],
    ['ch18','18','Guest Photos & Reels'],['ch06','06','Brochure Brief Prompt'],['ch11','11','Influencer & PR'],
  ]},
  { title:'Assets', items:[['brochure','★','Live Brochure']] }
];
"""

# Since part2 already ends with </script>, we only need to extract up to 2741 (0-indexed 2740)
part2 = lines[596:2741]

new_content = "".join(part1) + nav_groups_code + "".join(part2) + "\n</body>\n</html>\n"

with open(path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Repair completed successfully!")
