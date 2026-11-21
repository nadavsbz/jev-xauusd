"""Crash days: can a 'nervous / trending' regime be measured before a basket opens? (docs/CRASH_LINK_PLAN.md; ideas from the
Telegram group and the web: Taranto's volatility-to-drift gate (mql5.com/en/articles/21833), variance ratio, Kaufman efficiency
ratio, ADX-like trend strength). All from closed H1 bars before the basket's first level:
  er24  = |close move over 24h| / sum |hourly moves|   (efficiency: 1 = straight line, 0 = noise)
  vr4   = variance of 4h moves / (4 x variance of 1h moves) over the last 96h (> 1 trending, < 1 mean-reverting)
  volr  = average H1 range last 24h / last 240h        (volatility burst)
  drift = |24h move| / average H1 range                (Taranto inverse: high = drift dominates)
AUC cut vs not cut and P(cut) per quintile, per period. Usage: python research/growth/crash_regime.py DIR_WITH_oos_b.csv"""
import sys, pandas as pd, numpy as np
S = sys.argv[1]
B = pd.concat([pd.read_csv("data/derived/crash_signs/baskets.csv"), pd.read_csv(S + "/oos_b.csv")]).drop_duplicates(["report", "side", "t0"])
h = pd.read_csv("data/derived/intraday/XAUUSD_H1.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
c = h.close; d1 = c.diff(); rng = h.high - h.low
F = pd.DataFrame({"er24": (c - c.shift(24)).abs() / d1.abs().rolling(24).sum(),
                  "vr4": (c - c.shift(4)).rolling(96).var() / (4 * d1.rolling(96).var()),
                  "volr": rng.rolling(24).mean() / rng.rolling(240).mean(),
                  "drift": (c - c.shift(24)).abs() / rng.rolling(240).mean()})
i = c.index.searchsorted(pd.to_datetime(B.t0, unit="s")) - 2                    # last H1 bar fully closed before t0
for k in F: B[k] = np.where(i >= 240, F[k].values[np.maximum(i, 0)], np.nan)
B["cut"] = B.kind == "cut"
B["per"] = np.where(B.report.str.startswith("d6t"), "19-21", np.where(B.report == "yearf_live", "EG", "22-25"))
def auc(G, k):
    x, y = G[G.cut][k].dropna().values, G[~G.cut][k].dropna().values
    return (x[:, None] > y[None, :]).mean() + 0.5 * (x[:, None] == y[None, :]).mean() if len(x) and len(y) else np.nan
for k in F:
    print(f"\n== {k}  AUC all {auc(B, k):.2f}  " + "  ".join(f"{p} {auc(G, k):.2f}" for p, G in B.groupby("per")))
    B["q"] = pd.qcut(B[k], 5, labels=False, duplicates="drop")
    print((B.groupby(["per", "q"]).cut.mean().unstack() * 1000).round(1).to_string())
