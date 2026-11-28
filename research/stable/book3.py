"""C1+I2 book (book_tester.py, tester series) with and without US500_3DD (tester dd3_us500_2018_2026) as a third leg.
Same procedure: risk-parity weights from train vol 2020-2023, L = smallest leverage reaching 5%/month in train, holdout 2024..10.2026.
Descriptive (not a pre-registered gate): does the third leg lower the drawdown at the same 5%/month?  Usage: py -3.12 research/stable/book3.py"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/stable"); sys.path.insert(0, "research/third")
from book_tester import i2_daily, stats, show
from dd3_eval import daily
c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change().dropna()
i2 = i2_daily().reindex(c1.index).fillna(0); d3 = daily("dd3_us500_2018_2026").reindex(c1.index).fillna(0)
tr, ho = slice("2020-01-01", "2023-12-31"), slice("2024-01-01", "2026-10-30")
print("corr:", pd.concat([c1, i2, d3], axis=1, keys=["C1", "I2", "3DD"])["2020":].corr().round(2).to_dict())
target = 1.05 ** 12 - 1
for nm, legs in (("C1+I2", [c1, i2]), ("C1+I2+3DD", [c1, i2, d3])):
    iv = np.array([1 / x[tr].std() for x in legs]); w = iv / iv.sum(); u = sum(wi * x for wi, x in zip(w, legs))
    L = next(l for l in np.arange(0.1, 15, 0.01) if stats(l * u[tr])[0] >= target)
    print(f"== {nm}: weights {np.round(w, 3)}, L {L:.2f}")
    show(L * u[tr], "  L train"); show(L * u[ho], "  L holdout")
