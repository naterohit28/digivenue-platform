path = r"C:\Users\rohit\Downloads\DigiStories\_Web\venue-growth-bible-engine.html"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

interest_tags = ["<!DOCTYPE", "<html", "</html", "<head", "</head", "<body", "</body", "<script", "</script", "<style", "</style"]

for i, line in enumerate(lines, 1):
    for tag in interest_tags:
        if tag in line:
            clean_line = line.strip().encode('ascii', errors='ignore').decode('ascii')
            print(f"Line {i:4d}: {clean_line[:100]}")
