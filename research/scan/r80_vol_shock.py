"""Round 80 (prereg docs/prereg/r80_crypto_volume_shock_reversal.md): fade BTC/ETH hourly volume shocks (Binance data, RF costs).
Usage: py -3.12 research/scan/r80_vol_shock.py dev|test"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/stable")
import r66_structural as R
from scan import tcost
from r64_mass import loadh
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
R.PER = PER; R.SPAN = ("2019-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-12-31")
rows = []
for b, rf in (("BTCUSDT", "BTCUSD"), ("ETHUSDT", "ETHUSD")):
    x = pd.read_csv(f"data/derived/crypto/{b}_1h_binance.csv", parse_dates=["t"]).set_index("t")
    tc = tcost(rf, loadh(rf))
    hr = x.index.hour
    med = x.volume.groupby(hr).transform(lambda v: v.rolling(60, min_periods=40).median().shift(1))
    mad = x.volume.groupby(hr).transform(lambda v: (v - v.rolling(60, min_periods=40).median()).abs().rolling(60, min_periods=40).median().shift(1))
    vz = (x.volume - med) / (1.4826 * mad)
    ret = x.close / x.open - 1
    tr = pd.concat([x.high - x.low, (x.high - x.close.shift()).abs(), (x.low - x.close.shift()).abs()], axis=1).max(1) / x.close
    atr = tr.rolling(24).mean().shift(1); rng = (x.high - x.low) / x.close; p99 = rng.rolling(24 * 60, min_periods=24 * 40).quantile(0.99).shift(1)
    sig = (vz > 3) & (ret.abs() > 1.5 * atr) & (rng <= p99)
    O, H, L, C = x.open.values, x.high.values, x.low.values, x.close.values; ix = x.index; busy = -1
    for i in np.flatnonzero(sig.values):
        e = i + 1
        if e <= busy or e + 3 >= len(x): continue
        d = -np.sign(ret.iloc[i]); px = O[e]; vw = (H[i] + L[i] + C[i]) / 3; sl = px - d * 1.25 * (H[i] - L[i]); xp = None
        for j in range(e, e + 3):
            if (d > 0 and L[j] <= sl) or (d < 0 and H[j] >= sl): xp = sl; break
            if (d > 0 and H[j] >= vw) or (d < 0 and L[j] <= vw): xp = vw; break
        if xp is None: j = e + 2; xp = C[j]
        busy = j
        rows.append((ix[e].normalize(), d * (xp / px - 1) - 2 * tc, 2 * tc))
T = pd.DataFrame(rows, columns=["d", "net", "cost"]).set_index("d").sort_index()
print(f"===== {PER} {R.SPAN}  n in span {len(T[R.SPAN[0]:R.SPAN[1]])}")
R.report(T, "r80 crypto volume-shock fade")
