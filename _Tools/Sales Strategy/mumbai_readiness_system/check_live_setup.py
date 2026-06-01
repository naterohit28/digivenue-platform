"""
check_live_setup.py
───────────────────
A friendly checker. Run this AFTER you paste your Google Maps API key.

It will:
  1. Look for your key
  2. Make ONE small test call to Google
  3. Tell you, in plain English, whether real data is ready

Run it like this (from inside the mumbai_readiness_system folder):

    python check_live_setup.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import requests

# Make sure we can print cleanly on Windows terminals
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from database.db import load_google_api_key  # noqa: E402

FIND_PLACE_URL = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'

LINE = '-' * 58


def main() -> None:
    print()
    print(LINE)
    print("  DigiVenue — Google Maps Live Data Checker")
    print(LINE)

    # ── Step 1: find the key ─────────────────────────────────────
    key = load_google_api_key(ROOT)
    if not key:
        print("""
  [X]  No API key found yet.

  HOW TO FIX (one time):
   1. Go to the 'configs' folder.
   2. Find the file:  secrets.example.json
   3. Make a copy of it, rename the copy to:  secrets.local.json
   4. Open it and paste your key between the quotes.
   5. Save, then run this checker again.

  (You get the key free from https://console.cloud.google.com
   — ask Claude to walk you through it.)
""")
        print(LINE)
        return

    masked = key[:6] + '...' + key[-4:] if len(key) > 12 else '(short key)'
    print(f"\n  [OK] Found a key:  {masked}")

    # ── Step 2: make ONE test call ───────────────────────────────
    print("  [..] Testing it against Google (one small request)...")
    test_query = "iLeaf Grand Banquets Vashi Maharashtra"
    try:
        resp = requests.get(
            FIND_PLACE_URL,
            params={'input': test_query, 'inputtype': 'textquery', 'fields': 'place_id', 'key': key},
            timeout=15,
        )
        data = resp.json()
    except Exception as e:
        print(f"\n  [X]  Could not reach Google. Check your internet.\n       Technical detail: {e}\n")
        print(LINE)
        return

    status = data.get('status', 'UNKNOWN')

    # ── Step 3: explain the result in plain English ──────────────
    if status == 'OK':
        found = len(data.get('candidates', []))
        print(f"\n  [SUCCESS]  Your key works! Google answered and found {found} match.")
        print("""
  You are READY for real data.

  NEXT STEP — pull real data for all your halls:
      python run_pipeline.py

  Each hall will then be tagged either:
      'google_live'   = real numbers from Google
      'ai_estimate'   = Google could not find it (still a guess)
""")
    elif status == 'REQUEST_DENIED':
        print("""
  [X]  Google rejected the key (status: REQUEST_DENIED).

  Most common reasons:
   - The 'Places API' is not switched ON for this key yet.
   - Billing is not enabled on the Google project.
   - The key has restrictions blocking this computer.

  Fix: in Google Cloud Console, enable 'Places API' and make sure
  billing is turned on (you still get $200 free monthly credit).
""")
    elif status == 'OVER_QUERY_LIMIT':
        print("""
  [!]  Key works but you have hit a usage limit for now.
       Wait a bit, or check your billing/quota in Google Cloud Console.
""")
    elif status == 'ZERO_RESULTS':
        print("""
  [OK] Your key works (Google answered), but the test hall was not
       found. That is fine — run the full pipeline and most halls
       will still be matched:
           python run_pipeline.py
""")
    else:
        msg = data.get('error_message', 'no extra detail provided')
        print(f"""
  [?]  Unexpected response from Google.
       Status: {status}
       Detail: {msg}
""")

    print(LINE)


if __name__ == '__main__':
    main()
