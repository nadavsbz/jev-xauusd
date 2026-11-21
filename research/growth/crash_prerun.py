"""Crash days: is a basket opened right after a sharp run in its own direction (the user's screenshot 5.11.2026: buys opened after a
+$80 rally, then the drop) more likely to be cut? (docs/CRASH_LINK_PLAN.md) For every clone basket: gold's move over the 4 / 12 / 24
closed H1 bars before the first level, signed so > 0 = the basket's direction (a run up before a buy basket), in the 120-bar average
H1 range. P(cut) per quintile, per period, and AUC cut vs not cut. Usage: python research/growth/crash_prerun.py DIR_WITH_oos_b.csv"""
import sys, pandas as pd, numpy as np
S = sys.argv[1]
B = pd.concat([pd.read_csv("data/derived/crash_signs/baskets.csv"), pd.read_csv(S + "/oos_b.csv")]).drop_duplicates(["report", "side", "t0"])
h = pd.read_csv("data/derived/intraday/XAUUSD_H1.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
c, a = h.close, (h.high - h.low).rolling(120).mean()
i = c.index.searchsorted(pd.to_datetime(B.t0, unit="s")) - 1                 # last H1 bar closed before... (bar open <= t0)
i = np.where(i >= 0, i, 0) - 1                                                # bar fully closed before t0
sg = np.where(B.side == "buy", 1, -1)
for n in (4, 12, 24):
    ok = i - n >= 120
    B[f"run{n}"] = np.where(ok, sg * (c.values[i] - c.values[np.maximum(i - n, 0)]) / a.values[i], np.nan)
B["cut"] = B.kind == "cut"
B["per"] = np.where(B.report.str.startswith("d6t"), "19-21", np.where(B.report == "yearf_live", "EG", "22-25"))
def auc(G, k):
    x, y = G[G.cut][k].dropna(), G[~G.cut][k].dropna()
    return (x.values[:, None] > y.values[None, :]).mean() if len(x) and len(y) else np.nan
print(B.groupby("per").cut.agg(["size", "sum"]))
for n in (4, 12, 24):
    k = f"run{n}"
    print(f"\n== {k}  AUC all {auc(B, k):.2f}  " + "  ".join(f"{p} {auc(G, k):.2f}" for p, G in B.groupby("per")))
    B["q"] = pd.qcut(B[k], 5, labels=False)
    t = B.groupby(["per", "q"]).cut.mean().unstack() * 1000
    t["edges"] = None; print((t.drop(columns="edges")).round(1).to_string())
    print("edges:", np.round(pd.qcut(B[k], 5, retbins=True)[1], 2))
print("\n== extreme runs (P(cut) per 1000 baskets, n)")
for k, th in (("run4", 3), ("run4", 5), ("run12", 6), ("run12", 10)):
    print(k, ">", th, "  ".join(f"{p} {G[G[k] > th].cut.mean() * 1000:.1f} (n={int((G[k] > th).sum())}) vs rest {G[G[k] <= th].cut.mean() * 1000:.1f}"
                               for p, G in B.groupby("per")))
