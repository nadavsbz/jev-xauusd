"""The one-account setup that runs on the ECN demo since 1.11.2026 (docs/STABLE_SYSTEM_PLAN.md, Codex round 6): both bots in one
account, each sized on the WHOLE equity at half the x1.5 target - C1 AssetVol 0.075 (c1_ecn_av075_full) and the fixed IndexNoise
TargetVol 0.075 (in3_tv075_*, one run per year + holdout). Account daily return = C1's + the Nasdaq bot's (no 0.5 weights).
Usage: python research/stable/portfolio_one.py (from the repo root)"""
import pandas as pd
import sys; sys.path.insert(0, "research/stable")
from portfolio_x15 import i2_daily, rep

n_new = i2_daily("in3_tv075")
c = pd.read_csv("data/derived/c1_equity/c1_ecn_av075_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change().dropna()
n = n_new.reindex(c.index).fillna(0); acct = c + n
print(f"corr C1/Nasdaq {c.corr(n):.2f}")
rep(c, "C1 0.075 alone"); rep(n, "Nasdaq 0.075 (fixed)"); rep(acct, "one account x1.5")
rep(acct, "  holdout", "2025-10-25")
