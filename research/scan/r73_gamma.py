"""Round 73 (prereg docs/prereg/r73_gamma_regime_intraday.md, commit bdc183f): US500 afternoon momentum in low-GEX quintile,
reversal in high-GEX quintile (GEX of t-1 vs prior 250 days). Usage: py -3.12 research/scan/r73_gamma.py dev|test"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/stable")
import r66_structural as R
from scan import tcost, E
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
R.PER = PER; R.SPAN = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-12-31")
g = pd.read_csv("data/derived/macro/dix_gex.csv", parse_dates=["date"]).set_index("date").gex
q20 = g.rolling(250, min_periods=200).quantile(0.2).shift(1); q80 = g.rolling(250, min_periods=200).quantile(0.8).shift(1)
reg = pd.Series(np.where(g < q20, -1, np.where(g > q80, 1, 0)), index=g.index)     # regime of day t-1 -> applies to the next trading day
m = pd.read_csv("data/derived/scan/m5/US500Cash.csv"); m.index = pd.to_datetime(m.time, unit="s"); m = m[~m.index.duplicated()]
tc = tcost("US500Cash", m.resample("1h").last().dropna()); pt = E.loc[".US500Cash", "point"]
rows = {"both": [], "low": [], "high": []}
gd = reg.index
for d in sorted(set(m.index.normalize())):
    if d.dayofweek > 4: continue
    k = gd.searchsorted(d) - 1
    if k < 0: continue
    rg = reg.iloc[k]
    if rg == 0: continue
    o, a, b = R.et2srv(d, 9, 30), R.et2srv(d, 14, 35), R.et2srv(d, 15, 55)
    if not all(t in m.index for t in (o, a, b)): continue
    sgn = np.sign(m.open[a] / m.open[o] - 1) * (1 if rg < 0 else -1)
    if sgn == 0: continue
    c = max(tc, m.spread[a] * pt / m.open[a]) + max(tc, m.spread[b] * pt / m.open[b])
    r = (d, sgn * (m.open[b] / m.open[a] - 1) - c, c)
    rows["both"].append(r); rows["low" if rg < 0 else "high"].append(r)
print(f"===== {PER} {R.SPAN}")
for k, nm in [("both", "r73 GEX regime (combined)"), ("low", "low-GEX momentum (desc)"), ("high", "high-GEX reversal (desc)")]:
    R.report(pd.DataFrame(rows[k], columns=["d", "net", "cost"]).set_index("d"), nm)
