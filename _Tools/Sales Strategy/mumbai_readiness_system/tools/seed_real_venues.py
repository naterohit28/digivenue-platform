"""
Generates raw/real_venues_seed.json from the 106 real venues in the
DigiVenue prospect database.

Each venue gets realistic mock Google signals based on its pitch strategy:
  DigiStories  → bad Instagram / Google visibility, few reviews, stale photos
  SmartOS      → decent reviews but no inquiry/ops systems
  Both         → weak on all fronts
"""
from __future__ import annotations

import json
import math
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ── Raw venue data (106 venues) ──────────────────────────────────────────────
VENUES = [
    # (id, name, area, suburb, type, cap_min, cap_max, pitch)
    (1,  "Swagat Banquet Hall",               "Dadar",          "Dadar",          "Standalone Banquet",    200, 800,  "Both"),
    (2,  "Swatantryaveer Savarkar Sabhagriha","Shivaji Park",   "Dadar",          "Standalone Hall",       300, 1000, "SmartOS"),
    (3,  "Kohinoor Hall",                     "Dadar",          "Dadar",          "Traditional Banquet",   200, 700,  "DigiStories"),
    (4,  "Mayfair Banquets",                  "Worli",          "South Mumbai",   "Standalone Banquet",    150, 800,  "DigiStories"),
    (5,  "Jewel of India (Jade Ballroom)",    "Worli",          "South Mumbai",   "Standalone Banquet",    200, 1000, "Both"),
    (6,  "Ramee Guestline Banquets",          "Dadar",          "Dadar",          "Mid-size Hotel Hall",   100, 400,  "SmartOS"),
    (7,  "Ahilyadevi Sabhagruh",              "Dadar",          "Dadar",          "Traditional Hall",      150, 500,  "SmartOS"),
    (8,  "Lala Lajpatrai Hall",               "Mahalaxmi",      "South Mumbai",   "Standalone Hall",       200, 800,  "DigiStories"),
    (9,  "Royal Symphony Banquet",            "Dadar",          "Dadar",          "Standalone Banquet",    100, 500,  "DigiStories"),
    (10, "Dadar Gymkhana Banquets",           "Shivaji Park",   "Dadar",          "Club Hall",             200, 1000, "SmartOS"),
    (11, "Sharda Sabhagriha",                 "Dadar",          "Dadar",          "Traditional Hall",      100, 400,  "SmartOS"),
    (12, "P. L. Deshpande Mini Hall",         "Prabhadevi",     "South Mumbai",   "Govt Hall",             150, 500,  "SmartOS"),
    (13, "Maharashtra College Hall",          "Byculla",        "South Mumbai",   "Community Hall",        300, 1200, "SmartOS"),
    (14, "Bombay Y.M.C.A. Banquets",          "Colaba",         "South Mumbai",   "Club Hall",             100, 400,  "SmartOS"),
    (15, "Royal Garden Banquet",              "Dadar",          "Dadar",          "Standalone Banquet",    100, 600,  "DigiStories"),
    (16, "Hindu Gymkhana Grounds",            "Marine Drive",   "South Mumbai",   "Club Lawn",             500, 2500, "DigiStories"),
    (17, "Parsi Gymkhana Grounds",            "Marine Drive",   "South Mumbai",   "Club Lawn",             400, 2000, "DigiStories"),
    (18, "Wodehouse Gymkhana Banquets",       "Colaba",         "South Mumbai",   "Club Hall",             100, 500,  "SmartOS"),
    (19, "Vivette Luxury Banquets",           "Malad West",     "Malad",          "Standalone Banquet",    200, 1000, "DigiStories"),
    (20, "Evershine Banquets",                "Malad West",     "Malad",          "Standalone Banquet",    300, 1500, "Both"),
    (21, "Merchant Banquet Hall",             "Malad West",     "Malad",          "Standalone Banquet",    150, 600,  "SmartOS"),
    (22, "Golden Leaf Banquet",               "Malad West",     "Malad",          "Standalone Banquet",    200, 1000, "DigiStories"),
    (23, "Royal Orchid Banquets",             "Chembur",        "Chembur",        "Standalone Banquet",    100, 600,  "Both"),
    (24, "The Acres Club",                    "Chembur",        "Chembur",        "Club Banquet",          150, 800,  "SmartOS"),
    (25, "GCC Hotel and Club",                "Mira Road",      "Mira Road",      "Resort Lawn",           300, 2500, "Both"),
    (26, "Juhu Club Millennium",              "Juhu",           "Andheri",        "Club Lawn",             200, 1500, "SmartOS"),
    (27, "Goldfinch Banquets",                "Andheri East",   "Andheri",        "Hotel Hall",            100, 600,  "SmartOS"),
    (28, "Tunga Paradise Banquet",            "Andheri East",   "Andheri",        "Hotel Hall",            100, 400,  "SmartOS"),
    (29, "VITS Hotel Banquets",               "Andheri East",   "Andheri",        "Hotel Hall",            150, 800,  "SmartOS"),
    (30, "Peninsula Grand Banquets",          "Sakinaka",       "Andheri",        "Standalone Banquet",    200, 1000, "DigiStories"),
    (31, "Kohinoor Continental Banquets",     "Andheri East",   "Andheri",        "Hotel Hall",            100, 500,  "SmartOS"),
    (32, "Swagat Banquet Hall Goregaon",      "Goregaon",       "Goregaon",       "Standalone Hall",       100, 500,  "DigiStories"),
    (33, "Imperial Hall",                     "Ghatkopar",      "Chembur",        "Standalone Hall",       150, 600,  "Both"),
    (34, "Royal Symphony Banquet Malad",      "Malad East",     "Malad",          "Standalone Banquet",    100, 500,  "SmartOS"),
    (35, "Elegance Banquet",                  "Borivali",       "Borivali",       "Standalone Banquet",    150, 800,  "DigiStories"),
    (36, "Sumati Hall",                       "Ghatkopar East", "Chembur",        "Standalone Hall",       100, 450,  "SmartOS"),
    (37, "Utsav Banquet Hall",                "Bhandup",        "Mulund",         "Standalone Banquet",    100, 500,  "DigiStories"),
    (38, "Dreamland Banquet Hall",            "Bhandup",        "Mulund",         "Standalone Hall",       150, 600,  "SmartOS"),
    (39, "The Gateway Banquet",               "Mulund West",    "Mulund",         "Standalone Banquet",    200, 1000, "DigiStories"),
    (40, "Shehnai Banquet Hall",              "Mulund East",    "Mulund",         "Standalone Hall",       100, 600,  "SmartOS"),
    (41, "Blossom Banquet Hall",              "Kurla",          "Kurla",          "Standalone Hall",       100, 500,  "SmartOS"),
    (42, "Club Emerald Banquets",             "Chembur",        "Chembur",        "Club Hall",             150, 600,  "SmartOS"),
    (43, "GCC Club Lawn",                     "Mira Road",      "Mira Road",      "Wedding Lawn",          400, 2000, "DigiStories"),
    (44, "Sapphire Banquet",                  "Kanjurmarg",     "Mulund",         "Standalone Banquet",    100, 600,  "DigiStories"),
    (45, "Grand Banquet at The Club",         "Andheri West",   "Andheri",        "Club Hall",             200, 800,  "SmartOS"),
    (46, "Eskay Resorts Lawn",                "Borivali West",  "Borivali",       "Resort Lawn",           500, 3000, "DigiStories"),
    (47, "Hotel Tip Top Plaza",               "Thane West",     "Thane West",     "Standalone Multiplex",  100, 2500, "Both"),
    (48, "iLeaf Ritz Banquets",               "Thane West",     "Thane West",     "Standalone Banquet",    200, 1500, "DigiStories"),
    (49, "Satkar Grand Banquets",             "Thane West",     "Thane West",     "Standalone Banquet",    150, 1000, "Both"),
    (50, "Madhav Banquet",                    "Thane West",     "Thane West",     "Standalone Banquet",    200, 1200, "DigiStories"),
    (51, "All Heavens Banquet",               "Thane West",     "Thane West",     "Standalone Banquet",    100, 500,  "DigiStories"),
    (52, "Maharaja Banquet",                  "Ghodbunder Rd",  "Thane West",     "Standalone Banquet",    150, 800,  "DigiStories"),
    (53, "Exotica Yeoor Hills",               "Yeoor Hills",    "Thane West",     "Nature Resort",         150, 800,  "DigiStories"),
    (54, "Bramha Banquet",                    "Thane West",     "Thane West",     "Standalone Banquet",    100, 600,  "DigiStories"),
    (55, "Symphony Banquet",                  "Thane West",     "Thane West",     "Standalone Banquet",    100, 500,  "SmartOS"),
    (56, "Korum Mall Banquets",               "Eastern Exp Hwy","Thane West",     "Standalone Banquet",    150, 800,  "SmartOS"),
    (57, "Regency Hall",                      "Kalyan",         "Kalyan",         "Standalone Banquet",    200, 1000, "Both"),
    (58, "Springtime Club",                   "Kalyan",         "Kalyan",         "Club Hall & Lawn",      200, 1500, "SmartOS"),
    (59, "Guru Nanak Darbar Banquet",         "Thane East",     "Thane East",     "Standalone Hall",       100, 600,  "SmartOS"),
    (60, "Shangrila Resort",                  "Bhiwandi Road",  "Thane West",     "Resort Lawn",           300, 2000, "DigiStories"),
    (61, "Shaurya Banquet",                   "Thane West",     "Thane West",     "Standalone Banquet",    150, 800,  "DigiStories"),
    (62, "Royal Banquet Hall Kalyan",         "Kalyan",         "Kalyan",         "Standalone Hall",       100, 500,  "SmartOS"),
    (63, "K. P. Banquet",                     "Thane West",     "Thane West",     "Standalone Banquet",    100, 600,  "SmartOS"),
    (64, "Nisarg Lawn & Banquet",             "Kalyan",         "Kalyan",         "Lawn & Banquet",        300, 1500, "DigiStories"),
    (65, "Savitri Banquet Hall",              "Dombivli",       "Dombivli",       "Standalone Hall",       100, 600,  "SmartOS"),
    (66, "Golden Palace Banquet",             "Dombivli",       "Dombivli",       "Standalone Hall",       150, 800,  "SmartOS"),
    (67, "iLeaf Grand Banquets",              "Vashi",          "Vashi",          "Standalone Banquet",    200, 1200, "DigiStories"),
    (68, "Grand Golden Banquet",              "Vashi",          "Vashi",          "Standalone Banquet",    150, 1000, "DigiStories"),
    (69, "Imperial Banquets",                 "Vashi",          "Vashi",          "Standalone Banquet",    100, 800,  "SmartOS"),
    (70, "Palm Beach Lawn & Banquets",        "Sanpada",        "Vashi",          "Lawn & Hall",           300, 2000, "DigiStories"),
    (71, "Vidhi Banquets",                    "Kopar Khairane", "Vashi",          "Standalone Banquet",    100, 600,  "SmartOS"),
    (72, "Gems Party Hall",                   "Vashi",          "Vashi",          "Standalone Banquet",    100, 500,  "DigiStories"),
    (73, "Golden Peacock Banquet",            "Kharghar",       "Kharghar",       "Standalone Banquet",    100, 800,  "SmartOS"),
    (74, "Panvel Grand Banquet",              "Panvel",         "Panvel",         "Standalone Banquet",    150, 1000, "Both"),
    (75, "Ashoka Banquet Hall",               "Vashi",          "Vashi",          "Standalone Hall",       100, 600,  "DigiStories"),
    (76, "Moraj Banquet Hall",                "Sanpada",        "Vashi",          "Standalone Hall",       100, 500,  "SmartOS"),
    (77, "Belapur Garden Banquet",            "Belapur",        "Belapur",        "Lawn & Banquet",        200, 1200, "DigiStories"),
    (78, "Shubham Karoti Banquet",            "Kopar Khairane", "Vashi",          "Standalone Hall",       100, 600,  "SmartOS"),
    (79, "Kesar Banquet",                     "Kharghar",       "Kharghar",       "Standalone Banquet",    100, 500,  "DigiStories"),
    (80, "Vishwa Jyot Banquet",               "Kharghar",       "Kharghar",       "Standalone Hall",       100, 600,  "SmartOS"),
    (81, "Royal Celebration Hall",            "Kamothe",        "Kharghar",       "Standalone Hall",       100, 500,  "SmartOS"),
    (82, "Celebration Banquet Hall",          "Nerul",          "Nerul",          "Standalone Banquet",    100, 600,  "SmartOS"),
    (83, "Raigad Fort Banquet",               "New Panvel",     "Panvel",         "Standalone Hall",       150, 800,  "SmartOS"),
    (84, "Shikara Hotel Banquets",            "Sanpada",        "Vashi",          "Traditional Resort",    100, 800,  "DigiStories"),
    (85, "Belapur Gymkhana Banquets",         "Belapur",        "Belapur",        "Club Hall",             150, 800,  "SmartOS"),
    (86, "Navi Mumbai Club Banquets",         "Nerul",          "Nerul",          "Club Hall & Lawn",      200, 1200, "SmartOS"),
    (87, "Siddhi Gardens & Banquets",         "Erandwane",      "Pune Central",   "Lawn & Hall",           200, 1500, "SmartOS"),
    (88, "Raaga Heritage Banquets",           "Hinjewadi",      "Hinjewadi",      "Lawn & Hall",           300, 2000, "Both"),
    (89, "Navyug Banquet Hall",               "Boat Club Rd",   "Pune Central",   "Standalone Banquet",    100, 600,  "DigiStories"),
    (90, "Emerald Party Hall",                "Baner",          "Pune West",      "Standalone Banquet",    100, 500,  "SmartOS"),
    (91, "Pyramids Garden",                   "Kothrud",        "Pune West",      "Standalone Lawn",       300, 1500, "DigiStories"),
    (92, "Shubharambh Lawns",                 "Karve Nagar",    "Pune West",      "Lawn & Banquet",        300, 2000, "DigiStories"),
    (93, "Oasis Banquets & Lawns",            "Hadapsar",       "Pune East",      "Lawn & Hall",           200, 1200, "SmartOS"),
    (94, "Yash Lawns",                        "Bibwewadi",      "Pune Central",   "Sprawling Lawn",        500, 3000, "DigiStories"),
    (95, "Raga Lawns",                        "Koregaon Park",  "Pune Central",   "Standalone Lawn",       300, 1500, "DigiStories"),
    (96, "Saket Banquets",                    "Erandwane",      "Pune Central",   "Standalone Banquet",    100, 600,  "SmartOS"),
    (97, "Abhishek Veg Banquet",              "Kothrud",        "Pune West",      "Standalone Hall",       100, 500,  "SmartOS"),
    (98, "Gandharva Lawns",                   "Pimple Saudagar","Pimple Saudagar","Lawn & Hall",           200, 1200, "DigiStories"),
    (99, "Royal Lawns",                       "Baner",          "Pune West",      "Standalone Lawn",       300, 1500, "DigiStories"),
    (100,"Laxmi Lawns",                       "Magarpatta",     "Pune East",      "Sprawling Lawn",        500, 4000, "DigiStories"),
    (101,"Shrushti Lawns",                    "DP Road",        "Pune Central",   "Lawn & Hall",           250, 1200, "SmartOS"),
    (102,"Balaji Banquets",                   "Wakad",          "Wakad",          "Standalone Banquet",    100, 600,  "SmartOS"),
    (103,"Vardhaman Lawns",                   "Gangadham",      "Wakad",          "Traditional Lawn",      300, 2000, "SmartOS"),
    (104,"Sai Palace Banquets",               "Wakad",          "Wakad",          "Standalone Banquet",    150, 800,  "DigiStories"),
    (105,"Nisarg Mangal Karyalaya",           "Erandwane",      "Pune Central",   "Mangal Karyalaya",      200, 1000, "Both"),
    (106,"Alpa Bachat Bhavan",                "Camp",           "Pune Camp",      "Standalone Venue",      300, 2000, "SmartOS"),
]


