path = r"C:\Users\rohit\Downloads\DigiStories\_Web\venue-growth-bible-engine.html"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines, 1):
    if "Growth Investment" in line:
        print(f"Line {i}: {line.strip()}")
        # print context
        start = max(0, i-5)
        end = min(len(lines), i+5)
        print("CONTEXT:")
        for idx in range(start, end):
            print(f"  {idx}: {lines[idx-1].strip()}")
        print("-" * 40)
