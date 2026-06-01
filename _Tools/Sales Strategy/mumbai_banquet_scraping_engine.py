import re
import csv
import json
import time
import os
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

# Dependencies note: pip install beautifulsoup4

class GooglePlacesScanner:
    """Handles querying Google Places API to extract banquet/venue profiles."""
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    def search_venues(self, query="banquet halls in Mumbai", sandbox_mode=False):
        """Searches Google Maps for venues matching the query."""
        if sandbox_mode or not self.api_key:
            print("Places Scanner: Running in SANDBOX mode (using simulated search results)...")
            return self._get_sandbox_results(query)
            
        print(f"Places Scanner: Querying Google Places API for '{query}'...")
        results = []
        params = {
            "query": query,
            "key": self.api_key
        }
        
        try:
            url = f"{self.base_url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
            for place in data.get("results", []):
                results.append({
                    "name": place.get("name"),
                    "address": place.get("formatted_address"),
                    "rating": place.get("rating", 0.0),
                    "reviews_count": place.get("user_ratings_total", 0),
                    "place_id": place.get("place_id"),
                    # We can fetch detailed fields (like website, phone) using Place Details API
                    "website": self._fetch_place_website(place.get("place_id"))
                })
        except Exception as e:
            print(f"Places Scanner Error: {e}. Falling back to sandbox.")
            return self._get_sandbox_results(query)
            
        return results

    def _fetch_place_website(self, place_id):
        """Fetches the website URL for a specific place using Place Details API."""
        if not self.api_key or not place_id:
            return ""
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "website",
            "key": self.api_key
        }
        try:
            url = f"{details_url}?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
            return data.get("result", {}).get("website", "")
        except:
            return ""

    def _get_sandbox_results(self, query):
        """Mock results to demonstrate pipeline execution."""
        # Simulated locations based on query words
        area = "Dadar"
        if "Thane" in query:
            area = "Thane West"
        elif "Vashi" in query or "Navi" in query:
            area = "Vashi"
        elif "Pune" in query:
            area = "Baner"
            
        return [
            {
                "name": f"Karnatak Banquet Hall",
                "address": f"Near Station, {area}, Mumbai, Maharashtra",
                "rating": 4.1,
                "reviews_count": 34,
                "place_id": "mock_id_1",
                "website": "http://karnatakbanquet.co.in" # Will crawl this in sandbox
            },
            {
                "name": f"Siddharth Celebration Lawn",
                "address": f"Link Road, {area}, Mumbai, Maharashtra",
                "rating": 3.7,
                "reviews_count": 8,
                "place_id": "mock_id_2",
                "website": "http://siddharthlawn.com"
            },
            {
                "name": f"Royal Palace Hall",
                "address": f"Opposite Highway, {area}, Mumbai, Maharashtra",
                "rating": 4.5,
                "reviews_count": 180,
                "place_id": "mock_id_3",
                "website": "http://royalpalacebanquets.in"
            }
        ]


