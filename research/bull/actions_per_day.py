"""Deals (entries + exits) per active day in a Bull Scalper tester report: the trade-count
check of docs/PORTFOLIO_PLAN.md (scenario A vs B). Writes the report hash and the statistics.
Usage: python research/bull/actions_per_day.py OUT_JSON REPORT.htm [REPORT.htm ...]"""
import hashlib, json, re, sys
import pandas as pd

out = {}
for rep in sys.argv[2:]:
    raw = open(rep, "rb").read(); text = raw.decode("utf-16")
    days = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S):
        c = [re.sub("<.*?>", "", x).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
        if len(c) == 13 and re.match(r"\d{4}\.\d\d\.\d\d", c[0]) and c[3] != "balance":
            days.append(c[0][:10])
    s = pd.Series(1, index=days).groupby(level=0).sum()
    out[rep.split("\\")[-1]] = {"report_sha256": hashlib.sha256(raw).hexdigest(), "active_days": int(len(s)),
                                "median_deals_per_active_day": float(s.median()), "mean": round(float(s.mean()), 1),
                                "days_50_or_more": int((s >= 50).sum())}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out, indent=1))
