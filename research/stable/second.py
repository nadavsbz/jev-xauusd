"""Second component for C1 (user 31.10.2026: "keep testing and improving, something with at least 20% a year"; the BD/C1 portfolio
failed its holdout). Wanted: a return stream that earns when C1 loses (C1 lost in 2022), net of costs, on RoboForex-Pro.
Daily bars, decided at a close and held from the next close (LAG 2 as C1), costs = measured spread per turnover + swap charges.
  R1  ETH/BTC ratio trend: C1's Donchian ensemble on the ratio; long ETH / short BTC dollar-neutral (or the reverse)
  R2  ETH/BTC ratio mean reversion: z of log(ratio) against its 20-day mean/std; -1 above +1.5, +1 below -1.5, out inside 0.25
  F1  FX RSI(2) both sides (Connors, as DIP in multi.py): long RSI2<10 above SMA200, short RSI2>90 below SMA200, out at SMA5
  F2  FX cross-sectional 5-day reversal: weight = minus the cross-sectional z of each pair's 5-day return (28 pairs)
Every component is scaled to 10% annual vol by its own trailing 90-day vol (lagged). EXPLORATION 2018-2025.10.24; the
holdout 25.10.2025-today is reported only for what passes the bar: Sharpe >= 0.5, correlation with C1 <= 0.2, and C1 + it
better than C1 alone (more positive years at no lower CAGR) - fixed before the run (docs/STABLE_SYSTEM_PLAN.md).
Usage: python research/stable/second.py"""
import os, sys
import numpy as np, pandas as pd
os.environ["CRY"] = "BTCUSD,ETHUSD"; sys.argv = sys.argv[:1]
sys.path.insert(0, "research/stable"); import intraday_trend as T

K = pd.read_csv("data/derived/rf_costs_20261030.csv").set_index("symbol")
FX = [s for s in K.index if len(s) == 6 and s[:3] in "EURGBPAUDNZDUSDCADCHFJPY" and s[3:] in "EURGBPAUDNZDUSDCADCHFJPY" and s != "XAUEUR"]
def load(s):
    d = pd.read_csv(f"data/derived/daily/{s}_D1.csv"); d.index = pd.DatetimeIndex(pd.to_datetime(d.time, unit="s")).normalize(); return d.close[~d.index.duplicated()]
P = pd.DataFrame({s: load(s) for s in FX + ["BTCUSD", "ETHUSD"]}).loc["2016":]
R = P.pct_change(fill_method=None).fillna(0)
def tc(s): return float(K.loc[s, "spread_pts"] * K.loc[s, "point"] / K.loc[s, "price"]) if s in FX else T.TC[s]

def net(W):
    """daily net return of weights W decided at close t (held from t+1)"""
    cols = list(W.columns); h = W.shift(2).fillna(0)
    t = pd.Series({s: tc(s) for s in cols}); fl = pd.Series({s: T.fin(s, 1) for s in cols}); fs = pd.Series({s: T.fin(s, -1) for s in cols})
    return (h * R[cols]).sum(1) - (h.diff().abs() * t).sum(1) - (h.clip(lower=0) * fl + (-h).clip(lower=0) * fs).sum(1) / 365

def scale(W, days=365):
    r0 = (W.shift(2) * R[W.columns]).sum(1); v = r0.rolling(90, min_periods=60).std() * np.sqrt(days)
    return W.mul((0.10 / v).clip(upper=5).fillna(0), axis=0)

lr = np.log(P.ETHUSD / P.BTCUSD).dropna()
def ratio_w(sig): return pd.DataFrame({"ETHUSD": sig, "BTCUSD": -sig}).reindex(P.index).fillna(0)
R1 = scale(ratio_w(T.donch(np.exp(lr), False)))
z = (lr - lr.rolling(20).mean()) / lr.rolling(20).std(); s2 = np.zeros(len(z)); q = 0
for i, v in enumerate(z.values):
    if np.isnan(v): s2[i] = 0; continue
    if q == 0 and v > 1.5: q = -1
    elif q == 0 and v < -1.5: q = 1
    elif q != 0 and abs(v) < 0.25: q = 0
    s2[i] = q
R2 = scale(ratio_w(pd.Series(s2, index=z.index)))

def rsi2(c):
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=0.5).mean(); dn = (-d.clip(upper=0)).ewm(alpha=0.5).mean(); return 100 - 100 / (1 + up / dn)
W1 = pd.DataFrame(0.0, index=P.index, columns=FX)
for s in FX:
    c = P[s].dropna(); r_ = rsi2(c).values; m200 = c.rolling(200).mean().values; m5 = c.rolling(5).mean().values; cv = c.values; p = np.zeros(len(c)); q = 0
    for i in range(len(c)):
        if q == 0 and r_[i] < 10 and cv[i] > m200[i]: q = 1
        elif q == 0 and r_[i] > 90 and cv[i] < m200[i]: q = -1
        elif (q == 1 and cv[i] > m5[i]) or (q == -1 and cv[i] < m5[i]): q = 0
        p[i] = q
    W1[s] = pd.Series(p, index=c.index).reindex(P.index).fillna(0) / len(FX)
F1 = scale(W1, 260)
r5 = P[FX].pct_change(5, fill_method=None)
F2 = scale(-(r5.sub(r5.mean(1), axis=0)).div(r5.std(1), axis=0).fillna(0) / len(FX), 260)

c1 = T.mix(); c1 = (1 + c1).groupby(c1.index.normalize()).prod() - 1   # C1 H6 net returns -> daily
S = {"C1": c1.reindex(P.index).fillna(0)}
for nm, W in (("R1", R1), ("R2", R2), ("F1", F1), ("F2", F2)): S[nm] = net(W)

def rep(x, nm, a="2018", b="2025-10-24"):
    x = x.loc[a:b]; eq = (1 + x).cumprod(); yrs = (x.index[-1] - x.index[0]).days / 365.25
    y = x.groupby(x.index.year).apply(lambda z: (1 + z).prod() - 1) * 100
    print(f"{nm:14s} CAGR {(eq.iloc[-1] ** (1 / yrs) - 1) * 100:5.1f}% Sh {x.mean() / x.std() * np.sqrt(365):5.2f} MDD {(eq / eq.cummax() - 1).min() * 100:6.1f}% |",
          " ".join(f"{int(k) % 100:02d}:{v:+.0f}" for k, v in y.items()), f"| pos {int((y > 0).sum())}/{len(y)}")

if __name__ == "__main__":
    for nm, x in S.items(): rep(x, nm)
    print("corr with C1 (2018-2025):", {k: round(S["C1"].loc["2018":"2025-10-24"].corr(v.loc["2018":"2025-10-24"]), 2) for k, v in S.items() if k != "C1"})
    for nm in ("R1", "R2", "F1", "F2"):
        for k in (0.5, 1.0):
            rep(S["C1"] + k * S[nm], f"C1+{k}x{nm}")
