"""Round 67 (prereg docs/prereg/r67_gold_asia_rev_cpi_fade.md, commit 36cdae3): G = gold reversal after Asia, F = US500 fade on CPI/NFP days.
Usage: py -3.12 research/scan/r67.py dev|test [G F]"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/stable")
import r66_structural as R
from scan import tcost, E
from r64_mass import loadh
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"; WHICH = sys.argv[2:] or ["G", "F"]
R.PER = PER; R.SPAN = ("2000-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-12-31")
TD = pd.Timedelta

def G():
    h = loadh("XAUUSD"); tc = tcost("XAUUSD", h); pt = E.loc["XAUUSD", "point"]; rows = []
    d = h.index.normalize(); a = h[(h.index.hour >= 2) & (h.index.hour <= 8)]
    g = a.groupby(a.index.normalize()); hi, lo = g.high.max(), g.low.min()
    cl = a[a.index.hour == 8].close; cl.index = cl.index.normalize()
    rng = (hi - lo); p80 = rng.rolling(250, min_periods=200).quantile(0.8).shift(1)
    for day in rng.index:
        if day not in cl.index or not np.isfinite(p80.get(day, np.nan)) or rng[day] <= p80[day]: continue
        pos = (cl[day] - lo[day]) / rng[day]
        sgn = -1 if pos >= 0.8 else (1 if pos <= 0.2 else 0)
        if sgn == 0: continue
        e, x = day + TD(hours=10), day + TD(hours=12)
        if e not in h.index or x not in h.index: continue
        c = max(tc, h.spread[e] * pt / h.open[e]) + max(tc, h.spread[x] * pt / h.open[x])
        rows.append((day, sgn * (h.open[x] / h.open[e] - 1) - c, c))
    R.report(pd.DataFrame(rows, columns=["d", "net", "cost"]).set_index("d"), "G gold Asia reversal")

def F():
    cal = pd.read_csv("data/derived/news/mt5_calendar_usd.csv")
    t = pd.to_datetime(cal[cal.event.isin(["Nonfarm Payrolls", "CPI m/m"])].time, unit="s").dt.tz_localize("UTC").dt.tz_convert("America/New_York")
    days = sorted(set(t[(t.dt.hour == 8) & (t.dt.minute == 30)].dt.tz_localize(None).dt.normalize()))
    m = pd.read_csv("data/derived/scan/m5/US500Cash.csv"); m.index = pd.to_datetime(m.time, unit="s"); m = m[~m.index.duplicated()]
    tc = tcost("US500Cash", m.resample("1h").last().dropna()); pt = E.loc[".US500Cash", "point"]; rows = []
    for d in days:
        o, a, b = R.et2srv(d, 9, 30), R.et2srv(d, 10), R.et2srv(d, 15, 55)
        if not all(k in m.index for k in (o, a, b)): continue
        sgn = -np.sign(m.open[a] / m.open[o] - 1)
        if sgn == 0: continue
        c = max(tc, m.spread[a] * pt / m.open[a]) + max(tc, m.spread[b] * pt / m.open[b])
        rows.append((d, sgn * (m.open[b] / m.open[a] - 1) - c, c))
    full = R.report(pd.DataFrame(rows, columns=["d", "net", "cost"]).set_index("d"), "F US500 CPI/NFP fade")
    try:
        r55 = pd.read_csv("data/derived/scan/R55_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
        j = pd.concat([full, r55], axis=1).dropna(); print(f"      corr r55: {j.corr().iloc[0,1]:.2f}")
    except Exception as e: print("      r55 series n/a:", type(e).__name__)

if __name__ == "__main__":
    print(f"===== {PER} {R.SPAN}")
    for w in WHICH: globals()[w]()
