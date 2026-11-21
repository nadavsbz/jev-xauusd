"""t317 (docs/prereg/research_t317.md): long FX vs USD on FOMC statement days. Usage: py -3.12 research/stable/t317.py dev|holdout"""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/stable")
from t310 import load
px = pd.concat([load(s) for s in ("FXE", "FXB", "FXY", "FXA")], axis=1).dropna()
ret = px.pct_change()
dates = [pd.Timestamp(x) for l in open("research/stable/fomc_dates.txt") if not l.startswith("#") for x in l.split()]
ev = ret.reindex([d for d in dates if d in ret.index]).dropna()
net = ev.mean(axis=1) - 4e-4
lo, hi = ("2007-01-01", "2013-12-31") if sys.argv[1] == "dev" else ("2014-01-01", "2100-01-01")
x = net[lo:hi]
out = dict(events=len(x), mean_bp=round(float(x.mean() * 1e4), 2), t=round(float(x.mean() / x.std() * np.sqrt(len(x))), 2),
           pos=round(float((x > 0).mean()), 2), ann_sharpe=round(float(x.mean() * 8 / (x.std() * np.sqrt(8))), 2),
           per_ccy_bp={c: round(float((ev[c][lo:hi] - 4e-4).mean() * 1e4), 2) for c in ev})
print(json.dumps(out, indent=1))
