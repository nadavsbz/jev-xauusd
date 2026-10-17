"""Exploratory (NOT pre-registered; asked by the user after the registered test): BTC Bot + Bull
Scalper (+ cash) without account 1, on their common period 2025-03-31..2026-10-13. BTC at $120k per
0.01 lot (full-period real-tick run), Bull = EGlobal real ticks with RoboForex costs. Both fixed lot:
daily P&L as a share of the starting allocation, added up. Max drawdown is realised-path drawdown plus
each tool's report floating drawdown on its weight at the same time (conservative).
Usage: python research/portfolio/btc_bull_frontier.py"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from curves import bull_daily, btc_daily  # noqa: E402

BTC_DD, BULL_DD = 67265.07 / 120000, 0.1354          # report floating drawdowns (share of starting deposit)
b = btc_daily(r"C:\MT5_JEV_TEST\btc_size_120000.htm", 120000); u = bull_daily()
days = pd.bdate_range("2025-03-31", "2026-10-13")
b = b.reindex(days).fillna(0); u = u.reindex(days).fillna(0)
print("alone: BTC x%.3f, Bull x%.3f, corr %.3f" % (1 + b.sum(), 1 + u.sum(), b.corr(u)))
rows = []
for wb in np.arange(0, 1.01, 0.1):
    for wu in np.arange(0, 1.01 - wb, 0.1):
        eq = 1 + (wb * b + wu * u).cumsum()
        dd_real = float((eq / eq.cummax() - 1).min())
        dd = dd_real - wb * BTC_DD - wu * BULL_DD
        yrs = len(days) / 261
        rows.append((round(wb, 1), round(wu, 1), round(float(eq.iloc[-1]), 3), round(dd * 100, 1), round((eq.iloc[-1] ** (1 / yrs) - 1) * 100, 1)))
t = pd.DataFrame(rows, columns=["btc", "bull", "mult", "dd_conservative_pct", "annual_pct"])
print(t[t.dd_conservative_pct >= -15].sort_values("mult", ascending=False).head(8).to_string(index=False))
print("\nfor reference, unrestricted top:")
print(t.sort_values("mult", ascending=False).head(4).to_string(index=False))
