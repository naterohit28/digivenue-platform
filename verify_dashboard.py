import os
import json
import re

def verify_dashboard_integration():
    errors = []
    successes = []

    # 1. Check file existence
    rc_path = "Sales Strategy/recommendations_confidence.json"
    fd_path = "_Web/founder-dashboard.html"
    sales_tool_path = "_Web/digistories-sales-tool-v2.html"
    growth_bible_path = "_Web/venue-growth-bible-engine.html"

    print("Checking intelligence moat files...")
    for p in [rc_path, fd_path]:
        if os.path.exists(p):
            successes.append(f"Moat file exists: {p} ({os.path.getsize(p)} bytes)")
        else:
            errors.append(f"Moat file missing: {p}")

    # 2. Check recommendations_confidence.json structure
    if os.path.exists(rc_path):
        print("Checking recommendations_confidence.json schema...")
        try:
            with open(rc_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                successes.append(f"Confidence JSON: Loaded list of {len(data)} rules successfully")
                # check one entry
                first = data[0]
                if all(k in first for k in ["rule_id", "recommendation", "applied_to", "successful", "success_rate"]):
                    successes.append("Confidence JSON: Fields match expected schema")
                else:
                    errors.append("Confidence JSON: Missing expected fields in entry schema")
            else:
                errors.append("Confidence JSON: Structure is not a valid non-empty list")
        except Exception as e:
            errors.append(f"Confidence JSON: Load error: {e}")

    # 3. Check Founder Dashboard contents
    if os.path.exists(fd_path):
        print("Verifying Founder Dashboard JS logic...")
        with open(fd_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Verify it has rule induction logic
        if "induceRules" in content and "DEFAULT_LEADS" in content and "handleFileImport" in content:
            successes.append("Founder Dashboard: Found induceRules(), DEFAULT_LEADS, and file import handlers")
        else:
            errors.append("Founder Dashboard: Missing rule induction or default leads array in JS")

    # 4. Check benchmark markers in Sales Tool
    if os.path.exists(sales_tool_path):
        print("Verifying benchmark markers in Sales Tool...")
        with open(sales_tool_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "loadBenchmarks" in content and "City Average" in content and "venue_intelligence_report" in content:
            successes.append("Sales Tool: loadBenchmarks, City Average, and VIR export logic verified")
        else:
            errors.append("Sales Tool: Missing loadBenchmarks, City Average, or VIR export logic")

    # 5. Check VIR bridge in Growth Bible
    if os.path.exists(growth_bible_path):
        print("Verifying VIR bridge in Growth Bible...")
        with open(growth_bible_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "venue_intelligence_report" in content and "loadConfidenceAndBenchmarks" in content:
            successes.append("Growth Bible: VIR dimensions override and confidence database logic verified")
        else:
            errors.append("Growth Bible: Missing VIR dimensions override or loadConfidenceAndBenchmarks logic")

    print("\n================ MOAT VERIFICATION SUMMARY ================")
    print(f"Total Checks Successful: {len(successes)}")
    print(f"Total Errors Found: {len(errors)}")
    for e in errors:
        print(f"[-] ERROR: {e}")
    for s in successes:
        print(f"[+] SUCCESS: {s}")
    print("===========================================================")

    if errors:
        return False
    return True

if __name__ == "__main__":
    verify_dashboard_integration()
