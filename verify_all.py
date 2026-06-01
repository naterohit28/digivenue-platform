import os
import json
import csv
import re

def verify_all():
    errors = []
    successes = []

    # 1. Check HTML files existence
    sales_tool_path = "_Web/digistories-sales-tool-v2.html"
    growth_bible_path = "_Web/venue-growth-bible-engine.html"
    intel_data_path = "_Web/intelligence_data.js"
    logo_path = "_Web/logo.svg"

    print("Checking file existence...")
    for p in [sales_tool_path, growth_bible_path, intel_data_path, logo_path]:
        if os.path.exists(p):
            successes.append(f"File exists: {p} ({os.path.getsize(p)} bytes)")
        else:
            errors.append(f"File missing: {p}")

    # 2. Check Sales Tool step structure
    if os.path.exists(sales_tool_path):
        print("Verifying Sales Tool structure...")
        with open(sales_tool_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verify it has all 10 step elements
        for i in range(10):
            step_id = f'id="st-{i}"'
            if step_id in content or f"id='st-{i}'" in content:
                successes.append(f"Sales Tool: Found step st-{i}")
            else:
                errors.append(f"Sales Tool: Missing step st-{i}")

        # Verify logo references
        if 'src="logo.svg"' in content:
            successes.append("Sales Tool: logo.svg is correctly referenced")
        else:
            errors.append("Sales Tool: logo.svg is not referenced correctly")

        # Verify no invert filter is on the logo
        if "invert" in content and "logo" in content:
            # check if invert style exists on the logo specifically
            logo_img_match = re.search(r'<img[^>]*logo\.svg[^>]*style="[^"]*invert[^"]*"', content)
            if logo_img_match:
                errors.append("Sales Tool: logo tag still contains an invert filter style")
            else:
                successes.append("Sales Tool: logo tag has no invert filter")
        else:
            successes.append("Sales Tool: logo tag has no invert filter")

    # 3. Check Growth Bible structure & chapters
    if os.path.exists(growth_bible_path):
        print("Verifying Growth Bible structure...")
        with open(growth_bible_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check NAV_GROUPS presence
        if "const NAV_GROUPS =" in content:
            successes.append("Growth Bible: Found NAV_GROUPS definition")
        else:
            errors.append("Growth Bible: Missing NAV_GROUPS definition")

        # Check logo reference
        if 'src="logo.svg"' in content:
            successes.append("Growth Bible: logo.svg is correctly referenced")
        else:
            errors.append("Growth Bible: logo.svg is not referenced correctly")

        if "invert" in content:
            errors.append("Growth Bible: Found unexpected invert filter in file")
        else:
            successes.append("Growth Bible: No invert filter in file")

        # Verify last reviewed stamp logic
        if "applyLastReviewedStamps" in content:
            successes.append("Growth Bible: Found applyLastReviewedStamps function")
        else:
            errors.append("Growth Bible: Missing applyLastReviewedStamps function")

    # 4. Check JSON/CSV generated outputs
    output_files = [
        "Sales Strategy/bcda_extracted_leads.json",
        "Sales Strategy/bcda_extracted_leads.csv",
        "Sales Strategy/bcda_maturity_index_tracker.json",
        "Sales Strategy/leads_audit_tracker.json",
        "Sales Strategy/bcda_statistics.json",
        "Sales Strategy/daily_outreach_queue.csv",
        "Sales Strategy/territory_clusters.json",
        "Sales Strategy/territory_clusters.csv",
        "Sales Strategy/competitor_radius_map.json",
        "Sales Strategy/business_entity_profiles.json",
        "Sales Strategy/intelligence_panels.json"
    ]

    print("Verifying pipeline outputs...")
    for out in output_files:
        if not os.path.exists(out):
            errors.append(f"Pipeline output missing: {out}")
            continue

        size = os.path.getsize(out)
        if size == 0:
            errors.append(f"Pipeline output empty: {out}")
            continue

        # Validate JSON format
        if out.endswith(".json"):
            try:
                with open(out, "r", encoding="utf-8") as f:
                    json.load(f)
                successes.append(f"JSON Validated: {out}")
            except Exception as e:
                errors.append(f"JSON Corrupted in {out}: {e}")

        # Validate CSV format
        if out.endswith(".csv"):
            try:
                with open(out, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                if len(rows) > 0:
                    successes.append(f"CSV Validated: {out} ({len(rows)} rows)")
                else:
                    errors.append(f"CSV Empty: {out}")
            except Exception as e:
                errors.append(f"CSV Corrupted in {out}: {e}")

    # 5. Check JS database file
    if os.path.exists(intel_data_path):
        print("Verifying intelligence JS bridge...")
        with open(intel_data_path, "r", encoding="utf-8") as f:
            js_content = f.read()
        
        if "window.PANELS =" in js_content or "window.PANELS=" in js_content:
            successes.append("JS Bridge: window.PANELS assignment found")
            # Parse the JSON payload inside window.PANELS = ...
            try:
                js_data = js_content.strip()
                prefix = "window.PANELS ="
                if js_data.startswith(prefix) or js_data.startswith("window.PANELS="):
                    curr_prefix = prefix if js_data.startswith(prefix) else "window.PANELS="
                    payload_str = js_data[len(curr_prefix):].strip()
                    if payload_str.endswith(";"):
                        payload_str = payload_str[:-1].strip()
                    json.loads(payload_str)
                    successes.append("JS Bridge: window.PANELS contains valid JSON data")
                else:
                    errors.append("JS Bridge: Could not extract JSON payload from window.PANELS")
            except Exception as e:
                errors.append(f"JS Bridge: window.PANELS has invalid JSON format: {e}")
        else:
            errors.append("JS Bridge: Missing window.PANELS assignment")

    # Print summary
    print("\n================ VERIFICATION SUMMARY ================")
    print(f"Total Checks Successful: {len(successes)}")
    print(f"Total Errors Found: {len(errors)}")
    print("======================================================")

    if errors:
        print("\nERRORS DETECTED:")
        for err in errors:
            print(f"[-] {err}")
        return False
    else:
        print("\n[+] ALL UPDATED FILES ARE WORKING PROPERLY AND STRUCTURED CORRECTLY!")
        return True

if __name__ == "__main__":
    verify_all()
