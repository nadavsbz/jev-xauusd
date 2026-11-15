"""Round 55 (docs/prereg/r55_on_reversal.md, 3fb37e2): overnight-intraday reversal on US500/USTECH/US30, RF M5.
Usage: py -3.12 research/scan/r55_on_reversal.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import tcost, scale, rep, load
from scan2 import mismatch
from r24_27 import bars, report
import r24_27
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
r24_27.PER = PER; r24_27.SPAN = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-10-30")

def one(s):
    m = bars(f"data/derived/scan/m5/{s}.csv")
    days = pd.Series(m.index.normalize().unique())
    sh = {d: pd.Timedelta(hours=6 if mismatch(d) else 7) for d in days}
    et = m.index - pd.to_timedelta([sh[d].value for d in m.index.normalize()])
    m = m.set_index(et); m = m[~m.index.duplicated()]
    tc = tcost(s, load(s)); rows = []
    for d, g in m.groupby(m.index.normalize()):
        t = g.index - d
        a = g[t == pd.Timedelta("09:30:00")]; b = g[t == pd.Timedelta("09:35:00")]; c = g[t == pd.Timedelta("15:55:00")]
        if len(a) and len(b) and len(c): rows.append((d, a.open.iloc[0], b.open.iloc[0], c.close.iloc[0]))
    x = pd.DataFrame(rows, columns=["d", "o", "e", "c"]).set_index("d")
    x["P"] = x.c.shift(1); x["on"] = x.o / x.P - 1
    sd = x.on.rolling(60, min_periods=40).std().shift(1)
    q = -np.sign(x.on).where(x.on.abs() >= sd, 0.0)
    r = q * (x.c / x.e - 1) - q.abs() * 2 * tc
    print(f"{s}: cost/side {tc*1e4:.2f} bp, days {len(x)}, trades {int((q != 0).sum())}")
    return r[q != 0], tc

if __name__ == "__main__":
    ev = {}
    for s in ("US500Cash", "USTECHCash", "US30Cash"):
        r, tc = one(s); ev[s] = r
        y = r.loc[r24_27.SPAN[0]:r24_27.SPAN[1]]
        print(f"   {s} {PER}: n {len(y)} mean {y.mean()*1e4:.2f} bp (RT cost {2*tc*1e4:.2f}) hit {(y>0).mean()*100:.0f}% t {y.mean()/y.std()*np.sqrt(len(y)):.2f}")
        report(r, s, f"r55_{s}")
    # basket: each index vol-scaled daily, equal weight, rescaled
    D = {s: scale(v.groupby(v.index).sum().reindex(pd.bdate_range(v.index[0], v.index[-1])).fillna(0)) for s, v in ev.items()}
    b = scale(pd.DataFrame(D).fillna(0).mean(1)); b.to_csv("data/derived/scan/r55_basket_daily.csv", header=["ret"])
    print("===== BASKET", PER); rep(b.loc[r24_27.SPAN[0]:r24_27.SPAN[1]], "r55 basket")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    j = pd.concat([b, i2], axis=1, keys=["X", "I2"]).loc[r24_27.SPAN[0]:r24_27.SPAN[1]].fillna(0)
    print("   basket corr I2:", round(j.corr().iloc[0, 1], 2))
