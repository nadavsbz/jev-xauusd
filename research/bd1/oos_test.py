"""Out-of-sample check of the crash-basket predictors from predictors.py.
Train = baskets starting before 2026-06-01, test = from 2026-06-01.
Hours 3-4 were spotted on the FULL table (train+test), so they are reported
only as a contaminated example; the honest test is the window chosen on
train alone."""
import numpy as np, pandas as pd
from scipy.stats import fisher_exact
o = pd.read_csv("data/derived/bd1/clusters_features.csv"); o["d"] = pd.to_datetime(o.t0, unit="s")
big = o[o.n >= 5]; tr, te = big[big.d < "2026-06-01"], big[big.d >= "2026-06-01"]
def test(name, rule):
    for lbl, s in [("train", tr), ("test", te)]:
        m = rule(s); a = [[(s.deep & m).sum(), (~s.deep & m).sum()], [(s.deep & ~m).sum(), (~s.deep & ~m).sum()]]
        print(f"{name:22s} {lbl}: flagged deep {a[0][0]}/{m.sum()}  unflagged deep {a[1][0]}/{(~m).sum()}  "
              f"p={fisher_exact(a, alternative='greater')[1]:.3f}")
# blind choice: the 2-hour window with the highest deep rate in TRAIN only
best = max((tr[tr.hour.isin([h, (h + 1) % 24])].deep.mean(), h) for h in range(24)
           if len(tr[tr.hour.isin([h, (h + 1) % 24])]) >= 10)
hb = [best[1], (best[1] + 1) % 24]
test(f"hours {hb} (train-chosen)", lambda s: s.hour.isin(hb))
test("hours [3, 4] (contaminated)", lambda s: s.hour.isin([3, 4]))
test("|mom24|>1.6 ATR", lambda s: s.mom24_atr.abs() > 1.6)
for lbl, s in [("train", o[o.d < "2026-06-01"]), ("test", o[o.d >= "2026-06-01"])]:
    m = s.hour.isin(hb)
    print(f"{lbl}: actual x{np.prod(1 + s.pnl_pct / 100):.2f}, skipping train-chosen hours x{np.prod(1 + s.pnl_pct[~m] / 100):.2f}")
