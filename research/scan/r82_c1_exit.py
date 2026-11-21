"""Round 82 (prereg docs/prereg/r82_c1_exit_variants.md): C1 with earlier exits, same entries, same vol as the base.
V1 give back half of the peak open profit (armed after sigma*sqrt(n)), V2 time exit after n bars, V3 exit channel n/4.
Usage: py -3.12 research/scan/r82_c1_exit.py dev|hold"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import tcost, scale
from r64_mass import loadh, swaps
from r77_c1_breadth import st
PART = sys.argv[1]

def donch_v(c, long_only, mode):
    st_ = []; cv = c.values; sig = c.pct_change().rolling(60).std().values
    for n in (10, 20, 30, 60, 90, 150, 250):
        hv, lv = c.rolling(n).max().values, c.rolling(n).min().values
        k = max(2, n // 4) if mode == "V3" else n // 2
        xl, xh = c.rolling(k).min().values, c.rolling(k).max().values
        p = np.zeros(len(c)); e = mx = arm = 0.0; t0 = 0
        for i in range(1, len(c)):
            q = p[i - 1]
            if q == 0:
                q = 1 if cv[i] >= hv[i] else (-1 if (not long_only and cv[i] <= lv[i]) else 0)
                if q != 0: e, mx, t0 = cv[i], 0.0, i; arm = (sig[i] if sig[i] == sig[i] else 0.0) * np.sqrt(n)
            else:
                pr = q * (cv[i] / e - 1); mx = max(mx, pr)
                if (q > 0 and cv[i] <= xl[i]) or (q < 0 and cv[i] >= xh[i]): q = 0
                elif mode == "V1" and arm > 0 and mx >= arm and pr < 0.5 * mx: q = 0
                elif mode == "V2" and i - t0 >= n: q = 0
            p[i] = q
        st_.append(p)
    return pd.Series(np.mean(st_, axis=0), index=c.index)

D = {}
for s in ("BTCUSD", "ETHUSD"):
    h = loadh(s); tc = tcost(s, h); sl, ss = swaps(s, float(h.close.iloc[-1]))
    c = h.close.resample("6h").last().dropna()
    D[s] = (c, tc, sl, ss, c.index.to_series().diff().dt.total_seconds().fillna(0) / 86400 / 365)

def run(mode):
    out = []
    for s, (c, tc, sl, ss, dt) in D.items():
        w = (0.5 * donch_v(c, True, mode) + 0.5 * donch_v(c, False, mode)).shift(2).fillna(0); r = c.pct_change().fillna(0)
        net = w * r - w.diff().abs().fillna(0) * tc + np.where(w > 0, w * sl, -w * ss) * dt
        out.append(scale((1 + net).groupby(net.index.normalize()).prod() - 1))
    return scale(pd.concat(out, axis=1).fillna(0).mean(1))

a, z = ("2017", "2022") if PART == "dev" else ("2023", "2026")
res = {m: run(m) for m in ("BASE", "V1", "V2", "V3")}
sb, mb, _ = st(res["BASE"][a:z])
print(f"{PART} {a}-{z}: BASE Sh {sb:.2f} MDD {mb:.1f}")
for m in ("V1", "V2", "V3"):
    s_, m_, y_ = st(res[m][a:z])
    ok = (s_ >= sb + 0.10 and m_ >= mb) if PART == "dev" else (s_ >= sb + 0.05 and m_ >= mb - 1)
    print(f"  {m}: Sh {s_:.2f} ({s_ - sb:+.2f}) MDD {m_:.1f} corr {res[m].corr(res['BASE']):.2f} -> {'PASS' if ok else 'FAIL'} | {y_}")
