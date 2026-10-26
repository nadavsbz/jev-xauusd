"""Table of the BD settings search on the last year (docs/BD_OPT_PLAN.md): net % of the 120K deposit, max equity drawdown %,
their ratio, and the pre-registered 'promising' flag (net >= base x 1.10 and DD <= base DD x 1.2).
Usage: python research/bd1/opt_table.py [PREFIX=opt1]"""
import glob, json, sys

pre = sys.argv[1] if len(sys.argv) > 1 else "opt1"
def ev(p):
    d = json.load(open(p, encoding="utf-8")); s = d["summary_from_report"]
    dd = next(v for k, v in s.items() if "שווי" in k)
    return d["recomputed"]["net"] / d["recomputed"]["deposit"] * 100, float(dd.split("(")[1].rstrip("%)"))
rows = {p.split(f"{pre}_opt_")[1][:-5]: ev(p) for p in glob.glob(f"docs/evidence/{pre}_opt_*.json")}
bn, bd = rows.get("base", (None, None))
print(f"{'tag':10}{'net%':>8}{'DD%':>7}{'net/DD':>8}  promising")
for t, (n, d) in sorted(rows.items(), key=lambda x: -x[1][0]):
    ok = bn is not None and n >= bn * 1.10 and d <= bd * 1.2
    print(f"{t:10}{n:+8.0f}{d:7.1f}{n / d:8.2f}  {'YES' if ok else ''}")
