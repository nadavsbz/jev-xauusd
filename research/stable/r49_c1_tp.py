"""Round 49 (docs/SCAN_PLAN.md, pre-registered 14.11): profit-take per Donchian lookback in C1. After +X% from that lookback's
entry the lookback goes flat and stays locked until its normal exit condition fires. X in {0.10,0.20,0.30,0.50}; dev 2019-2023.
Usage: py -3.12 research/stable/r49_c1_tp.py [holdout]"""
import os, sys
os.environ.setdefault("CRY", "BTCUSD,ETHUSD"); HO = len(sys.argv) > 1 and sys.argv[1] == "holdout"; sys.argv = sys.argv[:1]
sys.path.insert(0, "research/stable")
import numpy as np, pandas as pd
import intraday_trend as it

X = None; GIVE = []
def donch(c, long_only):
    st = []
    for n in (10, 20, 30, 60, 90, 150, 250):
        hi, lo = c.rolling(n).max().values, c.rolling(n).min().values
        xl, xh = c.rolling(n // 2).min().values, c.rolling(n // 2).max().values
        cv = c.values; p = np.zeros(len(c)); q = 0; lock = 0; ent = pk = 0.0
        for i in range(1, len(c)):
            if lock:
                if (lock > 0 and cv[i] <= xl[i]) or (lock < 0 and cv[i] >= xh[i]): lock = 0
            if q == 0 and not lock:
                q = 1 if cv[i] >= hi[i] else (-1 if (not long_only and cv[i] <= lo[i]) else 0)
                if q: ent = pk = cv[i]
            elif q != 0:
                pk = max(pk, cv[i]) if q > 0 else min(pk, cv[i])
                g = q * (cv[i] / ent - 1)
                ex = (q > 0 and cv[i] <= xl[i]) or (q < 0 and cv[i] >= xh[i])
                if X is not None and g >= X: lock = q; ex = True
                if ex:
                    if X is None: GIVE.append((q * (pk / ent - 1), g))
                    q = 0
            p[i] = q
        st.append(p)
    return pd.Series(np.mean(st, axis=0), index=c.index)
it.donch = donch

def stats(r, a, b):
    x = r.loc[a:b]; eq = (1 + x).cumprod(); yrs = (x.index[-1] - x.index[0]).days / 365.25
    y = x.groupby(x.index.year).apply(lambda z: (1 + z).prod() - 1) * 100
    return (eq.iloc[-1] ** (1 / yrs) - 1) * 100, x.mean() / x.std() * it.PER_YEAR ** .5, (eq / eq.cummax() - 1).min() * 100, y

a, b = ("2024-01-01", "2026-11-13") if HO else ("2019-01-01", "2023-12-31")
print("assets", list(it.C.columns), "period", a, b)
for x in (None, 0.10, 0.20, 0.30, 0.50):
    X = x; r = it.mix(); c, s, d, y = stats(r, a, b)
    print(f"X={x}: CAGR {c:5.1f}% Sh {s:4.2f} MDD {d:5.1f}% |", " ".join(f"{k % 100:02d}:{v:+.0f}" for k, v in y.items()), flush=True)
    if x is None and GIVE:
        g = pd.DataFrame(GIVE, columns=["peak", "exit"]); w = g[g.peak > 0.05]
        print(f"   descr: trades {len(g)}, with peak >5%: {len(w)}, mean peak {w.peak.mean()*100:.1f}% exit {w.exit.mean()*100:.1f}% (giveback share {(1 - w.exit.sum()/w.peak.sum())*100:.0f}%)")
