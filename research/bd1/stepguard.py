"""Two-step guard on account 1's real baskets (docs/BD_STEPGUARD_PLAN.md, registered 21.10.2026): at a loss of T% of
the balance close the largest q of the open lots and stop adding levels; hold the rest to breakeven, a total stop at S%
or 10 days. Needs clusters.py --strict output (paths, positions) in JEV_DERIVED and the same snapshots."""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inputs import load, max_drawdown

K, SLIP1, SLIP2, HOLD = 100.0, 0.3, 0.5, 10 * 1440
DER = os.environ.get("JEV_DERIVED", "data/derived/bd1_rescue")
_, bars = load()
bt = bars.time.values; lo = bars.low.values; hi = bars.high.values; cl = bars.close.values; spr = bars.spread.values * 0.01
o = pd.read_csv(os.path.join(DER, "clusters_strict.csv")).sort_values("t0").reset_index(drop=True)
P = dict(np.load(os.path.join(DER, "paths_strict.npz")))
pos = pd.read_csv(os.path.join(DER, "positions_strict.csv"))
byc = {c: g for c, g in pos.groupby("cid")}
HALF = pd.Timestamp("2026-05-01").timestamp()


def one(i, T, q, S):
    c = o.cid[i]; a = P.get(str(c)); b0 = o.bal0[i]
    if a is None:
        return None
    a = a[a[:, 0] + 60 <= o.t1[i]]                       # minutes before the basket's last exit (rescue.py)
    k = np.where(a[:, 1] <= -T)[0]
    if not len(k):
        return None
    tm = a[k[0], 0]; m = np.searchsorted(bt, tm)
    g = byc[c]
    done = g[g.t1 <= tm + 59]; op = g[(g.t0 < tm + 60) & (g.t1 > tm + 59)]
    realised = done.pnl.sum()
    if not len(op):
        return None
    s = op.sgn.values.astype(float); v = op.volume.values; px = op.open_px.values; cost = op.cost.values
    mark = lambda p_, sp: np.where(s > 0, p_ - px, px - p_ - sp) * v * K + cost
    now = mark(cl[m], spr[m])
    order = np.argsort(-v, kind="stable"); cum = np.cumsum(v[order]) / v.sum()
    shut = np.zeros(len(v), bool); shut[order[:np.searchsorted(cum, q - 1e-9) + 1]] = True
    step1 = now[shut].sum() - SLIP1 / 100 * b0
    keep = ~shut
    if not keep.any():
        val, worst = realised + step1, a[:k[0] + 1, 1].min()
        return val / b0 * 100, min(worst, val / b0 * 100), tm
    i1 = min(len(bt), m + 1 + HOLD); sl = slice(m + 1, i1)
    s2, v2, px2, c2 = s[keep], v[keep], px[keep], cost[keep]
    bad = sum(np.where(sj > 0, lo[sl] - pj, pj - hi[sl] - spr[sl]) * vj * K + cj for sj, vj, pj, cj in zip(s2, v2, px2, c2))
    good = sum(np.where(sj > 0, hi[sl] - pj, pj - lo[sl] - spr[sl]) * vj * K + cj for sj, vj, pj, cj in zip(s2, v2, px2, c2))
    base = realised + step1
    stop = np.where(base + bad <= -S / 100 * b0)[0]; back = np.where(good >= 0)[0]
    js = stop[0] if len(stop) else 10**9; jb = back[0] if len(back) else 10**9
    if js <= jb and js < 10**9:
        val = -(S + SLIP2) / 100 * b0; worst = val
    elif jb < 10**9:
        val = base; worst = base + bad[:jb + 1].min()
    elif i1 - (m + 1) < HOLD:
        return "censored"                                # data ends before the 10-day horizon (PR 35 review)
    else:
        last = sum(np.where(sj > 0, cl[i1 - 1] - pj, pj - cl[i1 - 1] - spr[i1 - 1]) * vj * K + cj for sj, vj, pj, cj in zip(s2, v2, px2, c2))
        val = base + last; worst = base + bad.min()
    worst = min(worst / b0 * 100, a[:k[0] + 1, 1].min())
    return val / b0 * 100, min(worst, val / b0 * 100), tm


def run(T, q, S):
    r = o.pnl_pct.values.copy(); tr = o.mae_pct.values.copy(); cases = []
    keep = np.ones(len(o), bool)                       # censored baskets leave BOTH the rule and its baseline (PR 37 review)
    for i in range(len(o)):
        x = one(i, T, q, S)
        if isinstance(x, str):
            keep[i] = False
            continue
        if x is None:
            continue
        cases.append(dict(t=str(pd.to_datetime(x[2], unit="s")), sim=round(x[0], 2), real=round(float(r[i]), 2), guard=bool(o.guard[i])))
        r[i], tr[i] = x[0], x[1]
    out = {"T": T, "q": q, "S": S, "triggered": len(cases), "censored": int((~keep).sum()), "cases": cases, "base": {}}
    for h, msk in {"h1": o.t0.values < HALF, "h2": o.t0.values >= HALF, "all": np.ones(len(o), bool)}.items():
        msk = msk & keep
        eq, dd = max_drawdown(r[msk] / 100, tr[msk] / 100)
        out[h] = (round(float(eq[-1]), 3), round(float(dd), 2))
        eq, dd = max_drawdown(o.pnl_pct.values[msk] / 100, o.mae_pct.values[msk] / 100)
        out["base"][h] = (round(float(eq[-1]), 3), round(float(dd), 2))
    return out


if __name__ == "__main__":
    res = {"actual": {}}
    for h, msk in {"h1": o.t0.values < HALF, "h2": o.t0.values >= HALF, "all": np.ones(len(o), bool)}.items():
        eq, dd = max_drawdown(o.pnl_pct.values[msk] / 100, o.mae_pct.values[msk] / 100)
        res["actual"][h] = (round(float(eq[-1]), 3), round(float(dd), 2))
    print("actual", res["actual"]); res["grid"] = []
    for T in (10, 15):
        for q in (0.5, 0.75, 1.0):
            for S in ((25, 35) if q < 1 else (99,)):
                x = run(T, q, S); a = x["base"]
                x["candidate"] = q < 1 and all(x[h][0] > a[h][0] and x[h][1] > a[h][1] for h in ("h1", "h2"))
                res["grid"].append(x)
                print(T, q, S, "h1", x["h1"], "h2", x["h2"], "all", x["all"], "n", x["triggered"], "candidate", x["candidate"], flush=True)
    json.dump(res, open("docs/evidence/bd1_stepguard.json", "w"), indent=1)
