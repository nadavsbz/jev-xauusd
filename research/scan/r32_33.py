"""Scan rounds 32-33 of docs/SCAN_PLAN.md (pre-registered 12.11.2026 night). Usage: python research/scan/r32_33.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import scale
import r28_30
from r28_30 import corr_rep
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"; r28_30.PER = PER
SPAN = r28_30.SPAN = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
TD = pd.Timedelta
def bars(p):
    m = pd.read_csv(p); m.index = pd.to_datetime(m.time, unit="s"); return m[~m.index.duplicated()].query("close > 0")[["open", "high", "low", "close"]]
def finish(out, tag, name):
    ev = pd.Series(out).sort_index(); y = ev.loc[SPAN[0]:SPAN[1]]
    print(f"    events {len(y)}, mean net {y.mean()*1e4:.2f} bp, hit {(y>0).mean()*100:.0f}%, t {y.mean()/y.std()*np.sqrt(len(y)):.2f}")
    full = pd.Series(0.0, index=pd.bdate_range(ev.index[0], ev.index[-1])); full.loc[ev.index] = ev
    corr_rep(scale(full), tag, name)

g1 = bars("data/derived/scan/m1/XAUUSD.csv")
# round 32
news = pd.to_datetime(pd.read_csv("data/derived/news/news_high_rf.txt", header=None)[0], unit="s")
news = news[(news.dt.hour >= 14) & (news.dt.hour <= 17)]
first = news.groupby(news.dt.normalize()).min()
P = g1.open; out = {}
for d, t in first.items():
    a, b, z = P.get(t), P.get(t + TD(minutes=15)), P.get(d + TD(hours=22))
    if a is None or b is None or z is None: continue
    q = np.sign(b / a - 1)
    if q: out[d] = q * (z / b - 1) - 0.0003
finish(out, "R32_goldnews", "round 32 gold post-US-news drift")
# round 33
g5 = g1.resample("5min", label="left", closed="left").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
for sym, m, tc in (("EURUSD", bars("data/derived/scan/m5/EURUSD.csv"), 0.00007), ("XAUUSD", g5, 0.0001)):
    out = {}
    for d, x in m.groupby(m.index.normalize()):
        if d.dayofweek >= 5: continue
        rg = x.loc[d + TD(hours=2):d + TD(hours=8, minutes=55)]
        if len(rg) < 50: continue
        hi, lo = rg.high.max(), rg.low.min()
        w = x.loc[d + TD(hours=9):d + TD(hours=18, minutes=55)]
        br = w[(w.close > hi) | (w.close < lo)]
        if len(br) == 0: continue
        t = br.index[0]; q = 1 if br.close.iloc[0] > hi else -1
        rest = w.loc[t + TD(minutes=5):]
        if len(rest) == 0: continue
        e = rest.open.iloc[0]; stop = lo if q > 0 else hi
        hit = rest[rest.low <= stop] if q > 0 else rest[rest.high >= stop]
        if len(hit): px = min(stop, hit.open.iloc[0]) if q > 0 else max(stop, hit.open.iloc[0])
        else:
            ex = x.loc[d + TD(hours=19):d + TD(hours=19)]; px = ex.open.iloc[0] if len(ex) else rest.close.iloc[-1]
        out[d] = q * (px / e - 1) - 2 * tc
    finish(out, f"R33_asiabrk_{sym}", f"round 33 Asian-range breakout {sym}")
