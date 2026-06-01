path = r"C:\Users\rohit\Downloads\DigiStories\_Web\venue-growth-bible-engine.html"

with open(path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if "NAV_GROUPS" in line:
            print(f"Line {i}: {line.strip()}")
