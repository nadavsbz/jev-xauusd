"""Round 51 (docs/prereg/r51_owngold_c.md, committed 889b628 before running): OwnGold family C impulse-pullback continuation
on RF XAUUSD M1/M15. Usage: py -3.12 research/scan/r51_owngold_c.py [dev|holdout p r]"""
import sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
A, B = ("2019-01-01", "2023-12-31") if PER == "dev" else ("2024-01-01", "2026-11-13")
m1 = pd.read_csv("data/derived/scan/m1/XAUUSD.csv"); m1.index = pd.to_datetime(m1.time, unit="s")
m1 = m1.loc[pd.Timestamp(A) - pd.Timedelta(days=10):pd.Timestamp(B) + pd.Timedelta(days=1)]; m1 = m1[m1.close > 0]
m15 = m1.resample("15min").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
H, L, Cc = m15.high.values, m15.low.values, m15.close.values; T = m15.index
tr = np.maximum(H - L, np.maximum(np.abs(H - np.r_[np.nan, Cc[:-1]]), np.abs(L - np.r_[np.nan, Cc[:-1]])))
ATR = pd.Series(tr).rolling(14).mean().values
mt, mh, ml, mc = m1.index.values, m1.high.values, m1.low.values, m1.close.values
BUF = 0.20

def run(p, r):
    out = []; busy = np.datetime64("1970-01-01"); k = 15
    while k < len(T) - 1:
        ct = T[k] + pd.Timedelta(minutes=15); hh = ct.hour + ct.minute / 60
        mv = Cc[k] - Cc[k - 1]; I = H[k] - L[k]
        if not (10 <= hh <= 22) or ct < pd.Timestamp(A) or ct > pd.Timestamp(B) + pd.Timedelta(days=1) or not (abs(mv) >= p * ATR[k - 1]) or I <= 0: k += 1; continue
        d = 1 if mv > 0 else -1
        if (d == 1 and Cc[k] < L[k] + 2 * I / 3) or (d == -1 and Cc[k] > H[k] - 2 * I / 3): k += 1; continue
        origin, ext = (L[k], H[k]) if d == 1 else (H[k], L[k])
        j, ok = k + 1, False; pl = L[k] if d == 1 else H[k]
        while j <= min(k + 8, len(T) - 1) and T[j].normalize() == T[k].normalize():
            if (d == 1 and Cc[j] < origin) or (d == -1 and Cc[j] > origin): break
            pl = min(pl, L[j]) if d == 1 else max(pl, H[j])
            if (d == 1 and L[j] <= ext - r * I) or (d == -1 and H[j] >= ext + r * I): ok = True; break
            j += 1
        if not ok: k += 1; continue
        st = H[j] + BUF if d == 1 else L[j] - BUF; sl = pl - BUF if d == 1 else pl + BUF
        sld = abs(st - sl)
        if sld < 2.0 or sld > 2 * ATR[j]: k += 1; continue
        t1 = T[j] + pd.Timedelta(minutes=15)
        if np.datetime64(t1) < busy: k += 1; continue
        flat = t1.normalize() + pd.Timedelta(hours=22, minutes=45); exp = min(t1 + pd.Timedelta(minutes=60), flat)
        i = np.searchsorted(mt, np.datetime64(t1)); f = False
        while i < len(mt) and mt[i] < np.datetime64(exp):
            if (d == 1 and mh[i] >= st) or (d == -1 and ml[i] <= st): f = True; break
            i += 1
        if not f: k = j + 1; continue
        e = st; tp = e + d * 1.0 * I; t0 = mt[i]; x = None
        if (d == 1 and ml[i] <= sl) or (d == -1 and mh[i] >= sl): x = sl
        while x is None:
            i += 1
            if i >= len(mt) or mt[i] >= np.datetime64(flat): i -= 1; x = mc[i]; break
            if (d == 1 and ml[i] <= sl) or (d == -1 and mh[i] >= sl): x = sl; break
            if (d == 1 and mh[i] >= tp) or (d == -1 and ml[i] <= tp): x = tp; break
        busy = mt[i]
        out.append({"t": pd.Timestamp(t0), "gross": d * (x - e), "e": e, "sld": sld, "hold": (mt[i] - t0) / np.timedelta64(1, "m")})
        k = int(np.searchsorted(T.values, mt[i])) + 1
    return pd.DataFrame(out)

def report(d, lab, cost):
    d = d.copy(); d["bp"] = (d.gross - cost) / d.e * 1e4
    y = d.groupby(d.t.dt.year).bp.sum()
    rr = 0.01 * (d.gross - cost) / d.sld; eq = (1 + rr).cumprod(); dd = (eq / eq.cummax() - 1).min() * 100
    day = rr.groupby(d.t.dt.normalize()).sum(); lg = np.log1p(day); top = lg.nlargest(10).sum() / lg.sum() * 100 if lg.sum() > 0 else np.nan
    print(f"  {lab:6s} n={len(d)} mean {d.bp.mean():6.2f}bp med {d.bp.median():6.2f} hit {(d.bp>0).mean()*100:3.0f}% hold {d.hold.median():5.1f}m DD1% {dd:6.1f}% top10 {top:5.0f}% | yrs+ {(y>0).sum()}/{len(y)} " + " ".join(f"{k%100}:{v:+.0f}" for k, v in y.items()), flush=True)

grid = [(p, r) for p in (1.0, 1.5, 2.0) for r in (0.38, 0.50, 0.62)] if PER == "dev" else [(float(sys.argv[2]), float(sys.argv[3]))]
print(f"round 51 OwnGold C {PER} {A}..{B}")
for p, r in grid:
    d = run(p, r); print(f"p={p} r={r}")
    if not len(d): print("  no trades"); continue
    report(d, "base", 0.31); report(d, "stress", 0.51)
