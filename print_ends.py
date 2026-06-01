path = r"C:\Users\rohit\Downloads\DigiStories\_Web\venue-growth-bible-engine.html"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print("Last 20 lines:")
for idx in range(len(lines) - 20, len(lines)):
    print(f"  {idx+1}: {lines[idx].strip()}")
