"""Does doubling the demo risk in the EAs (C1 TargetVol 0.20->0.40, I2 TargetVol 0.15->0.30) really double the book, or do caps
(C1 MaxGross 3 / per-asset cap 3, I2 lev cap 5) and margin bend it? Compares 0.5*C1+0.5*I2 from the x2 runs with 2 x the demo-level runs.
Usage: py -3.12 research/stable/x2_check.py"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); sys.path.insert(0, "research/stable")
from guardian_sim import deals
from book_tester import show

def i2(tag):
    out = []
    for y in range(2020, 2027):
        x = deals(f"C:/MT5_JEV_TEST/{tag}_{y}.htm"); x = x[x.symbol == ".USTECHCash"]
        x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize()
        pnl = (x.profit + x.swap + x.commission).groupby(x.day).sum()
        eq = 120000 + pnl.cumsum(); out.append(pnl / eq.shift(1).fillna(120000))
    return pd.concat(out)
c = lambda f: pd.read_csv(f"data/derived/c1_equity/{f}_equity.csv", index_col=0, parse_dates=True).equity.pct_change().dropna()["2020":"2026-10-30"]
c1, c2 = c("c1_ecn_av15_full"), c("c1_ecn_av15_tv40_full")
i1, i22 = i2("in2dst_t").reindex(c1.index).fillna(0), i2("in2dst_tv30_t").reindex(c1.index).fillna(0)
print(f"vol ratio x2/x1: C1 {c2.std()/c1.std():.2f}  I2 {i22.std()/i1.std():.2f}")
show(c1, "C1 demo"); show(c2, "C1 x2 (EA)"); show(i1, "I2 demo"); show(i22, "I2 x2 (EA)")
show(0.5 * c1 + 0.5 * i1, "book demo"); show(2 * (0.5 * c1 + 0.5 * i1), "book x2 arithmetic"); show(0.5 * c2 + 0.5 * i22, "book x2 per-account (0.5/0.5)")
show(c2 + i22, "two accounts each x2, summed")
