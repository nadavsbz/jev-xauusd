"""Crash days: is the move against a deep basket a dollar / metals / stocks move, or gold alone? (docs/CRASH_LINK_PLAN.md)
For every clone basket that reached level 9: from the basket's first level to level 9 (closed H1 bars), the move of gold and,
over the same hours, of EURUSD (dollar, sign flipped), USDJPY, silver and the S&P 500 (demo-terminal H1, read-only export),
each in its own 120-bar average H1 range, signed so that > 0 = the same direction as gold's move against the basket.
Cut vs recovered: AUC per feature, overall and per period. Usage: python research/growth/crash_xasset.py DIR_WITH_oos_b.csv"""
import sys, pandas as pd, numpy as np
from scipy.stats import mannwhitneyu
sys.path[:0] = ["research/btc", "research/bd1"]
import guardian_sim as g
S = sys.argv[1]
B = pd.concat([pd.read_csv("data/derived/crash_signs/baskets.csv"), pd.read_csv(S + "/oos_b.csv")])
D = B[B.levels >= 9].drop_duplicates(["report", "side", "t0"])
def h1(f):
    h = pd.read_csv(f); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
    return h.close, (h.high - h.low).rolling(120).mean()
X = {"gold": h1("data/derived/intraday/XAUUSD_H1.csv"), "eur_inv": h1("data/derived/intraday/EURUSD_H1_demo.csv"),
     "usdjpy": h1("data/derived/intraday/USDJPY_H1_demo.csv"), "silver": h1("data/derived/intraday/XAGUSD_H1_demo.csv"),
     "spx": h1("data/derived/intraday/US500Cash_H1_demo.csv")}
SIGN = {"gold": 1, "eur_inv": -1, "usdjpy": -1, "silver": 1, "spx": 1}   # dollar up = gold down: eur and jpy flipped
rows = []
for rep, dd in D.groupby("report"):
    p = g.pair(g.deals(f"C:/MT5_JEV_TEST/{rep}.htm"))[0]
    for _, b in dd.iterrows():
        x = p[(p.side == b.side) & (p.t0 >= b.t0) & (p.t0 <= b.t1)].sort_values("t0")
        if len(x) < 9: continue
        t0, t9 = pd.to_datetime(x.t0.iloc[0], unit="s"), pd.to_datetime(x.t0.iloc[8], unit="s")
        against = -1 if b.side == "buy" else 1                    # gold's move against the basket: down for buys
        r = {"rep": rep, "cut": b.kind == "cut"}
        for k, (c, a) in X.items():
            i0, i9 = c.index.searchsorted(t0) - 1, c.index.searchsorted(t9) - 1
            if i0 < 120 or i9 <= i0: r[k] = np.nan; continue
            r[k] = SIGN[k] * against * (c.iloc[i9] - c.iloc[i0]) / a.iloc[i9]
        rows.append(r)
R = pd.DataFrame(rows); R["per"] = np.where(R.rep.str.startswith("d6t"), "19-21", np.where(R.rep == "yearf_live", "EG", "22-25"))
R["usd_conf"] = R[["eur_inv", "usdjpy"]].mean(axis=1)
print(R.cut.value_counts().to_dict(), R.notna().mean().round(2).to_dict())
for k in ["gold", "eur_inv", "usdjpy", "usd_conf", "silver", "spx"]:
    a, b = R[R.cut][k].dropna(), R[~R.cut][k].dropna(); u, pv = mannwhitneyu(a, b)
    per = {gname: round(mannwhitneyu(G[G.cut][k].dropna(), G[~G.cut][k].dropna())[0] / G[G.cut][k].notna().sum() / G[~G.cut][k].notna().sum(), 2)
           for gname, G in R.groupby("per")}
    print(f"{k:9s} AUC {u / len(a) / len(b):.3f} p {pv:.4f} med cut {a.median():.2f} rec {b.median():.2f} {per}")