# ── Approximate coordinates per suburb ───────────────────────────────────────
SUBURB_COORDS = {
    "Dadar":           "19.0176,72.8431",
    "South Mumbai":    "18.9220,72.8347",
    "Malad":           "19.1874,72.8484",
    "Chembur":         "19.0525,72.9005",
    "Mira Road":       "19.2812,72.8724",
    "Andheri":         "19.1136,72.8697",
    "Goregaon":        "19.1663,72.8496",
    "Mulund":          "19.1726,72.9565",
    "Kurla":           "19.0728,72.8826",
    "Borivali":        "19.2307,72.8567",
    "Thane West":      "19.2183,72.9781",
    "Thane East":      "19.2144,73.0100",
    "Kalyan":          "19.2403,73.1305",
    "Dombivli":        "19.2137,73.0910",
    "Vashi":           "19.0771,72.9988",
    "Kharghar":        "19.0474,73.0659",
    "Belapur":         "19.0219,73.0387",
    "Panvel":          "18.9894,73.1175",
    "Nerul":           "19.0327,73.0169",
    "Pune Central":    "18.5204,73.8567",
    "Pune West":       "18.5074,73.8077",
    "Pune East":       "18.5074,73.9109",
    "Hinjewadi":       "18.5912,73.7380",
    "Pimple Saudagar": "18.5912,73.7810",
    "Wakad":           "18.5945,73.7625",
    "Pune Camp":       "18.5155,73.8757",
}


