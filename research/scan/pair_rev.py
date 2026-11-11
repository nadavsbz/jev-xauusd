"""Scan round 12 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 evening): daily reversal of the USTECH/US30 session spread.
Signal = yesterday's session return (open of bar 16 -> close of bar 22, 15/21 in DST-mismatch weeks) of USTECH minus US30.
Today: short the outperformer, long the other, equal notional, open of bar 16 -> close of bar 22. 0.015% per side per leg.
Usage: python research/scan/pair_rev.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
from scan2 import mismatch
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
TC = 0.00015

def session(h):
    out = {}
    for d, x in h.groupby(h.index.normalize()):
        if d.dayofweek >= 5: continue
        k = 1 if mismatch(d) else 0; x = x.set_index(x.index.hour)
        if 16 - k in x.index and 22 - k in x.index: out[d] = x.loc[22 - k, "close"] / x.loc[16 - k, "open"] - 1
    return pd.Series(out)

if __name__ == "__main__":
    span = ("2000", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    a, b = session(load("USTECHCash")), session(load("US30Cash"))
    j = pd.concat([a, b], axis=1, keys=["nq", "dj"]).dropna()
    sig = np.sign(j.nq - j.dj).shift(1)
    raw = (-sig * (j.nq - j.dj) - 4 * TC * (sig != 0)).fillna(0)
    x = scale(raw); x.to_csv("data/derived/scan/R12_pair_daily.csv", header=["ret"])
    print(f"===== round 12 NQ/DJ session-spread reversal {PER} {span}")
    rep(x.loc[span[0]:span[1]], "PAIR reversal")
    y = raw.loc[span[0]:span[1]]; g = (-sig * (j.nq - j.dj)).loc[span[0]:span[1]]
    print(f"    days {int((y != 0).sum())}, mean net {y[y != 0].mean() * 1e4:.2f} bp, gross {g.mean() * 1e4:.2f} bp, hit {(y[y != 0] > 0).mean() * 100:.0f}%")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    k = pd.concat([x, i2, c1], axis=1, keys=["P", "I2", "C1"]).loc[span[0]:span[1]].dropna(subset=["P"]).fillna(0)
    print("corr:", k.corr().round(2).loc["P"].to_dict())
