"""Crash days: does a plain gold trend-follower make money exactly on the clone's cut days? (docs/CRASH_LINK_PLAN.md)
Trend: H1 Donchian breakout, long above the N-bar high / short below the N-bar low, exit at the opposite N/2 extreme, 1 oz,
$0.30 per side. BD: realised clone P&L per day (basket net by close day). Compares trend P&L on cut days with all days.
Usage: python research/growth/crash_trendhedge.py DIR_WITH_oos_b.csv"""
import sys, pandas as pd, numpy as np
S = sys.argv[1]
B = pd.concat([pd.read_csv("data/derived/crash_signs/baskets.csv"), pd.read_csv(S + "/oos_b.csv")]).drop_duplicates(["report", "side", "t0"])
h = pd.read_csv("data/derived/intraday/XAUUSD_H1.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
def trend(N):
    hi, lo = h.high.rolling(N).max().shift(1), h.low.rolling(N).min().shift(1)
    xh, xl = h.high.rolling(N // 2).max().shift(1), h.low.rolling(N // 2).min().shift(1)
    pos = np.zeros(len(h)); p = 0; C, H, L = h.close.values, h.high.values, h.low.values
    for i in range(N, len(h)):
        if p == 0: p = 1 if C[i] > hi.iloc[i] else -1 if C[i] < lo.iloc[i] else 0
        elif p == 1 and C[i] < xl.iloc[i]: p = -1 if C[i] < lo.iloc[i] else 0
        elif p == -1 and C[i] > xh.iloc[i]: p = 1 if C[i] > hi.iloc[i] else 0
        pos[i] = p
    pos = pd.Series(pos, h.index)
    pnl = pos.shift(1).fillna(0) * h.close.diff().fillna(0) - pos.diff().abs().fillna(0) * 0.30
    return pnl.groupby(pnl.index.date).sum()
cutdays = {(r, d) for r, d in zip(B[B.kind == "cut"].report, pd.to_datetime(B[B.kind == "cut"].t1, unit="s").dt.date)}
for N in (24, 48, 96):
    T = trend(N)
    for rep, G in B.groupby("report"):
        d0, d1 = pd.to_datetime(G.t0.min(), unit="s").date(), pd.to_datetime(G.t1.max(), unit="s").date()
        t = T[(T.index >= d0) & (T.index <= d1)]
        cd = [d for (r, d) in cutdays if r == rep and d in t.index]
        cd1 = sorted({x for d in cd for x in t.index[(t.index >= pd.Timestamp(d) - pd.Timedelta(days=2)) & (t.index <= pd.Timestamp(d))]})
        print(f"N={N:3d} {rep:16s} days {len(t):4d} trend total {t.sum():+8.0f}$/oz  mean/day {t.mean():+5.2f}  "
              f"cut days {len(set(cd)):2d} mean {t.loc[sorted(set(cd))].mean() if cd else np.nan:+6.2f}  "
              f"cut-day-and-2-before mean {t.loc[cd1].mean() if cd1 else np.nan:+6.2f}")
