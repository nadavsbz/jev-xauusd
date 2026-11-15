"""Round 66 (prereg docs/prereg/r66_structural4.md, commit 6932265): four structural ideas from Grok t263.
Usage: py -3.12 research/scan/r66_structural.py dev|test [A B C D]"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/stable")
from scan import tcost, E
from scan2 import mismatch
from r64_mass import loadh
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"; WHICH = sys.argv[2:] or list("ABCD")
SPAN = ("2000-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-12-31")
TD = pd.Timedelta
def et2srv(d, hh, mm=0): return d + TD(hours=hh + (6 if mismatch(d) else 7), minutes=mm)

def report(T, name):
    """T: DataFrame indexed by date with net, cost (per trade, summed over sides)."""
    T = T.sort_index()[SPAN[0]:SPAN[1]]
    if len(T) < 10: print(f"[{name}] n={len(T)} too few"); return
    full = pd.Series(0.0, index=pd.bdate_range(T.index[0], T.index[-1])); g = T.net.groupby(level=0).sum()
    full.loc[full.index.intersection(g.index)] = g.reindex(full.index.intersection(g.index)).values
    t = T.net.mean() / T.net.std() * np.sqrt(len(T)); sh = full.mean() / full.std() * np.sqrt(252)
    y = T.net.groupby(T.index.year).sum(); ratio = T.net.mean() / T.cost.mean()
    print(f"[{name}] n {len(T)}  net {T.net.mean()*1e4:.2f} bp  gross {(T.net+T.cost).mean()*1e4:.2f}  cost {T.cost.mean()*1e4:.2f}  net/cost {ratio:.2f}  t {t:.2f}  Sh {sh:.2f}  pos {int((y>0).sum())}/{len(y)}")
    print("      years bp:", " ".join(f"{a%100:02d}:{v*1e4:+.0f}" for a, v in y.items()))
    C1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change()
    from book_tester import i2_daily
    for nm, o in [("C1", C1), ("I2", i2_daily())]:
        j = pd.concat([full, o], axis=1).dropna()
        if len(j) > 50: print(f"      corr {nm}: {j.corr().iloc[0,1]:.2f} (n={len(j)})")
    passed = t >= 2 and sh >= 0.5 and (y > 0).mean() >= 0.6 and ratio >= 5
    print(f"      dev gate (t,Sh,years,net/cost; corr checked by eye above): {'PASS' if passed else 'KILL'}" if PER == "dev" else
          f"      holdout gate: {'PASS' if sh >= 0.5 and (y > 0).sum() >= 3 and T.net.mean() > 0 else 'FAIL'}")
    return full

def A():
    legs = {"EURUSD": -1, "GBPUSD": -1, "USDCHF": 1}; rows = []
    for s, eu in legs.items():
        h = loadh(s); tc = tcost(s, h); pt = E.loc[s, "point"]
        for d in sorted(set(h.index.normalize())):
            if d.dayofweek > 4: continue
            for sgn, a, b in ((eu, d + TD(hours=9), d + TD(hours=14)), (-eu, et2srv(d, 11), et2srv(d, 16))):
                if a not in h.index or b not in h.index: continue
                c = max(tc, h.spread[a] * pt / h.open[a]) + max(tc, h.spread[b] * pt / h.open[b])
                rows.append((d, s, sgn * (h.open[b] / h.open[a] - 1) - c, c))
    X = pd.DataFrame(rows, columns=["d", "s", "net", "cost"]).groupby(["d", "s"]).sum()
    report(X.groupby(level="d").mean(), "A home-hours FX")

def B():
    rows = []
    for s in ("US500Cash", "USTECHCash"):
        m = pd.read_csv(f"data/derived/scan/m5/{s}.csv"); m.index = pd.to_datetime(m.time, unit="s"); m = m[~m.index.duplicated()]
        tc = tcost(s, m.resample("1h").last().dropna()); pt = E.loc["." + s, "point"]
        days = sorted(set(m.index.normalize()))
        for p, d in zip(days[:-1], days[1:]):
            if d.dayofweek > 4: continue
            k0 = et2srv(p, 15, 55); a = et2srv(d, 15); b = et2srv(d, 15, 55)
            if k0 not in m.index or a not in m.index or b not in m.index: continue
            r = m.open[a] / m.close[k0] - 1
            if abs(r) <= 0.015: continue
            c = max(tc, m.spread[a] * pt / m.open[a]) + max(tc, m.spread[b] * pt / m.open[b])
            rows.append((d, np.sign(r) * (m.open[b] / m.open[a] - 1) - c, c))
    report(pd.DataFrame(rows, columns=["d", "net", "cost"]).set_index("d"), "B LETF rebalance")

def C():
    y = lambda n: pd.read_csv(f"data/raw/yahoo/{n}.csv", parse_dates=["date"]).set_index("date").iloc[:, -1]
    spy, tlt = y("SPY"), y("TLT"); spx = pd.read_csv("data/raw/yahoo/SPX.csv", parse_dates=["date"]).set_index("date").close
    spx = spx[~spx.index.duplicated()]; idx = spx.index.intersection(spy.index).intersection(tlt.index)
    tc = 2.56e-5 + 0.00005; swl, sws = -0.086, -0.018; rows = []
    per = pd.Series(idx.to_period("M"), idx)
    for mo, dd in per.groupby(per):
        dd = dd.index
        if len(dd) < 12: continue
        prev = idx[idx < dd[0]]
        if len(prev) == 0: continue
        base = prev[-1]; dec = dd[-6]; ex = dd[-1]
        gap = (spy[dec] / spy[base] - 1) - (tlt[dec] / tlt[base] - 1)
        if abs(gap) <= 0.02: continue
        sgn = -np.sign(gap); nights = (ex - dec).days
        sw = (swl if sgn > 0 else sws) * nights / 365
        rows.append((ex, sgn * (spx[ex] / spx[dec] - 1) - 2 * tc + sw, 2 * tc - min(sw, 0)))
    report(pd.DataFrame(rows, columns=["d", "net", "cost"]).set_index("d"), "C pension rebalance")

def D():
    u = loadh(".US500Cash"); a = loadh("AUDJPY"); tc = tcost("AUDJPY", a); pt = E.loc["AUDJPY", "point"]
    r = u.close.pct_change(); gap = u.index.to_series().diff() > TD(hours=1); r[gap] = np.nan
    sd = r.rolling(250, min_periods=200).std().shift(1); sig = r[(r.abs() > 2 * sd)]
    rows = []
    for t0, x in sig.items():
        t1 = t0 + TD(hours=1)
        if t1 not in a.index: continue
        c = 2 * max(tc, a.spread[t1] * pt / a.open[t1])
        rows.append((t1.normalize(), np.sign(x) * (a.close[t1] / a.open[t1] - 1) - c, c))
    report(pd.DataFrame(rows, columns=["d", "net", "cost"]).set_index("d"), "D US500->AUDJPY lead-lag")

if __name__ == "__main__":
    print(f"===== {PER} {SPAN}")
    for w in WHICH: globals()[w]()
