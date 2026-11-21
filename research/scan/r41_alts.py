"""Scan round 41 of docs/SCAN_PLAN.md (pre-registered 12.11.2026): C1 trend rule on XRP/SOL/DOGE/ADA (Binance 1h, RF Pro has them).
Usage: py -3.12 research/scan/r41_alts.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, trend, rep, E
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
SPAN = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
TC, SW = 0.0025, -20.0

def bn(s):
    h = pd.read_csv(f"data/raw/binance/{s}.csv"); h.index = pd.to_datetime(h.time, unit="s")
    h.index = h.index + pd.Timedelta(hours=2)            # UTC -> approx server (NY+7); H6 grid alignment only
    return h[~h.index.duplicated()]

def sh(x): return x.mean() / x.std() * np.sqrt(252)

if __name__ == "__main__":
    c1 = scale(sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD")))
    chk = scale(trend(bn("BTCUSDT"), tcost("BTCUSD", load("BTCUSD")), E.loc["BTCUSD", "swap_long"], E.loc["BTCUSD", "swap_short"]))
    rf = scale(trend(load("BTCUSD"), tcost("BTCUSD", load("BTCUSD")), E.loc["BTCUSD", "swap_long"], E.loc["BTCUSD", "swap_short"]))
    j = pd.concat([chk, rf], axis=1).loc[SPAN[0]:SPAN[1]].dropna()
    print(f"sanity: C1-BTC on Binance vs RF data: corr {j.corr().iloc[0, 1]:.2f}, Sh {sh(j.iloc[:, 0]):.2f} vs {sh(j.iloc[:, 1]):.2f}")
    alts = {s: scale(trend(bn(s + "USDT"), TC, SW, SW)) for s in ("XRP", "SOL", "DOGE", "ADA")}
    df = pd.DataFrame(alts)
    for s in alts: rep(df[s].loc[SPAN[0]:SPAN[1]].dropna(), f"  {s} (descr)")
    bask = scale(df.mean(axis=1, skipna=True).fillna(0))
    ext = scale(pd.concat([c1, bask], axis=1).fillna(0).mean(axis=1))
    b, c, e = (x.loc[SPAN[0]:SPAN[1]] for x in (bask, c1, ext))
    rep(b, "ALT BASKET"); rep(c, "C1 (BTC+ETH)"); rep(e, "C1 extended")
    print(f"corr basket vs C1: {pd.concat([b, c], axis=1).corr().iloc[0, 1]:.2f}")
    yrs = (b[b.index.dayofweek < 5].groupby(b.index.year[b.index.dayofweek < 5]).sum() > 0)
    gA = sh(b[b.index.dayofweek < 5]) >= (0.8 if PER == "dev" else 0.5) and yrs.mean() >= 0.7
    gB = sh(e[e.index.dayofweek < 5]) - sh(c[c.index.dayofweek < 5]) >= 0.15
    print(f"gate A (basket) {gA} | gate B (extended - C1 >= 0.15) {gB}  ->  {'PASS' if gA and gB else 'FAIL'}")
