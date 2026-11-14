"""Scan round 9 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 evening): the gotobi effect in USDJPY.
Gotobi day = 5/10/15/20/25/last of the month, moved back to Friday when it falls on a weekend (Japanese holidays ignored).
Long USDJPY from the open of server bar 23 on the eve of the gotobi day to the close of the bar that ends at 01:00 UTC
(server bar 02 in winter, 03 in EU summer), cost 0.005% per side, swap ignored (positive for longs).
Usage: python research/scan/gotobi.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
from scan2 import sunday
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
TC = 0.00005

def eu_dst(d):
    return sunday(d.year, 3, 0, True) <= d < sunday(d.year, 10, 0, True)

def gotobi_days(start, end):
    out = set()
    for m in pd.date_range(start, end, freq="MS"):
        last = (m + pd.offsets.MonthEnd(0)).day
        for dd in (5, 10, 15, 20, 25, last):
            t = pd.Timestamp(m.year, m.month, dd)
            while t.dayofweek >= 5: t -= pd.Timedelta(days=1)
            out.add(t)
    return out

def trade(h, day):
    """return of the eve-23:00 -> 01:00 UTC window ending on 'day' (server-time index), or None"""
    prev = day - pd.Timedelta(days=1)
    while prev.dayofweek >= 5: prev -= pd.Timedelta(days=1)     # Monday's eve is Friday 23:00 (market closed: skip below)
    a = prev + pd.Timedelta(hours=23); b = day + pd.Timedelta(hours=3 if eu_dst(day) else 2)
    if a not in h.index or b not in h.index or (day - prev).days > 1: return None
    return h.loc[b, "close"] / h.loc[a, "open"] - 1 - 2 * TC

if __name__ == "__main__":
    span = ("2018-10-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    h = pd.read_csv("data/derived/intraday/USDJPY_H1_demo.csv"); h.index = pd.to_datetime(h.time, unit="s")
    h = h[~h.index.duplicated()]; h = h[(h.close > 0) & (h.open > 0)]
    days = pd.bdate_range(h.index[0].normalize() + pd.Timedelta(days=2), h.index[-1].normalize())
    G = gotobi_days(days[0], days[-1])
    g, n = {}, {}
    for d in days:
        r = trade(h, d)
        if r is None: continue
        (g if d in G else n)[d] = r
    g = pd.Series(g); n = pd.Series(n)
    full = pd.Series(0.0, index=days); full.loc[g.index] = g
    x = scale(full); x.to_csv("data/derived/scan/R9_gotobi_daily.csv", header=["ret"])
    print(f"===== round 9 gotobi USDJPY {PER} {span}")
    rep(x.loc[span[0]:span[1]], "GOTOBI long")
    gy, ny = g.loc[span[0]:span[1]], n.loc[span[0]:span[1]]
    print(f"    gotobi trades {len(gy)}, mean net {gy.mean() * 1e4:.2f} bp, hit {(gy > 0).mean() * 100:.0f}%  | "
          f"same window non-gotobi (descriptive) {len(ny)} days, mean {ny.mean() * 1e4:.2f} bp")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([x, i2, c1], axis=1, keys=["G", "I2", "C1"]).loc[span[0]:span[1]].dropna(subset=["G"]).fillna(0)
    print("corr:", j.corr().round(2).loc["G"].to_dict())
