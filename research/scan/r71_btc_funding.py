"""Round 71 (prereg docs/prereg/r71_btc_funding_reversal.md, commit d69d545): fade extreme Binance BTC funding when daily ADX(14)<20.
Usage: py -3.12 research/scan/r71_btc_funding.py dev|test"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/stable")
import r66_structural as R
from scan import tcost
from r64_mass import loadh, swaps
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
R.PER = PER; R.SPAN = ("2020-09-10", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-12-31")

h = loadh("BTCUSD"); tc = tcost("BTCUSD", h); sl, ss = swaps("BTCUSD", float(h.close.iloc[-1]))
h.index = h.index.tz_localize("Europe/Athens", ambiguous="NaT", nonexistent="NaT").tz_convert("UTC").tz_localize(None)
h = h[h.index.notna()]; h = h[~h.index.duplicated()]
f = pd.read_csv("data/derived/crypto/btc_funding_binance.csv", parse_dates=["t"]).set_index("t").rate
f.index = f.index.round("h")
F24 = f.rolling("24h").mean()                                  # value at each print = mean of prints in the last 24h
daily = F24[F24.index.hour == 0]                               # at 00:00 UTC (includes the 00:00 print)
pct = daily.rolling(365, min_periods=300).apply(lambda x: (x[:-1] < x[-1]).mean() if len(x) > 1 else np.nan, raw=True)
med = F24.rolling("365D").median()
d = h.resample("1D").agg({"high": "max", "low": "min", "close": "last"}).dropna()
up, dn = d.high.diff(), -d.low.diff()
pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
tr = pd.concat([d.high - d.low, (d.high - d.close.shift()).abs(), (d.low - d.close.shift()).abs()], axis=1).max(1)
atr = tr.ewm(alpha=1 / 14, adjust=False).mean()
pdi = 100 * pd.Series(pdm, d.index).ewm(alpha=1 / 14, adjust=False).mean() / atr; mdi = 100 * pd.Series(mdm, d.index).ewm(alpha=1 / 14, adjust=False).mean() / atr
adx = (100 * (pdi - mdi).abs() / (pdi + mdi)).ewm(alpha=1 / 14, adjust=False).mean().shift(1)   # known up to yesterday

def run(use_adx):
    rows = []; busy = pd.Timestamp("2000-01-01")
    for t0, p in pct.dropna().items():
        if t0 < busy or not (p > 0.95 or p < 0.05): continue
        if use_adx and not (adx.get(t0.normalize(), np.nan) < 20): continue
        if t0 not in h.index: continue
        sgn = -1 if p > 0.95 else 1; px = h.open[t0]; end = t0 + pd.Timedelta(hours=48)
        chk = F24[(F24.index > t0) & (F24.index <= end)]
        cross = chk[(np.sign(chk - med.reindex(chk.index)) != np.sign(daily[t0] - med.get(t0, np.nan)))]
        xt = min(cross.index[0], end) if len(cross) else end
        if xt not in h.index:
            k = h.index.searchsorted(xt); xt = h.index[min(k, len(h) - 1)]
        g = sgn * (h.open[xt] / px - 1); nights = max((xt.normalize() - t0.normalize()).days, 0)
        sw = (sl if sgn > 0 else ss) * nights / 365
        rows.append((t0.normalize(), g - 2 * tc + sw, 2 * tc - min(sw, 0))); busy = xt
    return pd.DataFrame(rows, columns=["d", "net", "cost"]).set_index("d")

print(f"===== {PER} {R.SPAN}")
T = run(True); print(f"n={len((T[R.SPAN[0]:R.SPAN[1]]))}"); R.report(T, "r71 funding fade + ADX<20")
R.report(run(False), "r71 no ADX filter (descriptive)")
