"""Stage 0 of docs/CRASH_DETECT_PLAN.md: what gold did during account 1's baskets.
Per basket: high-low range of XAUUSDc from basket open to the moment of its worst
floating loss (mae_t), in % of the opening price; deep = floating loss of 10% or more."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bd1"))
from inputs import load  # noqa: E402

_, bars = load()
o = pd.read_csv("data/derived/bd1/clusters_strict.csv")
t = bars.time.values; hi = bars.high.values; lo = bars.low.values; op = bars.open.values
i0 = np.maximum(np.searchsorted(t, o.t0.values, side="right") - 1, 0)
i1 = np.searchsorted(t, o.mae_t.values, side="right")   # exclusive end: the slice a:b stops at the bar of the trough
o["p0"] = op[i0]
o["rng_pct"] = [(hi[a:b].max() - lo[a:b].min()) / p * 100 for a, b, p in zip(i0, i1, o.p0)]
o["hrs"] = (o.mae_t - o.t0) / 3600
o["deep"] = o.mae_pct <= -10
for c in ["rng_pct", "hrs", "n"]:
    print(c); print(o.groupby("deep")[c].describe().round(2).to_string())
for x in [0.75, 1, 1.5, 2]:
    s = o[o.rng_pct >= x]; print(f"range >= {x}%: baskets {len(s)}, deep {int(s.deep.sum())}")
print("deep baskets with both sides:", int(o[o.deep].side.eq("B,S").sum()), "of", int(o.deep.sum()))
