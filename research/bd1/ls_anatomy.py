"""Anatomy of the level-stop runs (round 8, docs/CRASH_LINK_PLAN.md): per tester report, the baskets by number of levels,
their count and net, so the stopped baskets (k levels, closed at a loss) are separated from the rest.
Usage: python research/bd1/ls_anatomy.py REPORT [REPORT ...]   (report names in C:\MT5_JEV_TEST)"""
import os, sys
import pandas as pd
sys.path[:0] = [os.path.join(os.path.dirname(__file__), "..", "btc"), os.path.dirname(__file__)]
import guardian_sim as g
from clone_vs_live import table

for name in sys.argv[1:]:
    p = g.pair(g.deals(f"C:/MT5_JEV_TEST/{name}.htm"))[0]
    b = table(p)
    s = b.groupby("n").net.agg(["size", "sum"]).round(0)
    w = b.groupby("n").net.apply(lambda x: (x < 0).sum())
    print(f"\n== {name}: baskets {len(b)} net {b.net.sum():+,.0f}")
    print(pd.concat([s, w.rename("losing")], axis=1).T.to_string())
