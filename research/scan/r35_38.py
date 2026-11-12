"""Scan rounds 35-38 of docs/SCAN_PLAN.md (pre-registered together 12.11.2026). Usage: python research/scan/r35_38.py [dev|test] [35 36 37 38]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, trend, E
from scan2 import mismatch
import r28_30
from r28_30 import corr_rep
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"; r28_30.PER = PER
SPAN = r28_30.SPAN = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
WHICH = sys.argv[2:] or ["35", "36", "37", "38"]
TD = pd.Timedelta; TC, SW = 0.000231, 0.086

def finish(ev, tag, name):
    ev = ev.sort_index(); y = ev.loc[SPAN[0]:SPAN[1]]
    print(f"    events {len(y)}, mean net {y.mean()*1e4:.2f} bp, hit {(y>0).mean()*100:.0f}%, t {y.mean()/y.std()*np.sqrt(len(y)):.2f}")
    full = pd.Series(0.0, index=pd.bdate_range(ev.index[0], ev.index[-1])); full.loc[full.index.intersection(ev.index)] = ev.groupby(level=0).sum()
    corr_rep(scale(full), tag, name)

def spx():
    d = pd.read_csv("data/raw/yahoo/SPX.csv", parse_dates=["date"]).set_index("date").close
    return d[~d.index.duplicated()].dropna()

def r35():
    m = pd.read_csv("data/derived/scan/m5/US500Cash.csv"); m.index = pd.to_datetime(m.time, unit="s"); P = m[~m.index.duplicated()].open
    cal = pd.read_csv("data/derived/news/mt5_calendar_usd.csv"); ev = pd.to_datetime(cal[cal.event == "Fed Interest Rate Decision"].time, unit="s")
    days = pd.DatetimeIndex(sorted(set(P.index.normalize()))); out = {}
    for t in ev:
        et = t.tz_localize("UTC").tz_convert("America/New_York").tz_localize(None)     # calendar times are UTC
        if not (13 <= et.hour + et.minute / 60 <= 15): continue          # scheduled 14:00 ET decisions only
        d = et.normalize(); k = days.searchsorted(d)
        if k == 0 or k >= len(days) or days[k] != d: continue
        p = days[k - 1]
        a = p + TD(hours=14 + (6 if mismatch(p) else 7)); z = d + TD(hours=13, minutes=55) + TD(hours=6 if mismatch(d) else 7)
        if a not in P.index or z not in P.index: continue
        nights = (d - p).days
        out[d] = P[z] / P[a] - 1 - TC - SW / 365 * nights
    finish(pd.Series(out), "R35_prefomc", "round 35 pre-FOMC drift (US500)")

def r36():
    c = spx(); bd = pd.bdate_range(c.index[0], c.index[-1]); hol = bd.difference(c.index); out = {}
    idx = c.index
    for i in range(1, len(idx) - 1):
        nxt = idx[i] + pd.offsets.BDay(1)
        if nxt in hol:                                   # idx[i] is the day before a holiday
            out[idx[i]] = c.iloc[i] / c.iloc[i - 1] - 1 - TC - SW / 365 * (idx[i] - idx[i - 1]).days
    finish(pd.Series(out), "R36_preholiday", "round 36 pre-holiday (SPX)")

def r37():
    c = spx(); idx = c.index; out = {}
    for mth in pd.period_range(idx[0], idx[-1], freq="M"):
        fr = pd.date_range(mth.start_time, mth.end_time, freq="W-FRI")
        if len(fr) < 3: continue
        f3 = fr[2]; end = idx[idx <= f3]
        if not len(end): continue
        e = end[-1]; st = idx[idx <= f3 - TD(days=7)]
        if not len(st) or e <= st[-1]: continue
        s = st[-1]
        out[e] = c[e] / c[s] - 1 - TC - SW / 365 * (e - s).days
    finish(pd.Series(out), "R37_opex", "round 37 option-expiration week (SPX)")

def r38():
    s = "XAGUSD"; h = load(s)
    # ecn_costs swap for XAGUSD is in points (mode 1): -13 / +1.6 pts x 0.001 x 5000 oz per night on 5000 x 50.62 = -9.37 / +1.15 %/yr
    x = scale(trend(h, tcost(s, h), -9.37, 1.15))
    corr_rep(x, "R38_silvertrend", "round 38 C1 trend rule on XAGUSD")

if __name__ == "__main__":
    for k in WHICH: globals()[f"r{k}"]()
