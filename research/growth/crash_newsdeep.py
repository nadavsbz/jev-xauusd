"""Crash days: does a deep basket that sits through a top US release get cut more often, or rescued more often, than a deep
basket that does not? (docs/CRASH_LINK_PLAN.md; the user's 5.11.2026 day: the 15:30 jobless-claims print gave the last push
down and then the reversal that closed the baskets). Deep = reached level 7 / 9. A basket "meets" a release when an
importance-3 USD event (data/derived/news/mt5_calendar_usd.csv, UTC) falls between its level-k time and its close.
Tester times are server wall time (Europe/Athens, VERIFIED in research/crash/pull_h1.py).
Usage: python research/growth/crash_newsdeep.py DIR_WITH_oos_b.csv"""
import sys, pandas as pd, numpy as np
from zoneinfo import ZoneInfo
sys.path[:0] = ["research/btc", "research/bd1"]
import guardian_sim as g
S = sys.argv[1]
B = pd.concat([pd.read_csv("data/derived/crash_signs/baskets.csv"), pd.read_csv(S + "/oos_b.csv")]).drop_duplicates(["report", "side", "t0"])
c = pd.read_csv("data/derived/news/mt5_calendar_usd.csv"); c = c[c.importance >= 3]
ev = np.sort(pd.to_datetime(c.time, unit="s", utc=True).dt.tz_convert(ZoneInfo("Europe/Athens")).dt.tz_localize(None)
             .astype("int64").values // 10**9)                                      # release time as server wall-clock epoch
rows = []
for rep, dd in B[B.levels >= 7].groupby("report"):
    p = g.pair(g.deals(f"C:/MT5_JEV_TEST/{rep}.htm"))[0]
    for _, b in dd.iterrows():
        x = p[(p.side == b.side) & (p.t0 >= b.t0) & (p.t0 <= b.t1)].sort_values("t0")
        for k in (7, 9):
            if len(x) < k: continue
            tk = x.t0.iloc[k - 1]
            n = np.searchsorted(ev, b.t1, "right") - np.searchsorted(ev, tk, "left")
            rows.append({"rep": rep, "k": k, "cut": b.kind == "cut", "news": n > 0})
R = pd.DataFrame(rows)
R["per"] = np.where(R.rep.str.startswith("d6t"), "19-21", np.where(R.rep == "yearf_live", "EG", "22-25"))
for k in (7, 9):
    Q = R[R.k == k]
    print(f"\n== deep from level {k}: P(cut) with a top release inside vs without")
    for p, G in [("all", Q)] + list(Q.groupby("per")):
        a, b = G[G.news], G[~G.news]
        print(f"{p:6s} with {a.cut.mean():.3f} (n={len(a)}, cut {a.cut.sum()})   without {b.cut.mean():.3f} (n={len(b)}, cut {b.cut.sum()})")

# control: a longer basket both meets more releases and is cut more often. Fixed window instead: a release within H hours
# after level k (whatever happens next), so exposure time is the same for every basket.
rows = []
for rep, dd in B[B.levels >= 7].groupby("report"):
    p = g.pair(g.deals(f"C:/MT5_JEV_TEST/{rep}.htm"))[0]
    for _, b in dd.iterrows():
        x = p[(p.side == b.side) & (p.t0 >= b.t0) & (p.t0 <= b.t1)].sort_values("t0")
        for k in (7, 9):
            if len(x) < k: continue
            tk = x.t0.iloc[k - 1]
            for H in (2, 6):
                n = np.searchsorted(ev, tk + H * 3600, "right") - np.searchsorted(ev, tk, "left")
                rows.append({"rep": rep, "k": k, "H": H, "cut": b.kind == "cut", "news": n > 0})
R = pd.DataFrame(rows); R["per"] = np.where(R.rep.str.startswith("d6t"), "19-21", np.where(R.rep == "yearf_live", "EG", "22-25"))
for (k, H), Q in R.groupby(["k", "H"]):
    print(f"\n== level {k}, release within {H}h after it")
    for p, G in [("all", Q)] + list(Q.groupby("per")):
        a, b = G[G.news], G[~G.news]
        print(f"{p:6s} with {a.cut.mean():.3f} (n={len(a)}, cut {a.cut.sum()})   without {b.cut.mean():.3f} (n={len(b)}, cut {b.cut.sum()})")
