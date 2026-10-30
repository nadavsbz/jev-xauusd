"""Intraday crypto trend (docs/STABLE_SYSTEM_PLAN.md, after S2; the AdaptiveTrend preprint, arXiv 2602.11708, uses 6h signals).
RoboForex-Pro H1 bars resampled to BAR hours (crypto trades 7 days). Same Donchian ensemble as S1/S2 with lookbacks in bars
{10,20,30,60,90,150,250}; enter at the N-bar high (low for shorts), exit at the N/2-bar opposite extreme; signal = mean state.
Position = signal x 10% / realized vol (60 bars), decided at a bar close, held over the next bar; component scaled to TARGET
annual vol by its own trailing vol (lagged). Costs: full spread per turnover (rf_costs_20261030.csv), 4.75%/yr financing.
EXPLORATION ONLY: 2019-2025 is seen; holdout 25.10.2025-today stays clean.
Metals (XAU/XAG): same rule, financing per direction from the measured swap (charges only).
Usage: python research/stable/intraday_trend.py [BAR_HOURS=6] [TARGET=0.20]"""
import glob, os, sys
import numpy as np, pandas as pd

BAR = int(sys.argv[1]) if len(sys.argv) > 1 else 6
TARGET = float(sys.argv[2]) if len(sys.argv) > 2 else 0.20
PER_YEAR = 365 * 24 / BAR
K = pd.read_csv("data/derived/rf_costs_20261030.csv").set_index("symbol")
CRY = ["BTCUSD", "ETHUSD", "XRPUSD", "SOLUSD"]
MET = ["XAUUSD", "XAGUSD"]

C = {}
for s in CRY + MET:
    f = f"data/derived/intraday/{s}_H1.csv"
    if not os.path.exists(f): continue
    d = pd.read_csv(f); d.index = pd.to_datetime(d.time, unit="s")
    C[s] = d.close.resample(f"{BAR}h").last()
C = pd.DataFrame(C).loc["2017-07-01":].ffill(limit=2)
R = C.pct_change(fill_method=None)
vol = R.rolling(60, min_periods=40).std() * np.sqrt(PER_YEAR)

def donch(c, long_only):
    st = []
    for n in (10, 20, 30, 60, 90, 150, 250):
        hi, lo = c.rolling(n).max().values, c.rolling(n).min().values
        xl, xh = c.rolling(n // 2).min().values, c.rolling(n // 2).max().values
        cv = c.values; p = np.zeros(len(c))
        for i in range(1, len(c)):
            q = p[i - 1]
            if q == 0: q = 1 if cv[i] >= hi[i] else (-1 if (not long_only and cv[i] <= lo[i]) else 0)
            elif q > 0 and cv[i] <= xl[i]: q = 0
            elif q < 0 and cv[i] >= xh[i]: q = 0
            p[i] = q
        st.append(p)
    return pd.Series(np.mean(st, axis=0), index=c.index)

def fin(s, side):
    k = K.loc[s]; sw = k.swap_long if side > 0 else k.swap_short
    return max(0.0, -(sw / 100 if k.swap_mode == 5 else sw * k.point / k.price * 365))

def comp(long_only, group=CRY):
    cols = [s for s in C.columns if s in group]
    W = pd.DataFrame({s: donch(C[s].dropna(), long_only).reindex(C.index) * (0.10 / vol[s]).clip(upper=3) / len(cols) for s in cols}).fillna(0)
    held = W.shift(1)
    tc = pd.Series({s: K.loc[s, "spread_pts"] * K.loc[s, "point"] / K.loc[s, "price"] if K.loc[s, "spread_pts"] else 0.001 for s in cols})
    r = (held * R[cols]).sum(axis=1) - (held.diff().abs() * tc).sum(axis=1) - (held.clip(lower=0) * pd.Series({s: fin(s, 1) for s in cols}) + (-held).clip(lower=0) * pd.Series({s: fin(s, -1) for s in cols})).sum(axis=1) / PER_YEAR
    v = r.rolling(int(PER_YEAR / 4), min_periods=60).std() * np.sqrt(PER_YEAR)
    return r * (TARGET / v).clip(upper=3).shift(1).fillna(0)

def rep(r, nm):
    x = r.loc["2018":"2025-10-24"]; eq = (1 + x).cumprod(); y = x.groupby(x.index.year).apply(lambda z: (1 + z).prod() - 1) * 100
    yrs = (x.index[-1] - x.index[0]).days / 365.25
    print(f"{nm:12s} CAGR {(eq.iloc[-1] ** (1 / yrs) - 1) * 100:5.1f}% Sh {x.mean() / x.std() * PER_YEAR ** .5:4.2f} MDD {(eq / eq.cummax() - 1).min() * 100:5.1f}% |",
          " ".join(f"{int(k) % 100:02d}:{v:+.0f}" for k, v in y.items()))
    return x

if __name__ == "__main__":
    print("bar", BAR, "h, assets", list(C.columns))
    L = rep(comp(True), f"long{BAR}h"); LS = rep(comp(False), f"ls{BAR}h")
    M = rep((L + LS) / 2, f"mix{BAR}h")
    ML = rep(comp(True, MET), f"metL{BAR}h"); MLS = rep(comp(False, MET), f"metLS{BAR}h")
    MM = rep((ML + MLS) / 2, f"metmix{BAR}h")
    for w in (0.5, 0.67):
        rep(w * M + (1 - w) * MM, f"cry{int(w*100)}+met")
