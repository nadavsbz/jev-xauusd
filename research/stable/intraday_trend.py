"""Intraday crypto trend (docs/STABLE_SYSTEM_PLAN.md, after S2; the AdaptiveTrend preprint, arXiv 2602.11708, uses 6h signals).
RoboForex-Pro H1 bars resampled to BAR hours (crypto trades 7 days). Same Donchian ensemble as S1/S2 with lookbacks in bars
{10,20,30,60,90,150,250}; enter at the N-bar high (low for shorts), exit at the N/2-bar opposite extreme; signal = mean state.
Position = signal x 10% / realized vol (60 bars), decided at a bar close, held over the next bar; component scaled to TARGET
annual vol by its own trailing vol (lagged). Costs: the 2026 median bar spread per turnover (see TC), 4.75%/yr financing. Env CRY=list of coins, SPREADX=cost multiplier.
EXPLORATION ONLY: 2019-2025 is seen; holdout 25.10.2025-today stays clean.
Metals (XAU/XAG): same rule, financing per direction from the measured swap (charges only).
Usage: python research/stable/intraday_trend.py [BAR_HOURS=6] [TARGET=0.20]"""
import glob, os, sys
import numpy as np, pandas as pd

BAR = int(sys.argv[1]) if len(sys.argv) > 1 else 6
TARGET = float(sys.argv[2]) if len(sys.argv) > 2 else 0.20
PER_YEAR = 365 * 24 / BAR
K = pd.read_csv("data/derived/rf_costs_20261030.csv").set_index("symbol")
CRY = os.environ.get("CRY", "BTCUSD,ETHUSD,XRPUSD,SOLUSD").split(",")
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

# turnover cost = median spread of the 2026 H1 bars (the only year the server stores bar spreads), x SPREADX for slippage;
# for BTC/ETH/XRP/SOL this is 0.02/0.07/0.36/0.29% (30.10.2026), far above the one-tick snapshot used before
SPREADX = float(os.environ.get("SPREADX", "1.0"))
TC = {}
for s in CRY + MET:
    f = f"data/derived/intraday/{s}_H1.csv"
    if os.path.exists(f):
        d = pd.read_csv(f); d = d[d.time >= 1767225600]
        TC[s] = float((d.spread * K.loc[s, "point"] / d.close).median()) * SPREADX

# Codex PR 44 (2xP1): (1) the weight computed at close t is executed at close t+1 and earns from t+1 on (LAG=2; LAG=1 = executed
# at the signal close, the old optimistic timing); (2) the vol-target multiplier is applied to the WEIGHTS, and turnover and
# financing are charged on the final combined weights, so resizing by the multiplier pays costs too.
LAG = int(os.environ.get("LAG", "2"))

def weights(long_only, group=CRY):
    """vol-targeted weights of one component, known at each bar close"""
    cols = [s for s in C.columns if s in group]
    W = pd.DataFrame({s: donch(C[s].dropna(), long_only).reindex(C.index) * (0.10 / vol[s]).clip(upper=3) / len(cols) for s in cols}).fillna(0)
    r0 = (W.shift(LAG) * R[cols]).sum(axis=1)   # the component's own return, for its realized vol (known at close t)
    v = r0.rolling(int(PER_YEAR / 4), min_periods=60).std() * np.sqrt(PER_YEAR)
    return W.mul((TARGET / v).clip(upper=3).fillna(0), axis=0)

def net(F):
    """net return of final weights F (decided at close t, held from close t+LAG-1 to t+LAG)"""
    cols = list(F.columns); held = F.shift(LAG).fillna(0)
    tc = pd.Series({s: TC[s] for s in cols})
    fl = pd.Series({s: fin(s, 1) for s in cols}); fs = pd.Series({s: fin(s, -1) for s in cols})
    return (held * R[cols]).sum(axis=1) - (held.diff().abs() * tc).sum(axis=1) - (held.clip(lower=0) * fl + (-held).clip(lower=0) * fs).sum(axis=1) / PER_YEAR

def comp(long_only, group=CRY): return net(weights(long_only, group))

def mix(group=CRY): return net(0.5 * weights(True, group) + 0.5 * weights(False, group))   # C1: netted like the EA

def rep(r, nm):
    x = r.loc["2018":"2025-10-24"]; eq = (1 + x).cumprod(); y = x.groupby(x.index.year).apply(lambda z: (1 + z).prod() - 1) * 100
    yrs = (x.index[-1] - x.index[0]).days / 365.25
    print(f"{nm:12s} CAGR {(eq.iloc[-1] ** (1 / yrs) - 1) * 100:5.1f}% Sh {x.mean() / x.std() * PER_YEAR ** .5:4.2f} MDD {(eq / eq.cummax() - 1).min() * 100:5.1f}% |",
          " ".join(f"{int(k) % 100:02d}:{v:+.0f}" for k, v in y.items()))
    return x

if __name__ == "__main__":
    print("bar", BAR, "h, assets", list(C.columns))
    L = rep(comp(True), f"long{BAR}h"); LS = rep(comp(False), f"ls{BAR}h")
    M = rep(mix(), f"mix{BAR}h")
    if os.environ.get("MET"):
        ML = rep(comp(True, MET), f"metL{BAR}h"); MLS = rep(comp(False, MET), f"metLS{BAR}h"); MM = rep(mix(MET), f"metmix{BAR}h")
