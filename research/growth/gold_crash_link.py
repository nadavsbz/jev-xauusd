"""Growth search, track B (pre-registered 3.11.2026 in docs/GROWTH_SEARCH_PLAN.md): BD's crash days vs the gold noise area.
B1 hedge: GX1/GX2 raw daily return on the close day of each cut basket vs the average day; daily corr with BD's net_pct.
B2 detection: at basket open, was the last closed H1 bar (anchor 10, checks 10..21) beyond the band AGAINST the basket
(buy: below lower, sell: above upper)? Cut vs deep_recovered rate, Fisher p. Data: data/derived/crash_signs/baskets.csv
(RoboForex 2022-2025 clone runs). Usage: python research/growth/gold_crash_link.py"""
import sys
import numpy as np, pandas as pd
from scipy.stats import fisher_exact
sys.path.insert(0, "research/growth")
import noise_more as N

B = pd.read_csv("data/derived/crash_signs/baskets.csv"); B = B[B.report.str.startswith("rf")]
B["d0"] = pd.to_datetime(B.t0, unit="s"); B["d1"] = pd.to_datetime(B.t1, unit="s").dt.normalize()

print("== B1 hedge")
bd = B.groupby("d1").net_pct.sum()
for nm in ("GX1", "GX2"):
    s, an, la, ex = N.COMP[nm]; g = N.strat(s, an, la, ex).loc["2022":"2025"]
    cut = B[B.kind == "cut"].d1.drop_duplicates(); gc = g.reindex(cut).dropna()
    j = pd.concat([bd, g], axis=1, keys=["bd", "g"]).dropna()
    print(f"{nm}: avg day {g.mean() * 1e4:+.1f}bp | cut days n={len(gc)} mean {gc.mean() * 1e4:+.1f}bp, >0 {np.mean(gc > 0):.0%} | "
          f"corr daily {j.bd.corr(j.g):+.2f} | hedge: {gc.mean() > 0 and gc.mean() >= 3 * abs(g.mean()) and j.bd.corr(j.g) < 0}")

print("== B2 detection (anchor 10)")
Cl, chk, up, lo, sig, prev = N.bands("XAUUSD", 10, 21, 22)
def state(r):
    d = r.d0.normalize(); k = r.d0.hour - 1                      # last bar closed before the open: bar k closes at k+1
    if d not in Cl.index or k < 10 or k > 21 or np.isnan(prev.get(d, np.nan)) or sig.loc[d].isna().any(): return "n/a"
    c = Cl.at[d, k]; U = up[d] * (1 + sig.at[d, k]); L = lo[d] * (1 - sig.at[d, k])
    against = (c < L) if r.side == "buy" else (c > U)
    withd = (c > U) if r.side == "buy" else (c < L)
    return "against" if against else ("with" if withd else "inside")
X = B[B.kind != "other"].copy(); X["st"] = X.apply(state, axis=1)
t = pd.crosstab(X.kind, X.st); print(t)
k = X[X.st != "n/a"]; a = ((k.kind == "cut") & (k.st == "against")).sum(); b = ((k.kind == "cut") & (k.st != "against")).sum()
c = ((k.kind != "cut") & (k.st == "against")).sum(); d = ((k.kind != "cut") & (k.st != "against")).sum()
rc, rd = a / (a + b), c / (c + d); p = fisher_exact([[a, b], [c, d]])[1]
print(f"against: cut {rc:.0%} vs deep {rd:.0%} ratio {rc / rd if rd else np.inf:.2f} p={p:.3f} | sign: {rc >= 1.5 * rd and p < 0.05}")
