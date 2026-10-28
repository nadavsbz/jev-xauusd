"""Morning table of crash-day variants (docs/BD_V4_PLAN.md): per config, realised result on each crash day,
month nets, wipes and worst equity drawdown, from the tester reports and evidence files.
Usage: python research/bd1/v4_table.py OUT.csv TAG [TAG ...]"""
import json, os, sys
import pandas as pd
sys.path[:0] = [os.path.join(os.path.dirname(__file__), "..", "btc")]
import guardian_sim as g

CRASH_DAYS = {"2026-05-28": "may26", "2026-05-29": "may26", "2026-06-05": "jun26", "2026-06-08": "jun26", "2026-07-01": "jul26",
              "2026-07-30": "jul26b", "2026-07-31": "jul26b", "2026-08-10": "aug26", "2026-08-27": "aug26", "2026-10-12": "oct26"}
CRASH = ["may26", "jun26", "jul26", "aug26", "oct26"]   # jul26b overlaps jul26: reported apart, never summed (Codex PR 39, P1); NORMAL = ["dec25", "mar26", "sep26"]

def run(rep):
    e = f"docs/evidence/{rep}.json"
    if not os.path.exists(e): return None
    d = json.load(open(e, encoding="utf-8")); r = d["recomputed"]
    dd = next(v for k, v in d["summary_from_report"].items() if "שווי" in k)
    x = g.deals(f"C:/MT5_JEV_TEST/{rep}.htm"); x = x[x.dir == "out"].copy()
    x["day"] = pd.to_datetime(x.t, unit="s").dt.strftime("%Y-%m-%d")
    daily = (x.profit + x.swap + x.commission).groupby(x.day).sum()
    return {"net": r["net"], "dep": r["deposit"], "dd": float(dd.split("(")[1].rstrip("%)")), "daily": daily,
            "wiped": r["net"] < -0.5 * r["deposit"]}

def base_name(tag, m):
    guard = tag.endswith("g20")
    if guard: return f"v3g20_{m}"
    return f"v3_{m}" if os.path.exists(f"docs/evidence/v3_{m}.json") else f"val5_{m}_clone"

def row(tag):
    out = {"tag": tag}
    runs = {m: run(f"{tag}_{m}" if tag not in ("v3",) or os.path.exists(f"docs/evidence/v3_{m}.json") else f"val5_{m}_clone") for m in CRASH + NORMAL}
    for day, m in CRASH_DAYS.items():
        r = runs.get(m); out[day] = round(float(r["daily"].get(day, 0)) / r["dep"] * 100, 1) if r else None   # % of month-start balance
    for grp, ms in (("crash", CRASH), ("normal", NORMAL)):
        got = {m: runs[m] for m in ms if runs.get(m)}
        out[grp + "_net"] = round(sum(r["net"] for r in got.values())); out[grp + "_n"] = len(got)
        out[grp + "_maxdd"] = max((r["dd"] for r in got.values()), default=None)
        out[grp + "_wipes"] = sum(r["wiped"] for r in got.values())
    return out

if __name__ == "__main__":
    t = pd.DataFrame([row(x) for x in sys.argv[2:]]); t.to_csv(sys.argv[1], index=False, encoding="utf-8-sig")
    pd.set_option("display.width", 250); print(t.to_string(index=False))
