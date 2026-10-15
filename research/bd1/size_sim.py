import numpy as np, pandas as pd
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
    eq = np.cumprod(1 + r); dd = (eq / np.maximum.accumulate(eq) - 1).min() * 100
    return eq[-1], dd, hit.sum(), unk.sum()
allm = np.ones(len(o), bool); late = (o.d >= "2026-06-01").values
print("f   X  | all: x_end worst/best  maxDD worst | Jun-Oct x_end worst | cuts unk")
for f in [1.0, 0.75, 0.5, 0.35, 0.25]:
    for X in [10, 15, 100]:
        a = run(allm, f, X, "worst"); b = run(allm, f, X, "best"); c = run(late, f, X, "worst")
        cagr = a[0] ** (365 / days) - 1
        print(f"{f:4.2f} {X:3d} | {a[0]:6.2f}/{b[0]:6.2f}  {a[1]:6.1f}  (annual {cagr*100:5.0f}%) | {c[0]:5.2f} | {a[2]:3d} {a[3]:2d}")
