"""Evaluate round 42 of docs/SCAN_PLAN.md (Bulloldtested, yearly RF tester runs) against its pre-registered gates.
Usage: py -3.12 research/bull/bullold_eval.py"""
import sys, json, os
import numpy as np, pandas as pd
sys.path.insert(0, "research/third"); sys.path.insert(0, "research/stable")
from dd3_eval import daily
from book_tester import i2_daily
ys = [y for y in range(2018, 2027) if os.path.exists(f"C:/MT5_JEV_TEST/bullold_rf_{y}.htm")]
B = pd.concat([daily(f"bullold_rf_{y}").loc[str(y)] for y in ys])
print("year  ret%   eqDD%  realticks  trades")
yr = {}
for y in ys:
    e = json.load(open(f"docs/evidence/bullold_rf_{y}.json", encoding="utf-8")); s = e.get("summary_from_report", e)
    r = ((1 + B.loc[str(y)]).prod() - 1) * 100; yr[y] = r
    print(y, f"{r:6.1f}", s.get("equity_dd_rel", s.get("Equity Drawdown Relative", "?")), s.get("history_quality", s.get("History Quality", "?")), s.get("total_trades", s.get("Total Trades", "?")))
x = B[B.index.dayofweek < 5]; sh = x.mean() / x.std() * np.sqrt(252)
I = i2_daily(); j = pd.concat([B, I], axis=1, keys=["B", "I2"]).fillna(0).loc[f"{ys[0]}":]
print(f"years positive {sum(v > 0 for v in yr.values())}/{len(yr)} | Sharpe {sh:.2f} | corr I2 {j.corr().iloc[0, 1]:.2f}")
