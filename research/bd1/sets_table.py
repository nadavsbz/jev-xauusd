"""Community set sweep table (docs/CRASH_LINK_PLAN.md, registered 4.11.2026): net % of deposit and balance max drawdown % per year,
profitable years, and the pre-registered labels: candidate = >=5/7 profitable years and DD <= 40% every year; strong = DD <= 25%.
Usage: python research/bd1/sets_table.py research/bd1/sets_results.jsonl"""
import json, re, sys
import pandas as pd
R = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
rows = []
for r in R:
    sid, y = re.match(r"cs_(\d+)_(\d{4})", r["report"]).groups()
    dd = float(re.search(r"\(([\d.]+)%\)", r["summary"].get("מאזן הפסד מקסימלי", "(0%)")).group(1))
    rows.append({"set": sid, "y": y, "net": 100 * r["net"] / r["deposit"], "dd": dd})
D = pd.DataFrame(rows).drop_duplicates(["set", "y"], keep="last")
N = D.pivot(index="set", columns="y", values="net").round(0)
M = D.groupby("set").dd.max()
N["runs"] = D.groupby("set").size(); N["plus"] = (D.assign(p=D.net > 0).groupby("set").p.sum())
N["maxDD"] = M.round(0)
N["label"] = ["strong" if (r.plus >= 5 and r.runs == 7 and r.maxDD <= 25) else "candidate" if (r.plus >= 5 and r.runs == 7 and r.maxDD <= 40) else ""
              for r in N.itertuples()]
print(N.sort_values("plus", ascending=False).to_string())
