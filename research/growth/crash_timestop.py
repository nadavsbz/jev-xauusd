"""Crash days: a time stop after level k (docs/CRASH_LINK_PLAN.md). For every clone basket that reached level K: hours from
level K to its close (cut vs recovered), and what closing the basket T hours after level K would have changed (static: positions
opened by then, priced at the H1 close; no compounding). Usage: python research/growth/crash_timestop.py DIR_WITH_oos_b.csv [K]"""
import sys, pandas as pd, numpy as np
sys.path[:0] = ["research/btc", "research/bd1"]
import guardian_sim as g
S = sys.argv[1]; K = int(sys.argv[2]) if len(sys.argv) > 2 else 9
B = pd.concat([pd.read_csv("data/derived/crash_signs/baskets.csv"), pd.read_csv(S + "/oos_b.csv")])
D = B[B.levels >= K].drop_duplicates(["report", "side", "t0"])
h = pd.read_csv("data/derived/intraday/XAUUSD_H1.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
TS = (1, 2, 4, 8, 12, 24, 48)
rows = []
for rep, dd in D.groupby("report"):
    p = g.pair(g.deals(f"C:/MT5_JEV_TEST/{rep}.htm"))[0]
    for _, b in dd.iterrows():
        x = p[(p.side == b.side) & (p.t0 >= b.t0) & (p.t0 <= b.t1)].sort_values("t0")
        if len(x) < K: continue
        sg = 1 if b.side == "buy" else -1; tk = x.t0.iloc[K - 1]
        r = {"rep": rep, "cut": b.kind == "cut", "net": x.net.sum(), "h_after": (x.t1.max() - tk) / 3600}
        for T in TS:
            te = tk + T * 3600
            if x.t1.max() <= te: r[f"g{T}"] = 0.0; continue          # closed before the time stop: nothing changes
            i = h.index.searchsorted(pd.to_datetime(te, unit="s")) - 1; px = h.close.iloc[i]
            o = x[x.t0 <= te]; r[f"g{T}"] = (sg * (px - o.p0) * o.vol * 100).sum() - x.net.sum()
        rows.append(r)
R = pd.DataFrame(rows)
print(f"level {K}: baskets {len(R)}, cut {R.cut.sum()}")
print("hours from level", K, "to close:"); print(R.groupby("cut").h_after.describe(percentiles=[.25, .5, .75]).round(1))
per = np.where(R.rep.str.startswith("d6t"), R.rep.str[6:10], np.where(R.rep == "yearf_live", "EG", R.rep.str[2:6]))
for T in TS:
    s = (R.groupby(per)[f"g{T}"].sum() / 1000).round(0)
    print(f"time stop {T:2d}h after level {K}: gain k$ {s.to_dict()} total {s.sum():.0f}, periods better {int((s > 0).sum())}/{len(s)}")
