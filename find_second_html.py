path = r"C:\Users\rohit\Downloads\DigiStories\_Web\venue-growth-bible-engine.html"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if i > 100 and ("<!DOCTYPE html>" in line or "<html" in line or "<body" in line):
        print(f"Line {i}: {line.strip()}")
