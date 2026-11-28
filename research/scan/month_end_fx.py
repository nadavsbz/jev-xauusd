"""Scan round 19 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 night): month-end equity-hedging flows (Melvin & Prins 2015).
Last weekday of each month: signal = US500 from the close of bar 22 on the previous month's last weekday to the close of bar 11
today (server time). Long EURUSD (sell USD) if positive, short if negative, from the open of bar 12 (10:00 London) to the close of
bar 17 (16:00 London fix). Cost 0.007% per side. Usage: python research/scan/month_end_fx.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
TC = 0.00007

if __name__ == "__main__":
    span = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    us, fx = load("US500Cash"), load("EURUSD")
    days = pd.bdate_range("2017-12-01", fx.index[-1].normalize())
    lastd = pd.Series(days, index=days).groupby([days.year, days.month]).max().tolist()
    out = {}
    for p, d in zip(lastd[:-1], lastd[1:]):
        a, b = p + pd.Timedelta(hours=22), d + pd.Timedelta(hours=11)
        i, z = d + pd.Timedelta(hours=12), d + pd.Timedelta(hours=17)
        if not all(t in us.index for t in (a, b)) or not all(t in fx.index for t in (i, z)): continue
        q = np.sign(us.loc[b, "close"] / us.loc[a, "close"] - 1)
        out[d] = q * (fx.loc[z, "close"] / fx.loc[i, "open"] - 1) - 2 * TC * (q != 0)
    ev = pd.Series(out); full = pd.Series(0.0, index=pd.bdate_range(ev.index[0], ev.index[-1])); full.loc[ev.index] = ev
    x = scale(full); x.to_csv("data/derived/scan/R19_monthend_daily.csv", header=["ret"])
    print(f"===== round 19 month-end hedging flows EURUSD {PER} {span}")
    rep(x.loc[span[0]:span[1]], "MONTH-END FX")
    y = ev.loc[span[0]:span[1]]
    print(f"    events {len(y)}, mean net {y.mean() * 1e4:.1f} bp, hit {(y > 0).mean() * 100:.0f}%, t {y.mean() / y.std() * np.sqrt(len(y)):.2f}")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([x, i2, c1], axis=1, keys=["M", "I2", "C1"]).loc[span[0]:span[1]].dropna(subset=["M"]).fillna(0)
    print("    corr:", j.corr().round(2).loc["M"].to_dict())
