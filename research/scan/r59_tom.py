"""Round 59 (docs/prereg/r59_tom_us500.md, a1bbc96): turn-of-month long US500, close of day -2 -> close of day +3.
Usage: py -3.12 research/scan/r59_tom.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import scale, rep, trend, tcost, load, E
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
A, B = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-10-30")
h = load("US500Cash"); tc = tcost("US500Cash", h); SW = -8.6
x = h[h.index.hour <= 22]; c = x.close.groupby(x.index.normalize()).last()
c = c[c.index.isin(h.index[h.index.hour == 22].normalize())]
ret = c.pct_change().fillna(0)
mon = c.index.to_period("M"); pos_in_m = pd.Series(range(len(c)), index=c.index).groupby(mon).rank().astype(int)
n_in_m = pd.Series(1, index=c.index).groupby(mon).transform("sum")
from_end = n_in_m - pos_in_m          # 0 = last day (-1), 1 = day -2
win = ((from_end == 0) | (pos_in_m <= 3)).astype(float)   # days whose return is held: -1, +1, +2, +3
gap = c.index.to_series().diff().dt.days.fillna(1)
net = win * (ret + SW / 100 / 365 * gap)
entry = (win.diff() == 1).astype(float); exit_ = (win.diff() == -1).astype(float)
net = net - (entry.shift(-1).fillna(0) * 0) - entry * tc - exit_.shift(-0) * 0
net = net - (win.shift(1).fillna(0) - win).clip(lower=0) * tc   # exit cost on the day after the last held day
x10 = scale(net); x10.to_csv("data/derived/scan/r59_daily.csv", header=["ret"])
y = x10.loc[A:B]; print(f"===== r59 TOM US500 {PER}"); rep(y, "r59 TOM")
ev = net.groupby((win.diff() == 1).cumsum()).sum()[1:]; evd = net[net != 0].groupby((win.diff() == 1).cumsum()[net != 0]).sum()
k = (win.diff() == 1).cumsum(); idx = k.loc[A:B].unique(); e = net.groupby(k).sum().loc[[i for i in idx if i > 0]]
print(f"events {len(e)}, mean net {e.mean()*1e4:.1f} bp, t {e.mean()/e.std()*np.sqrt(len(e)):.2f}, hit {(e>0).mean()*100:.0f}%")
r = ret.loc[A:B]; w = win.loc[A:B]
print(f"descriptive: mean daily ret in window {r[w==1].mean()*1e4:.1f} bp vs other days {r[w==0].mean()*1e4:.1f} bp")
c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
j = pd.concat([y, c1, i2], axis=1, keys=["X", "C1", "I2"]).loc[A:B].dropna(subset=["X"]).fillna(0)
print("corr", j.corr().round(2).loc["X"].to_dict())
