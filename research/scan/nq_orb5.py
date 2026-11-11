"""Scan round 11 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 evening): 5-minute ORB on USTECH (Zarattini & Aziz 2023).
Opening M5 bar = the bar opening at server 16:30 (15:30 in US/EU DST-mismatch weeks). Direction = its close vs open (doji: no
trade); entry at the next bar's open; stop = the opening bar's low (long) / high (short); target = 10R; else flat at the close
of the last bar that opens before server 23:00 (22:00). Cost 0.015% per side. Usage: python research/scan/nq_orb5.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
from scan2 import mismatch
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
TC = 0.00015

def orb5(m):
    out = {}
    for d, x in m.groupby(m.index.normalize()):
        if d.dayofweek >= 5: continue
        k = 1 if mismatch(d) else 0
        t0 = d + pd.Timedelta(hours=16 - k, minutes=30); tend = d + pd.Timedelta(hours=23 - k)
        if t0 not in x.index: continue
        b0 = x.loc[t0]; q = 1 if b0.close > b0.open else (-1 if b0.close < b0.open else 0)
        y = x[(x.index > t0) & (x.index < tend)]
        if q == 0 or len(y) < 10: out[d] = 0.0; continue
        e = y.open.iloc[0]; sl = b0.low if q == 1 else b0.high; risk = abs(e - sl)
        if risk <= 0 or (q == 1 and sl >= e) or (q == -1 and sl <= e): out[d] = 0.0; continue
        tp = e + q * 10 * risk; px = None
        for _, b in y.iterrows():
            if (q == 1 and b.low <= sl) or (q == -1 and b.high >= sl): px = min(sl, b.open) if q == 1 else max(sl, b.open); break
            if (q == 1 and b.high >= tp) or (q == -1 and b.low <= tp): px = max(tp, b.open) if q == 1 else min(tp, b.open); break
        if px is None: px = y.close.iloc[-1]
        out[d] = q * (px / e - 1) - 2 * TC
    return pd.Series(out)

if __name__ == "__main__":
    span = ("2000", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    m = pd.read_csv("data/derived/scan/m5/USTECHCash.csv"); m.index = pd.to_datetime(m.time, unit="s")
    m = m[~m.index.duplicated()]; m = m[(m.close > 0) & (m.open > 0)]
    print(f"===== round 11 NQ 5-min ORB {PER} {span}  data {m.index[0]:%Y-%m-%d} -> {m.index[-1]:%Y-%m-%d}")
    raw = orb5(m); x = scale(raw); x.to_csv("data/derived/scan/R11_orb5_daily.csv", header=["ret"])
    rep(x.loc[span[0]:span[1]], "ORB5 USTECH")
    y = raw.loc[span[0]:span[1]]; t = y[y != 0]
    print(f"    trades {len(t)}/{len(y)}, mean {t.mean() * 1e4:.1f} bp, hit {(t > 0).mean() * 100:.0f}%")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([x, i2, c1], axis=1, keys=["ORB5", "I2", "C1"]).loc[span[0]:span[1]].dropna(subset=["ORB5"]).fillna(0)
    print("corr:", j.corr().round(2).loc["ORB5"].to_dict())
    for w in (0.0, 0.5):     # descriptive: does it add to I2? Sharpe of (1-w) I2 + w ORB5
        z = scale((1 - w) * j.I2 + w * j.ORB5); z = z[z != 0]
        print(f"    I2 + ORB5 at weight {w:.1f}: Sharpe {z.mean() / z.std() * np.sqrt(252):.2f}")
