"""Multi-asset time-series momentum on RoboForex daily bars (docs/HYBRID_PLAN.md, step 1; Hurst, Ooi & Pedersen 2017).
Signal per asset at each daily close: average of sign(return over 21, 63, 252 days) (in [-1, 1]); position = signal x
(asset vol target / 60-day realized vol), traded at the NEXT close (no look-ahead); portfolio rescaled every day by its own
60-day realized vol to TARGET annual vol (lagged one day).
Costs: half the median daily-bar spread on every unit of turnover (spread column x point / price), plus a financing cost on gross
notional per year: FX/metals 2%, crypto 15% (RoboForex swaps not recorded; ASSUMED, conservative).
Prints calendar-year returns, CAGR, max drawdown and Sharpe; development 2012-2019, test 2020-2026 (rules fixed before the run).
Usage: python research/hybrid/tsmom.py [TARGET_VOL=0.15]"""
import glob, os, sys
import numpy as np, pandas as pd

TARGET = float(sys.argv[1]) if len(sys.argv) > 1 else 0.15
spec = pd.read_csv("data/derived/symspec.csv").drop_duplicates("symbol", keep="last").set_index("symbol")

def point(sym, px):
    if sym in spec.index: return spec.loc[sym, "point"]
    if sym.endswith("JPY"): return 0.001
    if sym[:3] in ("BTC", "ETH", "LTC", "XRP"): return 0.01 if px > 10 else 0.0001
    return 0.00001

closes, costs = {}, {}
for f in sorted(glob.glob("data/derived/daily/*_D1.csv")):
    s = os.path.basename(f)[:-7]
    d = pd.read_csv(f); d.index = pd.to_datetime(d.time, unit="s").dt.normalize()
    d = d[~d.index.duplicated()]
    if len(d) < 500: continue
    closes[s] = d.close
    costs[s] = (d.spread * point(s, d.close.median()) / d.close).rolling(250, min_periods=20).median()
C = pd.DataFrame(closes).sort_index().ffill(limit=3)
R = np.log(C).diff()            # log returns: signals and volatility only
S = C.pct_change()              # simple returns: P&L (Codex PR 42, P1: a weighted sum of log returns is not the portfolio return)
crypto = [s for s in C if s[:3] in ("BTC", "ETH", "LTC", "XRP")]
fin = pd.Series({s: (0.15 if s in crypto else 0.02) for s in C})   # per year, charged by calendar days (Codex PR 42, P2)
PPY = len(C.loc["2015":"2025"]) / 11                                  # observations per year of THIS calendar (252 or ~365 with crypto)

sig = sum(np.sign(np.log(C / C.shift(n))) for n in (21, 63, 252)) / 3
vol = R.rolling(60, min_periods=40).std() * np.sqrt(PPY)
w = (sig * (0.40 / vol)).clip(-4, 4)                  # per-asset 40% vol before the portfolio scaling
w = w.div(w.notna().sum(axis=1), axis=0)              # equal risk budget across the assets alive that day
# signal at close t-1 is EXECUTED at close t, so it earns from close t to close t+1: the held weight is w.shift(2)
# (Codex PR 42, P1: shift(1) credited the move from the very close the signal was computed on)
gross = (w.shift(2) * S).sum(axis=1)
pv = gross.rolling(60, min_periods=40).std() * np.sqrt(PPY)
scale = (TARGET / pv).shift(1).clip(upper=10)
W = w.mul(scale, axis=0)
H = W.shift(1)                                   # the weight decided at close t-1 and executed at close t ...
ret = (H.shift(1) * S).sum(axis=1)               # ... is held from close t to close t+1
tc = (H.diff().abs() * pd.DataFrame(costs).reindex(W.index).ffill() / 2).sum(axis=1)   # turnover cost on the execution day
days = pd.Series(C.index, index=C.index).diff().dt.days.fillna(1)
fc = (H.shift(1).abs() * fin).sum(axis=1) * days / 365
net = (ret - tc - fc).loc["2011-06-01":]          # simple daily return of the account
eq = (1 + net).cumprod()
yr = (1 + net).groupby(net.index.year).prod() - 1
dd = (eq / eq.cummax() - 1)
print(f"assets: {len(C.columns)} ({', '.join(C.columns)}); target vol {TARGET:.0%}")
print("calendar years:", " ".join(f"{y}:{v:+.0%}" for y, v in yr.items()))
for a, b in (("2012", "2019"), ("2020", "2026")):
    n = net.loc[a:b]; e = (1 + n).cumprod()
    yrs = (n.index[-1] - n.index[0]).days / 365.25
    print(f"{a}-{b}: CAGR {e.iloc[-1] ** (1 / yrs) - 1:+.1%}  Sharpe {n.mean() / n.std() * np.sqrt(PPY):.2f}  maxDD {(e / e.cummax() - 1).min():.1%}  "
          f"costs/yr {tc.loc[a:b].sum() / yrs:.1%} fin/yr {fc.loc[a:b].sum() / yrs:.1%}")
corr_gold = net.loc["2022":].corr(S["XAUUSD"].loc["2022":]) if "XAUUSD" in R else np.nan
print(f"daily correlation with gold 2022+: {corr_gold:.2f}")
