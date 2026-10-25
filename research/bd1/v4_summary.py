"""Summary table of v4 crash-day variants vs the frozen v3 (docs/BD_V4_PLAN.md).
Usage: python research/bd1/v4_summary.py TAG [TAG ...]   (reads docs/evidence/<TAG>_<month>.json)
v3 baseline: v3_<m>, else val5_<m>_clone (same code, validated run)."""
import json, os, sys

CRASH = ["may26", "jun26", "jul26", "jul26b", "aug26", "oct26"]; NORMAL = ["dec25", "mar26", "sep26"]

def ev(rep):
    p = f"docs/evidence/{rep}.json"
    if not os.path.exists(p): return None
    d = json.load(open(p, encoding="utf-8")); s = d["summary_from_report"]; r = d["recomputed"]
    dd = next((v for k, v in s.items() if "שווי" in k), "0 (0%)")
    return {"net": r["net"], "dep": r["deposit"], "dd_pct": float(dd.split("(")[1].rstrip("%)")), "wiped_on": r.get("end_of_test_date") if r["net"] < -0.5 * r["deposit"] else None}

def base(m): return ev(f"v3_{m}") or ev(f"val5_{m}_clone")

def row(tag):
    out = {"tag": tag}
    for grp, ms in (("crash", CRASH), ("normal", NORMAL)):
        got = [(m, ev(f"{tag}_{m}"), base(m)) for m in ms]
        got = [g for g in got if g[1] and g[2]]
        out[grp + "_months"] = len(got)
        out[grp + "_net"] = round(sum(g[1]["net"] for g in got)); out[grp + "_v3"] = round(sum(g[2]["net"] for g in got))
        out[grp + "_maxdd"] = max((g[1]["dd_pct"] for g in got), default=None)
        out[grp + "_wipes"] = sum(1 for g in got if g[1]["wiped_on"])
        out[grp + "_by_month"] = {g[0]: round(g[1]["net"]) for g in got}
    return out

if __name__ == "__main__":
    tags = sys.argv[1:] or ["v3"]
    for t in tags: print(json.dumps(row(t), ensure_ascii=False))
