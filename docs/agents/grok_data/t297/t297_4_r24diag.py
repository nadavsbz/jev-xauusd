#!/usr/bin/env python3
"""t297_4 (Grok): round-24 gates 2-4 as DIAGNOSTIC (AUDUSD ECN vs base17), realized only. PREREG_t297_4.md (sha 1166518b...)."""
import sys, json; sys.path.insert(0, "/workspace/t297")
import numpy as np, pandas as pd
from t297_common import IN, deals, pair, baskets, sha
YEARS = range(2019, 2026)
def load(path):
    d, dep = deals(path); dep = dep or 120000.0
    x = pd.DataFrame(d); x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize()
    pnl = (x.profit + x.swap + x.com).groupby(x.day).sum()
    eq = dep + pnl.cumsum(); r = pnl / eq.shift(1).fillna(dep)
    cut = {pd.Timestamp(b["t1"], unit="s").normalize() for b in baskets(pair(d), d) if b["net_pct"] <= -8}
    return pnl / dep * 100, r, cut, dep
A = {y: load(f"{IN}/ev24_rf{y}_aud_ecn.htm") for y in YEARS}; G = {y: load(f"{IN}/ev23_rf{y}_base17.htm") for y in YEARS}
out = dict(prereg_sha=sha("/workspace/t297/out/PREREG_t297_4.md"), per_year={})
pa = pd.concat([A[y][0] for y in YEARS]); pg = pd.concat([G[y][0] for y in YEARS])
U = pa.index.union(pg.index); c_all = float(pa.reindex(U).fillna(0).corr(pg.reindex(U).fillna(0)))
cutA = set().union(*[A[y][2] for y in YEARS]); cutG = set().union(*[G[y][2] for y in YEARS])
hit = [d for d in cutA if any(abs((d - g).days) <= 1 for g in cutG)]
share3 = len(hit) / len(cutA) * 100 if cutA else float("nan")
def mdd(r): e = (1 + r).cumprod(); return float((1 - e / np.maximum(e.cummax(), 1.0)).max() * 100), float((e.iloc[-1] - 1) * 100)
better = 0; ra, rg, rp = [], [], []
for y in YEARS:
    ia = A[y][1]; ig = G[y][1]; u = ia.index.union(ig.index); ia = ia.reindex(u).fillna(0); ig = ig.reindex(u).fillna(0)
    p = 0.5 * ia + 0.5 * ig; mp, tp = mdd(p); mg, tg = mdd(ig); ma, ta = mdd(ia)
    cy = float(A[y][0].reindex(u).fillna(0).corr(G[y][0].reindex(u).fillna(0)))
    better += mp < mg; ra.append(ta); rg.append(tg); rp.append(tp)
    out["per_year"][str(y)] = dict(corr=cy, aud_ret=ta, gold_ret=tg, port_ret=tp, aud_mdd=ma, gold_mdd=mg, port_mdd=mp, aud_cut_days=len(A[y][2]), gold_cut_days=len(G[y][2]))
mg_, mp_ = float(np.mean(rg)), float(np.mean(rp))
g4_ret = (mp_ >= 0.5 * mg_) if mg_ > 0 else (mp_ >= mg_)
out.update(gate2=dict(corr_all=c_all, pass_=c_all <= 0.3), gate3=dict(aud_cut_days=len(cutA), gold_cut_days=len(cutG), on_gold_pm1=len(hit), share=share3, pass_=share3 <= 30),
           gate4=dict(years_port_mdd_lower=int(better), mean_ret_gold=mg_, mean_ret_port=mp_, mean_ret_aud=float(np.mean(ra)), pass_=bool(better >= 5 and g4_ret)))
json.dump(out, open("/workspace/t297/out/t297_4_results.json", "w"), ensure_ascii=False, indent=1, default=float)
print(json.dumps(out, ensure_ascii=False, indent=1, default=float))
