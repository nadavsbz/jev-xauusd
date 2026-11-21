"""Scan round 4 of docs/SCAN_PLAN.md (pre-registered 11.11.2026): gold opening-range breakouts with a stop, flat by bar 22.
G1 = London: range of server bars 03..09, entries at closes of bars 10..20. G2 = NY: range of bar 16 (15 in DST-mismatch weeks),
entries at closes of 17..20 (shifted likewise), exit at bar 22 (21). One trade a day, SL = opposite side of the range.
Usage: python research/scan/gold_orb.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import scale, rep
from scan2 import mismatch
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
TC = 0.00005   # spread 0.003% + commission 0.002% per side [ASSUMED commission]

def orb(h, rng_hrs, entry_hrs, exit_hr):
    out, side = {}, {}
    for d, x in h.groupby(h.index.normalize()):
        x = x.set_index(x.index.hour)
        sh = -1 if (rng_hrs[0] >= 15 and mismatch(d)) else 0
        rh = [k + sh for k in rng_hrs]; eh = [k + sh for k in entry_hrs]; ex = exit_hr + sh
        if not all(k in x.index for k in rh + eh + [ex]): continue
        hi, lo = x.loc[rh, "high"].max(), x.loc[rh, "low"].min()
        q = 0; entry = sl = None; r = 0.0
        for k in eh + [ex]:
            if q == 0 and k in eh and k != ex:
                c = x.loc[k, "close"]
                if c > hi: q, entry, sl = 1, c, lo
                elif c < lo: q, entry, sl = -1, c, hi
                if q: r -= TC; t0 = k
                continue
            if q == 0: continue
            b = x.loc[k]
            if (q == 1 and b.low <= sl) or (q == -1 and b.high >= sl):
                px = min(sl, b.open) if q == 1 else max(sl, b.open)
                r += q * (px / entry - 1) - TC; q = 0; break
            if k == ex: r += q * (b.close / entry - 1) - TC; q = 0; break
        out[d] = r; side[d] = np.sign(r) if r else 0
    return pd.Series(out)

if __name__ == "__main__":
    h = pd.read_csv("data/derived/intraday/XAUUSD_H1.csv"); h.index = pd.to_datetime(h.time, unit="s")
    h = h[(h.close > 0)]
    span = ("2015-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    print(f"===== round 4 gold ORB {PER} {span}")
    for nm, a, b, ex in (("G1 London", list(range(3, 10)), list(range(10, 21)), 22), ("G2 NY", [16], list(range(17, 21)), 22)):
        raw = orb(h, a, b, ex); x = scale(raw); x.to_csv(f"data/derived/scan/R4_{nm.split()[0]}_daily.csv", header=["ret"])
        rep(x.loc[span[0]:span[1]], nm)
        y = raw.loc[span[0]:span[1]]; print(f"    raw: days traded {int((y != 0).sum())}/{len(y)}, mean/trade {y[y != 0].mean() * 1e4:.1f} bp, hit {(y[y != 0] > 0).mean() * 100:.0f}%")
