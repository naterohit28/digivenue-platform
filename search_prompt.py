import os

search_term = "UNIFIED MASTER UPGRADE PROMPT"
search_dir = r"c:\Users\rohit\Downloads\DigiStories"

found_files = []

for root, dirs, files in os.walk(search_dir):
    # skip node_modules, .git, etc.
    if any(p in root for p in [".git", ".claude", "__pycache__"]):
        continue
    for file in files:
        path = os.path.join(root, file)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                if search_term in f.read():
                    found_files.append(path)
        except Exception:
            pass

print("Found files:", found_files)
