"""Do deep baskets coincide with scheduled US releases (NFP, CPI, FOMC)?

Rules fixed before looking at the outcome table (written 2026-10-15):
- Event times: NFP and CPI 08:30 New York, FOMC decision 14:00 New York.
  Release dates from bls.gov archives and federalreserve.gov (listed below).
- Bar/deal clock = server time = New York + 7h (ASSUMED: the usual
  "New York close" server clock; the clock check in clusters.py only shows
  deals and bars share one clock, not its offset). A 2h margin on both sides
  covers a 1h DST mismatch.
- A basket is "exposed" when it is open at any moment in [event - 2h, event + 6h].
- Deep = MAE <= -10% of balance at basket start (same as the report).
- Train Nov-May, test Jun-Oct; Fisher exact test, one-sided (exposed deeper).
"""
import numpy as np, pandas as pd
from scipy.stats import fisher_exact

NFP = ["2025-11-20", "2025-12-16", "2026-01-09", "2026-02-11", "2026-03-06", "2026-04-03", "2026-05-08",
       "2026-06-05", "2026-07-02", "2026-08-07", "2026-09-04", "2026-10-02"]
CPI = ["2025-12-18", "2026-01-13", "2026-02-13", "2026-03-11", "2026-04-10", "2026-05-12", "2026-06-10",
       "2026-07-14", "2026-08-12", "2026-09-11"]
FOMC = ["2025-12-10", "2026-01-28", "2026-03-18", "2026-04-29", "2026-06-17", "2026-07-29", "2026-09-16"]
SERVER_MINUS_NY_H = 7
ev = ([pd.Timestamp(d) + pd.Timedelta(hours=8.5 + SERVER_MINUS_NY_H) for d in NFP + CPI] +
      [pd.Timestamp(d) + pd.Timedelta(hours=14 + SERVER_MINUS_NY_H) for d in FOMC])
ev = np.array(sorted(e.timestamp() for e in ev))

o = pd.read_csv("data/derived/bd1/clusters_strict.csv")
o["d"] = pd.to_datetime(o.t0, unit="s")
lo, hi = ev - 2 * 3600, ev + 6 * 3600
o["exposed"] = [bool(((t0 <= hi) & (t1 >= lo)).any()) for t0, t1 in zip(o.t0, o.t1)]
o["deep"] = o.mae_pct <= -10
o["deep_at_event"] = [bool(((mt >= lo) & (mt <= hi)).any()) for mt in o.mae_t]

for name, sub in [("Nov-May (train)", o[o.d < "2026-06-01"]), ("Jun-Oct (test)", o[o.d >= "2026-06-01"]),
                  ("all", o)]:
    t = pd.crosstab(sub.exposed, sub.deep).reindex(index=[True, False], columns=[True, False], fill_value=0)
    p = fisher_exact(t.values, alternative="greater")[1]
    r = lambda e: t.loc[e, True] / max(t.loc[e].sum(), 1) * 100
    print(f"{name}: exposed {t.loc[True].sum()} baskets, deep {t.loc[True, True]} ({r(True):.1f}%) | "
          f"not exposed {t.loc[False].sum()}, deep {t.loc[False, True]} ({r(False):.1f}%) | p={p:.3f}")
print("\ndeep baskets (MAE <= -10%):")
print(o[o.deep][["d", "side", "mae_pct", "pnl_pct", "guard", "exposed", "deep_at_event"]]
      .assign(d=lambda x: x.d.dt.strftime("%Y-%m-%d %H:%M")).round(1).to_string(index=False))
