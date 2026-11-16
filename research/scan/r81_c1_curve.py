"""Round 81 (prereg docs/prereg/r81_c1_curve_filter.md): halve C1 longs in a tightening regime (curve 10Y-3M falling, 3M up 20bp/20d).
Usage: py -3.12 research/scan/r81_c1_curve.py dev|test"""
import sys, glob
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
import r77_c1_breadth as B
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"; a, z = ("2019", "2022") if PER == "dev" else ("2023", "2026")
y = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("data/derived/macro/nom_*.csv"))]); y["Date"] = pd.to_datetime(y.Date)
y = y.set_index("Date").sort_index()[["3 Mo", "10 Yr"]].dropna(); y = y[~y.index.duplicated()]
cv = y["10 Yr"] - y["3 Mo"]; tight = (cv.diff(20) < 0) & (y["3 Mo"].diff(20) >= 0.20)
tight.index = tight.index + pd.Timedelta(days=1)
T = tight.astype(float).reindex(B.idx, method="ffill").fillna(0).astype(bool)
def run(filt):
    out = []
    for s in ("BTCUSD", "ETHUSD"):
        w = B.W[s].reindex(B.idx).fillna(0)
        if filt: w = w.where(~((w > 0) & T), 0.5 * w)
        tc, sl, ss, dt = B.NET[s]; r = B.R[s].reindex(B.idx).fillna(0); dt = dt.reindex(B.idx).fillna(0)
        net = w * r - w.diff().abs().fillna(0) * tc + np.where(w > 0, w * sl, -w * ss) * dt
        out.append(B.scale((1 + net).groupby(net.index.normalize()).prod() - 1))
    return B.scale(pd.concat(out, axis=1).fillna(0).mean(1))
print(f"tight share {a}-{z}: {T[a:z].mean():.2f}")
b, f = run(False), run(True); sb, mb, _ = B.st(b[a:z]); sf, mf, _ = B.st(f[a:z])
print(f"{PER} {a}-{z}: base Sh {sb:.2f} MDD {mb:.1f} | curve-filter Sh {sf:.2f} MDD {mf:.1f} ->", "PASS" if (sf >= sb + 0.10 and mf >= mb) else "KILL")
