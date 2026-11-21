"""GPT t321 P1: MDD threshold by block bootstrap (p95 over 365-day C1 paths / 252-position-day I2 paths), reference 2020..2025-10-24."""
import sys
sys.path.insert(0, "research/btc"); sys.path.insert(0, "research/stable")
import numpy as np, pandas as pd
from book_tester import i2_daily
rng = np.random.default_rng(20261121)
def mdd(r):
    e = np.cumprod(1 + r, axis=1); return -(e / np.maximum.accumulate(e, axis=1) - 1).min(axis=1)
def boot(r, L, B, n=20000):
    r = r.values; starts = rng.integers(0, len(r) - B, size=(n, -(-L // B)))
    p = np.concatenate([r[s:s + B] for s in starts.T], axis=0) if False else np.stack([np.concatenate([r[s:s + B] for s in row])[:L] for row in starts])
    return np.percentile(mdd(p), [50, 95, 99])
c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity["2020":"2025-10-24"].pct_change().dropna()
i2 = i2_daily()["2020":"2025-10-24"]; i2 = i2[i2 != 0]
for nm, r, L in (("C1 365 calendar days", c1, 365), ("I2 252 position days", i2, 252)):
    for B in (10, 30, 60):
        print(nm, f"block {B}: MDD p50/p95/p99 =", np.round(boot(r, L, B) * 100, 1))
