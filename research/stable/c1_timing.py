"""C1 timing diversification (pre-registered 1.11.2026 in docs/STABLE_SYSTEM_PLAN.md): C1 decides only at the closes of 6h bars
that start at server 00:00, so its result carries 'rebalance timing luck' (Hoffstein, Newfound Research).
  E1  the same C1 on 6h bars started at offsets 0..5h, equal weight
  E2  C1 on 4h, 6h and 12h bars, equal weight
Each run carries its own costs and the daily returns are averaged (conservative: one EA would net the positions).
Usage: python research/stable/c1_timing.py [hold]"""
import os, sys
import numpy as np, pandas as pd
HOLD = len(sys.argv) > 1 and sys.argv[1] == "hold"
os.environ["CRY"] = "BTCUSD,ETHUSD"; sys.argv = sys.argv[:1]
sys.path.insert(0, "research/stable"); import intraday_trend as T

H = {}
for s in T.CRY:
    d = pd.read_csv(f"data/derived/intraday/{s}_H1.csv"); d.index = pd.to_datetime(d.time, unit="s"); H[s] = d.close[~d.index.duplicated()]

def run(bar, off):
    """C1 daily net returns on bar-hour bars whose grid is shifted by off hours"""
    T.PER_YEAR = 365 * 24 / bar
    T.C = pd.DataFrame({s: H[s].resample(f"{bar}h", offset=f"{off}h").last() for s in T.CRY}).loc["2017-07-01":].ffill(limit=2)
    T.R = T.C.pct_change(fill_method=None); T.vol = T.R.rolling(60, min_periods=40).std() * np.sqrt(T.PER_YEAR)
    r = T.mix(); return (1 + r).groupby(r.index.normalize()).prod() - 1

def rep(x, nm, a, b):
    x = x.loc[a:b]; eq = (1 + x).cumprod(); yrs = (x.index[-1] - x.index[0]).days / 365.25
    y = x.groupby(x.index.year).apply(lambda z: (1 + z).prod() - 1) * 100
    print(f"{nm:10s} CAGR {(eq.iloc[-1] ** (1 / yrs) - 1) * 100:5.1f}% Sh {x.mean() / x.std() * np.sqrt(365):5.2f} MDD {(eq / eq.cummax() - 1).min() * 100:6.1f}% |",
          " ".join(f"{int(k) % 100:02d}:{v:+.0f}" for k, v in y.items()), f"| pos {int((y > 0).sum())}/{len(y)}", flush=True)

a, b = ("2025-10-25", "2026-10-30") if HOLD else ("2018", "2025-10-24")
O = {k: run(6, k) for k in range(6)}
for k, x in O.items(): rep(x, f"6h+{k}", a, b)
D = pd.DataFrame(O).fillna(0); rep(D.mean(1), "E1", a, b)
print("corr between offsets, mean:", round(D.loc[a:b].corr().values[np.triu_indices(6, 1)].mean(), 2))
F = {bar: run(bar, 0) for bar in (4, 12)}; F[6] = O[0]
for bar in (4, 12): rep(F[bar], f"{bar}h", a, b)
rep(pd.DataFrame(F).fillna(0).mean(1), "E2", a, b)
