"""
validate.py — DigiVenue validation harness.

Reads the live intelligence records + a blind ground-truth CSV and produces a
per-engine scorecard (accuracy metrics vs success criteria → PASS/FAIL).

Usage:
    python validate.py venue_intelligence_records.json ground_truth.csv

Ground-truth CSV columns (one row per venue):
    vir_id, true_reviews, true_rating, true_photos, true_ig_followers, true_website,
    expert_dmi, expert_stage, expert_position, ose_plausible, expert_top3
    (expert_top3 = semicolon-separated REC action ids, e.g. "gmb_setup;review_engine;whatsapp_cta")
"""
from __future__ import annotations
import csv, json, math, sys
from pathlib import Path

STAGES = ["Traditional", "Semi-Digital", "Modern", "Intelligent"]


def _pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return round(cov / (sx * sy), 3) if sx and sy else None

def _band(d):
    return "green" if d >= 70 else "amber" if d >= 40 else "red"

def _num(s):
    try:
        return float(s)
    except Exception:
        return None


def validate(records_path, gt_path):
    records = {r["vir"]["vir_id"]: r for r in json.loads(Path(records_path).read_text(encoding="utf-8"))}
    gt = list(csv.DictReader(Path(gt_path).read_text(encoding="utf-8").splitlines()))

    vir_fields, vir_hits = 0, 0
    dmi_pred, dmi_true, dmi_band_hits = [], [], 0
    vmf_exact, vmf_offone, vmf_n = 0, 0, 0
    cie_pos_hits, cie_n = 0, 0
    ose_plausible, ose_n = 0, 0
    rec_prec, rec_top1, rec_n = 0.0, 0, 0

    for row in gt:
        rec = records.get(row.get("vir_id", "").strip())
        if not rec:
            continue
        v = rec["vir"]

        # VIR field accuracy
        def cmp_count(true_s, got):
            t = _num(true_s)
            if t is None or got is None:
                return None
            return abs(got - t) <= max(2, 0.10 * t)  # within 10% (or +-2)
        g = lambda p: _g(v, p)
        checks = [
            cmp_count(row.get("true_reviews"), g("google_business.total_reviews")),
            cmp_count(row.get("true_rating"), g("google_business.rating")),
            cmp_count(row.get("true_photos"), g("google_business.total_photos")),
            cmp_count(row.get("true_ig_followers"), g("instagram.followers")),
            (None if row.get("true_website", "") == "" else (bool(int(row["true_website"])) == bool(g("website.exists")))),
        ]
        for c in checks:
            if c is not None:
                vir_fields += 1
                vir_hits += 1 if c else 0

        # DMI
        ed = _num(row.get("expert_dmi"))
        if ed is not None:
            d = rec["dmi"]["score"]
            dmi_pred.append(d); dmi_true.append(ed)
            dmi_band_hits += 1 if _band(d) == _band(ed) else 0

        # VMF
        es = (row.get("expert_stage") or "").strip()
        if es in STAGES:
            vmf_n += 1
            got = rec["maturity"]["stage"]
            if got == es:
                vmf_exact += 1
            if abs(STAGES.index(got) - STAGES.index(es)) <= 1:
                vmf_offone += 1

        # CIE position (coarse)
        ep = (row.get("expert_position") or "").strip()
        if ep:
            cie_n += 1
            cie_pos_hits += 1 if ep.lower() == (rec["competitive"]["position"] or "").lower() else 0

        # OSE plausibility
        op = (row.get("ose_plausible") or "").strip().upper()
        if op in ("P", "H", "L"):
            ose_n += 1
            ose_plausible += 1 if op == "P" else 0

        # REC precision@3
        et3 = [x.strip() for x in (row.get("expert_top3") or "").split(";") if x.strip()]
        if et3:
            rec_n += 1
            got_ids = [a.get("id") for a in rec["recommendations"][:3]]
            overlap = len(set(et3) & set(got_ids))
            rec_prec += overlap / 3.0
            if got_ids and et3 and got_ids[0] == et3[0]:
                rec_top1 += 1

    # ── assemble scorecard ──
    def pct(a, b):
        return round(100 * a / b, 1) if b else None
    dmi_r = _pearson(dmi_pred, dmi_true)
    dmi_mae = round(sum(abs(a - b) for a, b in zip(dmi_pred, dmi_true)) / len(dmi_pred), 1) if dmi_pred else None

    score = {
        "VIR": {"field_accuracy_%": pct(vir_hits, vir_fields), "n_fields": vir_fields,
                "PASS": (pct(vir_hits, vir_fields) or 0) >= 90},
        "DMI": {"pearson_r": dmi_r, "MAE": dmi_mae, "band_agreement_%": pct(dmi_band_hits, len(dmi_pred)),
                "PASS": bool(dmi_r and dmi_r >= 0.8 and dmi_mae is not None and dmi_mae <= 10 and (pct(dmi_band_hits, len(dmi_pred)) or 0) >= 80)},
        "CIE": {"position_agreement_%": pct(cie_pos_hits, cie_n), "n": cie_n,
                "PASS": (pct(cie_pos_hits, cie_n) or 0) >= 75},
        "OSE": {"plausible_%": pct(ose_plausible, ose_n), "n": ose_n,
                "PASS": (pct(ose_plausible, ose_n) or 0) >= 80},
        "VMF": {"exact_%": pct(vmf_exact, vmf_n), "within_one_%": pct(vmf_offone, vmf_n),
                "PASS": (pct(vmf_exact, vmf_n) or 0) >= 75 and (pct(vmf_offone, vmf_n) or 0) >= 95},
        "REC": {"precision@3": round(rec_prec / rec_n, 2) if rec_n else None, "top1_%": pct(rec_top1, rec_n),
                "PASS": bool(rec_n and (rec_prec / rec_n) >= 0.70 and (pct(rec_top1, rec_n) or 0) >= 60)},
    }
    return score


def _g(vir, path):
    node = vir
    for k in path.split("."):
        if not isinstance(node, dict) or k not in node:
            return None
        node = node[k]
    return node["value"] if isinstance(node, dict) and "value" in node else node


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    sc = validate(sys.argv[1], sys.argv[2])
    print("\n  DIGIVENUE VALIDATION SCORECARD")
    print("  " + "-" * 52)
    for engine, m in sc.items():
        status = "PASS" if m.get("PASS") else "FAIL"
        metrics = " · ".join(f"{k}={v}" for k, v in m.items() if k != "PASS")
        print(f"  [{status}] {engine:4} {metrics}")
    print("  " + "-" * 52)
    certified = sum(1 for m in sc.values() if m.get("PASS"))
    print(f"  Engines certified: {certified}/6" + ("  ->  PROVEN" if certified == 6 else ""))
