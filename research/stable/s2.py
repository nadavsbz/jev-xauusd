"""Stable system S2 = S1 with the broker's measured costs (data/derived/rf_costs_20261030.csv, RoboForex-Pro 30.10.2026):
financing per direction from the current swap (charges only; a positive swap is ignored, conservative), turnover cost = the full
current spread (half spread + the same again for slippage), the S1 class default when the server shows spread 0.
ASSUMED: today's swaps stand for the whole history (rate differentials were different in 2010-2021).
--- S1 docstring ---
Stable system S1 (docs/STABLE_SYSTEM_PLAN.md, pre-registered 30.10.2026): a portfolio of documented, independent edges on
RoboForex daily bars. No grid, no martingale; every position sized by volatility; decided at close t-1, held over day t.
Components (fixed rules from the literature, not optimized):
  A  time-series momentum on every asset: mean of sign(21/63/252-day return), position = signal x 10% / 60d vol
  B  RSI(2) dip-buying on stock indices (if the server has them): long when RSI2 < 10 and close > SMA200, out when close > SMA5
  C  gold long when close > SMA200
Costs: fixed per asset class (plan table) on turnover + financing per calendar day on gross exposure.
Each component is scaled to 10% annual vol by its own 60-day realized vol (lagged one day, capped at 3x gross leverage per unit).
Usage: python research/stable/s1.py [dev|test|holdout]   (dev = 2010-2018; test = 2019..2025-10-24, run once after freezing)"""
import glob, os, sys
import numpy as np, pandas as pd

