"""Round 105 (prereg docs/prereg/r105_c1_paper_daily.md): C1 as in the paper - daily bars, lookbacks 5..360 days,
long-only, per-asset min(0.25/vol90, 2). Base = frozen C1 (r94 run(False)). Usage: py -3.12 research/scan/r105_c1_paper_daily.py dev|hold"""
import sys, contextlib, io
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
PART = sys.argv[1]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", "dev"]; import r94_c1_stablecoin as base_mod
from scan import tcost, scale
from r64_mass import loadh, swaps

def comps(c, ns):
    out = []; cv = c.values
    for n in ns:
        hv = c.rolling(n).max().values; xl = c.rolling(max(n // 2, 1)).min().values
        p = np.zeros(len(c))
        for i in range(1, len(c)):
            q = p[i - 1]
            if q == 0: q = 1 if cv[i] >= hv[i] else 0
            elif cv[i] <= xl[i]: q = 0
            p[i] = q
        out.append(p)
    return np.array(out)

NS = (5, 10, 20, 30, 60, 90, 150, 250, 360)
legs = []
for s in ("BTCUSD", "ETHUSD"):
    h = loadh(s); tc = tcost(s, h); sl, ss = swaps(s, float(h.close.iloc[-1]))
    c = h.close.resample("1D").last().dropna(); r = c.pct_change().fillna(0)
    sig = pd.Series(comps(c, NS).mean(0), index=c.index)
    vol = r.rolling(90).std() * np.sqrt(365)
    w = (sig * (0.25 / vol).clip(upper=2.0)).fillna(0).shift(2).fillna(0)
    net = w * r - w.diff().abs().fillna(0) * tc + w * sl / 365
    legs.append(net)
NEW = scale(pd.concat(legs, axis=1).fillna(0).mean(1))
BASE = base_mod.run(False)
def st(x):
    eq = (1 + x).cumprod(); return x.mean() / x.std() * np.sqrt(len(x) / ((x.index[-1] - x.index[0]).days / 365.25)), (eq / eq.cummax() - 1).min() * 100, {y: round(g.sum() * 100) for y, g in x.groupby(x.index.year)}
a, b = ("2019", "2022") if PART == "dev" else ("2023", "2026")
sb, mb, yb = st(BASE[a:b]); sn, mn, yn = st(NEW[a:b])
ok = (sn >= sb + 0.10 and mn >= mb) if PART == "dev" else (sn >= sb + 0.05 and mn >= mb - 2)
print(f"{PART} {a}-{b}: corr {NEW[a:b].corr(BASE[a:b]):.2f}")
print(f"  BASE C1 (H6)   Sh {sb:.2f} MDD {mb:.1f} | {yb}")
print(f"  PAPER daily    Sh {sn:.2f} ({sn - sb:+.2f}) MDD {mn:.1f} -> {'PASS' if ok else 'FAIL'} | {yn}")
