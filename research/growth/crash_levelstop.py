"""Crash days: close the whole basket at a loss when gold reaches the price where level k+1 would open, k = 1..5 (the user's idea,
pre-registered 7.11.2026 in docs/CRASH_LINK_PLAN.md). Same clone baskets as crash_regime.py (RoboForex 2019-2025 + EG 2025-26).
Grid of the account-1 set: 3$ between levels (fixed up to level 6), level i lot = level-1 lot x 1.5^i, 100 oz per lot, 0.30$ spread
per oz on the close. A basket with more than k levels is replaced by that stop loss; the others keep their real net.
Approximation: the new basket BD would open after the stop is not in the data.
Usage: python research/growth/crash_levelstop.py DIR_WITH_oos_b.csv"""
import sys, pandas as pd, numpy as np
B = pd.concat([pd.read_csv("data/derived/crash_signs/baskets.csv"), pd.read_csv(sys.argv[1] + "/oos_b.csv")]).drop_duplicates(["report", "side", "t0"])
B["yr"] = np.where(B.report == "yearf_live", "EG", pd.to_datetime(B.t0, unit="s").dt.year.astype(str))
B["cut"] = B.kind == "cut"
lot1 = B.lots.values / np.array([sum(1.5 ** i for i in range(int(n))) for n in B.levels.values])
D, SPR = 3.0, 0.30
rows = []
for k in (1, 2, 3, 4, 5):
    lots = np.array([1.5 ** i for i in range(k)])
    loss_per_lot1 = -100 * (sum(lots[i] * D * (k - i) for i in range(k)) + SPR * lots.sum())   # all k levels closed at -3k from level 1
    hit = B.levels.values > k
    new = np.where(hit, lot1 * loss_per_lot1, B.net.values)
    B[f"k{k}"] = new
    rows.append((k, hit.sum(), B.cut.values[hit].sum(), (hit & (B.net.values > 0)).sum()))
T = B.groupby("yr")[["net"] + [f"k{k}" for k in range(1, 6)]].sum().round(0)
T.loc["total"] = T.sum()
print(T.to_string())
print("\nk | baskets stopped | cuts avoided of", B.cut.sum(), "| stopped baskets that would have closed in profit")
for k, n, c, w in rows: print(k, n, c, w)
better = {k: int(((T[f"k{k}"] > T.net).iloc[:-1]).sum()) for k in range(1, 6)}
print("\nyears better than no rule (of", len(T) - 1, "):", better)
