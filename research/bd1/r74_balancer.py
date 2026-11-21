"""Round 74 (prereg docs/prereg/r74_bd_gold_trend_balancer.md, commit 2f45c85): BD ms20_h1119 + w x gold long-only Donchian (C1 half).
Usage: py -3.12 research/bd1/r74_balancer.py"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); sys.path.insert(0, "research/stable"); sys.path.insert(0, "research/scan")
from guardian_sim import deals
from r64_mass import loadh
from scan import donch, tcost, scale
out = []
for y in range(2016, 2026):
    tag = "ev18" if y <= 2018 else "ev12"
    x = deals(f"C:/MT5_JEV_TEST/{tag}_rf{y}_ms20_h1119.htm"); x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize()
    pnl = (x.profit + x.swap + x.commission).groupby(x.day).sum()
    idx = pd.bdate_range(f"{y}-01-01", f"{y}-12-31"); pnl = pnl.reindex(idx).fillna(0)
    eq = 120000 + pnl.cumsum(); out.append(pnl / eq.shift(1).fillna(120000))
bd = pd.concat(out)
h = loadh("XAUUSD"); tc = tcost("XAUUSD", h); c = h.close.resample("6h").last().dropna(); r = c.pct_change().fillna(0)
w = donch(c, True).shift(2).fillna(0)
dtt = c.index.to_series().diff().dt.total_seconds().fillna(0) / 86400 / 365
net = w * r - w.diff().abs().fillna(0) * tc + w * (-0.055) * dtt
hd = scale((1 + net).groupby(net.index.normalize()).prod() - 1).reindex(bd.index).fillna(0)
d = h.close.resample("1D").last().dropna()

def yr(x):
    rows = {}
    for y, s in x.groupby(x.index.year):
        eq = (1 + s).cumprod(); rows[y] = ((eq.iloc[-1] - 1) * 100, (eq / eq.cummax() - 1).min() * 100)
    return rows
print("year   BD ret/MDD     hedge ret   " + "   ".join(f"w={w_} ret/MDD" for w_ in (0.5, 1.0)))
Y = {"bd": yr(bd), "h": yr(hd), 0.5: yr(bd + 0.5 * hd), 1.0: yr(bd + 1.0 * hd)}
for y in range(2016, 2026):
    print(f"{y}  {Y['bd'][y][0]:+6.1f}/{Y['bd'][y][1]:6.1f}   {Y['h'][y][0]:+6.1f}      " + "     ".join(f"{Y[w_][y][0]:+6.1f}/{Y[w_][y][1]:6.1f}" for w_ in (0.5, 1.0)))
for k in ("bd", 0.5, 1.0):
    v = Y[k]; pos = sum(v[y][0] > 0 for y in v); pos3 = sum(v[y][0] > 0 for y in (2016, 2017, 2018)); s3 = sum(v[y][0] for y in (2016, 2017, 2018))
    print(f"{str(k):4s} pos {pos}/10  2016-18 pos {pos3}/3 sum {s3:+.1f}  worst-year MDD {min(v[y][1] for y in v):.1f}")
stops = bd[bd < -0.05]
pre = [(hd[(hd.index > t - pd.Timedelta(days=14)) & (hd.index <= t)]).sum() * 100 for t in stops.index]
print("stop days:", [t.date().isoformat() for t in stops.index]); print("hedge sum over the 10 trading days up to each stop (%):", np.round(pre, 2), " mean", round(np.mean(pre), 2))
