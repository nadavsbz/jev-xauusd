"""Rule "close a deep basket on a partial recovery" (docs/BD_RESCUE_PLAN.md, registered 21.10.2026),
scored on account 1's real baskets and their minute paths (clusters.py --strict, paths_strict.npz).
Usage: JEV_DERIVED=data/derived/bd1_rescue python research/bd1/rescue.py"""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inputs import max_drawdown

SLIP = 0.5
DER = os.environ.get("JEV_DERIVED", "data/derived/bd1_rescue")
o = pd.read_csv(os.path.join(DER, "clusters_strict.csv")).sort_values("t0").reset_index(drop=True)
P = dict(np.load(os.path.join(DER, "paths_strict.npz")))
HALF = pd.Timestamp("2026-05-01").timestamp()


def apply(D, f):
    r = o.pnl_pct.values.copy(); tr = o.mae_pct.values.copy(); ru = o.runup_before_pct.values.copy(); rescued = []
    for i, c in enumerate(o.cid.values):
        a = P.get(str(c))
        if a is None:
            continue
        # only minutes that ended before the basket's last exit: in the exit minute itself the strict path has
        # already dropped the floating part but not yet booked the realised cash (reads ~0, not a real quote)
        a = a[a[:, 0] + 60 <= o.t1.values[i]]
        if not len(a):
            continue
        lo = a[:, 1]; worst = np.minimum.accumulate(lo)
        on = np.where(worst <= -D)[0]
        if not len(on):
            continue
        k = on[0]
        ex = np.where((np.arange(len(lo)) > k) & (lo >= f * worst))[0]
        if not len(ex):
            continue
        j = ex[0]; val = f * worst[j] - SLIP
        rescued.append(dict(cid=int(c), t=str(pd.to_datetime(a[j, 0], unit="s")), worst=round(float(worst[j]), 2),
                            exit=round(float(val), 2), real=round(float(o.pnl_pct[i]), 2), guard=bool(o.guard[i])))
        r[i] = val; tr[i] = worst[j]
        ru[i] = a[:j + 1, 2].max()                   # peak up to the simulated exit only (PR 35 review)
    return r, tr, ru, rescued


def score(r, tr, m, ru=None):
    ru = o.runup_before_pct.values if ru is None else ru
    eq, dd = max_drawdown(r[m] / 100, tr[m] / 100, ru[m] / 100, None)
    return round(float(eq[-1]), 3), round(float(dd), 2)


halves = {"h1": o.t0.values < HALF, "h2": o.t0.values >= HALF, "all": np.ones(len(o), bool)}
base = {h: score(o.pnl_pct.values, o.mae_pct.values, m) for h, m in halves.items()}
res = {"baskets": len(o), "deep_paths": len(P), "actual": base, "grid": []}
for D in (5, 10, 15):
    for f in (0.5, 0.33):
        r, tr, ru, resc = apply(D, f)
        s = {h: score(r, tr, m, ru) for h, m in halves.items()}
        cand = all(s[h][0] > base[h][0] and s[h][1] > base[h][1] for h in ("h1", "h2"))
        res["grid"].append(dict(D=D, f=f, **s, rescued=len(resc), saved_guard=sum(x["guard"] for x in resc),
                                cost_recovered=sum(x["real"] > 0 for x in resc), candidate=cand, cases=resc))
        print(D, f, s, "rescued", len(resc), "of them real guard", sum(x["guard"] for x in resc), "candidate", cand)
print("actual", base)
json.dump(res, open("docs/evidence/bd1_rescue.json", "w"), indent=1)
