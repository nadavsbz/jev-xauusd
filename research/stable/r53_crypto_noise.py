"""Round 53 (docs/prereg/r53_crypto_noise.md, d0d5dff): I2's noise-area rule unchanged on BTCUSD / ETHUSD, weekdays only.
Usage: py -3.12 research/stable/r53_crypto_noise.py [test]"""
import sys
TEST = len(sys.argv) > 1 and sys.argv[1] == "test"; sys.argv = sys.argv[:1]
sys.path.insert(0, "research/stable")
import numpy as np, pandas as pd
import second4 as S4, second as S2
a, b = ("2023-01-01", "2026-10-30") if TEST else ("2018-01-01", "2022-12-31")
raw = {}
for s in ("BTCUSD", "ETHUSD"):
    r = S4.strat(s); r[r.index.dayofweek >= 5] = 0.0; raw[s] = r
raw["MIX"] = pd.DataFrame(raw).fillna(0).mean(1)
X = {k: S4.scale_s(v).reindex(S4.C["C1"].index).fillna(0) for k, v in raw.items()}
for k, x in X.items():
    S2.rep(x, k, a, b)
    print(f"   corr C1 {x.loc[a:b].corr(S4.C['C1'].loc[a:b]):.2f} I2 {x.loc[a:b].corr(S4.C['I2'].loc[a:b]):.2f}; trades/day share {(raw[k].loc[a:b] != 0).mean():.2f}")
base = S4.C["C1"] + S4.C["I2"]
S2.rep(base, "C1+I2", a, b)
for k, x in X.items(): S2.rep(base + 0.5 * x, f"C1+I2+0.5{k}", a, b)
