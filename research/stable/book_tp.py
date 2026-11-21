"""C1 + I2 portfolio with I2 base (in2dst_t) vs I2 + TP 1.0% (in2tp100_t), same method as book_tester.py (tester daily returns,
C1 = c1_ecn_av15_full). Descriptive, answers the user's question 14.11; no new parameter chosen here.
Usage: py -3.12 research/stable/book_tp.py"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); sys.path.insert(0, "research/stable")
from guardian_sim import deals
from book_tester import stats, show

def i2(tag):
    out = []
    for y in range(2020, 2027):
        x = deals(f"C:/MT5_JEV_TEST/{tag}_{y}.htm"); x = x[x.symbol == ".USTECHCash"]
        x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize()
        pnl = (x.profit + x.swap + x.commission).groupby(x.day).sum()
        eq = 120000 + pnl.cumsum(); out.append(pnl / eq.shift(1).fillna(120000))
    return pd.concat(out)

c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change().dropna()
c1 = c1["2020":"2026-10-30"]
for tag in ("in2dst_t", "in2tp100_t"):
    s = i2(tag).reindex(c1.index).fillna(0)
    print(f"--- {tag}: corr with C1 {c1.corr(s):.2f}")
    show(s, "I2 alone")
    for l in (1.0, 1.5, 2.0):
        show(l * (0.5 * c1 + 0.5 * s), f"50/50 x{l} (x1 = live)")
