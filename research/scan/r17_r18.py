"""Scan rounds 17 and 18 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 night).
R17 = C1 long-only Donchian ensemble on H6 for USTECH/US500/US30, swap -8.6%/yr while long, cost 0.005%/side.
R18 = BTC weekend return (Fri bar 22 close -> Mon bar 00 close) -> USTECH Monday session in its sign (bar 03 open -> bar 22 close,
02/21 in DST-mismatch weeks), cost = yearly median spread + 0.0015%. Usage: python research/scan/r17_r18.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, donch, E
from scan2 import mismatch
from last_half import m5
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"

def long_trend(h, tc, sw_l):
    c = h.close.resample("6h").last().dropna(); r = c.pct_change().fillna(0)
    w = donch(c, True).shift(2).fillna(0)
    dt = c.index.to_series().diff().dt.total_seconds().fillna(0) / 86400 / 365
    net = w * r - w.diff().abs().fillna(0) * tc + w * sw_l * dt / 100
    return (1 + net).groupby(net.index.normalize()).prod() - 1

def corr_line(x, span):
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([x, i2, c1], axis=1, keys=["X", "I2", "C1"]).loc[span[0]:span[1]]
    j = j[j.index.dayofweek < 5].dropna(subset=["X"]).fillna(0)
    return j.corr().round(2).loc["X"].to_dict()

if __name__ == "__main__":
    span = ("2000", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    print(f"===== round 17 long-only index trend {PER} {span}")
    S = {s: scale(long_trend(load(s), 0.00005, -8.6)) for s in ("USTECHCash", "US500Cash", "US30Cash")}
    for s, x in S.items(): rep(x.loc[span[0]:span[1]], f"  {s}")
    b = scale(pd.DataFrame(S).fillna(0).mean(axis=1)); b.to_csv("data/derived/scan/R17_idxtrend_daily.csv", header=["ret"])
    rep(b.loc[span[0]:span[1]], "R17 BASKET"); print("    corr:", corr_line(b, span))

    print(f"===== round 18 BTC weekend -> USTECH Monday {PER} {span}")
    btc = load("BTCUSD"); nq = m5("USTECHCash")
    xs = nq[(nq.index.hour >= 16) & (nq.index.hour <= 22)]
    cost = (xs.spread * 0.1 / xs.close).groupby(xs.index.year).median() + 0.000015
    out = {}
    for d in pd.date_range("2018-01-01", nq.index[-1].normalize(), freq="W-MON"):
        f, m0 = d - pd.Timedelta(days=3) + pd.Timedelta(hours=22), d
        if f not in btc.index or m0 not in btc.index: continue
        q = np.sign(btc.loc[m0, "close"] / btc.loc[f, "close"] - 1)
        k = 1 if mismatch(d) else 0; a, z = d + pd.Timedelta(hours=3 - k), d + pd.Timedelta(hours=22 - k, minutes=55)
        y = nq[(nq.index >= a) & (nq.index <= z)]
        if len(y) < 100 or y.index[0] != a: continue
        out[d] = q * (y.close.iloc[-1] / y.open.iloc[0] - 1) - 2 * cost.get(d.year, cost.iloc[-1]) * (q != 0)
    raw = pd.Series(out); days = pd.bdate_range(raw.index[0], raw.index[-1])
    full = pd.Series(0.0, index=days); full.loc[raw.index] = raw
    x = scale(full); x.to_csv("data/derived/scan/R18_btcwknd_daily.csv", header=["ret"])
    rep(x.loc[span[0]:span[1]], "R18 BTC->Mon")
    y = raw.loc[span[0]:span[1]]; print(f"    Mondays {len(y)}, mean net {y.mean() * 1e4:.1f} bp, hit {(y > 0).mean() * 100:.0f}%"); print("    corr:", corr_line(x, span))
