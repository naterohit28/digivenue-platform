import re

path_sales = r"C:\Users\rohit\Downloads\DigiStories\_Web\digistories-sales-tool-v2.html"
with open(path_sales, "r", encoding="utf-8") as f:
    sales_content = f.read()

sales_content = sales_content.replace('src="GoogleDigiVenue/assets/images/logo-horizontal.svg"', 'src="logo.svg"')

with open(path_sales, "w", encoding="utf-8") as f:
    f.write(sales_content)


path_bible = r"C:\Users\rohit\Downloads\DigiStories\_Web\venue-growth-bible-engine.html"
with open(path_bible, "r", encoding="utf-8") as f:
    bible_content = f.read()

# Add logo image to the brand mark
if "digivenue-logo" not in bible_content:
    logo_html = """
    <div class="brand">
      <img src="logo.svg" alt="DigiVenue Logo" class="digivenue-logo" style="height: 24px; width: auto; margin-right: 15px; filter: brightness(0) invert(1);">
      <div class="brand-mark" id="brandMark">V</div>"""
    
    bible_content = bible_content.replace(
        '<div class="brand">\n      <div class="brand-mark" id="brandMark">V</div>',
        logo_html
    )

with open(path_bible, "w", encoding="utf-8") as f:
    f.write(bible_content)

print("Logos added.")
