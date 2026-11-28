"""Round 94 (prereg docs/prereg/r94_c1_stablecoin.md): stablecoin supply as a long/short weight filter on C1.
Usage: py -3.12 research/scan/r94_c1_stablecoin.py fetch|dev|hold"""
import sys, os, json, glob, datetime as dt
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
PART = sys.argv[1]
RAW = "data/raw/stablecoins"
if PART == "fetch":
    import urllib.request
    os.makedirs(RAW, exist_ok=True)
    req = urllib.request.Request("https://stablecoins.llama.fi/stablecoincharts/all", headers={"User-Agent": "research-client"})
    data = json.load(urllib.request.urlopen(req, timeout=60))
    f = f"{RAW}/all_{dt.date.today():%Y%m%d}.json"; json.dump(data, open(f, "w"))
    print(f"saved {len(data)} days -> {f}"); sys.exit()

from scan import tcost, scale
from r64_mass import loadh, swaps
import contextlib, io
with contextlib.redirect_stdout(io.StringIO()): from r77_c1_breadth import st   # silence its module-level report
data = json.load(open(sorted(glob.glob(f"{RAW}/all_*.json"))[-1]))
S = pd.Series({pd.Timestamp(int(x["date"]), unit="s").normalize(): x["totalCirculatingUSD"]["peggedUSD"] for x in data}).sort_index()
chg = S.pct_change(14)
ROLL = len(sys.argv) > 2 and sys.argv[2] == "roll"                     # r94b: rolling 365d (min 180)
z = ((chg - chg.rolling(365, min_periods=180).mean()) / chg.rolling(365, min_periods=180).std()) if ROLL else (chg - chg.expanding(365).mean()) / chg.expanding(365).std()
zprev = z.shift(1)                                                    # day d uses the value of d-1

def comps(c, long_only):
    out = []; cv = c.values
    for n in (10, 20, 30, 60, 90, 150, 250):
        hv, lv = c.rolling(n).max().values, c.rolling(n).min().values
        k = n // 2; xl, xh = c.rolling(k).min().values, c.rolling(k).max().values
        p = np.zeros(len(c))
        for i in range(1, len(c)):
            q = p[i - 1]
            if q == 0: q = 1 if cv[i] >= hv[i] else (-1 if (not long_only and cv[i] <= lv[i]) else 0)
            elif (q > 0 and cv[i] <= xl[i]) or (q < 0 and cv[i] >= xh[i]): q = 0
            p[i] = q
        out.append(p)
    return np.array(out)

def run(filt):
    out = []
    for s in ("BTCUSD", "ETHUSD"):
        h = loadh(s); tc = tcost(s, h); sl, ss = swaps(s, float(h.close.iloc[-1]))
        c = h.close.resample("6h").last().dropna()
        dtt = c.index.to_series().diff().dt.total_seconds().fillna(0) / 86400 / 365
        P = np.vstack([comps(c, True), comps(c, False)])              # 14 components, equal weight
        if filt:
            zz = zprev.reindex(c.index.normalize()).values
            mL = np.where(zz < 0, 0.5, 1.0); mS = np.where(zz > 0, 0.5, 1.0)   # NaN -> 1.0 both
            P = np.where(P > 0, P * mL, P * mS)
        w = pd.Series(P.mean(0), index=c.index).shift(2).fillna(0); r = c.pct_change().fillna(0)
        net = w * r - w.diff().abs().fillna(0) * tc + np.where(w > 0, w * sl, -w * ss) * dtt
        out.append(scale((1 + net).groupby(net.index.normalize()).prod() - 1))
    return scale(pd.concat(out, axis=1).fillna(0).mean(1))

a, b = ("2019", "2022") if PART == "dev" else ("2023", "2026")
base, flt = run(False), run(True)
sb, mb, yb = st(base[a:b]); sf, mf, yf = st(flt[a:b])
ok = (sf >= sb + 0.10 and mf >= mb) if PART == "dev" else (sf >= sb + 0.05 and mf >= mb - 1)
print(f"{PART} {a}-{b}: z coverage {zprev[a:b].notna().mean():.0%}, z>0 share {(zprev[a:b] > 0).mean():.0%}")
print(f"  BASE Sh {sb:.2f} MDD {mb:.1f} | {yb}")
print(f"  FILT Sh {sf:.2f} ({sf - sb:+.2f}) MDD {mf:.1f} corr {flt.corr(base):.2f} -> {'PASS' if ok else 'FAIL'} | {yf}")
