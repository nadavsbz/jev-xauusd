"""Round 100 (prereg docs/prereg/r100_tga_btc.md): extreme daily TGA change (rolling 756 q5/q95) -> BTC 72h, entry 16:15 ET on the publication day.
Usage: py -3.12 research/scan/r100_tga_btc.py dev|hold"""
import sys, json, glob
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import tcost, E
PART = sys.argv[1]; TD = pd.Timedelta
R = pd.DataFrame(json.load(open(sorted(glob.glob("data/raw/tga/ocb_*.json"))[-1])))
# the Fed-account closing balance across the three DTS formats (the 2022+ "Closing Balance" line carries it in open_today_bal)
a1 = R[R.account_type.isin(["Federal Reserve Account", "Treasury General Account (TGA)"])].set_index("record_date").close_today_bal
a2 = R[R.account_type == "Treasury General Account (TGA) Closing Balance"].set_index("record_date").open_today_bal
B = pd.to_numeric(pd.concat([a1, a2]), errors="coerce"); B.index = pd.to_datetime(B.index); B = B[~B.index.duplicated()].sort_index().dropna()
dT = B.diff().dropna()
q5 = dT.rolling(756).quantile(0.05).shift(1); q95 = dT.rolling(756).quantile(0.95).shift(1)
sig = pd.Series(np.where(dT > q95, -1, np.where(dT < q5, 1, 0)), dT.index)[q5.notna()]
pub = pd.Series(B.index[1:], index=B.index[:-1])          # publication day of record t = the next record date
nyt = lambda d, h, mi: (d + TD(hours=h, minutes=mi)).tz_localize("America/New_York")
srv = lambda ts: ts.tz_convert("Europe/Athens").tz_localize(None)

ev = pd.read_csv("data/derived/events.csv"); fomc = pd.to_datetime(ev[ev.kind == "FOMC"].utc).dt.tz_localize("UTC")
cal = pd.read_csv("data/derived/news/mt5_calendar_usd.csv"); cpi = pd.to_datetime(cal[cal.event == "CPI m/m"].time, unit="s").dt.tz_localize("UTC")
cpi18 = pd.to_datetime([f"2018-{m}-{d} 13:30" for m, d in ((1, 12), (2, 14), (3, 13), (4, 11), (5, 10), (6, 12), (7, 12), (8, 10), (9, 13), (10, 11), (11, 14))]).tz_localize("UTC")
MAC = pd.DatetimeIndex(list(fomc) + list(cpi) + list(cpi18))

m = pd.read_csv("data/derived/scan/m5/BTCUSD.csv"); m.index = pd.to_datetime(m.time, unit="s"); m = m[~m.index.duplicated()]
tc = tcost("BTCUSD", m.resample("1h").last().dropna()); pt = E.loc["BTCUSD", "point"]; sw = 0.0475 * 3 / 365
rows = []; busy = None; skip_mac = 0
for t, s in sig[sig != 0].items():
    if t not in pub.index: continue
    e = nyt(pub[t], 16, 15); x = e + TD(hours=72)
    if busy is not None and e < busy: continue
    if ((MAC >= e.tz_convert("UTC")) & (MAC < e.tz_convert("UTC") + TD(hours=24))).any(): skip_mac += 1; continue
    te, tx = srv(e), srv(x)
    if te not in m.index or tx not in m.index: continue
    c = max(tc, m.spread[te] * pt / m.open[te]) + max(tc, m.spread[tx] * pt / m.open[tx])
    rows.append(dict(d=pub[t], s=s, ret=m.open[tx] / m.open[te] - 1, c=c)); busy = x
T = pd.DataFrame(rows).set_index("d")
a, b = ("2018", "2022") if PART == "dev" else ("2023", "2026")
T = T[a:b]
net = T.s * T.ret - T.c - sw; net2 = T.s * T.ret - 2 * T.c - sw
tst = net.mean() / net.std() * np.sqrt(len(net)); yrs = net.groupby(net.index.year).sum()
pf = net[net > 0].sum() / -net[net < 0].sum(); nc = net.sum() / (T.c + sw).sum()
print(f"{PART} {a}-{b}: signals {int((sig[a:b] != 0).sum())}, macro-skipped (all) {skip_mac}, trades {len(T)} (long {(T.s > 0).sum()}, short {(T.s < 0).sum()})")
print(f"  gross {(T.s * T.ret).mean() * 100:.2f}%  net {net.mean() * 100:.2f}%  net@2x {net2.mean() * 100:.2f}%  t {tst:.2f}  PF {pf:.2f}  net/cost {nc:.2f}")
print("  by side net %:", {int(k): round(v * 100, 2) for k, v in net.groupby(T.s).mean().items()})
print("  years (net %):", {y: round(v * 100, 1) for y, v in yrs.items()}, "| n/yr", net.groupby(net.index.year).size().to_dict())
ok = (len(T) >= 40 and tst >= 2.0 and (yrs > 0).mean() >= 0.6 and nc >= 2 and net2.mean() > 0) if PART == "dev" else (net.mean() > 0 and tst >= 1.0 and pf >= 1.2)
print("  ->", "PASS" if ok else "FAIL")
