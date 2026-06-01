import os
import shutil
from pathlib import Path

base_dir = Path(r"c:\Users\rohit\Downloads\DigiStories")

folders = {
    "_Playbooks": base_dir / "_Playbooks",
    "_Web": base_dir / "_Web",
    "_Tools": base_dir / "_Tools",
    "_Leads": base_dir / "_Leads"
}

for f in folders.values():
    f.mkdir(exist_ok=True)

for item in base_dir.iterdir():
    if item.is_file():
        ext = item.suffix.lower()
        if ext == ".md":
            shutil.move(str(item), str(folders["_Playbooks"] / item.name))
        elif ext == ".html":
            shutil.move(str(item), str(folders["_Web"] / item.name))
        elif ext in [".json", ".csv"] and "bcda" in item.name.lower():
            shutil.move(str(item), str(folders["_Leads"] / item.name))
        elif ext == ".py" and item.name not in ["organize_digistories.py", "ddg_scrape.py", "scrape_real.py"]:
            shutil.move(str(item), str(folders["_Tools"] / item.name))

print("Organization complete!")
