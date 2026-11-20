#!/usr/bin/env python3
"""t297_3 (Grok): diversification between existing BD versions. Rules frozen in PREREG_t297_3.md (sha e71a6414...)."""
import sys, json, math, itertools; sys.path.insert(0, "/workspace/t297")
import numpy as np, pandas as pd
from t297_common import IN, mtm_daily, sha
YEARS = range(2017, 2026)
V = {"base17": "ev23_rf{y}_base17", "user": "ev87_rf{y}_user", "uh1119": "ev88_rf{y}_uh1119", "ms20_h1119_dd75": "ev84_rf{y}_ms20_h1119_dd75"}
rc, rw, cd, info = {}, {}, {}, {}
for v, pat in V.items():
    a, b, days, ntr, nb = [], [], set(), 0, 0
    for y in YEARS:
        m = mtm_daily(f"{IN}/{pat.format(y=y)}.htm")
        if m is None: continue
        g = m["daily"]; prev = g.eq_close.shift(1).fillna(m["deposit"])
        a.append(g.eq_close / prev - 1); b.append(g.eq_worst / prev - 1); ntr += len(m["pos"]); nb += len(m["baskets"])
        for bk in m["baskets"]:
            if bk["net_pct"] <= -8: days.add(pd.Timestamp(bk["t1"], unit="s").normalize())
    rc[v] = pd.concat(a); rw[v] = pd.concat(b); cd[v] = days; info[v] = dict(entries=ntr, baskets=nb, crash_days=len(days))
idx = pd.date_range("2017-01-01", "2025-12-31", freq="D")
R = pd.DataFrame({v: rc[v].reindex(idx).fillna(0) for v in V}); RW = pd.DataFrame({v: rw[v].reindex(idx).fillna(0) for v in V})
def stats(r, rwst=None):
    e = (1 + r).cumprod(); yrs = len(r) / 365.25; cagr = (e.iloc[-1] ** (1 / yrs) - 1) * 100
    mdd_c = float((1 - e / e.cummax()).max() * 100)
    if rwst is not None:
        pk = e.cummax().shift(1).fillna(1.0); ew = e.shift(1).fillna(1.0) * (1 + rwst); mdd_w = float((1 - ew / np.maximum(pk, e.shift(1).fillna(1.0))).max() * 100)
    else: mdd_w = None
    me = e.resample("ME").last(); mr = me / me.shift(1).fillna(1.0) - 1; k = max(1, math.ceil(0.05 * len(mr)))
    return dict(total=(e.iloc[-1] - 1) * 100, CAGR=cagr, MDD_close=mdd_c, MDD_worst=mdd_w, ES5_m=float(np.sort(mr.values)[:k].mean() * 100), vol_d=float(r.std() * 100))
def overlap(D1, D2, tol=0):
    if not D1 or not D2: return float("nan")
    if tol: inter1 = sum(any(abs((d - e).days) <= tol for e in D2) for d in D1); inter2 = sum(any(abs((d - e).days) <= tol for e in D1) for d in D2)
    else: inter1 = inter2 = len(D1 & D2)
    return 0.5 * (inter1 / len(D1) + inter2 / len(D2)) * 100
out = dict(prereg_sha=sha("/workspace/t297/out/PREREG_t297_3.md"), info=info, years=[min(YEARS), max(YEARS)])
out["feasible"] = sum(1 for v in V if info[v]["entries"] > 0) >= 3
out["standalone"] = {v: stats(R[v], RW[v]) for v in V}
out["annual"] = {v: {str(y): round(((1 + R[v][str(y)]).prod() - 1) * 100, 1) for y in YEARS} for v in V}
pairs = list(itertools.combinations(V, 2))
out["overlap_same_day"] = {f"{a}|{b}": overlap(cd[a], cd[b]) for a, b in pairs}
out["overlap_pm1"] = {f"{a}|{b}": overlap(cd[a], cd[b], 1) for a, b in pairs}
out["daily_corr"] = R.corr().round(3).to_dict()
med = float(np.median(list(out["overlap_same_day"].values())))
port = R.mean(axis=1); portw = RW.mean(axis=1)
sp = stats(port, portw); sb = out["standalone"]["base17"]
scale = port.std() / R["base17"].std(); sbs = stats(R["base17"] * scale, RW["base17"] * scale)
out.update(portfolio_equal=sp, base17_volmatched=dict(scale=float(scale), **sbs), median_pair_overlap=med)
f = []
npos = sum(1 for v in V if out["standalone"][v]["total"] > 0)
if npos < 3: f.append(f"1:only {npos} versions with positive standalone return")
if med > 40: f.append(f"2:median pair overlap {med:.0f}%>40%")
esr = (1 - sp["ES5_m"] / sb["ES5_m"]) * 100 if sb["ES5_m"] < 0 else float("nan")
mddr = (1 - sp["MDD_close"] / sb["MDD_close"]) * 100
if not esr >= 25: f.append(f"3:ES5 reduction {esr:.0f}%<25%")
if not mddr >= 20: f.append(f"4:MDD reduction {mddr:.0f}%<20%")
if sb["CAGR"] > 0 and sp["CAGR"] < sb["CAGR"] * 2 / 3: f.append("5:CAGR drop >1/3")
if not (sp["ES5_m"] > sbs["ES5_m"] and sp["MDD_close"] < sbs["MDD_close"]): f.append("6:not better than vol-matched base17 in both ES5 and MDD (exposure only)")
out.update(ES5_reduction=esr, MDD_reduction=mddr, fails=f, verdict="FAIL" if f else "PASS")
# fleet diagnostic
Bf = pd.read_csv("/workspace/t297/out/t297_2_baskets_mtm.csv"); Bf = Bf[Bf.pnl_pct <= -8]
Bf["day"] = pd.to_datetime(Bf.t1, utc=True).dt.tz_convert(None).dt.normalize()
FD = {str(a): set(g.day) for a, g in Bf.groupby("acc")}
out["fleet_diag"] = dict(crash_days={a: len(s) for a, s in FD.items()}, overlap_same_day={f"{a}|{b}": overlap(FD[a], FD[b]) for a, b in itertools.combinations(sorted(FD), 2)})
out["fleet_diag"]["median_pair_overlap"] = float(np.median(list(out["fleet_diag"]["overlap_same_day"].values())))
json.dump(out, open("/workspace/t297/out/t297_3_results.json", "w"), ensure_ascii=False, indent=1, default=float)
print(json.dumps(out, ensure_ascii=False, indent=1, default=float))
