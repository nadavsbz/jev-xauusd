"""Lot ratio x guard level on account 1's real baskets (docs/BD_LOTGUARD_PLAN.md, registered 21.10.2026).
Every basket is rescaled to a constant lot ratio R (balance cents per first-lot), the floating path is checked
against a close-all guard at G% of the balance. Needs clusters.py --strict output in JEV_DERIVED."""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inputs import max_drawdown

DER = os.environ.get("JEV_DERIVED", "data/derived/bd1_rescue")
SLIP, WIPE, HALF = 1.3, -90.0, pd.Timestamp("2026-05-01").timestamp()
o = pd.read_csv(os.path.join(DER, "clusters_strict.csv")).sort_values("t0").reset_index(drop=True)
pos = pd.read_csv(os.path.join(DER, "positions_strict.csv"))
v0 = pos.sort_values("t0_msc").groupby("cid").volume.first(); vmax = pos.groupby("cid").volume.max()
o["rho"] = o.bal0 / o.cid.map(v0); o["vmax"] = o.cid.map(vmax)
P = dict(np.load(os.path.join(DER, "paths_strict.npz")))
ag = pd.read_csv(os.path.join(DER, "after_guard.csv")).set_index("cid")
pmin = {}
for i in range(len(o)):
    a = P.get(str(o.cid[i]))
    if a is not None:
        a = a[a[:, 0] + 60 <= o.t1[i]]
        if len(a):
            pmin[i] = a[:, 1].min()
wk = pd.to_datetime(o.t0, unit="s").dt.to_period("W").values
rng = np.random.default_rng(11)


def run(R, G):
    s = (o.rho / R).values; r = s * o.pnl_pct.values; tr = s * o.mae_pct.values
    ntrig = nwipe = 0
    for i in range(len(o)):
        worst = s[i] * min(pmin.get(i, o.mae_pct[i]), o.mae_pct[i])
        if o.guard[i] and o.cid[i] in ag.index:          # the real guard cut it: continue it on paper
            g = ag.loc[o.cid[i]]
            after = s[i] * g.worst_lower
            if G is None or after > -G:
                if worst > (-G if G else WIPE) and after > WIPE:
                    r[i] = 0.0 if g.recovered else after; tr[i] = min(worst, after); continue
            worst = min(worst, after)
        if G is not None and worst <= -G:
            r[i] = tr[i] = -SLIP * G; ntrig += 1
        elif worst <= WIPE:
            r[i] = tr[i] = -100.0; nwipe += 1
    return r / 100, np.minimum(tr, r) / 100, ntrig, nwipe, s


def weeks(r, tr):
    d = pd.DataFrame({"w": wk, "r": r, "tr": tr})
    out = []
    for _, g in d.groupby("w", sort=True):
        c = np.cumprod(1 + g.r.values); prev = np.r_[1.0, c[:-1]]
        out.append((c[-1] - 1, min((prev * (1 + g.tr.values)).min(), c.min()) - 1))
    return np.array(out)


def boot(W, n=2000, blocks=13):
    st = rng.integers(0, len(W) - 4, size=(n, blocks))
    idx = (st[:, :, None] + np.arange(4)).reshape(n, -1)
    wr, wt = np.maximum(W[idx, 0], -1), np.maximum(W[idx, 1], -1)
    eq = np.cumprod(1 + wr, axis=1); prev = np.c_[np.ones(n), eq[:, :-1]]
    peak = np.maximum.accumulate(np.c_[np.ones(n), eq], axis=1)[:, :-1]
    dd = np.minimum(prev * (1 + wt) / peak - 1, 0).min(axis=1)
    low = np.minimum(prev * (1 + wt), eq).min(axis=1)
    return dict(median_x=round(float(np.median(eq[:, -1])), 2), p10_x=round(float(np.percentile(eq[:, -1], 10)), 2),
                p_dd50=round(float((dd <= -0.5).mean()), 3), p_wipe=round(float((low < 0.1).mean()), 3))


res = {"grid": []}
for R in (250e3, 300e3, 400e3, 500e3, 600e3, 800e3):
    for G in (10, 15, 20, 25, 30, 40, 60, None):
        r, tr, nt, nw, s = run(R, G)
        x = {"R": int(R), "G": G, "trig": nt, "wipes": nw, "lot_cap_share": round(float((s * o.vmax.values > 5).mean()), 4)}
        for h, m in {"h1": o.t0.values < HALF, "h2": o.t0.values >= HALF, "all": np.ones(len(o), bool)}.items():
            eq, dd = max_drawdown(r[m], tr[m]); x[h] = (round(float(eq[-1]), 2), round(float(dd), 1))
        x.update(boot(weeks(r, tr)))
        x["eligible"] = x["p_dd50"] <= 0.05 and x["h1"][0] > 0.1 and x["h2"][0] > 0.1
        res["grid"].append(x); print(x, flush=True)
el = [x for x in res["grid"] if x["eligible"]]
res["chosen"] = max(el, key=lambda x: x["median_x"]) if el else None
print("chosen", res["chosen"])
json.dump(res, open("docs/evidence/bd1_lotguard.json", "w"), indent=1)
