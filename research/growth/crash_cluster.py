"""Crash days: do cuts follow earlier trouble? (docs/CRASH_LINK_PLAN.md) Per weekday of each clone run: P(cut today) given a cut,
or a deep basket (>= 9 levels, any outcome), in the previous N weekdays, against the rest.
Usage: python research/growth/crash_cluster.py DIR_WITH_oos_b.csv"""
import sys, pandas as pd, numpy as np
S = sys.argv[1]
B = pd.concat([pd.read_csv("data/derived/crash_signs/baskets.csv"), pd.read_csv(S + "/oos_b.csv")])
B["d1"] = pd.to_datetime(B.t1, unit="s").dt.normalize(); B["d0"] = pd.to_datetime(B.t0, unit="s").dt.normalize()
out = []
for rep, b in B.groupby("report"):
    days = pd.bdate_range(b.d0.min(), b.d1.max())
    cut = pd.Series(days.isin(b[b.kind == "cut"].d1), index=days).astype(int)
    deep = pd.Series(days.isin(b[(b.levels >= 9) & (b.kind != "cut")].d1), index=days).astype(int)
    big = pd.Series(days.isin(b[(b.levels >= 6)].d1), index=days).astype(int)
    for N in (1, 3, 5, 10):
        out.append(pd.DataFrame({"rep": rep, "N": N, "cut": cut, "prev_cut": cut.shift(1).rolling(N).max(),
                                 "prev_deep": deep.shift(1).rolling(N).max(), "prev_l6": big.shift(1).rolling(N).max()}))
A = pd.concat(out).dropna()
for c in ("prev_cut", "prev_deep", "prev_l6"):
    print(c); print(A.groupby(["N", c]).cut.agg(["mean", "size"]).unstack().round(3))
A["per"] = np.where(A.rep.str.startswith("d6t"), "19-21", np.where(A.rep == "yearf_live", "EG", "22-25"))
print("by period, N=5:"); print(A[A.N == 5].groupby(["per", "prev_deep"]).cut.agg(["mean", "size"]).unstack().round(3))
print(A[A.N == 5].groupby(["per", "prev_cut"]).cut.agg(["mean", "size"]).unstack().round(3))
