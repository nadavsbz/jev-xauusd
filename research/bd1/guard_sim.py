import sys, numpy as np, pandas as pd
from inputs import max_drawdown, peak_before_cut
o = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else "data/derived/bd1/clusters_strict.csv")
o["d"] = pd.to_datetime(o.t0, unit="s")
LOWS = dict(np.load(sys.argv[1].replace("clusters", "record_lows").replace(".csv", ".npz") if len(sys.argv) > 1
                    else "data/derived/bd1/record_lows_strict.npz"))
real = o.guard & (o.pnl_pct < -5)          # the real guard closes (crash baskets)
SLIP = 0.5                                  # extra % lost past the level (gap/slippage), ASSUMED
def run(sub, X, unknown):
    r = sub.pnl_pct.values.copy() / 100
    tr = sub.mae_pct.values / 100
    hit = sub.mae_pct.values <= -X
    r[hit] = -(X + SLIP) / 100
    # real guard closed first, before reaching X: continuation unknown
    unk = real.loc[sub.index].values & ~hit
    if unknown == "worst": r[unk] = -(X + SLIP) / 100
    else: r[unk] = sub.loc[unk, "pnl_pct"].clip(lower=None).values * 0 + 0.02  # recovers with +2%
    cut = hit | (unk & (unknown == "worst"))
    tr = np.where(cut, np.minimum(r, 0), tr)   # a cut basket bottoms at the cut
    rb = sub.runup_before_pct.values / 100      # floating peak before the trough
    rb = np.where(hit, [peak_before_cut(LOWS, c, -X) / 100 if h else 0 for c, h in zip(sub.cid.values, hit)], rb)
    ru = np.where(cut, rb, sub.runup_pct.values / 100)   # a cut basket has no later run-up
    eq, dd = max_drawdown(r, tr, rb, ru)       # drawdown from floating peaks to floating lows
    return eq[-1], dd, hit.sum(), unk.sum()
for name, sub in [("all 2025-11..2026-10", o), ("Nov-May", o[o.d < "2026-06-01"]), ("Jun-Oct", o[o.d >= "2026-06-01"])]:
    eq, dd = max_drawdown(sub.pnl_pct.values / 100, sub.mae_pct.values / 100,
                          sub.runup_before_pct.values / 100, sub.runup_pct.values / 100)
    print(f"\n== {name}: actual x{eq[-1]:.2f}, maxDD incl. floating {dd:.1f}%")
    print(" X%   x_end(worst)  maxDD   x_end(best)  maxDD  cuts unknown")
    for X in [5, 8, 10, 12, 15, 20, 25]:
        a = run(sub, X, "worst"); b = run(sub, X, "best")
        print(f"{X:3d}  {a[0]:9.2f}  {a[1]:7.1f}  {b[0]:9.2f}  {b[1]:6.1f}  {a[2]:4d} {a[3]:4d}")