def _google_signals(pitch: str, idx: int) -> dict:
    """Generate realistic Google-level signals based on pitch strategy."""
    # Deterministic variation using venue index
    var = (idx * 7 + 3) % 10  # 0-9

    if pitch == "DigiStories":
        return {
            "rating": round(3.7 + var * 0.06, 1),
            "review_count": 12 + var * 3,
            "photo_count": 6 + var * 2,
            "owner_response_presence": 0,
            "latest_review_date": (date.today() - timedelta(days=50 + var * 4)).isoformat(),
        }
    elif pitch == "SmartOS":
        return {
            "rating": round(4.0 + var * 0.05, 1),
            "review_count": 38 + var * 5,
            "photo_count": 22 + var * 3,
            "owner_response_presence": 1 if var > 4 else 0,
            "latest_review_date": (date.today() - timedelta(days=15 + var * 3)).isoformat(),
        }
    else:  # Both
        return {
            "rating": round(3.5 + var * 0.05, 1),
            "review_count": 8 + var * 2,
            "photo_count": 4 + var,
            "owner_response_presence": 0,
            "latest_review_date": (date.today() - timedelta(days=65 + var * 3)).isoformat(),
        }


def build_seed() -> list[dict]:
    rows = []
    for (idx, name, area, suburb, vtype, cap_min, cap_max, pitch) in VENUES:
        coords = SUBURB_COORDS.get(suburb, "19.0760,72.8777")
        g = _google_signals(pitch, idx)
        rows.append({
            "external_id":            f"real-{idx:03d}",
            "business_name":          name,
            "category":               "banquet_hall",
            "area":                   area,
            "suburb":                 suburb,
            "address":                f"{area}, {suburb}, Maharashtra",
            "phone_numbers":          None,
            "website":                None,
            "google_maps_url":        f"https://maps.google.com/?q={name.replace(' ', '+')}+{area}",
            "rating":                 g["rating"],
            "review_count":           g["review_count"],
            "latest_review_date":     g["latest_review_date"],
            "owner_response_presence":g["owner_response_presence"],
            "photo_count":            g["photo_count"],
            "coordinates":            coords,
            "operating_hours":        "10:00-22:00",
            "google_confidence_score":0.75,
            "venue_type":             vtype,
            "capacity_min":           cap_min,
            "capacity_max":           cap_max,
            "pitch_strategy":         pitch,
        })
    return rows


if __name__ == "__main__":
    seed = build_seed()
    out_path = ROOT / "raw" / "real_venues_seed.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(seed, indent=2), encoding="utf-8")
    print(f"Written {len(seed)} venues to {out_path}")
