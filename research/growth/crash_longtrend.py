"""Crash days: does trading BD only with the long trend (previous day's close vs its 100/200-day average) cut the deep
baskets? (docs/CRASH_LINK_PLAN.md, pre-registered 7.11.2026). Same basket data and H1 gold bars as crash_regime.py.
Aligned = buy basket with the previous daily close above the N-day average, or sell basket below it.
Per period: cut rate aligned vs against, net of the kept (aligned) baskets vs a placebo that drops the same number of
baskets at random (200 draws). An approximation: baskets are not independent (Overlap/Hedge link the two sides).
Usage: python research/growth/crash_longtrend.py DIR_WITH_oos_b.csv"""
import sys, pandas as pd, numpy as np
S = sys.argv[1]
B = pd.concat([pd.read_csv("data/derived/crash_signs/baskets.csv"), pd.read_csv(S + "/oos_b.csv")]).drop_duplicates(["report", "side", "t0"])
h = pd.read_csv("data/derived/intraday/XAUUSD_H1.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
d = h.close.resample("1D").last().dropna()                                          # server-day closes
B["cut"] = B.kind == "cut"
B["per"] = np.where(B.report.str.startswith("d6t"), "19-21", np.where(B.report == "yearf_live", "EG", "22-25"))
day = pd.to_datetime(B.t0, unit="s").dt.floor("D")
rng = np.random.default_rng(1)
for N in (100, 200):
    ma = d.rolling(N).mean()
    i = d.index.searchsorted(day) - 1                                               # last full day before the basket's day
    ok = i >= N
    up = np.where(ok, d.values[np.maximum(i, 0)] > ma.values[np.maximum(i, 0)], False)
    B["al"] = np.where(ok, np.where(B.side == "buy", up, ~up), np.nan)
    print(f"\n== N={N}")
    for p, G in B[B.al.notna()].groupby("per"):
        a, x = G[G.al == 1], G[G.al == 0]
        ca, cx = a.cut.mean() * 1000, x.cut.mean() * 1000
        pl = np.array([G.net.values[rng.permutation(len(G))[:len(a)]].sum() for _ in range(200)])
        print(f"{p}: baskets {len(G)} aligned {len(a)/len(G):.0%} | cuts/1000 with {ca:.1f} against {cx:.1f} (x{cx/ca if ca else np.inf:.1f})"
              f" | net all {G.net.sum():+,.0f} kept {a.net.sum():+,.0f} dropped {x.net.sum():+,.0f}"
              f" | placebo kept median {np.median(pl):+,.0f}, kept beats {np.mean(a.net.sum() > pl):.0%}")
