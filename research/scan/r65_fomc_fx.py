"""Round 65 (prereg docs/prereg/r65_fomc_fx.md, commit 601c47e): short USD vs 7 G10 on scheduled FOMC decision days, 00:00-00:00 ET.
Usage: py -3.12 research/scan/r65_fomc_fx.py [dev|test]"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/stable")
from scan import tcost, E
from scan2 import mismatch
from r64_mass import loadh
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
SPAN = ("2010-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-12-31")
LEGS = {"EURUSD": 1, "GBPUSD": 1, "AUDUSD": 1, "NZDUSD": 1, "USDJPY": -1, "USDCHF": -1, "USDCAD": -1}
OLD = """2010-01-27 2010-03-16 2010-04-28 2010-06-23 2010-08-10 2010-09-21 2010-11-03 2010-12-14 2011-01-26 2011-03-15 2011-04-27 2011-06-22
2011-08-09 2011-09-21 2011-11-02 2011-12-13 2012-01-25 2012-03-13 2012-04-25 2012-06-20 2012-08-01 2012-09-13 2012-10-24 2012-12-12 2013-01-30
2013-03-20 2013-05-01 2013-06-19 2013-07-31 2013-09-18 2013-10-30 2013-12-18 2014-01-29 2014-03-19 2014-04-30 2014-06-18 2014-07-30 2014-09-17
2014-10-29 2014-12-17 2015-01-28 2015-03-18 2015-04-29 2015-06-17 2015-07-29 2015-09-17 2015-10-28 2015-12-16 2016-01-27 2016-03-16 2016-04-27
2016-06-15 2016-07-27 2016-09-21 2016-11-02 2016-12-14 2017-02-01 2017-03-15 2017-05-03 2017-06-14 2017-07-26 2017-09-20 2017-11-01 2017-12-13
2018-01-31 2018-03-21 2018-05-02 2018-06-13 2018-08-01 2018-09-26 2018-11-08""".split()
cal = pd.read_csv("data/derived/news/mt5_calendar_usd.csv")
e = pd.to_datetime(cal[cal.event == "Fed Interest Rate Decision"].time, unit="s").dt.tz_localize("UTC").dt.tz_convert("America/New_York")
NEW = e[(e.dt.hour >= 13) & (e.dt.hour < 15)].dt.tz_localize(None).dt.normalize()
EV = sorted(set(pd.to_datetime(OLD)) | set(NEW))

rows = {}
for s, d in LEGS.items():
    h = loadh(s); tc = tcost(s, h); pt = E.loc[s, "point"]
    sw = (E.loc[s, "swap_long"] if d > 0 else E.loc[s, "swap_short"]) * pt
    vol = h.close.resample("1D").last().dropna().pct_change().rolling(60).std().shift(1)
    for D in EV:
        a = D + pd.Timedelta(hours=6 if mismatch(D) else 7); n = D + pd.Timedelta(days=1); b = n + pd.Timedelta(hours=6 if mismatch(n) else 7)
        if a not in h.index or b not in h.index: continue
        pa, pb = h.open[a], h.open[b]
        c_in = max(tc, h.spread[a] * pt / pa); c_out = max(tc, h.spread[b] * pt / pb)
        nights = 3 if D.dayofweek == 2 else 1
        g = d * (pb / pa - 1); swp = sw / pa * nights
        v = vol.asof(D)
        rows[(D, s)] = dict(g=g, cost=c_in + c_out, sw=swp, net=g - c_in - c_out + swp, iv=1 / v if v and np.isfinite(v) else np.nan)
X = pd.DataFrame(rows).T; X.index.names = ["d", "s"]; X = X.astype(float)
X["w"] = X.iv / X.groupby(level="d").iv.transform("sum")
B = X.groupby(level="d").apply(lambda z: pd.Series({k: (z[k] * z.w).sum() for k in ("g", "cost", "sw", "net")}))
B = B[SPAN[0]:SPAN[1]]; n = len(B)
t = B.net.mean() / B.net.std() * np.sqrt(n)
full = pd.Series(0.0, index=pd.bdate_range(SPAN[0], min(pd.Timestamp(SPAN[1]), B.index[-1]))); full.loc[B.index] = B.net.values
sh = full.mean() / full.std() * np.sqrt(252); y = B.net.groupby(B.index.year).sum()
print(f"== {PER} {SPAN} events {n}  legs/event {X.groupby(level='d').size().mean():.1f}")
print(f"basket net {B.net.mean()*1e4:.2f} bp (gross {B.g.mean()*1e4:.2f}, cost {B.cost.mean()*1e4:.2f}, swap {B.sw.mean()*1e4:.2f})  t {t:.2f}  hit {(B.net>0).mean():.2f}")
print(f"Sharpe {sh:.2f}  pos years {int((y>0).sum())}/{len(y)} |", " ".join(f"{a%100:02d}:{v*1e4:+.0f}" for a, v in y.items()), "bp")
print("per leg net bp:", X[SPAN[0]:SPAN[1]].net.groupby(level="s").mean().mul(1e4).round(1).to_dict() if False else
      X.loc[(X.index.get_level_values(0) >= SPAN[0]) & (X.index.get_level_values(0) <= SPAN[1])].net.groupby(level="s").mean().mul(1e4).round(1).to_dict())
r35 = pd.read_csv("data/derived/scan/R35_prefomc_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
C1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change()
from book_tester import i2_daily
for nm, o in [("r35", r35), ("C1", C1), ("I2", i2_daily())]:
    j = pd.concat([full, o], axis=1).dropna(); print(f"corr {nm}: {j.corr().iloc[0,1]:.2f} (n={len(j)})")