PERIOD = sys.argv[1] if len(sys.argv) > 1 else "dev"
SPAN = {"dev": ("2010-01-01", "2018-12-31"), "test": ("2019-01-01", "2025-10-24"), "holdout": ("2025-10-25", "2030-01-01")}[PERIOD]
MAJ = {"EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "NZDUSD"}
IDX = {"US500", "SP500", "US30", "NAS100", "USTEC", "GER40", "DE40", "UK100", "JP225"}
NRG = {"XTIUSD", "XBRUSD", "WTI", "BRENT", "XNGUSD"}
CRY = {"BTCUSD", "ETHUSD", "LTCUSD", "XRPUSD", "ADAUSD", "SOLUSD", "DOGEUSD"}
MET = {"XAUUSD", "XAGUSD", "XAUEUR", "XPTUSD", "XPDUSD"}

def cls(s):
    if s in MAJ: return 0.00010, 0.02
    if s in MET: return 0.00020, 0.02
    if s in IDX or s in NRG: return 0.00020, 0.03
    if s in CRY: return 0.00100, 0.15
    return 0.00025, 0.03

C = {}
for f in sorted(glob.glob("data/derived/daily/*_D1.csv")):
    s = os.path.basename(f)[:-7]
    d = pd.read_csv(f); d.index = pd.to_datetime(d.time, unit="s").dt.normalize(); d = d[~d.index.duplicated()]
    if len(d) >= 300: C[s] = d.close
C = pd.DataFrame(C).sort_index()
C = C[C.index.dayofweek < 5].ffill(limit=3)
R = C.pct_change(fill_method=None)
days = pd.Series(C.index, index=C.index).diff().dt.days.fillna(1)   # calendar days per bar, for financing
vol = R.rolling(60, min_periods=40).std() * np.sqrt(252)

K = pd.read_csv("data/derived/rf_costs_20261030.csv").set_index("symbol")
def fin_rate(s, side):
    if s not in K.index or pd.isna(K.loc[s, "price"]): return cls(s)[1]
    k = K.loc[s]; sw = k.swap_long if side > 0 else k.swap_short
    a = sw / 100 if k.swap_mode == 5 else sw * k.point / k.price * 365
    return max(0.0, -a)
def tc_rate(s):
    if s not in K.index or pd.isna(K.loc[s, "price"]) or K.loc[s, "spread_pts"] == 0: return cls(s)[0]
    return K.loc[s, "spread_pts"] * K.loc[s, "point"] / K.loc[s, "price"]
def run(W):
    """W: target weights decided at close t (index t); held over t+1. Returns daily net return of the component."""
    held = W.shift(1)
    tc = pd.Series({s: tc_rate(s) for s in W.columns})
    fl = pd.Series({s: fin_rate(s, 1) for s in W.columns}); fs = pd.Series({s: fin_rate(s, -1) for s in W.columns})
    gross = (held * R[W.columns]).sum(axis=1)
    cost = (held.diff().abs() * tc).sum(axis=1) + (held.clip(lower=0) * fl + (-held).clip(lower=0) * fs).sum(axis=1) * days / 365
    return gross - cost

def scale(r, target=0.10):
    v = r.rolling(60, min_periods=40).std() * np.sqrt(252)
    k = (target / v).clip(upper=3).shift(1).fillna(0)
    return r * k

comp = {}
# A: time-series momentum
sig = sum(np.sign(C / C.shift(n) - 1) for n in (21, 63, 252)) / 3
WA = (sig * 0.10 / vol).clip(-3, 3) / max(1, C.shape[1]) * np.sqrt(C.shape[1])   # equal risk, ~diversified unit
comp["A_tsmom"] = scale(run(WA.fillna(0)))
# B: RSI2 dips on indices
ix = [s for s in C.columns if s in IDX]
if ix:
    WB = pd.DataFrame(0.0, index=C.index, columns=ix)
    for s in ix:
        c = C[s]; dlt = c.diff(); up = dlt.clip(lower=0).ewm(alpha=0.5).mean(); dn = (-dlt.clip(upper=0)).ewm(alpha=0.5).mean()
        rsi = 100 - 100 / (1 + up / dn); sma200 = c.rolling(200).mean(); sma5 = c.rolling(5).mean()
        pos = np.zeros(len(c))
        for i in range(1, len(c)):
            p = pos[i - 1]
            if p == 0 and rsi.iloc[i] < 10 and c.iloc[i] > sma200.iloc[i]: p = 1
            elif p == 1 and c.iloc[i] > sma5.iloc[i]: p = 0
            pos[i] = p
        WB[s] = pos * (0.10 / vol[s]).clip(upper=3) / len(ix)
    comp["B_rsi2"] = scale(run(WB.fillna(0)))
    # E: indices long above SMA200 (Faber)
    WE = pd.DataFrame({s: (C[s] > C[s].rolling(200).mean()).astype(float) * (0.10 / vol[s]).clip(upper=3) / len(ix) for s in ix})
    comp["E_idx200"] = scale(run(WE.fillna(0)))
# F / G: Donchian ensemble (Zarattini, Pagani & Barbon 2025 for crypto, long only; long-short on FX and metals)
def donch(c, long_only):
    st = []
    for n in (10, 20, 30, 60, 90, 150, 250):
        hi, lo = c.rolling(n).max(), c.rolling(n).min(); xl, xh = c.rolling(n // 2).min(), c.rolling(n // 2).max()
        p = np.zeros(len(c)); cv, hv, lv, xlv, xhv = c.values, hi.values, lo.values, xl.values, xh.values
        for i in range(1, len(c)):
            q = p[i - 1]
            if q == 0:
                q = 1 if cv[i] >= hv[i] else (-1 if (not long_only and cv[i] <= lv[i]) else 0)
            elif q > 0 and cv[i] <= xlv[i]: q = 0
            elif q < 0 and cv[i] >= xhv[i]: q = 0
            p[i] = q
        st.append(p)
    return pd.Series(np.mean(st, axis=0), index=c.index)
cr = [s for s in C.columns if s in CRY]
if cr:
    WF = pd.DataFrame({s: donch(C[s].dropna(), True).reindex(C.index) * (0.10 / vol[s]).clip(upper=3) / len(cr) for s in cr})
    comp["F_cryDon"] = scale(run(WF.fillna(0)))
fx = [s for s in C.columns if s not in CRY | IDX | NRG]
WG = pd.DataFrame({s: donch(C[s].dropna(), False).reindex(C.index) * (0.10 / vol[s]).clip(upper=3) / np.sqrt(len(fx)) for s in fx})
comp["G_fxDon"] = scale(run(WG.fillna(0)))
# H: the same ensemble, long only, on metals (added 30.10 after the first dev look: FX long-short failed, crypto long-only passed)
mt = [s for s in C.columns if s in MET]
WH = pd.DataFrame({s: donch(C[s].dropna(), True).reindex(C.index) * (0.10 / vol[s]).clip(upper=3) / len(mt) for s in mt})
comp["H_metDon"] = scale(run(WH.fillna(0)))
# C: gold above SMA200
g = C["XAUUSD"]; WC = pd.DataFrame({"XAUUSD": (g > g.rolling(200).mean()).astype(float) * (0.10 / vol["XAUUSD"]).clip(upper=3)})
comp["C_gold200"] = scale(run(WC.fillna(0)))

P = pd.DataFrame(comp).loc[SPAN[0]:SPAN[1]]
def stats(r):
    eq = (1 + r).cumprod(); dd = (eq / eq.cummax() - 1).min()
    yrs = (r.index[-1] - r.index[0]).days / 365.25
    return dict(cagr=eq.iloc[-1] ** (1 / yrs) - 1, sharpe=r.mean() / r.std() * np.sqrt(252), mdd=dd)
print("assets:", C.shape[1], "indices:", ix, "| period", PERIOD, SPAN)
Y = P.groupby(P.index.year).apply(lambda x: (1 + x).prod() - 1) * 100
P["EQW"] = P.mean(axis=1); P["EQW"] = scale(P["EQW"].reindex(P.index))   # risk-equal mix, rescaled to 10%
Y["EQW"] = P["EQW"].groupby(P.index.year).apply(lambda x: (1 + x).prod() - 1) * 100
print(Y.round(1).to_string())
for k in P: print(k, {a: round(b, 3) for a, b in stats(P[k].dropna()).items()})
print("corr\n", P.corr().round(2).to_string())
