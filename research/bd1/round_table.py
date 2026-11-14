r"""Per-year table of one or more every-year rounds: net % of the 120K deposit / equity drawdown %, positive years, 7-year multiplier.
Usage: python research/bd1/round_table.py RESULTS.jsonl [RESULTS.jsonl ...]"""
import json, sys, collections
D = collections.defaultdict(dict)
for f in sys.argv[1:]:
    for l in open(f, encoding="utf-8"):
        r = json.loads(l)
        if "report" not in r: continue
        _, y, t = r["report"].split("_", 2)
        D[t][y[2:]] = (r["net"] / 1200, float(r["summary"]["שווי הפסד מקסימלי"].split("(")[1][:-2]))
for t, d in D.items():
    m = 1
    for v in d.values(): m *= 1 + v[0] / 100
    print(f"{t:16}", " ".join(f"{y}:{d[y][0]:+4.0f}/{d[y][1]:.0f}" for y in sorted(d)), f"pos {sum(v[0] > 0 for v in d.values())}/{len(d)} x{m:.2f}")
