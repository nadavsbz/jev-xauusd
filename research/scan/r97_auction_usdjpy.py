"""Round 97 (prereg docs/prereg/r97_treasury_auction_usdjpy.md): weak/strong 7-30Y Treasury auction -> USDJPY 13:05-15:55 ET.
Usage: py -3.12 research/scan/r97_auction_usdjpy.py dev|hold"""
import sys, json, glob
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan2 import mismatch
PART = sys.argv[1]; TD = pd.Timedelta

# auctions: nominal notes/bonds, original term 7/10/20/30Y, no TIPS/FRN
A = pd.DataFrame(json.load(open(sorted(glob.glob("data/raw/auctions/notes_bonds_*.json"))[-1])))
A = A[A.original_security_term.isin(["7-Year", "10-Year", "20-Year", "30-Year"]) & (A.inflation_index_security == "No") & (A.floating_rate == "No")]
for c in ("bid_to_cover_ratio", "indirect_bidder_accepted", "total_accepted"): A[c] = pd.to_numeric(A[c], errors="coerce")
A = A.dropna(subset=["bid_to_cover_ratio", "indirect_bidder_accepted", "total_accepted"]).copy()
A["d"] = pd.to_datetime(A.auction_date); A["ind"] = A.indirect_bidder_accepted / A.total_accepted; A = A.sort_values("d")
sig = []
for term, g in A.groupby("original_security_term"):
    for i in range(12, len(g)):
        p = g.iloc[i - 12:i]; x = g.iloc[i]
        b20, b80 = np.quantile(p.bid_to_cover_ratio, [0.2, 0.8]); i20, i80 = np.quantile(p.ind, [0.2, 0.8])
        s = 1 if (x.bid_to_cover_ratio < b20 and x.ind < i20) else (-1 if (x.bid_to_cover_ratio > b80 and x.ind > i80) else 0)
        sig.append((x.d, s))
S = pd.DataFrame(sig, columns=["d", "s"]); S = S[S.s != 0].groupby("d").s.agg(lambda v: v.iloc[0] if v.nunique() == 1 else 0)
S = S[S != 0]

# macro days (ET dates): FOMC/NFP from events.csv, CPI from the MT5 calendar (12.2018+) + the 2018 BLS release dates
ev = pd.read_csv("data/derived/events.csv"); ev = pd.to_datetime(ev.utc).dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.normalize().dt.tz_localize(None)
cal = pd.read_csv("data/derived/news/mt5_calendar_usd.csv"); cal = cal[cal.event == "CPI m/m"]
cpi = pd.to_datetime(cal.time, unit="s").dt.tz_localize("UTC").dt.tz_convert("America/New_York").dt.normalize().dt.tz_localize(None)
cpi18 = pd.to_datetime(["2018-01-12", "2018-02-14", "2018-03-13", "2018-04-11", "2018-05-10", "2018-06-12", "2018-07-12", "2018-08-10",
                        "2018-09-13", "2018-10-11", "2018-11-14", "2018-12-12"])
MACRO = set(ev) | set(cpi) | set(cpi18)

m = pd.read_csv("data/derived/scan/m5/USDJPY.csv"); m.index = pd.to_datetime(m.time, unit="s"); m = m[~m.index.duplicated()]
pt = 0.001
sp = m.spread * pt / m.open
base = float(sp["2026"].median()) + 0.00005
print(f"cost per side (median 2026 spread + 0.005% comm): {base * 100:.4f}%", "-> over the 0.02% gate, STOP" if base > 0.0002 else "-> ok")
if base > 0.0002: sys.exit()
cost = lambda t: max(base, sp[t])

rows = []
for d, s in S.items():
    if d in MACRO: continue
    k = 6 if mismatch(d) else 7
    te, tx = d + TD(hours=13 + k, minutes=5), d + TD(hours=15 + k, minutes=55)
    if te not in m.index or tx not in m.index: continue
    rows.append(dict(d=d, s=s, ret=m.open[tx] / m.open[te] - 1, c=cost(te) + cost(tx)))
T = pd.DataFrame(rows).set_index("d")
a, b = ("2018", "2022") if PART == "dev" else ("2023", "2026")
T = T[a:b]; net = T.s * T.ret - T.c; gross = T.s * T.ret
tst = net.mean() / net.std() * np.sqrt(len(net)); yrs = net.groupby(net.index.year).sum()
pf = net[net > 0].sum() / -net[net < 0].sum(); nc = net.sum() / T.c.sum()
print(f"{PART} {a}-{b}: signals {len(S[a:b])}, trades {len(T)} (long/weak {(T.s > 0).sum()}, short/strong {(T.s < 0).sum()})")
print(f"  gross/trade {gross.mean() * 1e4:.1f}bp  net/trade {net.mean() * 1e4:.1f}bp  cost/trade {T.c.mean() * 1e4:.1f}bp  t {tst:.2f}  PF {pf:.2f}  net/cost {nc:.2f}")
print("  by side net bp:", {int(k): round(v * 1e4, 1) for k, v in net.groupby(T.s).mean().items()})
print("  years (net %):", {y: round(v * 100, 2) for y, v in yrs.items()}, "| n/yr", net.groupby(net.index.year).size().to_dict())
ok = (len(T) >= 25 and tst >= 2.0 and (yrs > 0).mean() >= 0.6 and nc >= 2) if PART == "dev" else (net.mean() > 0 and tst >= 1.0 and pf >= 1.2)
print("  ->", "PASS" if ok else "FAIL")
