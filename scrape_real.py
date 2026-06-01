import re
import json
import urllib.request

try:
    url = "https://weddingz.in/banquet-halls/mumbai/"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read().decode('utf-8')
    
    # Extract JSON state
    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html)
    if match:
        data = json.loads(match.group(1))
        # Explore the data
        # We can also just regex for "name":"Venue Name"
    else:
        # Regex fallback
        pass
        
    names = re.findall(r'"name":"([^"]+)"', html)
    venues = [n for n in set(names) if "Banquet" in n or "Hall" in n or "Lawn" in n or "Club" in n]
    
    with open('real_venues.txt', 'w', encoding='utf-8') as f:
        f.write("\n".join(venues))
    print("Found", len(venues), "venues.")
except Exception as e:
    print("Error:", e)
