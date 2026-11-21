"""Scan round 31 of docs/SCAN_PLAN.md (pre-registered 12.11.2026 night): DAX opening-range breakout (09:00-09:15 CET range).
Usage: python research/scan/r31_dax_orb.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import scale
from r28_30 import corr_rep
import r28_30
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"; r28_30.PER = PER
r28_30.SPAN = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
TC, TD = 0.00008, pd.Timedelta
m = pd.read_csv("data/derived/scan/m5/DE40Cash.csv"); m.index = pd.to_datetime(m.time, unit="s"); m = m[~m.index.duplicated()].query("close > 0")
out = {}
for d, x in m.groupby(m.index.normalize()):
    if d.dayofweek >= 5: continue
    rg = x.loc[d + TD(hours=10):d + TD(hours=10, minutes=10)]
    if len(rg) < 3: continue
    hi, lo = rg.high.max(), rg.low.min()
    w = x.loc[d + TD(hours=10, minutes=15):d + TD(hours=18, minutes=25)]
    br = w[(w.close > hi) | (w.close < lo)]
    if len(br) == 0: continue
    t = br.index[0]; q = 1 if br.close.iloc[0] > hi else -1
    rest = w.loc[t + TD(minutes=5):]
    if len(rest) == 0: continue
    e = rest.open.iloc[0]; stop = lo if q > 0 else hi
    hit = rest[rest.low <= stop] if q > 0 else rest[rest.high >= stop]
    if len(hit): px = min(stop, hit.open.iloc[0]) if q > 0 else max(stop, hit.open.iloc[0])
    else:
        ex = x.loc[d + TD(hours=18, minutes=30):d + TD(hours=18, minutes=30)]; px = ex.open.iloc[0] if len(ex) else rest.close.iloc[-1]
    out[d] = q * (px / e - 1) - 2 * TC
ev = pd.Series(out); y = ev.loc[r28_30.SPAN[0]:r28_30.SPAN[1]]
print(f"    days {len(y)}, mean net {y.mean()*1e4:.2f} bp, hit {(y>0).mean()*100:.0f}%, t {y.mean()/y.std()*np.sqrt(len(y)):.2f}, long {y[ev.reindex(y.index)>-9].mean()*1e4:.2f}")
full = pd.Series(0.0, index=pd.bdate_range(ev.index[0], ev.index[-1])); full.loc[ev.index] = ev
corr_rep(scale(full), "R31_daxorb", "round 31 DAX opening-range breakout")
