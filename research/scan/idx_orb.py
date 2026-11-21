"""Scan round 5 of docs/SCAN_PLAN.md (pre-registered 11.11.2026): opening-range breakout on DE40, US500, US30, JP225.
Range = first local-cash H1 bar, entries at closes of the next 4 bars, SL = opposite side, flat at the last bar before the close.
The hypothesis is the equal-weight basket; single indices are descriptive. Usage: python research/scan/idx_orb.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
from scan2 import mismatch, sunday
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
COMM = 0.00005

def eu_dst(d):
    return sunday(d.year, 3, 0, True) <= d < sunday(d.year, 10, 0, True)

def hours(s, d):
    """(range bar, entry bars, exit bar) in server time for day d"""
    if s == "DE40Cash": return 10, [11, 12, 13, 14], 17
    if s in ("US500Cash", "US30Cash"):
        k = -1 if mismatch(d) else 0; return 16 + k, [17 + k, 18 + k, 19 + k, 20 + k], 22 + k
    k = 2 + (1 if eu_dst(d) else 0)                     # JP225: 00:00 UTC; server = UTC+2 / +3
    return k, [k + 1, k + 2, k + 3, k + 4], k + 5

def orb(s, h, tc):
    out = {}
    for d, x in h.groupby(h.index.normalize()):
        if d.dayofweek >= 5: continue
        x = x.set_index(x.index.hour); rb, eh, ex = hours(s, d)
        if not all(k in x.index for k in [rb] + eh + [ex]): continue
        hi, lo = x.loc[rb, "high"], x.loc[rb, "low"]
        q = 0; r = 0.0
        for k in eh + [ex]:
            if q == 0:
                if k == ex: break
                c = x.loc[k, "close"]
                if c > hi: q, entry, sl = 1, c, lo
                elif c < lo: q, entry, sl = -1, c, hi
                if q: r -= tc
                continue
            b = x.loc[k]
            if (q == 1 and b.low <= sl) or (q == -1 and b.high >= sl):
                px = min(sl, b.open) if q == 1 else max(sl, b.open)
                r += q * (px / entry - 1) - tc; q = 0; break
            if k == ex: r += q * (b.close / entry - 1) - tc; q = 0; break
        out[d] = r
    return pd.Series(out)

if __name__ == "__main__":
    span = ("2000", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    print(f"===== round 5 index ORB {PER} {span}")
    S = {}
    for s in ("DE40Cash", "US500Cash", "US30Cash", "JP225Cash"):
        h = load(s); tc = tcost(s, h) if s != "DE40Cash" else max(0.000008, 0.0001) + COMM
        raw = orb(s, h, tc); S[s] = scale(raw)
        y = raw.loc[span[0]:span[1]]; t = y[y != 0]
        rep(S[s].loc[span[0]:span[1]], f"  {s}"); print(f"      trades {len(t)}/{len(y)}, mean {t.mean() * 1e4:.1f} bp, hit {(t > 0).mean() * 100:.0f}%, tc {tc * 1e4:.2f} bp")
    df = pd.DataFrame(S).fillna(0); b = scale(df.mean(axis=1)); b.to_csv("data/derived/scan/R5_basket_daily.csv", header=["ret"])
    print("--- BASKET (the hypothesis)"); rep(b.loc[span[0]:span[1]], "R5 BASKET")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([b, i2, c1], axis=1, keys=["R5", "I2", "C1"]).loc[span[0]:span[1]].dropna()
    j = j[j.index.dayofweek < 5]
    print("corr:", j.corr().round(2).loc["R5"].to_dict(), f"(n={len(j)})")
