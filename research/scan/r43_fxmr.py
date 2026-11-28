"""Scan round 43 of docs/SCAN_PLAN.md (pre-registered 13.11.2026): daily Bollinger mean reversion on FX crosses, fixed stop, no grid.
Usage: py -3.12 research/scan/r43_fxmr.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, scale, rep, E
import r28_30
from r28_30 import corr_rep
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"; r28_30.PER = PER
SPAN = r28_30.SPAN = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
PAIRS = ("AUDCAD", "EURGBP", "AUDNZD", "NZDCAD")

def sleeve(s):
    h = load(s); c = h.close[h.index.hour == 22]; c.index = c.index.normalize(); c = c[c.index.dayofweek < 5]
    pt = E.loc[s, "point"]; sp = float((h.spread * pt / h.close).loc["2024":].median()); tc = sp + 0.00005
    sl, ss = (E.loc[s, k] * pt * 365 / c.iloc[-1] * 100 for k in ("swap_long", "swap_short"))   # % per year
    z = ((c - c.rolling(20).mean()) / c.rolling(20).std()).values
    q, age, pos = 0, 0, np.zeros(len(c))
    for i in range(len(c)):
        if np.isnan(z[i]): continue
        if q:
            age += 1
            if (q > 0 and z[i] >= 0) or (q < 0 and z[i] <= 0) or age >= 10 or abs(z[i]) > 3.5: q = 0
        if q == 0 and abs(z[i]) > 2 and abs(z[i]) <= 3.5: q, age = (-1 if z[i] > 0 else 1), 0
        pos[i] = q
    p = pd.Series(pos, index=c.index); r = c.pct_change().fillna(0)
    dt = c.index.to_series().diff().dt.days.fillna(0) / 365
    fin = np.where(p.shift(1) > 0, sl, np.where(p.shift(1) < 0, ss, 0)) * dt / 100
    net = p.shift(1).fillna(0) * r - p.diff().abs().fillna(0) * tc + fin
    print(f"  {s}: tc {tc*1e4:.2f} bp, swap %/yr L {sl:+.2f} S {ss:+.2f}, trades {int((p.diff().abs() > 0).sum() / 2)}, in market {(p != 0).mean()*100:.0f}%")
    return net

if __name__ == "__main__":
    S = {s: scale(sleeve(s)) for s in PAIRS}
    for s in PAIRS: rep(S[s].loc[SPAN[0]:SPAN[1]], f"  {s} (descr)")
    b = scale(pd.DataFrame(S).fillna(0).mean(axis=1))
    corr_rep(b, "R43_fxmr", "round 43 FX-cross mean reversion basket")
