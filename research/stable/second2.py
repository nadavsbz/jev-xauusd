"""Second component for C1, round 2: metals (pre-registered 1.11.2026 in docs/STABLE_SYSTEM_PLAN.md, same bar as second.py).
  G1  gold/silver ratio trend: C1's Donchian ensemble on XAU/XAG; long XAG / short XAU dollar-neutral (or the reverse), daily bars
  G2  gold/silver ratio mean reversion: z of log(ratio) vs its 20-day mean/std; in at +-1.5, out inside 0.25, daily bars
  G3  gold Asian session: long XAUUSD from the 01:00 server open to the 10:00 open (before London), flat over the rollover
  G4  gold New York session: short XAUUSD from the 16:00 open to the 23:00 open (the complement hypothesis)
Hours fixed in advance (web: "gold rises overnight, falls in US hours"), not picked from the data. Costs: median 2026 spread per
entry and exit; swap per the RF table (intraday_trend.fin) on daily legs. Each scaled to 10% annual vol by its own lagged 90-day vol.
Usage: python research/stable/second2.py [hold]"""
import sys
import numpy as np, pandas as pd
HOLD = len(sys.argv) > 1 and sys.argv[1] == "hold"; sys.argv = sys.argv[:1]
import second as S2
T = S2.T

def load(s):
    d = pd.read_csv(f"data/derived/daily/{s}_D1.csv"); d.index = pd.DatetimeIndex(pd.to_datetime(d.time, unit="s")).normalize(); return d.close[~d.index.duplicated()]
M = pd.DataFrame({s: load(s) for s in ("XAUUSD", "XAGUSD")}).loc["2016":].dropna(); RM = M.pct_change().fillna(0)

def net_d(W):
    """daily net return of metal weights W decided at close t, held from t+1 (LAG 2 as C1); swap on trading days x 7/5"""
    h = W.shift(2).fillna(0); c = list(W.columns)
    t = pd.Series({s: T.TC[s] for s in c}); fl = pd.Series({s: T.fin(s, 1) for s in c}); fs = pd.Series({s: T.fin(s, -1) for s in c})
    return (h * RM[c]).sum(1) - (h.diff().abs() * t).sum(1) - (h.clip(lower=0) * fl + (-h).clip(lower=0) * fs).sum(1) / 365 * 7 / 5

def scale_d(W):
    r0 = (W.shift(2) * RM[W.columns]).sum(1); v = r0.rolling(90, min_periods=60).std() * np.sqrt(260)
    return W.mul((0.10 / v).clip(upper=5).fillna(0), axis=0)

lr = np.log(M.XAUUSD / M.XAGUSD)
def ratio_w(sig): return pd.DataFrame({"XAGUSD": sig, "XAUUSD": -sig}).reindex(M.index).fillna(0)   # +1 = silver beats gold
G1 = net_d(scale_d(ratio_w(-T.donch(np.exp(lr), False))))      # ratio up = gold beats silver -> short the ratio legs reversed
z = (lr - lr.rolling(20).mean()) / lr.rolling(20).std(); s2 = np.zeros(len(z)); q = 0
for i, v in enumerate(z.values):
    if np.isnan(v): continue
    if q == 0 and v > 1.5: q = 1          # ratio high -> expect silver to catch up: long XAG / short XAU
    elif q == 0 and v < -1.5: q = -1
    elif q != 0 and abs(v) < 0.25: q = 0
    s2[i] = q
G2 = net_d(scale_d(ratio_w(pd.Series(s2, index=z.index))))

h = pd.read_csv("data/derived/intraday/XAUUSD_H1.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
tc = T.TC["XAUUSD"]
def session(a, b, side):
    """gross daily return of holding XAUUSD from the a:00 open to the b:00 open, minus one entry and one exit spread"""
    x = h[(h.index.hour >= a) & (h.index.hour < b)]
    d = x.groupby(x.index.normalize()).agg(o=("open", "first"), c=("close", "last"))
    return side * (d.c / d.o - 1) - 2 * tc
def scale_s(r):
    v = r.rolling(90, min_periods=60).std().shift(1) * np.sqrt(260)
    return r * (0.10 / v).clip(upper=5).fillna(0)
G3 = scale_s(session(1, 10, 1)); G4 = scale_s(session(16, 23, -1))

C = {"C1": S2.S["C1"]}
for nm, x in (("G1", G1), ("G2", G2), ("G3", G3), ("G4", G4)): C[nm] = x.reindex(C["C1"].index).fillna(0)

if __name__ == "__main__":
    a, b = ("2025-10-25", "2026-10-30") if HOLD else ("2018", "2025-10-24")
    for nm, x in C.items(): S2.rep(x, nm, a, b)
    print("corr with C1:", {k: round(C["C1"].loc[a:b].corr(v.loc[a:b]), 2) for k, v in C.items() if k != "C1"})
    for nm in ("G1", "G2", "G3", "G4"):
        for k in (0.5, 1.0): S2.rep(C["C1"] + k * C[nm], f"C1+{k}x{nm}", a, b)
