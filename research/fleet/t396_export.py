"""t396: export BD 20 vs 50 yearly tester deals normalized to the 120K deposit, plus report quality/summary, for Grok.
Usage: py -3.12 research/fleet/t396_export.py"""
import os, re, sys, json
import pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals
OUT = "docs/agents/grok_data/t396_tester"; os.makedirs(OUT, exist_ok=True); DEP = 120000.0; summ = {}
for sp in (20, 50):
    for y in ("2022", "2023", "2024", "2025", "2026"):
        rep = f"C:/MT5_JEV_TEST/t396_b{sp}_{y}.htm"
        t = open(rep, "rb").read().decode("utf-16"); t = re.sub(r"[|\s]*\|[|\s]*", "|", re.sub("<[^>]+>", "|", t)); g = lambda k: t[t.find(k):].split("|")[1]
        d = deals(rep); d = d[d.symbol == "XAUUSD"].copy(); d["ts"] = pd.to_datetime(d.t, unit="s")
        e = d[["ts", "dir", "type", "price", "comment"]].copy(); e["vol_per_100k"] = d.volume / DEP * 1e5
        for c in ("profit", "swap", "commission"): e[c + "_pct"] = 100 * d[c] / DEP
        e.to_csv(f"{OUT}/{y}_b{sp}.csv.gz", index=False)
        summ[f"{y}_b{sp}"] = dict(quality=g("איכות היסטוריה:"), net=g("סך רווח נקי:"), eq_dd=g("שווי הפסד מקסימלי:"), trades=g("סך עסקאות:"), ticks=g("טיקטוקים:"))
json.dump(summ, open(f"{OUT}/summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k, v in summ.items(): print(k, v["quality"], v["net"], v["eq_dd"], v["trades"])
