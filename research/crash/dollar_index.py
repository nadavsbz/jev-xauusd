"""Synthetic US dollar index (stage 1, signal S6) from five H1 pairs, ICE USDX weights without
SEK (not available at the broker), renormalised. ASSUMED: close enough for a range percentile.
High/low of the index are bounds built from each pair's high or low by the sign of its weight
(an index high needs EUR and GBP low and the others high in the same hour), so the hourly range
is slightly overstated.
Usage: python research/crash/dollar_index.py FX_DIR OUT_DIR"""
import glob, os, sys
import numpy as np, pandas as pd

W = {"EURUSD": -0.576, "USDJPY": 0.136, "GBPUSD": -0.119, "USDCAD": 0.091, "USDCHF": 0.036}
S = sum(abs(v) for v in W.values()); W = {k: v / S for k, v in W.items()}   # renormalised to 1 without SEK (review PR #23)


def load(fx, sym):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(fx, f"fx_{sym}_h1_*.csv")))])
    return d.drop_duplicates("timestamp").set_index("timestamp").sort_index()


def main():
    fx, out = sys.argv[1], sys.argv[2]
    pairs = {s: load(fx, s) for s in W}
    idx = sorted(set.intersection(*[set(p.index) for p in pairs.values()]))
    lc = sum(w * np.log(pairs[s].loc[idx, "close"].values) for s, w in W.items())
    lo_ = sum(w * np.log(pairs[s].loc[idx, "open"].values) for s, w in W.items())
    hi = sum(w * np.log(pairs[s].loc[idx, "high" if w > 0 else "low"].values) for s, w in W.items())
    lo = sum(w * np.log(pairs[s].loc[idx, "low" if w > 0 else "high"].values) for s, w in W.items())
    d = pd.DataFrame({"timestamp": idx, "open": np.exp(lo_) * 50, "high": np.exp(hi) * 50, "low": np.exp(lo) * 50, "close": np.exp(lc) * 50})
    yr = pd.to_datetime(d.timestamp, unit="ms").dt.year
    for y, g in d.groupby(yr):
        g.to_csv(os.path.join(out, f"dollaridxusd_h1_{y}.csv"), index=False)
    print(len(d), "hours", pd.to_datetime(d.timestamp.iloc[0], unit="ms"), "->", pd.to_datetime(d.timestamp.iloc[-1], unit="ms"))


if __name__ == "__main__":
    main()
