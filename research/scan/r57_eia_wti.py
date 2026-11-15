"""Round 57 (docs/prereg/r57_eia_wti.md, 734e2b2): WTI on EIA days, sign of 10:30-11:00 ET -> trade 14:00-14:30 ET, SL 2xATR(30m,20d).
Usage: py -3.12 research/scan/r57_eia_wti.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan2 import mismatch
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
A, B = ("2018-12-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-10-30")
m = pd.read_csv("data/derived/scan/m5/WTI.csv"); m.index = pd.to_datetime(m.time, unit="s"); m = m[~m.index.duplicated()].query("close > 0")
nd = m.index.normalize(); sh = {d: pd.Timedelta(hours=6 if mismatch(d) else 7) for d in nd.unique()}
m.index = m.index - pd.to_timedelta([sh[d].value for d in nd]); m = m[~m.index.duplicated()]
pt = 0.01
day = m.index.normalize(); tod = m.index - day
# cost per side
x26 = m[(m.index.year == 2026) & (tod == pd.Timedelta("14:00:00"))]
tc = max(float((x26.spread * pt / x26.close).median()), 1e-4) + 0.5e-4
# ATR of 30-min bars over previous 20 trading days
h30 = m[["high", "low"]].resample("30min").agg({"high": "max", "low": "min"}).dropna()
rng = (h30.high - h30.low).groupby(h30.index.normalize()).mean()
atr = rng.rolling(20).mean().shift(1)
cal = pd.read_csv("data/derived/news/mt5_calendar_usd.csv"); cal = cal[cal.event == "EIA Crude Oil Stocks Change"]
ev = sorted(set((pd.to_datetime(cal.time, unit="s").dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize())))
rows = []
for d in ev:
    if not (pd.Timestamp(A) <= d <= pd.Timestamp(B)): continue
    g = m[day == d]; t = g.index - d
    a, b = g[t == pd.Timedelta("10:30:00")], g[t == pd.Timedelta("10:55:00")]
    w = g[(t >= pd.Timedelta("14:00:00")) & (t <= pd.Timedelta("14:25:00"))]
    if not len(a) or not len(b) or len(w) < 6 or d not in atr.index or not np.isfinite(atr[d]): continue
    s = np.sign(b.close.iloc[0] / a.open.iloc[0] - 1)
    if s == 0: continue
    e = w.open.iloc[0]; sl = e - s * 2 * atr[d]; px = w.close.iloc[-1]; hit = False
    for r in w.itertuples():
        if (s > 0 and r.low <= sl) or (s < 0 and r.high >= sl):
            px = min(r.open, sl) if s > 0 else max(r.open, sl); hit = True; break
    rows.append({"d": d, "s": s, "gross": s * (px / e - 1), "sl": hit})
t = pd.DataFrame(rows).set_index("d"); t["net"] = t.gross - 2 * tc
print(f"===== r57 EIA WTI {PER} {A}..{B}: cost/side {tc*1e4:.2f} bp (RT {2*tc*1e4:.2f}, 5x = {10*tc*1e4:.1f} bp)")
print(f"n {len(t)}, net mean {t.net.mean()*1e4:.2f} bp, gross {t.gross.mean()*1e4:.2f}, hit {(t.net>0).mean()*100:.0f}%, t {t.net.mean()/t.net.std()*np.sqrt(len(t)):.2f}, SL hits {t.sl.mean()*100:.0f}%")
print("by year (sum net bp, n):", t.groupby(t.index.year).net.agg(lambda v: (round(v.sum()*1e4), len(v))).to_dict())
