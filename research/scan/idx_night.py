"""Scan round 8 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 evening): US index 'overnight' premium without swap.
O1 = long an equal-weight basket of USTECH, US500, US30 from the open of server bar 02 (amended: 01 does not exist) to the close of bar 15 (14 in DST-mismatch
weeks). The basket is the hypothesis; single indices are descriptive. Usage: python research/scan/idx_night.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
from scan2 import mismatch
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"

def window(h, tc, a=3, b=15):   # amended twice before results: index CFDs open at bar 03 (02 in DST-mismatch weeks)
    out = {}
    for d, x in h.groupby(h.index.normalize()):
        if d.dayofweek >= 5: continue
        k = 1 if mismatch(d) else 0; e = b - k; a0 = a - k
        x = x.set_index(x.index.hour)
        if a0 not in x.index or e not in x.index: continue
        out[d] = x.loc[e, "close"] / x.loc[a0, "open"] - 1 - 2 * tc
    return pd.Series(out)

if __name__ == "__main__":
    span = ("2000", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    print(f"===== round 8 US index night window {PER} {span}")
    S = {}
    for s in ("USTECHCash", "US500Cash", "US30Cash"):
        h = load(s); tc = tcost(s, h); raw = window(h, tc); S[s] = scale(raw)
        y = raw.loc[span[0]:span[1]]
        rep(S[s].loc[span[0]:span[1]], f"  {s}"); print(f"      raw mean {y.mean() * 1e4:.2f} bp/day net, hit {(y > 0).mean() * 100:.0f}%, tc {tc * 1e4:.2f} bp/side")
    b = scale(pd.DataFrame(S).fillna(0).mean(axis=1)); b.to_csv("data/derived/scan/R8_O1_daily.csv", header=["ret"])
    print("--- BASKET (the hypothesis)"); rep(b.loc[span[0]:span[1]], "O1 BASKET")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    s1 = pd.read_csv("data/derived/scan/R7_S1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([b, i2, c1, s1], axis=1, keys=["O1", "I2", "C1", "S1"]).loc[span[0]:span[1]]
    j = j[j.index.dayofweek < 5].dropna(subset=["O1"]).fillna(0)
    print("corr:", j.corr().round(2).loc["O1"].to_dict())
