from duckduckgo_search import DDGS

try:
    with DDGS() as ddgs:
        results = ddgs.maps("banquet hall mumbai", place="Mumbai")
        
        venues = []
        for r in results:
            name = r.get("title", "")
            address = r.get("address", "")
            phone = r.get("phone", "")
            rating = r.get("rating", "")
            venues.append(f"{name} | {address} | {phone} | {rating}")
            
        with open('real_venues_ddg.txt', 'w', encoding='utf-8') as f:
            f.write("\n".join(venues))
            
        print(f"Found {len(venues)} real venues using Maps API.")
except Exception as e:
    print("Error:", e)
