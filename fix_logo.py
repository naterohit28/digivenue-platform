import re

path_bible = r"C:\Users\rohit\Downloads\DigiStories\_Web\venue-growth-bible-engine.html"
with open(path_bible, "r", encoding="utf-8") as f:
    bible_content = f.read()

# Remove the inversion filter that made it invisible on light backgrounds
bible_content = bible_content.replace(
    'filter: brightness(0) invert(1);',
    ''
)

with open(path_bible, "w", encoding="utf-8") as f:
    f.write(bible_content)

print("Logo visibility fixed.")
