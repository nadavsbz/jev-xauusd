"""Rule "close the whole basket when its k-th position opens" (a real-time
signal: the grid depth is visible on the chart), scored on the real baskets.

Fixed before looking at results (2026-10-15):
- k from 6 to 20; selection on Nov-May (train) by end multiplier subject to
  max drawdown, then scored once on Jun-Oct (test).
- Cut value = realised P&L of positions already closed + the open positions
  marked at the k-th deal's own price (a quote known at that second), minus
  SLIP (0.5% of the balance, ASSUMED) for spread and closing many lots at once.
- Peak and low before the cut come from the basket equity path (floating +
  realised) over minutes that ended before the k-th deal (clusters.py).
- Baskets with fewer than k positions keep their real result (including the
  real guard's cuts).
- Drawdown from floating peaks to floating lows, as in the report.
"""
import numpy as np, pandas as pd
from inputs import max_drawdown

SLIP = 0.5
o = pd.read_csv("data/derived/bd1/clusters_strict.csv"); o["d"] = pd.to_datetime(o.t0, unit="s")
LV = dict(np.load("data/derived/bd1/levels_strict.npz"))


def run(sub, k):
    r = sub.pnl_pct.values / 100; tr = sub.mae_pct.values / 100
    rb = sub.runup_before_pct.values / 100; ru = sub.runup_pct.values / 100
    r, tr, rb, ru = r.copy(), tr.copy(), rb.copy(), ru.copy()
    cuts = 0
    for i, (c, n) in enumerate(zip(sub.cid.values, sub.n.values)):
        if k is None or n < k or str(c) not in LV:
            continue
        a = LV[str(c)][k - 1]                       # k, t, realised, floating, peak, low so far
        val = (a[2] + a[3] - SLIP) / 100
        r[i] = val; tr[i] = min(a[5] / 100, val, 0); rb[i] = max(a[4] / 100, 0); ru[i] = rb[i]
        cuts += 1
    eq, dd = max_drawdown(r, tr, rb, ru)
    return eq[-1], dd, cuts


periods = [("Nov-May (train)", o[o.d < "2026-06-01"]), ("Jun-Oct (test)", o[(o.d >= "2026-06-01") & (o.d < "2026-10-16")]),
           ("all", o[o.d < "2026-10-16"])]
rows = []
for k in [None] + list(range(6, 21)):
    row = {"k": "none" if k is None else k}
    for name, sub in periods:
        x, dd, cuts = run(sub, k)
        row[name] = f"x{x:5.2f} {dd:6.1f}% ({cuts})"
        row[name + "_x"], row[name + "_dd"] = x, dd
    rows.append(row)
t = pd.DataFrame(rows)
print(t[["k"] + [p[0] for p in periods]].to_string(index=False))
tr_ok = t[(t.k != "none")]
best = tr_ok.loc[tr_ok["Nov-May (train)_x"].idxmax()]
print(f"\nchosen on train (highest multiplier): k={best.k} -> test {best['Jun-Oct (test)']}")
ok15 = tr_ok[tr_ok["Nov-May (train)_dd"] >= -15]
if len(ok15):
    b = ok15.loc[ok15["Nov-May (train)_x"].idxmax()]
    print(f"chosen on train with max DD <= 15%: k={b.k} -> test {b['Jun-Oct (test)']}")
else:
    print("no k keeps train max DD within 15%")
