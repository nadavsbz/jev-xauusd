"""Table of DragonClone_v7 runs over the 5 real-tick periods vs the v7 baseline (docs/BD_V7_PLAN.md).
Usage: python research/bd1/v7_table.py [BASE_TAG] TAG [TAG ...]   (reads docs/evidence/v7_<period>_<tag>.json; BASE_TAG default 'off')
Prints % of the 120K deposit per period, the 5-period multiplier, and how many periods beat the baseline."""
import json, os, sys

PERIODS = ["rf2022", "rf2023", "rf2024", "rf2025", "eg2526"]

def pct(period, tag):
    p = f"docs/evidence/v7_{period}_{tag}.json"
    if not os.path.exists(p): return None
    r = json.load(open(p, encoding="utf-8"))["recomputed"]
    return r["net"] / r["deposit"] * 100

def mult(v):
    m = 1.0
    for x in v: m *= max(0.0, 1 + x / 100)
    return m

if __name__ == "__main__":
    a = sys.argv[1:]; base = a.pop(0) if a and a[0].startswith("base=") else "base=off"; base = base[5:]
    b = [pct(p, base) for p in PERIODS]
    print("tag".ljust(10) + "".join(p.rjust(9) for p in PERIODS) + "   mult  beats")
    for t in [base] + a:
        v = [pct(p, t) for p in PERIODS]
        cells = "".join((f"{x:+.0f}%" if x is not None else "-").rjust(9) for x in v)
        done = [(x, y) for x, y in zip(v, b) if x is not None and y is not None]
        m = mult([x for x in v if x is not None]) if all(x is not None for x in v) else None
        print(t.ljust(10) + cells + (f"  x{m:.2f}" if m is not None else "     -") + f"  {sum(x > y for x, y in done)}/{len(done)}")
