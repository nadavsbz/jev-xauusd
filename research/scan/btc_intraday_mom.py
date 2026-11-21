"""Scan round 20 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 night): BTC intraday momentum (Wen, Bouri, Xu & Zhao 2022).
UTC day: signal = M5 open 00:00 -> close of the 00:25 bar; trade in its sign from the open of 23:30 to the close of 23:55 UTC.
Server = UTC+2 (UTC+3 in EU summer). Cost 0.025% per side. Usage: python research/scan/btc_intraday_mom.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
from scan2 import sunday
from last_half import m5
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
TC = 0.00025

def off(t):     # server - UTC in hours at UTC time t
    return 3 if sunday(t.year, 3, 0, True) + pd.Timedelta(hours=1) <= t < sunday(t.year, 10, 0, True) + pd.Timedelta(hours=1) else 2

if __name__ == "__main__":
    span = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    m = m5("BTCUSD"); idx = set(m.index)
    out, gross = {}, {}
    for u in pd.date_range("2018-01-01", m.index[-1].normalize() - pd.Timedelta(days=1)):
        o = off(u); s = lambda h, mi: u + pd.Timedelta(hours=h + o, minutes=mi)
        a, b, c, d = s(0, 0), s(0, 25), s(23, 30), s(23, 55)
        if not all(t in idx for t in (a, b, c, d)): continue
        q = np.sign(m.loc[b, "close"] / m.loc[a, "open"] - 1)
        g = q * (m.loc[d, "close"] / m.loc[c, "open"] - 1); gross[u] = g; out[u] = g - 2 * TC * (q != 0)
    raw, g = pd.Series(out), pd.Series(gross)
    x = scale(raw); x.to_csv("data/derived/scan/R20_btcmom_daily.csv", header=["ret"])
    print(f"===== round 20 BTC intraday momentum {PER} {span}")
    rep(x.loc[span[0]:span[1]], "BTC first->last half")
    y, gy = raw.loc[span[0]:span[1]], g.loc[span[0]:span[1]]
    print(f"    days {len(y)}, mean net {y.mean() * 1e4:.2f} bp, gross {gy.mean() * 1e4:.2f} bp, hit {(y > 0).mean() * 100:.0f}%, gross by year {gy.groupby(gy.index.year).mean().mul(1e4).round(1).to_dict()}")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([x, i2, c1], axis=1, keys=["B", "I2", "C1"]).loc[span[0]:span[1]].dropna(subset=["B"]).fillna(0)
    print("    corr:", j.corr().round(2).loc["B"].to_dict())
