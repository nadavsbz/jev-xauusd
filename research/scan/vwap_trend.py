"""Scan round 16 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 night): session-VWAP trend on US500 M5 (Zarattini & Aziz 2023).
VWAP from the 16:30 server bar (15:30 in DST-mismatch weeks), typical price x tick_volume. Position = sign(close - VWAP) at each bar
close 16:30..22:50, filled at the next bar's open; flat at the close of the 22:55 bar. Cost per side per change = the yearly median
spread (bars 16-22) + 0.0015%. Usage: python research/scan/vwap_trend.py [dev|test] [symbol]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
from scan2 import mismatch
from last_half import m5
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
SYM = sys.argv[2] if len(sys.argv) > 2 else "US500Cash"

def run(m):
    x0 = m[(m.index.hour >= 16) & (m.index.hour <= 22)]
    cost = (x0.spread * 0.1 / x0.close).groupby(x0.index.year).median() + 0.000015
    out, turns = {}, {}
    for d, x in m.groupby(m.index.normalize()):
        if d.dayofweek >= 5: continue
        k = 1 if mismatch(d) else 0
        a, z = d + pd.Timedelta(hours=16 - k, minutes=30), d + pd.Timedelta(hours=22 - k, minutes=55)
        y = x[(x.index >= a) & (x.index <= z)]
        if len(y) < 70 or y.index[0] != a or y.index[-1] != z: continue
        tp = (y.high + y.low + y.close) / 3; w = y.tick_volume.clip(lower=1)
        vwap = (tp * w).cumsum() / w.cumsum()
        pos = np.sign(y.close - vwap).values[:-1]                 # decided at the close of bars 0..n-2
        o, c = y.open.values, y.close.values
        r = 0.0; q = 0; n = 0; tc = cost.get(d.year, cost.iloc[-1])
        for i in range(1, len(y)):                                  # bar i: hold pos[i-1] from its open to its close
            nq = pos[i - 1]
            if nq != q: r -= abs(nq - q) * tc; n += abs(nq - q); q = nq
            r += q * (c[i] / o[i] - 1) + (q * (o[i] / c[i - 1] - 1) if i > 1 else 0) * 0   # gaps between M5 bars ignored (continuous)
        r -= abs(q) * tc; n += abs(q)
        out[d] = r; turns[d] = n
    return pd.Series(out), pd.Series(turns)

if __name__ == "__main__":
    span = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    raw, turns = run(m5(SYM))
    x = scale(raw); x.to_csv(f"data/derived/scan/R16_vwap_{SYM}_daily.csv", header=["ret"])
    print(f"===== round 16 VWAP trend {SYM} {PER} {span}")
    rep(x.loc[span[0]:span[1]], "VWAP trend")
    y = raw.loc[span[0]:span[1]]
    print(f"    days {len(y)}, mean net {y.mean() * 1e4:.2f} bp, hit {(y > 0).mean() * 100:.0f}%, side-changes/day {turns.loc[span[0]:span[1]].mean():.1f}")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([x, i2, c1], axis=1, keys=["V", "I2", "C1"]).loc[span[0]:span[1]].dropna(subset=["V"]).fillna(0)
    print("corr:", j.corr().round(2).loc["V"].to_dict())
    for w in (0.0, 0.5):
        z = scale((1 - w) * j.I2 + w * j.V); z = z[z != 0]
        print(f"    I2 + VWAP at weight {w:.1f}: Sharpe {z.mean() / z.std() * np.sqrt(252):.2f}")
