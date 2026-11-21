"""Round 52 (docs/prereg/r52_book_3dd_fixed.md): C1+I2 (0.5/0.5, as the demo) + k x 3DD, k in {0.25, 0.5}, each book scaled to
B0's train vol, train 2020-2023 / holdout 2024..2026-10-30. Usage: py -3.12 research/stable/r52_book_3dd.py"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/stable"); sys.path.insert(0, "research/third")
from book_tester import i2_daily, stats, show
from dd3_eval import daily
c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change().dropna()
i2 = i2_daily().reindex(c1.index).fillna(0); d3 = daily("dd3_us500_2018_2026").reindex(c1.index).fillna(0)
tr, ho = slice("2020-01-01", "2023-12-31"), slice("2024-01-01", "2026-10-30")
B0 = 0.5 * c1 + 0.5 * i2
print(f"3DD native: share of days in market {(d3['2020':] != 0).mean():.2f}, ann vol {d3['2020':].std()*np.sqrt(365)*100:.1f}%, corr C1 {d3.corr(c1):.2f} I2 {d3.corr(i2):.2f}")
for nm, b in (("B0", B0), ("k=0.25", B0 + 0.25 * d3), ("k=0.5", B0 + 0.5 * d3)):
    b = b * (B0[tr].std() / b[tr].std())
    for lab, s in (("train", tr), ("holdout", ho)):
        c, d, sh = stats(b[s]); y = b[s].groupby(b[s].index.year).apply(lambda z: (1 + z).prod() - 1)
        print(f"{nm:7s} {lab:7s} CAGR {c*100:5.1f}% ({((1+c)**(1/12)-1)*100:.2f}%/mo) MDD {d*100:6.1f}% Sh {sh:.2f} yrs+ {(y>0).sum()}/{len(y)} |", " ".join(f"{k%100}:{v*100:+.0f}" for k, v in y.items()))
