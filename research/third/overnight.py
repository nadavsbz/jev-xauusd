"""Candidate 2 of docs/THIRD_COMPONENT_PLAN.md: overnight premium, long close -> next open, every day, NDX/SPX/DAX/N225 equal weight.
Costs: swap per calendar night (-8.6%/yr US, -7.2% DAX/N225) + RT_COST per night (pre-registered 0.02%; sensitivity 0.003%).
Writes data/derived/third/overnight_daily.csv (main cost) for port3.py.
Usage: python research/third/overnight.py"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/third")
from rsi2 import SWAP, stats

def sleeve(name, rt):
    d = pd.read_csv(f"data/raw/yahoo/{name}.csv", parse_dates=["date"]).set_index("date")
    d = d[~d.index.duplicated()].dropna()
    d = d[(d.open > 0) & (d.close > 0)]
    stale = (d.open == d.close.shift(1)).mean()          # open copied from the previous close = no real overnight gap
    nights = d.index.to_series().diff().dt.days.fillna(1)
    r = d.open / d.close.shift(1) - 1 - SWAP[name] / 365 * nights - rt
    return r.fillna(0), stale

if __name__ == "__main__":
    for rt, lab in ((0.0002, "main 0.02%"), (0.00003, "sensitivity 0.003%")):
        R = {}
        for n in SWAP:
            R[n], st = sleeve(n, rt)
            if rt == 0.0002: print(f"{n}: share of days open == previous close: {st:.1%}")
        df = pd.DataFrame(R).fillna(0); port = df.mean(axis=1)
        print(f"===== costs {lab}")
        for a, b, w in (("2000", "2015", "2000-2015"), ("2016", "2026-10-31", "2016-2026"), ("2020", "2026-10-31", "2020-2026")):
            print(f"--- {w}")
            for n in SWAP: stats(df[n].loc[a:b], n)
            stats(port.loc[a:b], "PORT(1/4)")
        if rt == 0.0002:
            os.makedirs("data/derived/third", exist_ok=True); port.to_csv("data/derived/third/overnight_daily.csv", header=["ret"])
