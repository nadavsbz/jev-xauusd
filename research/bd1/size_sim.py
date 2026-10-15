import numpy as np, pandas as pd
from inputs import max_drawdown
o = pd.read_csv("data/derived/bd1/clusters_strict.csv"); o["d"] = pd.to_datetime(o.t0, unit="s")
real = (o.guard & (o.pnl_pct < -5)).values
SLIP = 0.5
days = (o.t1.max() - o.t0.min()) / 86400
def run(sub_mask, f, X, unknown):
    p = o.pnl_pct.values[sub_mask] * f / 100; m = o.mae_pct.values[sub_mask] * f
    rl = real[sub_mask]
    r = p.copy(); hit = m <= -X; r[hit] = -(X + SLIP) / 100
    unk = rl & ~hit  # real guard fired before our level: continuation unknown
    r[unk] = -(X + SLIP) / 100 if unknown == "worst" else 0.02 * f
    cut = hit | (unk & (unknown == "worst"))
    tr = np.where(cut, np.minimum(r, 0), m / 100)   # floating low inside each basket
    eq, dd = max_drawdown(r, tr)                    # drawdown includes each basket's floating low
    return eq[-1], dd, hit.sum(), unk.sum()
allm = np.ones(len(o), bool); late = (o.d >= "2026-06-01").values
print("f   X  | all: x_end worst/best  maxDD worst | Jun-Oct x_end worst | cuts unk")
for f in [1.0, 0.75, 0.5, 0.35, 0.25]:
    for X in [10, 15, 100]:
        a = run(allm, f, X, "worst"); b = run(allm, f, X, "best"); c = run(late, f, X, "worst")
        cagr = a[0] ** (365 / days) - 1
        print(f"{f:4.2f} {X:3d} | {a[0]:6.2f}/{b[0]:6.2f}  {a[1]:6.1f}  (annual {cagr*100:5.0f}%) | {c[0]:5.2f} | {a[2]:3d} {a[3]:2d}")

# Grid search: choose (f, X) on Nov-May only, then score the choice on Jun-Oct.
# Criterion fixed in advance: highest end multiplier with max drawdown <= 15%
# (the user's loss limit), unknown continuations scored as "worst".
tr_m = (o.d < "2026-06-01").values
grid = [(round(f, 2), X) for f in np.arange(0.20, 1.001, 0.05) for X in range(5, 26)]
rows = []
for f, X in grid:
    a = run(tr_m, f, X, "worst"); b = run(late, f, X, "worst"); c = run(allm, f, X, "worst")
    rows.append(dict(f=f, X=X, train_x=a[0], train_dd=a[1], test_x=b[0], test_dd=b[1], all_x=c[0], all_dd=c[1]))
g = pd.DataFrame(rows)
ok = g[g.train_dd >= -15]
print(f"\ngrid {len(g)} combos; {len(ok)} keep train max DD within 15%")
print("chosen on train:"); print(ok.nlargest(1, "train_x").round(2).to_string(index=False))
print("top 5 on train (for stability):"); print(ok.nlargest(5, "train_x").round(2).to_string(index=False))
print("combos with ALL-period DD <= 15% (in-sample, for reference):", (g.all_dd >= -15).sum())
print(g[g.all_dd >= -15].nlargest(5, "all_x").round(2).to_string(index=False))
