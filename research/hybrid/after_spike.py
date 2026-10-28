"""Conditional reversal or continuation after a large M15 move (the moment a grid starts averaging) (docs/HYBRID_PLAN.md, step 0).
Signal: |r| of a bar > k x its rolling 96-bar std (past only). Outcome: the next h bars' return, signed in the spike's direction
(>0 = continuation, <0 = reversal), in bp, gross (no costs), per period, with t-stat.
Usage: python research/hybrid/after_spike.py"""
import glob
import numpy as np, pandas as pd

for k in (2, 3, 4):
    line = []
    for f in sorted(glob.glob("data/derived/crash_signs/bars_*_PERIOD_M15.csv")):
        p = f.split("bars_")[1].split("_")[0]
        b = pd.read_csv(f); lc = np.log(b.close); r = lc.diff()
        r[np.abs(r) > 0.03] = np.nan
        sd = r.rolling(96, min_periods=60).std().shift(1)
        sig = np.sign(r) * (np.abs(r) > k * sd)
        cells = []
        for h in (1, 4, 16, 96):
            fwd = (lc.shift(-h) - lc) * 1e4
            v = (fwd * sig)[sig != 0].dropna()
            cells.append(f"h{h}:{v.mean():+.1f}(t{v.mean() / v.std() * np.sqrt(len(v)):+.1f})")
        line.append(f"{p} n{int((sig != 0).sum())} " + " ".join(cells))
    print(f"k={k}"); print("\n".join("  " + x for x in line))