class WebpageSocialExtractor:
    """Crawls venue websites to extract phone numbers, emails, and social handles."""
    def __init__(self):
        # Regex patterns
        self.phone_pattern = re.compile(r"(?:\+91|0?\d{2,5})[-.\s]?\d{4}[-.\s]?\d{4,6}")
        self.email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        self.ig_pattern = re.compile(r"instagram\.com/([a-zA-Z0-9._]+)")
        self.fb_pattern = re.compile(r"facebook\.com/([a-zA-Z0-9._-]+)")
        self.wa_pattern = re.compile(r"(?:wa\.me|api\.whatsapp\.com/send.*?phone=)(\d+)")

    def scan_website(self, url, sandbox_mode=False):
        """Scans website homepage to extract contact and social channels."""
        result = {
            "phones": [],
            "emails": [],
            "instagram": "None",
            "facebook": "None",
            "whatsapp_link": "None"
        }
        
        if not url:
            return result
            
        if sandbox_mode:
            # Sandbox mock crawl results
            if "karnatak" in url:
                return {
                    "phones": ["+91 9820123456"],
                    "emails": ["info@karnatakbanquet.co.in"],
                    "instagram": "@karnatakbanquethall_mumbai",
                    "facebook": "fb/karnatakbanquet",
                    "whatsapp_link": "None"
                }
            elif "siddharth" in url:
                return {
                    "phones": ["022-25418976"],
                    "emails": ["siddharthlawns@gmail.com"],
                    "instagram": "None",
                    "facebook": "None",
                    "whatsapp_link": "None"
                }
            else:
                return {
                    "phones": ["+91 9930987654"],
                    "emails": ["bookings@royalpalace.in"],
                    "instagram": "@royalpalacebanquets",
                    "facebook": "fb/royalpalacebanquets",
                    "whatsapp_link": "wa.me/919930987654"
                }

        print(f"Web Scanner: Crawling {url}...")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read()
                
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text()
            
            # Find phones, emails
            result["phones"] = list(set(self.phone_pattern.findall(text)))[:3]
            result["emails"] = list(set(self.email_pattern.findall(text)))[:2]
            
            # Look at href links for socials
            for a in soup.find_all("a", href=True):
                href = a["href"].lower()
                
                ig_match = self.ig_pattern.search(href)
                if ig_match:
                    result["instagram"] = "@" + ig_match.group(1).rstrip("/")
                    
                fb_match = self.fb_pattern.search(href)
                if fb_match:
                    result["facebook"] = fb_match.group(1).rstrip("/")
                    
                wa_match = self.wa_pattern.search(href)
                if wa_match:
                    result["whatsapp_link"] = "wa.me/" + wa_match.group(1)
                    
        except Exception as e:
            print(f"Web Scanner Warning: Could not crawl {url} ({e})")
            
        return result


class BCDAModernizationEngine:
    """Integrates DMI calculation and structures outreach templates."""
    def calculate_dmi(self, venue):
        rating = venue["rating"]
        reviews = venue["reviews_count"]
        ig = venue["instagram"]
        website = venue["website"]
        whatsapp = venue["whatsapp_link"]
        
        # Scoring Logic
        # 1. Instagram Presence (Max 30: Activity 20 + Reels 10)
        ig_activity = 0
        reel_consistency = 0
        if ig != "None":
            if "_mumbai" in ig: # Dormant profile
                ig_activity = 10
                reel_consistency = 3
            else:
                ig_activity = 18
                reel_consistency = 8
                
        # 2. Google Presence (Max 20 reviews & ratings)
        google_reviews = 0
        if reviews > 0:
            if reviews < 10:
                google_reviews = 5
            elif reviews < 50:
                google_reviews = 12
            else:
                google_reviews = 16
            
            if rating >= 4.4:
                google_reviews += 4
            elif rating >= 4.0:
                google_reviews += 2
                
        # 3. Web & CTA conversion (Max 35: CTA 15 + Website 10 + WhatsApp 10)
        inquiry_cta = 12 if website else 0
        website_quality = 8 if website else 0
        whatsapp_integration = 8 if whatsapp != "None" else 0
        
        # 4. Operations & Brand (Max 15)
        brand_consistency = 4 if ig != "None" and website else 1
        response_structure = 8 if whatsapp != "None" else 2
        
        score = (
            ig_activity + reel_consistency + google_reviews +
            inquiry_cta + website_quality + whatsapp_integration +
            brand_consistency + response_structure
        )
        
        # Classification
        if score < 35:
            status = "Invisible"
            tier = "Tier C (Traditional - Needs Education)"
        elif score < 65:
            status = "Present but Weak"
            tier = "Tier B (Growth Business)"
        else:
            status = "Active"
            tier = "Tier A (Fastest Converter)"
            
        # Outreach Snapshot
        snapshot = (
            f"BCA Digital Initiative — {venue['name']} Audit Snapshot:\n"
            f"- Instagram Freshness: {'Weak' if ig_activity < 12 else 'Active'}\n"
            f"- Google Maps Visibility: {'Moderate' if google_reviews < 15 else 'High'}\n"
            f"- Inquiry Management: {'Manual / Offline' if inquiry_cta < 10 else 'Digital'}\n"
            f"- WhatsApp Structure: {'Unorganized' if whatsapp_integration < 8 else 'Structured'}\n"
            f"- Booking Workflow: {'Offline Register' if response_structure < 8 else 'Systemized'}\n"
            f"Digital Maturity Score: {score}/100 ({status})"
        )
        
        pitch = (
            f"Namaste Bhai, Rohit Nate here from Dadar (fellow BCA member). "
            f"We are running the BCA Digital Readiness Initiative. Here is the quick audit snapshot for your venue:\n\n"
            f"{snapshot}\n\n"
            f"I have your 2-page detailed report. Let me know if we can discuss on WhatsApp."
        )
        
        return {
            "dmi_score": score,
            "dmi_status": status,
            "target_tier": tier,
            "snapshot": snapshot,
            "whatsapp_pitch": pitch
        }


