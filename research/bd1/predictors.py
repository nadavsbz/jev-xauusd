"""Exploratory: features known before a basket starts vs deep baskets.
Quintile edges are fixed on the selection period (before 2026-06-01) only;
oos_test.py applies them to the test period."""
import numpy as np, pandas as pd
from inputs import load
_, bars = load()
o = pd.read_csv("data/derived/bd1/clusters_strict.csv")
bt = bars.time.values; hi = bars.high.values; lo = bars.low.values; cl = bars.close.values
# hourly true range series for trailing features (only data BEFORE basket start - no look-ahead)
h = bars.assign(hr=bars.time // 3600).groupby("hr").agg(h=("high","max"), l=("low","min"), c=("close","last"))
h["tr"] = np.maximum(h.h, h.c.shift()) - np.minimum(h.l, h.c.shift())
h["atr24"] = h.tr.rolling(24).mean(); h["atr240"] = h.tr.rolling(240).mean()
h["mom24"] = h.c - h.c.shift(24)
hr0 = o.t0 // 3600 - 1                       # last fully closed hour before the basket
f = h.reindex(hr0.values).reset_index(drop=True)
o["atr_ratio"] = (f.atr24 / f.atr240).values      # recent vs longer-term volatility
o["atr24"] = f.atr24.values
o["mom24_atr"] = (f.mom24 / f.atr240).values      # 24h trend strength
d = pd.to_datetime(o.t0, unit="s"); o["hour"] = d.dt.hour; o["wd"] = d.dt.weekday
o["deep"] = o.mae_pct <= -12
big = o[(o.n >= 5) & (pd.to_datetime(o.t0, unit="s") < "2026-06-01")]   # selection period only
print(len(big), "baskets with >=5 levels in Nov-May;", big.deep.sum(), "deep (MAE<=-12%)")
for col in ["atr_ratio", "atr24", "mom24_atr"]:
    q = pd.qcut(big[col], 5, duplicates="drop")
    print(f"\n{col}: deep-rate by quintile"); print(big.groupby(q, observed=True).deep.agg(["sum","size"]).to_string())
print("\nhour:"); print(big.groupby("hour").deep.agg(["sum","size"]).T.to_string())
print("\nweekday:"); print(big.groupby("wd").deep.agg(["sum","size"]).T.to_string())
print("\ndeep baskets:"); print(o[o.deep][["t0","n","mae_pct","pnl_pct","atr_ratio","mom24_atr","hour"]].assign(t0=lambda x: pd.to_datetime(x.t0,unit="s")).round(2).to_string())
o.to_csv("data/derived/bd1/clusters_features.csv", index=False)
