"""Growth search, track A (pre-registered 3.11.2026 in docs/GROWTH_SEARCH_PLAN.md): the I2 'noise area' rule of
research/stable/second4.py, unchanged, on six more markets, anchored on each exchange's open (server time, fixed in advance):
  GX1 XAUUSD 10 (London)   GX2 XAUUSD 16 (New York)   SX1 XAGUSD 10   DX1 .DE40Cash 10   JX1 .JP225Cash 3   OX1 WTI 16
Bar: Sharpe >= 0.5 net and >= 60% positive years on data start..2025-10-24, and C1 + I2 + 0.5x component lifts the Sharpe
of C1 + I2 by >= 0.1. Only passers get the holdout. Usage: python research/growth/noise_more.py [hold]"""
import os, sys
import numpy as np, pandas as pd
HOLD = len(sys.argv) > 1 and sys.argv[1] == "hold"
sys.argv = sys.argv[:1]; sys.path.insert(0, "research/stable")
import second4 as S4
S2 = S4.S2

COMP = {"GX1": ("XAUUSD", 10, 21, 22), "GX2": ("XAUUSD", 16, 21, 22), "SX1": ("XAGUSD", 10, 21, 22),
        "DX1": (".DE40Cash", 10, 17, 18), "JX1": (".JP225Cash", 3, 7, 8), "OX1": ("WTI", 16, 20, 21)}

def bars(s):
    h = pd.read_csv(f"data/derived/intraday/{s}_H1.csv"); h.index = pd.to_datetime(h.time, unit="s")
    return h[~h.index.duplicated()]

def cost(s):
    m = S4.E.loc[s, "med_spread_2026"] if s in S4.E.index else np.nan
    return max(float(m) if m == m else 0.0, 0.0001) + 0.00005

def bands(s, anchor, last, ex, lb=14):
    """per day: the closes of bars anchor..ex, the anchor open, prev-day exit close and sigma_k (lagged)"""
    h = bars(s); hr = h.index.hour; sel = (hr >= anchor) & (hr <= ex)
    O = h.open[hr == anchor]; O.index = O.index.normalize()
    Cl = pd.DataFrame({"c": h.close[sel], "d": h.index[sel].normalize(), "k": hr[sel]}).pivot_table(index="d", columns="k", values="c")
    Cl = Cl.dropna(); Cl = Cl[Cl.index.isin(O.index)]; o = O.reindex(Cl.index)
    chk = list(range(anchor, last + 1)); prev = Cl[ex].shift(1)
    sig = Cl[chk].div(o, axis=0).sub(1).abs().rolling(lb).mean().shift(1)
    up = pd.concat([o, prev], axis=1).max(1); lo = pd.concat([o, prev], axis=1).min(1)
    return Cl, chk, up, lo, sig, prev

def strat(s, anchor, last, ex, sgn=1):
    Cl, chk, up, lo, sig, prev = bands(s, anchor, last, ex); tc = cost(s)
    out = pd.Series(0.0, index=Cl.index)
    for d in Cl.index[16:]:
        if np.isnan(prev[d]) or sig.loc[d].isna().any(): continue
        q = 0; r = 0.0; lastc = None
        for k in chk + [ex]:
            c = Cl.at[d, k]
            if lastc is not None and q != 0: r += q * (c / lastc - 1)
            lastc = c
            if k == ex: nq = 0
            else:
                U = up[d] * (1 + sig.at[d, k]); L = lo[d] * (1 - sig.at[d, k])
                nq = sgn * (1 if c > U else (-1 if c < L else 0))
            r -= abs(nq - q) * tc; q = nq
        out[d] = r
    return out

def sharpe(x): return x.mean() / x.std() * np.sqrt(365)

if __name__ == "__main__":
    base = S4.C["C1"] + S4.C["I2"]; idx = base.index
    a, b = ("2025-10-25", "2026-10-30") if HOLD else ("2010", "2025-10-24")
    print(f"--- {'HOLDOUT' if HOLD else 'EXPLORATION'} {a}..{b}")
    S2.rep(base, "C1+I2", a, b); sb = sharpe(base.loc[a:b])
    R = {}
    for nm, (s, an, la, ex) in COMP.items():
        x = S4.scale_s(strat(s, an, la, ex)); R[nm] = x
        x = x.reindex(idx).fillna(0); xs = x.loc[a:b]; xs = xs.loc[xs.ne(0).idxmax():] if not HOLD else xs
        y = xs.groupby(xs.index.year).apply(lambda z: (1 + z).prod() - 1)
        lift = sharpe((base + 0.5 * x).loc[a:b]) - sb
        print(f"{nm} {s:11s}", end=" "); S2.rep(xs, "", xs.index[0], b)
        print(f"     corr C1 {S4.C['C1'].loc[a:b].corr(x.loc[a:b]):+.2f} I2 {S4.C['I2'].loc[a:b].corr(x.loc[a:b]):+.2f} | "
              f"lift +0.5x: {lift:+.2f} | pass: Sh {sharpe(xs) >= 0.5} years {(y > 0).mean() >= 0.6} lift {lift >= 0.1}")
    os.makedirs("data/derived/growth", exist_ok=True)
    pd.DataFrame(R).to_csv("data/derived/growth/noise_more_daily.csv")
