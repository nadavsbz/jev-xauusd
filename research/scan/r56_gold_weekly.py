"""Round 56 (docs/prereg/r56_gold_weekly_breakout.md, a752f1f): gold breakout of the previous week's range, weekly trailing exit.
Usage: py -3.12 research/scan/r56_gold_weekly.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import scale, rep, load, trend, tcost, E
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
A, B = ("2015-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-10-30")
COST, SWL, SWS, OFF = 0.31, -0.60, 0.19, 0.20

h = pd.read_csv("data/derived/intraday/XAUUSD_H1.csv"); h.index = pd.to_datetime(h.time, unit="s")
h = h[~h.index.duplicated()].query("close > 0")[["open", "high", "low", "close"]].sort_index()
wk = (h.index - pd.to_timedelta(h.index.dayofweek, unit="D")).normalize()
W = h.groupby(wk).agg(H=("high", "max"), L=("low", "min")); W = W.shift(1)   # previous full week, keyed by current week
PH, PL = W.H.reindex(wk).values, W.L.reindex(wk).values
o, hi, lo, cl = (h[c].values for c in ("open", "high", "low", "close")); ix = h.index
q, ent, sl, R, prev = 0, 0.0, 0.0, 0.0, cl[0]
bar_r = np.zeros(len(h)); trades = []

def close_at(px, i):
    global q
    bar_r[i] += q * (px / prev - 1)
    tr = trades[-1]; tr["exit"] = px; tr["t1"] = ix[i]; tr["gross"] = q * (px / tr["entry"] - 1); q_old = q; q = 0
    return q_old

for i in range(1, len(h)):
    if ix[i].normalize() != ix[i - 1].normalize() and q:          # swap per calendar night
        n = (ix[i].normalize() - ix[i - 1].normalize()).days
        s = n * (SWL if q > 0 else SWS) / cl[i - 1]; bar_r[i] += s; trades[-1]["swap"] += s
    prev = cl[i - 1]
    if np.isnan(PH[i]): continue
    done = False
    if q:   # exit check: stricter of SL and trailing
        if q > 0:
            lvl = max(ent - R, PL[i])
            if lo[i] <= lvl: close_at(min(o[i], lvl), i); done = True
        else:
            lvl = min(ent + R, PH[i])
            if hi[i] >= lvl: close_at(max(o[i], lvl), i); done = True
        if not done: bar_r[i] += q * (cl[i] / prev - 1); continue
        prev_px = None
    # entry (flat, possibly right after an exit in this bar -> only from the next bar, per prereg "next bar")
    if done: continue
    up, dn = hi[i] >= PH[i] + OFF, lo[i] <= PL[i] - OFF
    if not (up or dn): continue
    if up and dn: side = 1 if abs(PH[i] + OFF - o[i]) <= abs(o[i] - (PL[i] - OFF)) else -1
    else: side = 1 if up else -1
    q = side; R = PH[i] - PL[i]
    ent = max(o[i], PH[i] + OFF) if side > 0 else min(o[i], PL[i] - OFF)
    c = COST / ent; bar_r[i] -= c
    trades.append({"t0": ix[i], "q": side, "entry": ent, "cost": c, "swap": 0.0})
    slv = ent - R if side > 0 else ent + R                       # same-bar SL check (conservative)
    if (side > 0 and lo[i] <= slv) or (side < 0 and hi[i] >= slv):
        prev = ent; close_at(slv, i)
    else: bar_r[i] += q * (cl[i] / ent - 1)

r = pd.Series(bar_r, index=ix); d = r.groupby(ix.normalize()).sum()
t = pd.DataFrame([x for x in trades if "exit" in x]); t["net"] = t.gross - t.cost + t.swap
t = t[(t.t0 >= A) & (t.t0 <= B)]
x = scale(d); x.to_csv("data/derived/scan/r56_daily.csv", header=["ret"])
print(f"===== r56 gold weekly breakout {PER} {A}..{B}")
rep(x.loc[A:B], "r56 (10% vol)")
print(f"trades {len(t)}, net mean {t.net.mean()*1e4:.1f} bp (gross {t.gross.mean()*1e4:.1f}, cost {t.cost.mean()*1e4:.1f}, swap {t.swap.mean()*1e4:.1f}), "
      f"hit {(t.net>0).mean()*100:.0f}%, median hold {(t.t1-t.t0).median()}, long share {(t.q>0).mean():.2f}")
print("by year net bp:", t.groupby(t.t0.dt.year).net.agg(lambda v: round(v.sum()*1e4)).to_dict())
i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
j = pd.concat([x, i2, c1], axis=1, keys=["X", "I2", "C1"]).loc[A:B].dropna(subset=["X"]).fillna(0)
print("corr:", j.corr().round(2).loc["X"].to_dict())
