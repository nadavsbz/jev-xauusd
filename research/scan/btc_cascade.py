"""Scan round 21 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 night): fade extreme hourly BTC moves (liquidation cascades).
sigma = std of the previous 720 hourly close-to-close returns; r < -3 sigma -> long, r > +3 sigma -> short, entry at the next bar's
open, exit at the close of the 6th bar from entry; no overlapping trades. Cost 0.025%/side, swap 4.75%/yr pro rata.
Usage: python research/scan/btc_cascade.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
TC, SW, K, HOLD = 0.00025, 0.0475, 3.0, 6

if __name__ == "__main__":
    span = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    h = load("BTCUSD"); r = h.close.pct_change(); sig = r.rolling(720, min_periods=500).std().shift(1)
    o, c, t = h.open.values, h.close.values, h.index
    trades = []; i = 721
    while i < len(h) - HOLD - 1:
        if np.isfinite(sig.iloc[i]) and abs(r.iloc[i]) > K * sig.iloc[i]:
            q = -np.sign(r.iloc[i]); e, x = i + 1, i + HOLD
            hrs = (t[x] - t[e]).total_seconds() / 3600
            if hrs <= HOLD + 2:                                    # skip if the 6 bars straddle a data gap
                ret = q * (c[x] / o[e] - 1) - 2 * TC - SW * hrs / 24 / 365
                trades.append((t[x].normalize(), q, ret)); i = x + 1; continue
        i += 1
    T = pd.DataFrame(trades, columns=["day", "q", "ret"])
    daily = T.groupby("day").ret.sum(); full = pd.Series(0.0, index=pd.date_range(daily.index[0], daily.index[-1])); full.loc[daily.index] = daily
    x = scale(full); x.to_csv("data/derived/scan/R21_cascade_daily.csv", header=["ret"])
    print(f"===== round 21 BTC cascade fade {PER} {span}")
    rep(x.loc[span[0]:span[1]], "CASCADE fade")
    Tp = T[(T.day >= span[0]) & (T.day <= span[1])]
    for nm, g in (("all", Tp), ("long after drop", Tp[Tp.q > 0]), ("short after pump", Tp[Tp.q < 0])):
        print(f"    {nm:17s} n {len(g):4d} mean {g.ret.mean() * 1e4:6.1f} bp hit {(g.ret > 0).mean() * 100:3.0f}%")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([x, i2, c1], axis=1, keys=["X", "I2", "C1"]).loc[span[0]:span[1]].dropna(subset=["X"]).fillna(0)
    print("    corr:", j.corr().round(2).loc["X"].to_dict())
