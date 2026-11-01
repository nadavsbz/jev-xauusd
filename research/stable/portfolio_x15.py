"""Portfolio check at the chosen risk (docs/STABLE_SYSTEM_PLAN.md, user 1.11.2026: x1.5, max drawdown 25%, ramp to x2), from tester
runs that size themselves: C1 AssetVol 0.15 (continuous 1.2020-30.10.2026, Pro and ECN) and IndexNoise TargetVol 0.15 (.USTECHCash,
one run per year + holdout, each from 120,000; it is flat every night, so a day's return = the day's P&L / the run's equity before it).
Portfolio = half the capital in each bot, re-balanced daily (= both bots in one account, each sized on half the equity).
x2 = the same daily returns x 4/3. Pre-registered bar: every year positive and MDD <= 15% at x1.5.
Usage: python research/stable/portfolio_x15.py"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals

def i2_daily(prefix):
    out = []
    for p in list(range(2020, 2026)) + ["holdout"]:
        x = deals(f"C:/MT5_JEV_TEST/{prefix}_{p}.htm"); x = x[x.symbol == ".USTECHCash"]
        x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize()
        pnl = (x.profit + x.swap + x.commission).groupby(x.day).sum()
        eq = 120000 + pnl.cumsum(); out.append(pnl / eq.shift(1).fillna(120000))
    return pd.concat(out)

def rep(x, nm, a="2020", b="2026-10-30"):
    x = x.loc[a:b]; eq = (1 + x).cumprod(); yrs = (x.index[-1] - x.index[0]).days / 365.25
    y = x.groupby(x.index.year).apply(lambda z: (1 + z).prod() - 1) * 100
    print(f"{nm:22s} CAGR {(eq.iloc[-1] ** (1 / yrs) - 1) * 100:5.1f}% Sh {x.mean() / x.std() * np.sqrt(365):5.2f} MDD {(eq / eq.cummax() - 1).min() * 100:6.1f}% |",
          " ".join(f"{int(k) % 100:02d}:{v:+.0f}" for k, v in y.items()), f"| pos {int((y > 0).sum())}/{len(y)}")

i2 = i2_daily("in2_tv15")
for srv in ("c1r5_ls05_av15_full", "c1_ecn_av15_full"):
    c = pd.read_csv(f"data/derived/c1_equity/{srv}_equity.csv", index_col=0, parse_dates=True).equity.pct_change().dropna()
    n = i2.reindex(c.index).fillna(0); p = 0.5 * c + 0.5 * n
    print(f"--- C1 from {srv}; corr C1/Nasdaq {c.corr(n):.2f}")
    rep(c, "C1 x1.5 alone"); rep(n, "Nasdaq x1.5 alone"); rep(p, "portfolio x1.5"); rep(p * 4 / 3, "portfolio x2")
    rep(p, "  holdout x1.5", "2025-10-25"); rep(p * 4 / 3, "  holdout x2", "2025-10-25")
