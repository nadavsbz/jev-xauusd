"""Round 75 (prereg docs/prereg/r75_book_voltarget.md): de-risk-only EWMA vol target on the 0.5*C1+0.5*I2 demo book.
Usage: py -3.12 research/stable/r75_voltarget.py"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); sys.path.insert(0, "research/stable")
from x2_check import i2, c
b = (0.5 * c("c1_ecn_av15_full") + 0.5 * i2("in2dst_t").reindex(c("c1_ecn_av15_full").index).fillna(0)).dropna()
lam = 0.5 ** (1 / 20); var = b.pow(2).ewm(alpha=1 - lam, adjust=False).mean().shift(1)
sig = np.sqrt(var * 365); tgt = b["2020":"2022"].std() * np.sqrt(365)
raw = (tgt / sig).clip(upper=1).fillna(1); m = []; cur = 1.0
for v in raw:
    if abs(v - cur) >= 0.10: cur = v
    m.append(cur)
m = pd.Series(m, index=b.index); cost = m.diff().abs().fillna(0) * 0.0003; v = m * b - cost
def st(x):
    eq = (1 + x).cumprod(); yrs = (x.index[-1] - x.index[0]).days / 365.25
    return dict(cagr=eq.iloc[-1] ** (1 / yrs) - 1, mdd=(eq / eq.cummax() - 1).min(), es5=x[x <= x.quantile(0.05)].mean(), sh=x.mean() / x.std() * np.sqrt(365))
print(f"target vol {tgt:.3f}; mean m {m.mean():.2f}; m changes {(m.diff() != 0).sum()}")
for nm, sl in [("2020-2022", slice("2020", "2022")), ("2023-2026", slice("2023", "2026"))]:
    a, z = st(b[sl]), st(v[sl])
    ok = (z["mdd"] >= 0.85 * a["mdd"]) and (z["es5"] > a["es5"]) and (z["cagr"] >= 0.9 * a["cagr"]) and (z["sh"] >= a["sh"] - 0.05)
    print(f"{nm}: base CAGR {a['cagr']*100:5.1f}% MDD {a['mdd']*100:5.1f}% ES5 {a['es5']*100:5.2f}% Sh {a['sh']:.2f} | VT CAGR {z['cagr']*100:5.1f}% MDD {z['mdd']*100:5.1f}% ES5 {z['es5']*100:5.2f}% Sh {z['sh']:.2f} -> {'PASS' if ok else 'FAIL'}")
