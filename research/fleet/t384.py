"""t384 (docs/prereg/research_t384.md v2.2): tester fidelity for BD Lars, per segment. This script computes M1 (cut agreement)
and M3 (realized to each side's own cut) and exports tester deals normalized to the deposit for Grok's M2 (equity on one
M1 price source, as t385). Live side: data/derived/lars/segments_t384.csv. Usage: py -3.12 research/fleet/t384.py"""
import sys, re, json, os
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals
from scipy.stats import spearmanr

S = pd.read_csv("data/derived/lars/segments_t384.csv", parse_dates=["start", "start_live", "cut_live", "end_live"])
OUT = "docs/agents/grok_data/t384_tester"


def quality(rep):
    t = open(f"C:/MT5_JEV_TEST/{rep}.htm", "rb").read().decode("utf-16")
    t = re.sub(r"[|\s]*\|[|\s]*", "|", re.sub("<[^>]+>", "|", t)); g = lambda k: t[t.find(k):].split("|")[1]
    return g("איכות היסטוריה:"), g("טיקטוקים:"), g("נרות:")


def seg(rep, r, floor):
    d = deals(f"C:/MT5_JEV_TEST/{rep}.htm"); d = d[d.symbol == "XAUUSD"].copy()
    d["ts"] = pd.to_datetime(d.t, unit="s"); dep = r.e_start_live
    pre = d[(d.dir == "in") & (d.ts < r.start_live)]                   # baskets opened before the live start: known mismatch (v2.1)
    w = d[(d.ts >= r.start_live) & (d.ts < r.end_live)].copy()
    w["cash"] = w.profit + w.swap + w.commission
    cut = None
    if floor is not None:
        hit = w[(w.dir == "out") & (w.balance <= floor * 1.01)]
        cut = hit.ts.iloc[0] if len(hit) else None
    own = w[w.ts <= cut + pd.Timedelta(minutes=5)] if cut is not None else w
    common_end = min([x for x in (cut, r.cut_live, r.end_live) if x is not None and pd.notna(x)])
    common = w[w.ts <= common_end + pd.Timedelta(minutes=5)]
    return d, dict(cut_T=cut, pnl_own_pct=100 * own.cash.sum() / dep, pnl_common_pct=100 * common.cash.sum() / dep,
                   n_pre_start=int(len(pre)), q=quality(rep))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True); rows = []
    for i, r in enumerate(S.itertuples(), 1):
        tag = f"{r.acct}_{i:02d}"
        if not os.path.exists(f"C:/MT5_JEV_TEST/t384_c_{tag}.htm"): continue       # excluded segment (floor >= start equity)
        floor = r.e_start_live * (1 - (100 * (1 - r.floor / r.e_start_live)) / 100) if pd.notna(r.floor) else None
        row = dict(seg_id=f"A{r.acct}_{r.start:%Y%m%d}", tag=tag, cut_L=r.cut_live if pd.notna(r.cut_live) else None,
                   live_pct=100 * r.live_pnl * 100 / r.e_start_live, lot_matched=r.lot_matched, open_start=r.open_at_start, open_end=r.open_at_end)
        for kind in ("c", "b", "s"):
            d, x = seg(f"t384_{kind}_{tag}", r, floor if kind != "b" else None)
            row.update({f"{kind}_{k}": v for k, v in x.items()})
            if kind in ("c", "b"):
                e = d[["ts", "dir", "type", "price", "volume", "profit", "swap", "commission"]].copy()
                e["vol_per_100k"] = e.volume / r.e_start_live * 1e5
                for c in ("profit", "swap", "commission"): e[c + "_pct"] = 100 * e[c] / r.e_start_live
                e.drop(columns=["volume", "profit", "swap", "commission"]).to_csv(f"{OUT}/{row['seg_id']}_{kind}.csv.gz", index=False)
        rows.append(row)
    T = pd.DataFrame(rows)
    T["cutL"] = T.cut_L.notna(); T["cutT"] = T.c_cut_T.notna()
    main = T[~T.open_start & ~T.open_end]
    def m1(t):
        a = (t.cutL == t.cutT).mean(); pe = t.cutL.mean() * t.cutT.mean() + (1 - t.cutL.mean()) * (1 - t.cutT.mean())
        k = (a - pe) / (1 - pe) if pe < 1 else float("nan")
        timing = [abs((x.c_cut_T - x.cut_L).total_seconds()) / 3600 for x in t.itertuples() if x.cutL and x.cutT]
        return dict(n=len(t), cuts_live=int(t.cutL.sum()), cuts_tester=int(t.cutT.sum()), agree=round(a, 3), kappa=round(k, 3),
                    only_tester=int((t.cutT & ~t.cutL).sum()), only_live=int((t.cutL & ~t.cutT).sum()), both_cut_hours_apart=[round(h, 1) for h in timing])
    def m3(t, col):
        dlt = t[col] - t.live_pct
        return dict(spearman=round(float(spearmanr(t[col], t.live_pct).correlation), 3), sum_dev_ratio=round(float(abs(dlt.sum()) / t.live_pct.abs().sum()), 3),
                    median_abs_dev_pp=round(float(dlt.abs().median()), 2), sign_agree=round(float((np.sign(t[col]) == np.sign(t.live_pct)).mean()), 3))
    out = dict(M1_main=m1(main), M1_all=m1(T), M3_clone_own=m3(main, "c_pnl_own_pct"), M3_clone_common=m3(main, "c_pnl_common_pct"),
               M3_bd_nofloor_common=m3(main, "b_pnl_common_pct"), M3_sp50_common=m3(main, "s_pnl_common_pct"),
               quality=sorted(set(x for q in T.c_q for x in [q[0]])), pre_start_mismatch=T[T.c_n_pre_start > 0].seg_id.tolist())
    T.drop(columns=["c_q", "b_q", "s_q"]).to_csv(f"{OUT}/t384_segments_tester.csv", index=False)
    print(json.dumps(out, indent=1, default=str, ensure_ascii=False))
    print(T[["seg_id", "live_pct", "c_pnl_common_pct", "b_pnl_common_pct", "cut_L", "c_cut_T"]].round(2).to_string(index=False))
