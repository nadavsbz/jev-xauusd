"""Round 77 (prereg docs/prereg/r77_c1_breadth.md): C1 python rule on BTC+ETH, baseline vs breadth-confirmed weights, same vol.
Usage: py -3.12 research/scan/r77_c1_breadth.py"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import donch, tcost, scale
from r64_mass import loadh, swaps
W, R, NET = {}, {}, {}
for s in ("BTCUSD", "ETHUSD"):
    h = loadh(s); tc = tcost(s, h); sl, ss = swaps(s, float(h.close.iloc[-1]))
    c = h.close.resample("6h").last().dropna(); R[s] = c.pct_change().fillna(0)
    W[s] = (0.5 * donch(c, True) + 0.5 * donch(c, False)).shift(2).fillna(0)
    NET[s] = (tc, sl, ss, c.index.to_series().diff().dt.total_seconds().fillna(0) / 86400 / 365)
idx = W["BTCUSD"].index.intersection(W["ETHUSD"].index)
def run(breadth):
    out = []
    for s, o in (("BTCUSD", "ETHUSD"), ("ETHUSD", "BTCUSD")):
        w = W[s].reindex(idx).fillna(0); wo = W[o].reindex(idx).fillna(0)
        if breadth: w = w.where((np.sign(w) == np.sign(wo)) | (w.abs() >= 0.999), 0.5 * w)
        tc, sl, ss, dt = NET[s]; r = R[s].reindex(idx).fillna(0); dt = dt.reindex(idx).fillna(0)
        net = w * r - w.diff().abs().fillna(0) * tc + np.where(w > 0, w * sl, -w * ss) * dt
        out.append(scale((1 + net).groupby(net.index.normalize()).prod() - 1))
    return scale(pd.concat(out, axis=1).fillna(0).mean(1))
def st(x):
    x = x[x.ne(0).idxmax():]; eq = (1 + x).cumprod()
    return x.mean() / x.std() * np.sqrt(365), (eq / eq.cummax() - 1).min() * 100, x.groupby(x.index.year).sum().mul(100).round(0).to_dict()
b, f = run(False), run(True)
for nm, a, z in [("dev 2017-2022", "2017", "2022"), ("holdout 2023-2026", "2023", "2026")]:
    sb, mb, yb = st(b[a:z]); sf, mf, yf = st(f[a:z])
    print(f"{nm}: base Sh {sb:.2f} MDD {mb:.1f} | breadth Sh {sf:.2f} MDD {mf:.1f} | years base {yb} breadth {yf}")
print("corr base vs breadth:", round(b.corr(f), 3))
