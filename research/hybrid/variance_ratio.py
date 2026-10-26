"""Is gold mean-reverting at short horizons and trending at long ones? (docs/HYBRID_PLAN.md, step 0)
Variance ratio VR(q) = Var(q-bar return) / (q * Var(1-bar return)) on M15 log closes, per period; VR<1 = mean reversion
(what a grid harvests), VR>1 = trend (what pyramiding / trend following harvests). Lo-MacKinlay z under heteroskedasticity.
Usage: python research/hybrid/variance_ratio.py"""
import glob
import numpy as np, pandas as pd

Q = [2, 4, 8, 16, 32, 96, 192, 480, 960]   # 30m 1h 2h 4h 8h 1d 2d 5d 10d (in M15 bars, ~96 per day)

def vr(r, q):
    r = r - r.mean(); n = len(r)
    var1 = (r ** 2).sum() / (n - 1)
    rq = np.convolve(r, np.ones(q), "valid")
    m = q * (n - q + 1) * (1 - q / n)
    varq = (rq ** 2).sum() / m
    v = varq / var1   # m already holds the factor q
    # heteroskedasticity-robust z (Lo & MacKinlay 1988)
    d = np.array([(r[j:] ** 2 * r[:-j] ** 2).sum() / ((r ** 2).sum() ** 2) for j in range(1, q)])
    th = (((2 * (q - np.arange(1, q)) / q) ** 2) * d).sum() * n
    return v, (v - 1) / np.sqrt(th / n)

rows = []
for f in sorted(glob.glob("data/derived/crash_signs/bars_*_PERIOD_M15.csv")):
    p = f.split("bars_")[1].split("_")[0]
    b = pd.read_csv(f); r = np.diff(np.log(b.close.values))
    r = r[np.abs(r) < 0.03]   # drop weekend/session gaps that span closures
    for q in Q:
        v, z = vr(r, q); rows.append({"period": p, "q": q, "vr": round(v, 3), "z": round(z, 1)})
t = pd.DataFrame(rows).pivot(index="q", columns="period", values=["vr", "z"])
print(t.to_string())
