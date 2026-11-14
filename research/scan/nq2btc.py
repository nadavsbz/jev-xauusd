"""Scan round 14 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 night): delayed Nasdaq -> Bitcoin transmission.
Signal = USTECH open of bar 16 -> close of bar 18 (15 -> 17 in DST-mismatch weeks). Trade BTCUSD in its sign from the open of
bar 19 to the close of bar 22 (18 -> 21). Cost 0.025% per side. Usage: python research/scan/nq2btc.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
from scan2 import mismatch
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
TC = 0.00025

def hourly(h):
    return {d: x.set_index(x.index.hour) for d, x in h.groupby(h.index.normalize()) if d.dayofweek < 5}

if __name__ == "__main__":
    span = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    N, B = hourly(load("USTECHCash")), hourly(load("BTCUSD"))
    out, gross = {}, {}
    for d, n in N.items():
        if d not in B: continue
        k = 1 if mismatch(d) else 0; b = B[d]
        if not all(h in n.index for h in (16 - k, 18 - k)) or not all(h in b.index for h in (19 - k, 22 - k)): continue
        q = np.sign(n.loc[18 - k, "close"] / n.loc[16 - k, "open"] - 1)
        g = q * (b.loc[22 - k, "close"] / b.loc[19 - k, "open"] - 1); gross[d] = g; out[d] = g - 2 * TC * (q != 0)
    raw = pd.Series(out); g = pd.Series(gross)
    x = scale(raw); x.to_csv("data/derived/scan/R14_nq2btc_daily.csv", header=["ret"])
    print(f"===== round 14 NQ -> BTC {PER} {span}")
    rep(x.loc[span[0]:span[1]], "NQ->BTC")
    y, gy = raw.loc[span[0]:span[1]], g.loc[span[0]:span[1]]
    print(f"    days {len(y)}, mean net {y.mean() * 1e4:.2f} bp, gross {gy.mean() * 1e4:.2f} bp, hit {(y > 0).mean() * 100:.0f}%, gross by year {gy.groupby(gy.index.year).mean().mul(1e4).round(1).to_dict()}")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([x, i2, c1], axis=1, keys=["NB", "I2", "C1"]).loc[span[0]:span[1]].dropna(subset=["NB"]).fillna(0)
    print("corr:", j.corr().round(2).loc["NB"].to_dict())
