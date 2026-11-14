"""Candidate 3 of docs/THIRD_COMPONENT_PLAN.md: turn of the month. Long from the close of the second-to-last trading day of a month
to the close of the third trading day of the next month, NDX/SPX/DAX/N225 equal weight, frozen rules.
Costs: 0.02% per round trip, swap per calendar night held. Writes data/derived/third/tom_daily.csv.
Usage: python research/third/tom.py"""
import os, sys
import pandas as pd
sys.path.insert(0, "research/third")
from rsi2 import SWAP, RT_COST, stats

def sleeve(name):
    d = pd.read_csv(f"data/raw/yahoo/{name}.csv", parse_dates=["date"]).set_index("date").close
    d = d[~d.index.duplicated()].dropna()
    ym = d.index.to_period("M")
    k = pd.Series(range(len(d)), index=d.index).groupby(ym).cumcount()            # 0-based trading day of the month
    left = pd.Series(range(len(d)), index=d.index).groupby(ym).cumcount(ascending=False)  # 0 = last trading day
    pos = ((left <= 1) | (k <= 1)).astype(float)   # held at the close of day -2 and -1, and of days 1-2; sold at the close of day 3
    held = pos.shift(1).fillna(0)
    nights = d.index.to_series().diff().dt.days.fillna(1)
    ret = held * (d.pct_change().fillna(0) - SWAP[name] / 365 * nights)
    ret -= pos.diff().abs().fillna(0) * RT_COST / 2
    return ret, pos

if __name__ == "__main__":
    R, P = {}, {}
    for n in SWAP: R[n], P[n] = sleeve(n)
    df = pd.DataFrame(R).fillna(0); port = df.mean(axis=1)
    for a, b, lab in (("2000", "2015", "2000-2015"), ("2016", "2026-10-31", "2016-2026"), ("2020", "2026-10-31", "2020-2026")):
        print(f"--- {lab}")
        for n in SWAP: stats(df[n].loc[a:b], n)
        stats(port.loc[a:b], "PORT(1/4)")
    print("exposure:", {n: round(P[n].loc["2016":].mean(), 2) for n in SWAP})
    os.makedirs("data/derived/third", exist_ok=True); port.to_csv("data/derived/third/tom_daily.csv", header=["ret"])
