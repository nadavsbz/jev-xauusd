"""Scan round 34 of docs/SCAN_PLAN.md (pre-registered 12.11.2026): Grok t202 NR7 / inside-day, first-touch intraday replay.
Usage: python research/scan/r34_nr7.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import scale
from scan2 import mismatch
import r28_30
from r28_30 import corr_rep
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"; r28_30.PER = PER
SPAN = r28_30.SPAN = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
TD = pd.Timedelta

def bars(p):
    m = pd.read_csv(p); m.index = pd.to_datetime(m.time, unit="s")
    return m[~m.index.duplicated()].query("close > 0 and open > 0")[["open", "high", "low", "close"]]

def windows(m, kind):
    """dict day -> (o,h,l,c arrays) of the trading window; also the day's H/L (signal bar)"""
    out = {}
    for d, g in m.groupby(m.index.normalize()):
        if d.dayofweek >= 5: continue
        mm = mismatch(d)
        end = d + TD(hours=22 if mm else 23)
        if kind == "idx": g = g.loc[d + TD(hours=15 if mm else 16, minutes=30):end - TD(seconds=1)]
        else: g = g.loc[:end - TD(seconds=1)]
        if len(g) < 10: continue
        out[d] = g
    return out

def replay(g, H, L, cost):
    o, h, l, c = g.open.values, g.high.values, g.low.values, g.close.values
    q = 0; e = 0.0
    for i in range(len(o)):
        if q == 0:
            up, dn = h[i] >= H, l[i] <= L
            if up and dn:                                   # both sides in one bar before entry: full loss (pre-registered)
                if o[i] >= H: return L / o[i] - 1 - cost, "both"
                if o[i] <= L: return -(H / o[i] - 1) - cost, "both"
                return -(H - L) / ((H + L) / 2) - cost, "both"
            if up: q, e = 1, max(o[i], H)
            elif dn: q, e = -1, min(o[i], L)
            continue
        if q > 0 and l[i] <= L: return min(o[i], L) / e - 1 - cost, "stop"
        if q < 0 and h[i] >= H: return -(max(o[i], H) / e - 1) - cost, "stop"
    if q == 0: return None, "none"
    return q * (c[-1] / e - 1) - cost, "close"

def run(path, kind, cost, rule, tag, name):
    W = windows(bars(path), kind); days = sorted(W)
    HL = pd.DataFrame({d: (W[d].high.max(), W[d].low.min()) for d in days}, index=["H", "L"]).T
    rng = HL.H - HL.L
    nr7 = rng < rng.shift(1).rolling(6).min()
    ins = (HL.H < HL.H.shift(1)) & (HL.L > HL.L.shift(1))
    sig = nr7 if rule == "nr7" else ins
    out, kinds = {}, []
    for a, b in zip(days[:-1], days[1:]):
        if not sig.get(a, False): continue
        r, k = replay(W[b], HL.H[a], HL.L[a], cost); kinds.append(k)
        if r is not None: out[b] = r
    ks = pd.Series(kinds).value_counts().to_dict()
    print(f"===== {name}: signal days {int(sig.sum())}, outcomes {ks}")
    ev = pd.Series(out).sort_index(); y = ev.loc[SPAN[0]:SPAN[1]]
    print(f"    trades {len(y)}, mean net {y.mean()*1e4:.2f} bp, hit {(y>0).mean()*100:.0f}%, t {y.mean()/y.std()*np.sqrt(len(y)):.2f}")
    print("    by year (sum %):", (y.groupby(y.index.year).sum() * 100).round(1).to_dict())
    full = pd.Series(0.0, index=pd.bdate_range(ev.index[0], ev.index[-1])); full.loc[ev.index] = ev
    corr_rep(scale(full), tag, name)

if __name__ == "__main__":
    run("data/derived/scan/m5/US500Cash.csv", "idx", 0.000231, "nr7", "R34_nr7_us500", "round 34 NR7_US500")
    run("data/derived/scan/m5/US500Cash.csv", "idx", 0.000231, "id", "R34_id_us500", "round 34 ID_US500")
    run("data/derived/scan/m1/XAUUSD.csv", "fx", 0.0002, "nr7", "R34_nr7_xau", "round 34 NR7_XAU")