def run_pipeline(api_key=None, query="banquet halls in Dadar", sandbox=True):
    print("==================================================")
    print("     BOMBAY CATERERS DIGITAL ANALYSIS ENGINE     ")
    print("==================================================")
    
    # 1. Initialize Modules
    scanner = GooglePlacesScanner(api_key)
    extractor = WebpageSocialExtractor()
    modernizer = BCDAModernizationEngine()
    
    # 2. Extract Maps Listings
    raw_venues = scanner.search_venues(query, sandbox_mode=sandbox)
    print(f"Extracted {len(raw_venues)} venues from Google Maps search.\n")
    
    final_leads = []
    
    # 3. Process each venue
    for idx, venue in enumerate(raw_venues):
        print(f"[{idx+1}/{len(raw_venues)}] Processing: {venue['name']}...")
        
        # Scan Website
        site_url = venue["website"]
        contacts = extractor.scan_website(site_url, sandbox_mode=sandbox)
        
        # Merge Places & Crawl data
        lead = {
            "name": venue["name"],
            "address": venue["address"],
            "rating": venue["rating"],
            "reviews_count": venue["reviews_count"],
            "website": site_url if site_url else "None",
            "phones": ", ".join(contacts["phones"]) if contacts["phones"] else "Pending",
            "emails": ", ".join(contacts["emails"]) if contacts["emails"] else "Pending",
            "instagram": contacts["instagram"],
            "facebook": contacts["facebook"],
            "whatsapp_link": contacts["whatsapp_link"]
        }
        
        # Calculate Digital Maturity Index (DMI) and generate pitch
        metrics = modernizer.calculate_dmi(lead)
        lead.update(metrics)
        
        final_leads.append(lead)
        print(f"  --> Maturity Score: {lead['dmi_score']}/100 ({lead['dmi_status']})")
        print(f"  --> Tier: {lead['target_tier']}\n")
        time.sleep(0.5) # Politeness delay
        
    # 4. Save to CSV and JSON
    csv_file = r"c:\Users\rohit\Downloads\DigiStories\bcda_extracted_leads.csv"
    json_file = r"c:\Users\rohit\Downloads\DigiStories\bcda_extracted_leads.json"
    
    # Write JSON
    with open(json_file, "w", encoding="utf-8") as jf:
        json.dump(final_leads, jf, indent=2)
        
    # Write CSV
    if final_leads:
        keys = final_leads[0].keys()
        with open(csv_file, "w", newline="", encoding="utf-8") as cf:
            dict_writer = csv.DictWriter(cf, keys)
            dict_writer.writeheader()
            dict_writer.writerows(final_leads)
            
    print("==================================================")
    print("PIPELINE EXECUTION COMPLETE")
    print(f"Saved JSON database to: {json_file}")
    print(f"Saved CSV spreadsheet to: {csv_file}")
    print("==================================================")

if __name__ == "__main__":
    # Test-drive the pipeline in Sandbox mode
    run_pipeline(api_key=None, query="banquet halls in Dadar", sandbox=True)
