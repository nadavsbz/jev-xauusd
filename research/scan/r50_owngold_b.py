"""Round 50 (docs/SCAN_PLAN.md, pre-registered 14.11): OwnGold family B - M15 contraction (NR7 / inside bar) OCO stop breakout on
RF XAUUSD M1. Server time UTC+2/+3. Signal bar close in [10:00, 22:00] server, flatten 22:45. Fill on M1 bid high/low; SL first
when both touched in one minute. Cost $0.31/oz RT (stress $0.51). Usage: py -3.12 research/scan/r50_owngold_b.py [dev|holdout]"""
import sys
import numpy as np, pandas as pd
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
A, B = ("2019-01-01", "2023-12-31") if PER == "dev" else ("2024-01-01", "2026-11-13")
m1 = pd.read_csv("data/derived/scan/m1/XAUUSD.csv"); m1.index = pd.to_datetime(m1.time, unit="s")
m1 = m1.loc[pd.Timestamp(A) - pd.Timedelta(days=10):B]; m1 = m1[m1.close > 0]
m15 = m1.resample("15min").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
rg = m15.high - m15.low
tr = pd.concat([rg, (m15.high - m15.close.shift()).abs(), (m15.low - m15.close.shift()).abs()], axis=1).max(axis=1)
atr = tr.rolling(14).mean()
nr7 = rg < rg.shift(1).rolling(6).min()
ins = (m15.high <= m15.high.shift()) & (m15.low >= m15.low.shift())
mt, mh, ml, mc = m1.index.values, m1.high.values, m1.low.values, m1.close.values
BUF = 0.20

def run(sig, m):
    out = []; busy_until = np.datetime64("1970-01-01")
    for t in m15.index[sig & (rg >= 1.6) & (rg >= 0.25 * atr) & (rg <= atr)]:
        close_t = t + pd.Timedelta(minutes=15); hh = close_t.hour + close_t.minute / 60
        if not (10 <= hh <= 22) or close_t < pd.Timestamp(A) or close_t > pd.Timestamp(B) + pd.Timedelta(days=1): continue
        if np.datetime64(close_t) < busy_until: continue
        H, L, C = m15.high[t] + BUF, m15.low[t] - BUF, rg[t]
        flat = close_t.normalize() + pd.Timedelta(hours=22, minutes=45)
        exp = min(close_t + pd.Timedelta(minutes=60), flat)
        i = np.searchsorted(mt, np.datetime64(close_t)); q = 0
        while i < len(mt) and mt[i] < np.datetime64(exp):
            up, dn = mh[i] >= H, ml[i] <= L
            if up and dn: q = 0; break          # both sides in one minute: ambiguous, skip (no fill assumed)
            if up: q, e = 1, H; break
            if dn: q, e = -1, L; break
            i += 1
        if not q: continue
        sl = L if q == 1 else H; tp = e + q * m * C; t0 = mt[i]; x = None
        if (q == 1 and ml[i] <= sl) or (q == -1 and mh[i] >= sl): x = sl  # stopped in the fill minute
        while x is None:
            i += 1
            if i >= len(mt) or mt[i] >= np.datetime64(flat): i -= 1; x = mc[i]; break
            if (q == 1 and ml[i] <= sl) or (q == -1 and mh[i] >= sl): x = sl; break
            if (q == 1 and mh[i] >= tp) or (q == -1 and ml[i] <= tp): x = tp; break
        busy_until = mt[i]
        out.append({"t": pd.Timestamp(t0), "q": q, "gross": q * (x - e), "e": e, "hold": (mt[i] - t0) / np.timedelta64(1, "m")})
    return pd.DataFrame(out)

print(f"round 50 OwnGold B {PER} {A}..{B}")
rows = [("NR7", nr7), ("inside", ins)] if PER == "dev" else [(sys.argv[2], {"NR7": nr7, "inside": ins}[sys.argv[2]])] if len(sys.argv) > 2 else []
ms = (1.5, 2.0, 3.0) if PER == "dev" else (float(sys.argv[3]),)
for nm, s in rows:
    for m in ms:
        d = run(s, m)
        if not len(d): print(nm, m, "no trades"); continue
        for cost, lab in ((0.31, "base"), (0.51, "stress")):
            d["bp"] = (d.gross - cost) / d.e * 1e4
            y = d.groupby(d.t.dt.year).bp.sum()
            print(f"{nm:6s} m={m} {lab:6s} n={len(d)} mean {d.bp.mean():6.2f}bp med {d.bp.median():6.2f} hit {(d.bp>0).mean()*100:3.0f}% hold med {d.hold.median():5.1f}m | yrs+ {(y>0).sum()}/{len(y)} " + " ".join(f"{k%100}:{v:+.0f}" for k, v in y.items()), flush=True)
