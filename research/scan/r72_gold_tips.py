"""Round 72 (prereg docs/prereg/r72_gold_tips_dxy.md, commit 5237d70): weekly gold by 10y TIPS + DXY surprise.
Usage: py -3.12 research/scan/r72_gold_tips.py dev|test"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/stable")
import r66_structural as R
from scan import tcost
from r64_mass import loadh, swaps
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
R.PER = PER; R.SPAN = ("2015-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-12-31")
h = loadh("XAUUSD"); tc = tcost("XAUUSD", h); sl, ss = swaps("XAUUSD", float(h.close.iloc[-1]))
tips = pd.read_csv("data/derived/macro/tips10.csv", index_col=0, parse_dates=True).iloc[:, 0]
dxy = pd.read_csv("data/derived/macro/dxy.csv", index_col=0, parse_dates=True).iloc[:, 0]
wk = lambda s: s.groupby(s.index.to_period("W-SUN")).last()
dT, dD = wk(tips).diff(), wk(dxy).diff().reindex(wk(tips).index)
sig = pd.Series(np.where((dT >= 0.15) & (dD > 0), -1, np.where((dT <= -0.15) & (dD < 0), 1, 0)), index=dT.index)
hw = h.index.to_period("W-SUN"); rows = []; daily = pd.Series(0.0, index=pd.bdate_range("2015-01-01", "2026-12-31"))
dc = h.close.resample("1D").last().dropna()
for wper, s in sig.items():
    if s == 0: continue
    nxt = wper + 1; bars = h[hw == nxt]
    if len(bars) < 20: continue
    a, b = bars.index[0], bars.index[-1]; po, pc = bars.open.iloc[0], bars.close.iloc[-1]
    sw = (sl if s > 0 else ss) * 6 / 365
    rows.append((b.normalize(), s * (pc / po - 1) - 2 * tc + sw, 2 * tc - min(sw, 0)))
    days = dc[(dc.index >= a.normalize()) & (dc.index <= b.normalize())]
    prev = po
    for dd, cl in days.items():
        if dd in daily.index: daily[dd] += s * (cl / prev - 1)
        prev = cl
    if days.index[0] in daily.index: daily[days.index[0]] -= tc
    if days.index[-1] in daily.index: daily[days.index[-1]] -= tc - sw
T = pd.DataFrame(rows, columns=["d", "net", "cost"]).set_index("d")
print(f"===== {PER} {R.SPAN}  long {(sig[sig != 0] > 0).sum()} short {(sig[sig != 0] < 0).sum()} (all years)")
R.report(T, "r72 gold TIPS+DXY weekly", daily=daily)
