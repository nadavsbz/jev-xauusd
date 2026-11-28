"""Round 62 (prereg docs/prereg/r62_cot_reversal_wti.md, commit 3ac10ff): Grok H2 - COT Managed Money weekly-change reversal on WTI.
Price = EIA WTI spot daily (no roll jumps). Usage: py -3.12 research/scan/r62_cot_wti.py [dev|test]"""
import sys
import numpy as np, pandas as pd
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
SPAN = ("2012-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-12-31")
TC, SWL, SWS = 0.000376, -0.06, -0.03

c = pd.read_csv("data/derived/cot/wti_cot.csv", parse_dates=["date"]).set_index("date").sort_index()
net = (c.M_Money_Positions_Long_All - c.M_Money_Positions_Short_All) / c.Open_Interest_All
ch = net.diff(); z = (ch - ch.rolling(156).mean().shift(1)) / ch.rolling(156).std().shift(1)

p = pd.read_csv("data/derived/oil/wti_spot.csv", parse_dates=["date"]).set_index("date").px.sort_index()
r = p.pct_change(); bad = (p <= 0) | (p.shift(1) <= 0); r[bad | bad.shift(1, fill_value=False)] = 0.0; r = r.fillna(0)
days = p.index

pos = pd.Series(0.0, index=days); trades = []; busy_until = None
for d, zz in z[SPAN[0]:SPAN[1]].dropna().items():
    if abs(zz) < 1.5: continue
    i = days.searchsorted(d + pd.Timedelta(days=7))           # entry at Tuesday close (+7d) or next trading day
    if i + 10 >= len(days): continue
    if busy_until is not None and i < busy_until: continue
    s = -1.0 if zz >= 1.5 else 1.0; j = i + 10; busy_until = j
    pos.iloc[i + 1:j + 1] = s                                    # returns from day i+1..j earned
    seg = r.iloc[i + 1:j + 1]; nights = (days[j] - days[i]).days
    g = s * ((1 + seg).prod() - 1); sw = (SWL if s > 0 else SWS) * nights / 365
    trades.append(dict(d=days[i], s=s, z=zz, gross=g, net=g - 2 * TC + sw, sw=sw))

T = pd.DataFrame(trades).set_index("d")
dl = pos * r; dl[pos.diff().fillna(0) != 0] -= 0  # costs booked per trade below
cost = pd.Series(0.0, index=days)
for d, t in T.iterrows():
    i = days.get_loc(d); cost.iloc[i + 1] -= 2 * TC; cost.iloc[i + 1:i + 11] += t.sw / 10
D = (dl + cost)[SPAN[0]:SPAN[1]]
tt = T.net.mean() / T.net.std() * np.sqrt(len(T)); sh = D.mean() / D.std() * np.sqrt(252)
y = D.groupby(D.index.year).sum() * 100
print(f"== {PER} {SPAN}  n {len(T)}  long {int((T.s > 0).sum())} short {int((T.s < 0).sum())}")
print(f"net/trade {T.net.mean()*1e4:.1f} bp (gross {T.gross.mean()*1e4:.1f}, swap {T.sw.mean()*1e4:.1f}, cost {-2*TC*1e4:.1f})  t {tt:.2f}  hit {(T.net > 0).mean():.2f}")
print(f"daily Sharpe {sh:.2f}  pos years {int((y > 0).sum())}/{len(y)} |", " ".join(f"{a % 100:02d}:{v:+.1f}" for a, v in y.items()))
print("by side bp:", T.groupby("s").net.mean().mul(1e4).round(1).to_dict())
try:
    C1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change()
    j = pd.concat([D, C1], axis=1).dropna(); j = j[j.iloc[:, 0] != 0]
    print(f"corr with C1 (overlap, active days n={len(j)}): {j.corr().iloc[0, 1]:.2f}")
except Exception as e: print("C1 corr n/a", e)
