"""Scan round 7 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 evening): gold session seasonality, flat every day, no swap.
S1 = long from the open of server bar 01 to the close of bar 09 (Asia). S2 = short from the open of bar 16 to the close of bar 22
(15 / 21 in US-EU DST-mismatch weeks; NY). Cost 0.005% per side. Usage: python research/scan/gold_session.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
from scan2 import mismatch
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
TC = 0.00005

def session(h, a, b, side, dst):
    out = {}
    for d, x in h.groupby(h.index.normalize()):
        if d.dayofweek >= 5: continue
        k = -1 if (dst and mismatch(d)) else 0
        x = x.set_index(x.index.hour)
        if a + k not in x.index or b + k not in x.index: continue
        out[d] = side * (x.loc[b + k, "close"] / x.loc[a + k, "open"] - 1) - 2 * TC
    return pd.Series(out)

if __name__ == "__main__":
    span = ("2015-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    h = pd.read_csv("data/derived/intraday/XAUUSD_H1.csv"); h.index = pd.to_datetime(h.time, unit="s")
    h = h[~h.index.duplicated()]; h = h[(h.close > 0) & (h.open > 0)]
    print(f"===== round 7 gold sessions {PER} {span}")
    S = {}
    for nm, a, b, side, dst in (("S1 Asia long", 1, 9, 1, False), ("S2 NY short", 16, 22, -1, True)):
        raw = session(h, a, b, side, dst); S[nm[:2]] = x = scale(raw)
        x.to_csv(f"data/derived/scan/R7_{nm[:2]}_daily.csv", header=["ret"]); rep(x.loc[span[0]:span[1]], nm)
        y = raw.loc[span[0]:span[1]]; print(f"    raw mean {y.mean() * 1e4:.2f} bp/day net, hit {(y > 0).mean() * 100:.0f}%, days {len(y)}")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([S["S1"], S["S2"], i2, c1], axis=1, keys=["S1", "S2", "I2", "C1"]).loc[span[0]:span[1]]
    j = j[j.index.dayofweek < 5].dropna(subset=["S1", "S2"]).fillna(0)
    print("corr:\n", j.corr().round(2).loc[["S1", "S2"], ["I2", "C1", "S1", "S2"]])
