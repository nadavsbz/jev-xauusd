"""C1 + I2 portfolio from the MT5 tester runs (docs/STABLE_SYSTEM_PLAN.md, round 4). C1: the continuous 1.1.2020-30.10.2026 run
(c1r5_ls05_full, daily MTM equity saved by tester_sharpe.py). I2: IndexNoise on .USTECHCash, one run per year + holdout, 1 lot;
it is flat every night, so its day-end balance is its equity. I2's daily $ P&L per lot / (day open x contract 1) = its return per
1x notional, then scaled to 10% annual vol by its own lagged 90-day vol (as second4.py) and added to C1's daily return x k.
Usage: python research/stable/portfolio_c1i2.py"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals

c = pd.read_csv("data/derived/c1_equity/c1r5_ls05_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change().dropna()
x = pd.concat([deals(f"C:/MT5_JEV_TEST/in_ustech_{p}.htm") for p in list(range(2020, 2026)) + ["holdout"]])
x = x[x.symbol == ".USTECHCash"]; x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize()
pnl = (x.profit + x.swap + x.commission).groupby(x.day).sum()
h = pd.read_csv("data/derived/intraday/.USTECHCash_H1.csv"); h.index = pd.to_datetime(h.time, unit="s")
O = h.open[h.index.hour == 16]; O.index = O.index.normalize()
# the vol multiplier is computed on trading days (as second4.scale_s and the EA), then aligned to C1's calendar days
# (Codex PR 44, 1.11, P2: weekend zeros had lowered the vol estimate and raised the exposure by ~18%)
r = (pnl / O.reindex(pnl.index)).dropna(); r = r.reindex(O.loc[r.index[0]:r.index[-1]].index).fillna(0)
v = r.rolling(90, min_periods=60).std().shift(1) * np.sqrt(260); i2 = (r * (0.10 / v).clip(upper=5).fillna(0)).reindex(c.index).fillna(0)

def rep(x, nm, a="2020", b="2026-10-30"):
    x = x.loc[a:b]; eq = (1 + x).cumprod(); yrs = (x.index[-1] - x.index[0]).days / 365.25
    y = x.groupby(x.index.year).apply(lambda z: (1 + z).prod() - 1) * 100
    print(f"{nm:12s} CAGR {(eq.iloc[-1] ** (1 / yrs) - 1) * 100:5.1f}% Sh {x.mean() / x.std() * np.sqrt(365):5.2f} MDD {(eq / eq.cummax() - 1).min() * 100:6.1f}% |",
          " ".join(f"{int(k) % 100:02d}:{v:+.0f}" for k, v in y.items()), f"| pos {int((y > 0).sum())}/{len(y)}")

print("corr C1/I2:", round(c.corr(i2), 2))
for nm, s in (("C1", c), ("I2", i2), ("C1+0.5xI2", c + 0.5 * i2), ("C1+1.0xI2", c + i2)): rep(s, nm)
print("holdout 25.10.2025-30.10.2026:")
for nm, s in (("C1", c), ("I2", i2), ("C1+0.5xI2", c + 0.5 * i2), ("C1+1.0xI2", c + i2)): rep(s, nm, "2025-10-25")
