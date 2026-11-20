#!/usr/bin/env python3
"""t297_1 (Grok): BD sleeve in the C1+I2 x1.5 portfolio. Rules frozen in PREREG_t297_1.md (sha 8f0be93c...)."""
import sys, json, math; sys.path.insert(0, "/workspace/t297")
import numpy as np, pandas as pd
from t297_common import IN, deals, daily_returns, sha
SEED = 20261119
def i2_daily():
    out = []
    for y in range(2018, 2027):
        d, dep = deals(f"{IN}/in2dst_t_{y}.htm"); dep = dep or 120000.0
        if not d: continue
        x = pd.DataFrame(d); x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize()
        pnl = (x.profit + x.swap + x.com).groupby(x.day).sum()
        eq = dep + pnl.cumsum(); out.append(pnl / eq.shift(1).fillna(dep))
    return pd.concat(out).sort_index()
c1 = pd.read_csv(f"{IN}/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change().dropna()
i2 = i2_daily()
bdc, bdw = daily_returns([f"{IN}/ev23_rf{y}_base17.htm" for y in range(2016, 2026)])
def sim(rc, rb, rbw, mode, w, me):
    """rc,rb,rbw: lists of daily returns; me: list of bool month-end. -> dict of paths"""
    core = 1.0 - w; B = w; H = 1.0; coreStar = core; C_BD = w
    P = []; Pw = []; Bs = []; bdpnl = 0.0; refills = 0; refill_amt = 0.0; withdrawn = 0.0; Bmax = B; stress = 0.0
    for i in range(len(rc)):
        Hprev = H
        bw = B * (1 + rbw[i]); d = B * rb[i]; bdpnl += d
        core *= 1 + rc[i]; B += d
        if B < 0: B = 0.0
        p = core + B; pw_pre = core + min(bw, B)  # intraday worst, before any month-end transfer (bugfix 14:25)
        if me[i] and w > 0:
            if mode == "A":
                if B > 0.15 * p: withdrawn += B - 0.15 * p; core += B - 0.15 * p; B = 0.15 * p
                elif p >= Hprev:
                    if B < w * p:
                        amt = min(w * p - B, max(0.0, core - coreStar))
                        if amt > 0: refills += 1; refill_amt += amt; core -= amt; B += amt
                    coreStar = core
            elif mode == "B":
                if B > C_BD: withdrawn += B - C_BD; core += B - C_BD; B = C_BD
        p = core + B; H = max(H, p)
        P.append(p); Pw.append(pw_pre); Bs.append(B); Bmax = max(Bmax, B)
        stress = max(stress, 1 - core / H)
    return dict(P=np.array(P), Pw=np.array(Pw), B=np.array(Bs), bdpnl=bdpnl, refills=refills, refill_amt=refill_amt, withdrawn=withdrawn, Bmax=Bmax, stress=stress)
def mdd(P, Pw=None):
    pk = np.maximum.accumulate(np.concatenate([[1.0], P]))[:-1]  # peak through previous day close
    pk2 = np.maximum(pk, P)
    a = (1 - P / pk2).max()
    b = (1 - Pw / pk).max() if Pw is not None else None
    return a, b
def metrics(r, idx):
    P = r["P"]; s = pd.Series(P, idx); yrs = (idx[-1] - idx[0]).days / 365.25 + 1 / 365.25
    cagr = P[-1] ** (1 / yrs) - 1
    m_close, m_worst = mdd(P, r["Pw"])
    me = s.resample("ME").last(); mr = me / me.shift(1).fillna(1.0) - 1
    k = max(1, math.ceil(0.05 * len(mr))); es5m = np.sort(mr.values)[:k].mean()
    dr = s / s.shift(1).fillna(1.0) - 1; kd = max(1, math.ceil(0.05 * len(dr))); es5d = np.sort(dr.values)[:kd].mean()
    # recovery: longest underwater stretch
    pk = np.maximum.accumulate(P); under = P < pk - 1e-12; best = cur = 0; open_ = False
    for u in under:
        cur = cur + 1 if u else 0; best = max(best, cur)
    open_ = bool(under[-1]); 
    yr = s.resample("YE").last(); yret = yr / yr.shift(1).fillna(1.0) - 1
    tot = P[-1] - 1
    return dict(CAGR=cagr * 100, MDD_close=m_close * 100, MDD_worst=m_worst * 100, ES5_m=es5m * 100, ES5_d=es5d * 100,
                recovery_days=best, underwater_at_end=open_, BD_share=(r["bdpnl"] / tot * 100 if tot else float("nan")), BD_pnl=r["bdpnl"] * 100,
                final=P[-1], refills=r["refills"], refill_amt=r["refill_amt"] * 100, withdrawn=r["withdrawn"] * 100, Bmax_pct_P0=r["Bmax"] * 100,
                stress_sleeve_wipe_DD=r["stress"] * 100, years={str(k.year): round(v * 100, 1) for k, v in yret.items()})
def frame(a, b):
    idx = pd.date_range(a, b, freq="D")
    rc = (0.5 * c1.reindex(idx).fillna(0) + 0.5 * i2.reindex(idx).fillna(0))
    return idx, rc, bdc.reindex(idx).fillna(0), bdw.reindex(idx).fillna(0)
def run(idx, rc, rb, rbw):
    me = list(pd.Series(idx).dt.is_month_end); res = {}
    res["0%"] = metrics(sim(list(rc), list(rb), list(rbw), "A", 0.0, me), idx)
    for mode in ("A", "B", "H"):
        for w in (0.05, 0.10, 0.15):
            res[f"{mode}{int(w*100)}"] = metrics(sim(list(rc), list(rb), list(rbw), mode, w, me), idx)
    return res
def bootstrap(idx, rc, rb, rbw, n=2000):
    rng = np.random.default_rng(SEED); s = pd.Series(range(len(idx)), idx); months = [g.values for _, g in s.groupby([idx.year, idx.month])]
    rc, rb, rbw = np.asarray(rc), np.asarray(rb), np.asarray(rbw); nm = len(months); out = {}
    cfg = [("0%", "A", 0.0)] + [(f"{m}{int(w*100)}", m, w) for m in ("A", "B", "H") for w in (0.05, 0.10, 0.15)]
    paths = []
    for _ in range(n):
        pick = rng.integers(0, nm, nm); ii = np.concatenate([months[j] for j in pick])
        me = np.zeros(len(ii), bool); pos = np.cumsum([len(months[j]) for j in pick]) - 1; me[pos] = True
        paths.append((ii, me, pos))
    for name, m, w in cfg:
        over = 0; negy = 0; ny = 0; mdds = []
        for ii, me, pos in paths:
            r = sim(list(rc[ii]), list(rb[ii]), list(rbw[ii]), m, w, list(me)); a, _ = mdd(r["P"], r["Pw"]); mdds.append(a)
            over += a > 0.25
            Pm = np.concatenate([[1.0], r["P"][pos]])
            for k in range(0, nm - 11, 12):
                ny += 1; negy += Pm[k + 12] < Pm[k]
        out[name] = dict(P_MDD_gt25=over / n * 100, P_neg_year=negy / ny * 100, MDD_p50=float(np.median(mdds)) * 100, MDD_p95=float(np.percentile(mdds, 95)) * 100)
    return out
def verdict(res, bs):
    v = {}; base = res["0%"]
    def fails(k):
        r = res[k]; f = []
        if bs[k]["P_MDD_gt25"] > 5: f.append("1:P(MDD>25%)>5%")
        dC = r["CAGR"] - base["CAGR"]; worse = base["ES5_m"] - r["ES5_m"]
        if (dC <= 0 and worse > 0) or worse > dC: f.append(f"2:ΔES5 worse {worse:.2f} > ΔCAGR {dC:.2f}")
        if dC < 1 and (r["MDD_close"] - base["MDD_close"]) > 5: f.append("3:ΔCAGR<1 & ΔMDD>5")
        if r["MDD_worst"] > 25: f.append("budget:MDD_worst>25%")
        return f
    for k in res:
        v[k] = fails(k)
    for w in (5, 10, 15):
        if not v[f"A{w}"] and v[f"H{w}"]: v[f"A{w}"].append("4:depends on refill (H fails)")
    pick = {}
    for mode in ("A", "B"):
        ok = [w for w in (5, 10, 15) if not v[f"{mode}{w}"]]
        pick[mode] = f"{max(ok)}%" if ok else "0%"
    return v, pick
if __name__ == "__main__":
    out = {"prereg_sha": sha("/workspace/t297/out/PREREG_t297_1.md"), "inputs": {}}
    idx, rc, rb, rbw = frame("2020-01-01", "2025-12-31")
    out["coverage"] = dict(c1=[str(c1.index.min().date()), str(c1.index.max().date())], i2=[str(i2.index.min().date()), str(i2.index.max().date())], bd=[str(bdc.index.min().date()), str(bdc.index.max().date())],
                           corr_core_bd_daily=float(np.corrcoef(rc, rb)[0, 1]), corr_c1_i2=float(c1.reindex(idx).fillna(0).corr(i2.reindex(idx).fillna(0))))
    res = run(idx, rc, rb, rbw); bs = bootstrap(idx, rc, rb, rbw); v, pick = verdict(res, bs)
    out.update(main=res, bootstrap=bs, fails=v, pick=pick)
    # D2 diagnostic 2016-2019, core = cash
    idx2 = pd.date_range("2016-01-01", "2019-12-31", freq="D"); z = pd.Series(0.0, idx2)
    out["D2_2016_2019_core_cash"] = run(idx2, z, bdc.reindex(idx2).fillna(0), bdw.reindex(idx2).fillna(0))
    # BD alone chained, both windows
    for a, b in (("2016-01-01", "2025-12-31"), ("2020-01-01", "2025-12-31")):
        e = (1 + bdc.loc[a:b]).cumprod(); out[f"BD_alone_{a[:4]}_{b[:4]}"] = dict(total=(e.iloc[-1] - 1) * 100, MDD_close=float((1 - e / e.cummax()).max() * 100))
    json.dump(out, open("/workspace/t297/out/t297_1_results.json", "w"), ensure_ascii=False, indent=1, default=float)
    rows = [dict(cfg=k, **{kk: vv for kk, vv in r.items() if kk != "years"}, **bs[k], fails="; ".join(v[k]) or "PASS") for k, r in res.items()]
    pd.DataFrame(rows).to_csv("/workspace/t297/out/t297_1_table.csv", index=False)
    print(pd.DataFrame(rows)[["cfg", "CAGR", "MDD_close", "MDD_worst", "ES5_m", "recovery_days", "BD_share", "refills", "withdrawn", "P_MDD_gt25", "P_neg_year", "fails"]].round(2).to_string())
    print("pick", pick); print("coverage", out["coverage"]); print({k: out[k] for k in out if k.startswith("BD_alone")})
    for k, r in res.items(): print(k, r["years"])
