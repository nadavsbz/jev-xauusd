#!/usr/bin/env python3
"""t297_2 (Grok): fleet circuit breaker within the same move. Rules frozen in PREREG_t297_2.md (sha fbc24285...)."""
import sys, json, math; sys.path.insert(0, "/workspace/algotrade/jev-xauusd/research/grok_crash"); sys.path.insert(0, "/workspace/t297")
import numpy as np, pandas as pd
import run_analysis as RA
from t297_common import sha
W0 = pd.Timestamp("2026-04-15", tz="UTC")
m1 = pd.read_pickle(RA.OUT / "m1_mid_2026.pkl"); M_END = m1.index.max()
MT = RA.index_utc_ns(m1.index); ML = m1["low"].values; MH = m1["high"].values; MC = m1["close"].values
rows = []
for acc, meta in RA.ACCOUNTS.items():
    d = RA.load_deals(acc); K = RA.estimate_K(d); p, ex = RA.gold_positions(d); p = RA.cluster_positions(p)
    cs = d.sort_values("t"); ct = np.array([RA.utc_ns(x) for x in cs["t"]]); cb = cs["cash"].cumsum().to_numpy()
    for cid, g in p.groupby("cid"):
        t0 = g.t0.min()
        if pd.isna(t0) or t0 < W0: continue
        k = int(np.searchsorted(ct, RA.utc_ns(t0), "left") - 1); b0 = float(cb[k]) if k >= 0 else 0.0
        still = bool(g.still_open.any()); t1 = g.t1.max()
        r = dict(acc=acc, cid=int(cid), t0=t0, t1=t1, b0=b0, pnl=float(g.pnl.sum()), n=len(g), still=still,
                 side=1 if (g.volume * g.sgn).sum() >= 0 else -1, first_px=float(g.sort_values("t0").open_px.iloc[0]), K=K, tz=meta["tz"],
                 guard=bool(g.guard.fillna(False).any()))
        r["pnl_pct"] = r["pnl"] / b0 * 100 if b0 > 0 else np.nan
        measurable = (not still) and pd.notna(t1) and t1 <= M_END and b0 > 0
        r["measurable"] = measurable; r["t_hit"] = pd.NaT; r["mae_pct"] = np.nan
        if measurable:
            a = int(np.searchsorted(MT, RA.utc_ns(t0), "right") - 1); b = int(np.searchsorted(MT, RA.utc_ns(t1), "right"))
            a = max(a, 0); T = MT[a:b]
            if len(T) == 0: r["measurable"] = False
            else:
                mtm = np.zeros(len(T))
                for q in g.itertuples():
                    q0 = RA.utc_ns(q.t0); q1 = RA.utc_ns(q.t1)
                    i = np.searchsorted(T, q0, "right") - 1; j = np.searchsorted(T, q1, "right") - 1  # bar containing entry / exit
                    i = max(i, 0)
                    adv = ML[a:b] if q.sgn > 0 else MH[a:b]
                    if j > i: mtm[i:j] += q.sgn * q.volume * (adv[i:j] - q.open_px) * K + q.entry_cash
                    mtm[max(j, i):] += q.pnl
                mtm = np.minimum(mtm, np.inf); pct = mtm / b0 * 100
                r["mae_pct"] = float(min(pct.min(), r["pnl_pct"]))
                hit = np.nonzero(pct <= -8)[0]
                if len(hit): r["t_hit"] = pd.Timestamp(int(T[hit[0]]), tz="UTC")
                elif r["pnl_pct"] <= -8: r["t_hit"] = t1
        rows.append(r)
B = pd.DataFrame(rows).sort_values("t0").reset_index(drop=True)
B["crash"] = B.mae_pct <= -8
def alarms(literal=False):
    C = B[B.crash & B.t_hit.notna()].sort_values("t_hit"); out = []; active_end = None
    for r in C.itertuples():
        Ta = r.t_hit
        if active_end is not None and Ta <= active_end: continue
        tz = r.tz; srv = Ta.tz_convert(tz); day_end = (srv.normalize() + pd.Timedelta(days=1)).tz_convert("UTC")
        ia = int(np.searchsorted(MT, RA.utc_ns(Ta), "left")); i0 = int(np.searchsorted(MT, RA.utc_ns(r.t0), "right") - 1)
        down = r.side > 0
        Pstart = MC[ia] if literal else r.first_px
        ext = (ML[max(i0, 0):ia + 1].min() if down else MH[max(i0, 0):ia + 1].max()) if not literal else MC[ia]
        last_new = MT[ia]; end = None; why = None
        for k in range(ia + 1, len(MT)):
            t = MT[k]
            if t >= RA.utc_ns(day_end): end, why = day_end, "day_end"; break
            if down:
                if ML[k] < ext: ext = ML[k]; last_new = t
                rng = Pstart - ext; ret = MC[k] >= ext + 0.5 * rng and rng > 0
            else:
                if MH[k] > ext: ext = MH[k]; last_new = t
                rng = ext - Pstart; ret = MC[k] <= ext - 0.5 * rng and rng > 0
            if t - last_new >= 4 * 3600 * 10**9: end, why = pd.Timestamp(int(last_new + 4 * 3600 * 10**9), tz="UTC"), "4h_no_new_extreme"; break
            if ret: end, why = pd.Timestamp(int(t), tz="UTC"), "retrace50"; break
        if end is None: end, why = M_END, "data_end"
        out.append(dict(Ta=Ta, end=end, why=why, acc=r.acc, cid=r.cid, side=int(r.side), hours=(end - Ta).total_seconds() / 3600))
        active_end = end
    return pd.DataFrame(out)
