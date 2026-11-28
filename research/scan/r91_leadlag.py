"""Round 91 (prereg docs/prereg/r91_leadlag_scan.md): daily lead-lag scan over 15 RF instruments.
Usage: py -3.12 research/scan/r91_leadlag.py dev|hold"""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import tcost
from r64_mass import loadh, swaps
PART = sys.argv[1]
U = ["XAUUSD", "XAGUSD", "WTI", "BRENT", ".US500Cash", ".USTECHCash", ".DE40Cash", ".JP225Cash",
     "EURUSD", "USDJPY", "AUDUSD", "GBPUSD", "USDCAD", "BTCUSD", "ETHUSD"]
C, TC, SW = {}, {}, {}
for s in U:
    h = loadh(s); x = h.close[h.index.hour == 22]; x.index = x.index.normalize()
    C[s] = x[x.index.dayofweek < 5]; TC[s] = tcost(s.lstrip("."), h); SW[s] = swaps(s, float(h.close.iloc[-1]))
P = pd.DataFrame(C).dropna()
R = P.pct_change()
gap = pd.Series(P.index, index=P.index).diff().dt.days.fillna(1)       # nights held (weekends = 3)
def strat(L, F, k, sgn):
    sig = np.sign(P[L] / P[L].shift(k) - 1) * sgn
    pos = sig.shift(1)                                                  # decided at close t, held t -> t+1
    sl, ss = SW[F]
    sw = np.where(pos > 0, pos * sl, -pos * ss) * gap / 365
    return (pos * R[F] - pos.diff().abs() * TC[F] + sw).dropna()
def tstat(x): return x.mean() / x.std() * np.sqrt(len(x)) if x.std() > 0 else 0.0
if PART == "dev":
    D = slice("2019", "2022"); sel = []
    for L in U:
        for F in U:
            if L == F: continue
            for k in (1, 5):
                raw = strat(L, F, k, 1)[D]
                sgn = 1 if tstat(raw) >= 0 else -1
                x = strat(L, F, k, sgn)[D]; t = tstat(x)
                if t >= 3.3: sel.append(dict(L=L, F=F, k=k, sgn=sgn, t=round(t, 2), sh=round(x.mean() / x.std() * np.sqrt(260), 2)))
    print(f"dev 2019-2022: {len(P[D])} days, 420 tests, selected {len(sel)}")
    for s in sel: print("  ", s)
    json.dump(sel, open("research/scan/r91_selected.json", "w"), indent=1)
else:
    sel = json.load(open("research/scan/r91_selected.json")); H = slice("2023", "2026")
    if not sel: print("no pair selected in dev -> no exploitable link")
    for s in sel:
        x = strat(s["L"], s["F"], s["k"], s["sgn"])[H]; t = tstat(x); sh = x.mean() / x.std() * np.sqrt(260)
        ok = x.mean() > 0 and t >= 2.0 and sh >= 0.5
        print(f"hold {s['L']}->{s['F']} k={s['k']} sgn={s['sgn']}: n={len(x)} mean {x.mean()*1e4:+.1f}bp t={t:.2f} Sh {sh:.2f} -> {'PASS' if ok else 'FAIL'}")
