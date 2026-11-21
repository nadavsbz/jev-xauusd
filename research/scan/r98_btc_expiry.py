"""Round 98 (prereg docs/prereg/r98_btc_deribit_expiry.md): fade the 00-08 UTC BTC move on the last-Friday Deribit expiry, hold 48h.
Usage: py -3.12 research/scan/r98_btc_expiry.py dev|hold"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import tcost, E
PART = sys.argv[1]; TD = pd.Timedelta
m = pd.read_csv("data/derived/scan/m5/BTCUSD.csv"); m.index = pd.to_datetime(m.time, unit="s"); m = m[~m.index.duplicated()]
tc = tcost("BTCUSD", m.resample("1h").last().dropna()); pt = E.loc["BTCUSD", "point"]
sw = 0.0475 * 2 / 365
srv = lambda utc: utc.tz_localize("UTC").tz_convert("Europe/Athens").tz_localize(None)   # server clock = Frankfurt+1
rows = []
for mo in pd.date_range("2018-01-01", "2026-10-31", freq="MS"):
    fri = (mo + pd.offsets.MonthEnd(0)); fri = fri - TD(days=(fri.dayofweek - 4) % 7)
    t0, t8, te, tx = (srv(fri + TD(hours=h, minutes=mi)) for h, mi in ((0, 0), (8, 0), (8, 5), (56, 5)))
    if not all(t in m.index for t in (t0, t8, te, tx)): print("missing bar", fri.date()); continue
    r = m.open[t8] / m.open[t0] - 1; s = -1 if r >= 0.02 else (1 if r <= -0.02 else 0)
    c = max(tc, m.spread[te] * pt / m.open[te]) + max(tc, m.spread[tx] * pt / m.open[tx])
    rows.append(dict(d=fri, r=r, s=s, ret=m.open[tx] / m.open[te] - 1, c=c))
D = pd.DataFrame(rows).set_index("d")
a, b = ("2018", "2022") if PART == "dev" else ("2023", "2026")
T = D[a:b]; T = T[T.s != 0]
net = T.s * T.ret - T.c - sw; net2 = T.s * T.ret - 2 * T.c - sw; gross = T.s * T.ret
tst = net.mean() / net.std() * np.sqrt(len(net)); yrs = net.groupby(net.index.year).sum()
pf = net[net > 0].sum() / -net[net < 0].sum(); nc = net.sum() / (T.c + sw).sum()
print(f"{PART} {a}-{b}: expiries {len(D[a:b])}, trades {len(T)} (long {(T.s > 0).sum()}, short {(T.s < 0).sum()}), cost/side {tc * 100:.4f}%")
print(f"  gross/trade {gross.mean() * 100:.2f}%  net {net.mean() * 100:.2f}%  net@2x {net2.mean() * 100:.2f}%  t {tst:.2f}  PF {pf:.2f}  net/cost {nc:.2f}")
print("  by side net %:", {int(k): round(v * 100, 2) for k, v in net.groupby(T.s).mean().items()})
print("  years (net %):", {y: round(v * 100, 2) for y, v in yrs.items()}, "| n/yr", net.groupby(net.index.year).size().to_dict())
ok = (len(T) >= 20 and tst >= 2.0 and (yrs > 0).mean() >= 0.6 and nc >= 2 and net2.mean() > 0) if PART == "dev" else (net.mean() > 0 and tst >= 1.0 and pf >= 1.2)
print("  ->", "PASS" if ok else "FAIL")