def evaluate(A):
    X = B[B.measurable].copy(); X["cancel"] = False; X["alarm"] = -1
    for i, a in A.iterrows():
        m = (X.acc != a.acc) & (X.t0 > a.Ta) & (X.t0 <= a.end)
        X.loc[m, "cancel"] = True; X.loc[m, "alarm"] = i
    cz = X[X.cancel]; saved = -cz.pnl_pct[cz.pnl_pct < 0].sum(); lost = cz.pnl_pct[cz.pnl_pct > 0].sum()
    fleet_profit = X.pnl_pct.sum()
    # secondary crashes
    sec = []; seen = set()  # bookkeeping fix 14:45: each crash basket counted once, under the earliest alarm whose 24h covers it
    for i, a in A.iterrows():
        s = X[(X.acc != a.acc) & X.crash & X.t_hit.notna() & (X.t_hit >= a.Ta) & (X.t_hit <= a.Ta + pd.Timedelta(hours=24))]
        for r in s.itertuples():
            if (r.acc, r.cid) in seen: continue
            seen.add((r.acc, r.cid))
            sec.append(dict(alarm=i, acc=r.acc, cid=r.cid, t0=str(r.t0), t_hit=str(r.t_hit), after=bool(r.t0 > a.Ta), prevented=bool(r.cancel), pnl_pct=r.pnl_pct, mae_pct=r.mae_pct))
    S = pd.DataFrame(sec)
    def es5(df):
        df = df.copy(); df["day"] = df.t1.dt.tz_convert("UTC").dt.normalize()
        g = df.groupby(["day", "acc"]).pnl_pct.sum().unstack().reindex(columns=list(RA.ACCOUNTS)).fillna(0)
        days = pd.date_range(X.t0.min().normalize(), M_END.normalize(), freq="D", tz="UTC"); g = g.reindex(days).fillna(0); f = g.mean(axis=1)
        k = max(1, math.ceil(0.05 * len(f))); return float(np.sort(f.values)[:k].mean())
    es_b = es5(X); es_a = es5(X[~X.cancel])
    per = cz.groupby("alarm").pnl_pct.sum()  # net effect of cancelling = -sum pnl (positive = good)
    net = saved - lost; best = (-per).max() if len(per) else 0.0
    n_sec = len(S); n_after = int(S.after.sum()) if n_sec else 0; n_prev = int(S.prevented.sum()) if n_sec else 0
    res = dict(n_alarms=len(A), n_cancelled=int(X.cancel.sum()), saved_pct=saved, lost_pct=lost, net_pct=net, fleet_profit_pct=fleet_profit,
               insurance_cost_share=(lost / fleet_profit * 100 if fleet_profit > 0 else float("nan")), ES5_before=es_b, ES5_after=es_a,
               ES5_reduction=(1 - es_a / es_b) * 100 if es_b < 0 else float("nan"), n_secondary=n_sec, n_secondary_after=n_after,
               share_after=(n_after / n_sec * 100 if n_sec else float("nan")), n_secondary_prevented=n_prev, net_without_best_alarm=net - best)
    f = []
    if not n_sec or res["share_after"] < 25: f.append("1:<25% of secondary crashes started after alarm")
    if saved < lost: f.append("2:saved<lost")
    if not (res["insurance_cost_share"] <= 20): f.append("3:insurance cost>20% of fleet profit")
    if not (res["ES5_reduction"] >= 20): f.append("4:ES5 reduction<20%")
    if net > 0 and net - best <= 0: f.append("5:depends on a single alarm/day")
    res["fails"] = f; res["verdict"] = "FAIL" if f else "PASS"
    return res, S, X
if __name__ == "__main__":
    C = B[B.crash]; meas_share = (B[B.crash].measurable.mean() * 100) if len(C) else float("nan")
    allcrash_realized = B[(B.pnl_pct <= -8)]
    out = dict(prereg_sha=sha("/workspace/t297/out/PREREG_t297_2.md"), n_baskets=len(B), n_measurable=int(B.measurable.sum()), m1_end=str(M_END),
               n_crash_mtm=int(C.shape[0]), n_crash_measurable=int(C.measurable.sum()), crash_measurable_share=meas_share,
               n_realized_le8=int(len(allcrash_realized)), n_realized_le8_unmeasurable=int((~allcrash_realized.measurable).sum()),
               n_guard_cut=int(B.guard.sum()))
    blocked = (C.measurable.sum() + int((~allcrash_realized.measurable).sum())) and (int(C.measurable.sum()) / max(1, int(C.measurable.sum()) + int((~allcrash_realized.measurable).sum())) * 100 < 80)
    out["blocked"] = bool(blocked)
    A = alarms(); res, S, X = evaluate(A); out["primary"] = res
    A2 = alarms(literal=True); res2, S2, _ = evaluate(A2); out["sensitivity_literal_retrace"] = res2
    out["alarms"] = A.assign(Ta=A.Ta.astype(str), end=A.end.astype(str)).to_dict("records")
    json.dump(out, open("/workspace/t297/out/t297_2_results.json", "w"), ensure_ascii=False, indent=1, default=str)
    S.to_csv("/workspace/t297/out/t297_2_secondary.csv", index=False)
    B.assign(t0=B.t0.astype(str), t1=B.t1.astype(str), t_hit=B.t_hit.astype(str)).drop(columns=["tz"]).to_csv("/workspace/t297/out/t297_2_baskets_mtm.csv", index=False)
    print(json.dumps({k: v for k, v in out.items() if k not in ("alarms",)}, ensure_ascii=False, indent=1, default=str))
    print(A.why.value_counts().to_dict(), 'median h', A.hours.median())
