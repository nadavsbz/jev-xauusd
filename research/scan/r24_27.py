"""Scan rounds 24-27 of docs/SCAN_PLAN.md (pre-registered together 12.11.2026 night). Server time follows EU DST (EET):
London = server - 2, CET = server - 1 always; ET = server - 7, or server - 6 in US/EU mismatch weeks.
Usage: python research/scan/r24_27.py [dev|test] [24 25 26 27]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
from scan2 import mismatch
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
WHICH = sys.argv[2:] or ["24", "25", "26", "27"]
SPAN = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
TD = pd.Timedelta

def bars(path):
    m = pd.read_csv(path); m.index = pd.to_datetime(m.time, unit="s")
    return m[~m.index.duplicated()].query("close > 0 and open > 0")[["open", "high", "low", "close"]]

def report(ev, name, tag):
    ev = ev.sort_index(); ev = ev.groupby(ev.index.normalize()).sum()
    full = pd.Series(0.0, index=pd.bdate_range(ev.index[0], ev.index[-1])); full.loc[full.index.intersection(ev.index)] = ev.reindex(full.index.intersection(ev.index))
    x = scale(full); x.to_csv(f"data/derived/scan/{tag}_daily.csv", header=["ret"])
    y = ev.loc[SPAN[0]:SPAN[1]]
    print(f"===== {name} {PER}"); rep(x.loc[SPAN[0]:SPAN[1]], tag)
    print(f"    events {len(y)}, mean net {y.mean() * 1e4:.2f} bp, hit {(y > 0).mean() * 100:.0f}%, t {y.mean() / y.std() * np.sqrt(len(y)):.2f}")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([x, i2, c1], axis=1, keys=["X", "I2", "C1"]).loc[SPAN[0]:SPAN[1]].dropna(subset=["X"]).fillna(0)
    print("    corr:", j.corr().round(2).loc["X"].to_dict())

def r24():
    m = bars("data/derived/scan/m5/BTCUSD.csv"); TC, SW = 0.00025, 0.0475; out = {}
    for f in pd.date_range("2017-12-01", m.index[-1], freq="W-FRI"):
        mon = f + TD(days=3)
        tc = f + TD(days=1) - TD(hours=1 if mismatch(f) else 0)
        to = mon - TD(hours=1 if mismatch(mon) else 0)
        a = m.loc[tc - TD(minutes=30):tc - TD(minutes=5)]; b = m.loc[to:to + TD(minutes=30)]
        if len(a) == 0 or len(b) == 0: continue
        pc, po = a.close.iloc[-1], b.open.iloc[0]; t0 = b.index[0]
        g = po / pc - 1
        if abs(g) < 0.01: continue
        q = -np.sign(g); w = m.loc[t0:to + TD(hours=48)]
        hit = w[(w.low <= pc) & (w.high >= pc)] if True else None
        touch = w[(w.high >= pc)] if q > 0 else w[(w.low <= pc)]
        if len(touch): px, tx = pc, touch.index[0]
        else: px, tx = w.close.iloc[-1], w.index[-1]
        hrs = (tx - t0).total_seconds() / 3600
        out[tx] = q * (px / po - 1) - 2 * TC - SW * hrs / 24 / 365
    report(pd.Series(out), "round 24 BTC CME-gap fill", "R24_cmegap")

def r25():
    m = bars("data/derived/scan/m5/DE40Cash.csv"); TC = 0.00008; out = {}
    days = sorted(set(m.index.normalize())); prev = None
    for d in days:
        if d.dayofweek >= 5: continue
        cl = m.loc[d + TD(hours=18, minutes=25):d + TD(hours=18, minutes=25)]
        op = m.loc[d + TD(hours=10):d + TD(hours=10)]
        if prev is not None and len(op):
            po = op.open.iloc[0]; g = po / prev - 1
            if abs(g) >= 0.003:
                q = -np.sign(g); w = m.loc[d + TD(hours=10):d + TD(hours=12, minutes=55)]
                touch = w[w.high >= prev] if q > 0 else w[w.low <= prev]
                if len(touch): px = prev
                else:
                    e = m.loc[d + TD(hours=13):d + TD(hours=13)]; px = e.open.iloc[0] if len(e) else w.close.iloc[-1]
                out[d] = q * (px / po - 1) - 2 * TC
        prev = cl.close.iloc[0] if len(cl) else None
    report(pd.Series(out), "round 25 DE40 opening-gap fade", "R25_degap")

def r26():
    m = bars("data/derived/scan/m1/XAUUSD.csv"); P = m.open; out = {}
    for d in sorted(set(m.index.normalize())):
        if d.dayofweek >= 5: continue
        a, z = P.get(d + TD(hours=16, minutes=30)), P.get(d + TD(hours=17))
        if a is None or z is None: continue
        out[d] = -(z / a - 1) - 0.0002
    report(pd.Series(out), "round 26 gold PM-fix window short", "R26_goldfix")

def r27():
    m = bars("data/derived/scan/m5/EURUSD.csv"); P = m.open; TC = 0.00007; out = {}
    for d in sorted(set(m.index.normalize())):
        if d.dayofweek >= 5: continue
        a, b, z = P.get(d + TD(hours=17, minutes=30)), P.get(d + TD(hours=18)), P.get(d + TD(hours=19))
        if a is None or b is None or z is None: continue
        q = -np.sign(b / a - 1)
        if q == 0: continue
        out[d] = q * (z / b - 1) - 2 * TC
    report(pd.Series(out), "round 27 EURUSD WM-fix reversal", "R27_wmfix")

if __name__ == "__main__":
    for k in WHICH: globals()[f"r{k}"]()
