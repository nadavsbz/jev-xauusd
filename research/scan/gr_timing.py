"""Scan round 22 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 night): does Gold Reaper V3.0 have real timing, or just gold drift?
Basket = tickets opened in the same minute and direction. Replay on RF ECN M1 opens (broker time == RF server time, NY+7).
Null: same basket, same direction / time of day / hold, on a random other trading day within +-60 days; 2000 draws.
Usage: python research/scan/gr_timing.py"""
import numpy as np, pandas as pd

F = "docs/agents/grok_data/myfxbook/goldreaper_history.csv"
m = pd.read_csv("data/derived/scan/m1/XAUUSD.csv"); m.index = pd.to_datetime(m.time, unit="s"); m = m[~m.index.duplicated()]
P = m.open; LO, HI = m.low, m.high

t = pd.read_csv(F)
t = t[t.Symbol == "XAUUSD"].copy()
t["o"] = pd.to_datetime(t["Open Date"], format="%m.%d.%Y %H:%M"); t["c"] = pd.to_datetime(t["Close Date"], format="%m.%d.%Y %H:%M")
t["q"] = np.where(t.Action == "Buy", 1, -1)
t["ret"] = t.q * (t["Close Price"] / t["Open Price"] - 1)
# replay per ticket and alignment check
t["po"], t["pc"] = P.reindex(t.o).values, P.reindex(t.c).values
inbar = (t["Open Price"] >= LO.reindex(t.o).values - 0.5) & (t["Open Price"] <= HI.reindex(t.o).values + 0.5)
gap = (t["Open Price"] - t.po).abs()
print(f"tickets {len(t)}, with M1 bars {t.po.notna().sum()} / exit bars {t.pc.notna().sum()}; open price in bar(+-0.5$) {inbar.mean()*100:.1f}%, median |gap| {gap.median():.2f}$")
if inbar.mean() < 0.8: raise SystemExit("alignment failed - stop (amended rule: >=80% of fills inside the M1 bar at shift 0)")
t = t[t.po.notna() & t.pc.notna()]
one = pd.Timedelta(minutes=1)
t["rep1"] = t.q * (P.reindex(t.c + one).values / P.reindex(t.o + one).values - 1)   # copier: next-minute opens
t = t[t.rep1.notna()]

rng = np.random.default_rng(22)
B = []
for (o, q), g in t.groupby(["o", "q"]):
    w = g.Lots / g.Lots.sum()
    hold = (g.c - o)                                             # per ticket
    d0 = o.normalize(); tod = o - d0
    cands = []
    for k in range(-60, 61):
        if k == 0: continue
        e = d0 + pd.Timedelta(days=k) + tod
        if e.dayofweek >= 5: continue
        ex = e + hold
        pe, px = P.get(e), P.reindex(ex).values
        if pe is None or np.isnan(px).any(): continue
        cands.append(float((w * q * (px / pe - 1)).sum()))
    if len(cands) < 10: continue
    B.append(dict(o=o, q=q, csv=float((w * g.ret).sum()), rep=float((w * g.ret).sum()), rep1=float((w * g.rep1).sum()), cand=np.array(cands)))
print(f"baskets {len(B)} (with >=10 null days)")
N = 2000
sims = np.zeros(N); simL = np.zeros(N); simS = np.zeros(N)
L = [b for b in B if b["q"] > 0]; S = [b for b in B if b["q"] < 0]
draw = {id(b): rng.choice(b["cand"], N) for b in B}
for grp, arr in ((B, sims), (L, simL), (S, simS)):
    arr[:] = np.mean([draw[id(b)] for b in grp], axis=0)
for nm, grp, arr in (("all", B, sims), ("long", L, simL), ("short", S, simS)):
    rep = np.mean([b["rep"] for b in grp]); csv = np.mean([b["rep1"] for b in grp])
    p = (arr >= rep).mean()
    print(f"  {nm:5s} n {len(grp):3d}  GR fills {rep*1e4:6.2f} bp  copier(+1m) {csv*1e4:6.2f} bp  null mean {arr.mean()*1e4:6.2f} bp  "
          f"excess {(rep-arr.mean())*1e4:6.2f} bp  p {p:.4f}  | copier excess {(csv-arr.mean())*1e4:6.2f} bp p {(arr >= csv).mean():.4f}")
yr = pd.Series([b["rep"] - b["cand"].mean() for b in B], index=[b["o"] for b in B])
print("  excess by half-year (bp):", yr.groupby([yr.index.year, (yr.index.month > 6) + 1]).mean().mul(1e4).round(1).to_dict())
