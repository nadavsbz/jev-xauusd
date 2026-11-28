"""Scan round 13 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 night): market intraday momentum (Gao, Han, Li & Zhou 2018)
on the US index basket from M5 bars. Signal = close of the 22:55 bar of the previous trading day -> close of today's 16:55 bar
(server time; 21:55 / 15:55 in US/EU DST-mismatch weeks). Position in its sign from the open of the 22:30 bar to the close of
the 22:55 bar (21:30 / 21:55). Cost per side = that year's median spread of the index (NY hours, M5) + 0.0015%.
Usage: python research/scan/last_half.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
from scan2 import mismatch
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
PT = 0.1

def m5(s):
    m = pd.read_csv(f"data/derived/scan/m5/{s}.csv"); m.index = pd.to_datetime(m.time, unit="s")
    return m[~m.index.duplicated()].query("close > 0 and open > 0")

def year_cost(m):
    x = m[(m.index.hour >= 16) & (m.index.hour <= 22)]
    return (x.spread * PT / x.close).groupby(x.index.year).median() + 0.000015

def strat(m):
    tc = year_cost(m); out = {}; prev_close = None
    for d, x in m.groupby(m.index.normalize()):
        if d.dayofweek >= 5: continue
        k = 1 if mismatch(d) else 0
        t_sig, t_in, t_out = (d + pd.Timedelta(hours=16 - k, minutes=55), d + pd.Timedelta(hours=22 - k, minutes=30),
                              d + pd.Timedelta(hours=22 - k, minutes=55))
        if prev_close is not None and all(t in x.index for t in (t_sig, t_in, t_out)):
            q = np.sign(x.loc[t_sig, "close"] / prev_close - 1)
            c = tc.get(d.year, tc.iloc[-1])
            out[d] = q * (x.loc[t_out, "close"] / x.loc[t_in, "open"] - 1) - 2 * c * (q != 0)
        if t_out in x.index: prev_close = x.loc[t_out, "close"]
    return pd.Series(out)

if __name__ == "__main__":
    span = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    print(f"===== round 13 last-half-hour momentum {PER} {span}")
    S = {}
    for s in ("USTECHCash", "US500Cash", "US30Cash"):
        try: m = m5(s)
        except FileNotFoundError: print(f"  {s} missing"); continue
        raw = strat(m); S[s] = scale(raw); y = raw.loc[span[0]:span[1]]
        rep(S[s].loc[span[0]:span[1]], f"  {s}"); print(f"      mean net {y.mean() * 1e4:.2f} bp, hit {(y > 0).mean() * 100:.0f}%, cost/side by year {(year_cost(m) * 1e4).round(2).to_dict()}")
    b = scale(pd.DataFrame(S).fillna(0).mean(axis=1)); b.to_csv("data/derived/scan/R13_lasthalf_daily.csv", header=["ret"])
    print(f"--- BASKET ({len(S)} indices, the hypothesis)"); rep(b.loc[span[0]:span[1]], "LAST-HALF BASKET")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([b, i2, c1], axis=1, keys=["LH", "I2", "C1"]).loc[span[0]:span[1]].dropna(subset=["LH"]).fillna(0)
    print("corr:", j.corr().round(2).loc["LH"].to_dict())
    for w in (0.0, 0.5):
        z = scale((1 - w) * j.I2 + w * j.LH); z = z[z != 0]
        print(f"    I2 + basket at weight {w:.1f}: Sharpe {z.mean() / z.std() * np.sqrt(252):.2f}")
