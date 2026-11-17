"""Round 104 (prereg docs/prereg/r104_i2_paper_m5.md): I2 as in the paper on M5 - 09:30 ET anchor, half-hour checks,
trailing stop max(UB,VWAP)/min(LB,VWAP), flat at 15:55 ET. Base = our I2 (scan2 "i2", DST fix) on H1.
Usage: py -3.12 research/scan/r104_i2_paper_m5.py dev|hold"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import tcost, scale, load
from scan2 import run
PART = sys.argv[1]
m = pd.read_csv("data/derived/scan/m5/USTECHCash.csv"); m.index = pd.to_datetime(m.time, unit="s"); m = m[~m.index.duplicated()]
m.index = m.index.tz_localize("Europe/Athens", ambiguous="NaT", nonexistent="NaT").tz_convert("America/New_York").tz_localize(None)
m = m[m.index.notna()]
h1 = load("USTECHCash"); tc = tcost("USTECHCash", h1)
m["d"] = m.index.normalize(); m["tm"] = m.index.hour * 60 + m.index.minute
m = m[(m.tm >= 570) & (m.tm <= 955)]                                  # 09:30 .. 15:55 bars (bar open times)
CHK = [600 + 30 * k for k in range(12)]                                # 10:00 .. 15:30: decision at the close of the bar ending then
rows = {}
for d, g in m.groupby("d"):
    g = g.set_index("tm")
    if 570 not in g.index or 955 not in g.index or not all((c - 5) in g.index for c in CHK): continue
    tp = (g.high + g.low + g.close) / 3; v = g.tick_volume.astype(float)
    vw = (tp * v).cumsum() / v.cumsum().replace(0, np.nan)
    rows[d] = dict(O=g.open[570], X=g.close[955], C=[g.close[c - 5] for c in CHK], VW=[vw[c - 5] for c in CHK])
D = pd.DataFrame(rows).T.sort_index()
C = np.array(D.C.tolist(), float); O = D.O.values.astype(float); X = D.X.values.astype(float); VW = np.array(D.VW.tolist(), float)
MV = pd.DataFrame(np.abs(C / O[:, None] - 1)).rolling(14).mean().shift(1).values
ret = np.zeros(len(D))
for i in range(15, len(D)):
    if np.isnan(MV[i]).any(): continue
    prev = X[i - 1]; up, lo = max(O[i], prev), min(O[i], prev)
    q, r, last = 0, 0.0, None
    for j in range(len(CHK)):
        c = C[i, j]
        if q and last is not None: r += q * (c / last - 1)
        last = c
        U, L = up * (1 + MV[i, j]), lo * (1 - MV[i, j])
        if q == 1 and c < max(U, VW[i, j]): nq = 0
        elif q == -1 and c > min(L, VW[i, j]): nq = 0
        else: nq = q
        if nq == 0: nq = 1 if c > U else (-1 if c < L else 0)
        r -= abs(nq - q) * tc; q = nq
    if q: r += q * (X[i] / last - 1); r -= abs(q) * tc               # flat at 15:55
    ret[i] = r
NEW = scale(pd.Series(ret, index=D.index))
BASE = scale(run(h1, tc, "i2", True))
def st(x):
    x = x[x.index.dayofweek < 5]; eq = (1 + x).cumprod()
    return x.mean() / x.std() * np.sqrt(252), (eq / eq.cummax() - 1).min() * 100, {y: round(g.sum() * 100, 1) for y, g in x.groupby(x.index.year)}
a, b = ("2018", "2022") if PART == "dev" else ("2023", "2026")
sb, mb, yb = st(BASE[a:b]); sn, mn, yn = st(NEW[a:b])
ok = (sn >= sb + 0.10 and mn >= mb) if PART == "dev" else (sn >= sb + 0.05 and mn >= mb - 2)
print(f"{PART} {a}-{b}: M5 days {len(NEW[a:b])}, cost/side {tc * 100:.4f}%, corr {NEW[a:b].corr(BASE[a:b]):.2f}")
print(f"  BASE I2 H1   Sh {sb:.2f} MDD {mb:.1f} | {yb}")
print(f"  PAPER M5     Sh {sn:.2f} ({sn - sb:+.2f}) MDD {mn:.1f} -> {'PASS' if ok else 'FAIL'} | {yn}")
