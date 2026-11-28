"""Round 99 (prereg docs/prereg/r99_jp225_boj_afternoon.md): Tokyo morning drop <= -1% -> long JP225 12:35-14:55 JST.
Usage: py -3.12 research/scan/r99_jp225_boj.py dev|hold"""
import sys, json, glob
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import tcost, E
PART = sys.argv[1]; TD = pd.Timedelta
m = pd.read_csv("data/derived/scan/m5/JP225Cash.csv"); m.index = pd.to_datetime(m.time, unit="s"); m = m[~m.index.duplicated()]
tc = tcost("JP225Cash", m.resample("1h").last().dropna()); pt = E.loc[".JP225Cash", "point"]
cost = lambda t: max(tc, m.spread[t] * pt / m.open[t])
r = json.load(open(sorted(glob.glob("data/raw/n225/N225_*.json"))[-1]))["chart"]["result"][0]
TSE = set(pd.to_datetime(r["timestamp"], unit="s", utc=True).tz_convert("Asia/Tokyo").normalize().tz_localize(None))
srv = lambda jst: jst.tz_localize("Asia/Tokyo").tz_convert("Europe/Athens").tz_localize(None)
rows = []; miss = 0
for d in sorted(TSE):
    t0, t1, te, tx = (srv(d + TD(hours=h, minutes=mi)) for h, mi in ((9, 0), (11, 30), (12, 35), (14, 55)))
    if not all(t in m.index for t in (t0, t1, te, tx)): miss += 1; continue
    am = m.open[t1] / m.open[t0] - 1
    rows.append(dict(d=d, am=am, s=int(am <= -0.01), ret=m.open[tx] / m.open[te] - 1, c=cost(te) + cost(tx)))
D = pd.DataFrame(rows).set_index("d")
a, b = ("2018", "2022") if PART == "dev" else ("2023", "2026")
T = D[a:b]; T = T[T.s != 0]
net = T.ret - T.c; gross = T.ret
tst = net.mean() / net.std() * np.sqrt(len(net)); yrs = net.groupby(net.index.year).sum()
pf = net[net > 0].sum() / -net[net < 0].sum(); nc = net.sum() / T.c.sum()
A_, B_ = net[:"2021-03-18"], net["2021-03-19":]
print(f"{PART} {a}-{b}: TSE days {len(D[a:b])} (missing bars, all years: {miss}), trades {len(T)}, cost/side {tc * 100:.4f}%")
print(f"  gross/trade {gross.mean() * 1e4:.1f}bp  net {net.mean() * 1e4:.1f}bp  cost {T.c.mean() * 1e4:.1f}bp  t {tst:.2f}  PF {pf:.2f}  net/cost {nc:.2f}")
print(f"  regime A (<=18.3.2021): n {len(A_)} net {A_.mean() * 1e4 if len(A_) else float('nan'):.1f}bp | regime B: n {len(B_)} net {B_.mean() * 1e4 if len(B_) else float('nan'):.1f}bp")
print("  years (net %):", {y: round(v * 100, 2) for y, v in yrs.items()}, "| n/yr", net.groupby(net.index.year).size().to_dict())
ok = (len(T) >= 30 and tst >= 2.0 and (yrs > 0).mean() >= 0.6 and nc >= 2 and len(B_) > 0 and B_.mean() > 0) if PART == "dev" else (net.mean() > 0 and tst >= 1.0 and pf >= 1.2)
print("  ->", "PASS" if ok else "FAIL")
