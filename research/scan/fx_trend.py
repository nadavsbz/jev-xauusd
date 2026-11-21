"""Scan round 10 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 evening): the C1 rule (scan.trend) on an FX basket.
Swap points from ecn_costs converted to % per year as points x point x 365 / price. Basket = hypothesis; pairs descriptive.
Usage: python research/scan/fx_trend.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
PAIRS = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD", "EURJPY")

def swap_pct(s, px):
    r = E.loc[s]; return r.swap_long * r.point * 365 / px * 100, r.swap_short * r.point * 365 / px * 100

if __name__ == "__main__":
    span = ("2000", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    print(f"===== round 10 FX trend (C1 rule) {PER} {span}")
    S = {}
    for s in PAIRS:
        try: h = load(s)
        except FileNotFoundError: print(f"  {s} missing"); continue
        sl, ss = swap_pct(s, h.close.iloc[-1]); tc = tcost(s, h)
        S[s] = x = scale(trend(h, tc, sl, ss))
        rep(x.loc[span[0]:span[1]], f"  {s}"); print(f"      from {h.index[0]:%Y-%m}, swap %/yr L {sl:+.2f} S {ss:+.2f}, tc {tc * 1e4:.2f} bp")
    b = scale(pd.DataFrame(S).fillna(0).mean(axis=1)); b.to_csv("data/derived/scan/R10_fx_daily.csv", header=["ret"])
    print(f"--- BASKET ({len(S)} pairs, the hypothesis)"); rep(b.loc[span[0]:span[1]], "FX BASKET")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([b, i2, c1], axis=1, keys=["FX", "I2", "C1"]).loc[span[0]:span[1]]
    j = j[j.index.dayofweek < 5].dropna(subset=["FX"]).fillna(0)
    print("corr:", j.corr().round(2).loc["FX"].to_dict())
