#!/usr/bin/env python3
"""t298b Stage B (Grok): t297_1 frozen rules on 1.2020-10.2026. Reuses sim/mdd/metrics/series from /workspace/t297/t297_1_sleeve.py unchanged.
BD: base17 (MTM daily) up to 31.10.2025; from 1.11.2025 Account-1 monthly returns (profit/opening balance) booked on month's last calendar day.
11.2025 has no Account-1 row -> BD return 0 (primary). Sensitivity S11 only: 11.2025 excluded from window is impossible (calendar), so alt = same as primary; no invented value."""
import sys, json, math; sys.path.insert(0, "/workspace/t297")
import numpy as np, pandas as pd
import t297_1_sleeve as T
from t297_1_sleeve import sim, mdd, metrics, c1, i2, bdc, bdw, SEED
from t297_common import sha
W = (0.05, 0.10, 0.15, 0.20); MODES = ("A", "B", "H")
live = json.load(open("/workspace/t298b/in/cmp_live_months.json"))
live_r = {m: p / b for m, b, lot, p in live}
def frame(a, b):
    idx = pd.date_range(a, b, freq="D")
    rc = (0.5 * c1.reindex(idx).fillna(0) + 0.5 * i2.reindex(idx).fillna(0))
    rb = bdc.loc[:"2025-10-31"].reindex(idx).fillna(0); rbw = bdw.loc[:"2025-10-31"].reindex(idx).fillna(0)
    for m, r in live_r.items():
        d = pd.Period(m).end_time.normalize()
        if d in idx: rb[d] = r; rbw[d] = r   # no intra-month info: worst = close on the booking day
    return idx, rc, rb, rbw
def run(idx, rc, rb, rbw):
    me = list(pd.Series(idx).dt.is_month_end); res = {"0%": metrics(sim(list(rc), list(rb), list(rbw), "A", 0.0, me), idx)}
    for mode in MODES:
        for w in W: res[f"{mode}{int(w*100)}"] = metrics(sim(list(rc), list(rb), list(rbw), mode, w, me), idx)
    return res
def bootstrap(idx, rc, rb, rbw, n=2000):
    rng = np.random.default_rng(SEED); s = pd.Series(range(len(idx)), idx); months = [g.values for _, g in s.groupby([idx.year, idx.month])]
    rc, rb, rbw = np.asarray(rc), np.asarray(rb), np.asarray(rbw); nm = len(months); out = {}
    cfg = [("0%", "A", 0.0)] + [(f"{m}{int(w*100)}", m, w) for m in MODES for w in W]
    paths = []
    for _ in range(n):
        pick = rng.integers(0, nm, nm); ii = np.concatenate([months[j] for j in pick])
        me = np.zeros(len(ii), bool); pos = np.cumsum([len(months[j]) for j in pick]) - 1; me[pos] = True
        paths.append((ii, me, pos))
    for name, m, w in cfg:
        over = 0; negy = 0; ny = 0; mdds = []
        for ii, me, pos in paths:
            r = sim(list(rc[ii]), list(rb[ii]), list(rbw[ii]), m, w, list(me)); a, _ = mdd(r["P"], r["Pw"]); mdds.append(a); over += a > 0.25
            Pm = np.concatenate([[1.0], r["P"][pos]])
            for k in range(0, nm - 11, 12): ny += 1; negy += Pm[k + 12] < Pm[k]
        out[name] = dict(P_MDD_gt25=over / n * 100, P_neg_year=negy / ny * 100, MDD_p50=float(np.median(mdds)) * 100, MDD_p95=float(np.percentile(mdds, 95)) * 100)
    return out
def verdict(res, bs):
    v = {}; s = {}; base = res["0%"]
    for k, r in res.items():
        f = []
        if bs[k]["P_MDD_gt25"] > 5: f.append("1:P(MDD>25%)>5%")
        dC = r["CAGR"] - base["CAGR"]; worse = base["ES5_m"] - r["ES5_m"]
        if (dC <= 0 and worse > 0) or worse > dC: f.append(f"2:dES5 worse {worse:.2f} > dCAGR {dC:.2f}")
        if dC < 1 and (r["MDD_close"] - base["MDD_close"]) > 5: f.append("3:dCAGR<1 & dMDD>5")
        if r["MDD_worst"] > 25: f.append("budget:MDD_worst>25%")
        v[k] = f
        s[k] = (r["MDD_worst"] <= 25 and bs[k]["P_MDD_gt25"] <= 5 and dC > 0) if k != "0%" else None   # Claude's summary criterion
    for w in W:
        if not v[f"A{int(w*100)}"] and v[f"H{int(w*100)}"]: v[f"A{int(w*100)}"].append("4:depends on refill (H fails)")
    pick = {m: (f"{max(ok)}%" if (ok := [int(w*100) for w in W if not v[f"{m}{int(w*100)}"]]) else "0%") for m in ("A", "B")}
    pick_summary = {m: (f"{max(ok)}%" if (ok := [int(w*100) for w in W if s[f"{m}{int(w*100)}"]]) else "0%") for m in ("A", "B")}
    return v, s, pick, pick_summary
def table(res, bs, v, s):
    base = res["0%"]
    return [dict(cfg=k, CAGR=r["CAGR"], dCAGR=r["CAGR"] - base["CAGR"], MDD_close=r["MDD_close"], MDD_worst=r["MDD_worst"], ES5_m=r["ES5_m"], BD_share=r["BD_share"],
                 refills=r["refills"], withdrawn=r["withdrawn"], stress=r["stress_sleeve_wipe_DD"], **bs[k], fails="; ".join(v[k]) or "PASS", summary_pass=s[k]) for k, r in res.items()]
def evaluate(a, b, n=2000):
    idx, rc, rb, rbw = frame(a, b); res = run(idx, rc, rb, rbw); bs = bootstrap(idx, rc, rb, rbw, n); v, s, pick, ps = verdict(res, bs)
    return dict(window=[a, b], main=res, bootstrap=bs, fails=v, summary_pass=s, pick=pick, pick_summary=ps, table=table(res, bs, v, s))
def sensitivity():
    """diagnostic: core = cash, w = 10%. Good year G = Account-1 12.2025-10.2026 (+11.2025 = 0). Bad years = base17 calendar 2016(Oct-Dec),2017,2018,2019."""
    G = [0.0] + [live_r[m] for m, *_ in live]  # monthly
    bad = {}
    for y in (2016, 2017, 2018, 2019):
        x = bdc.loc[f"{y}-01-01":f"{y}-12-31"]; bad[y] = list((1 + x).resample("ME").prod() - 1)
    out = dict(G_year=float(np.prod([1 + g for g in G]) - 1), bad_years={y: float(np.prod([1 + r for r in v]) - 1) for y, v in bad.items()})
    lg = math.log(1 + out["G_year"]); lb = np.mean([math.log(1 + r) for r in out["bad_years"].values()])
    out["H_breakeven_bad_per_good"] = lg / -lb if lb < 0 else float("inf")
    badm = sum(bad.values(), [])  # 2016-2019 months in order, cycled
    for mode in ("H", "A", "B"):
        for order in ("bad_first", "good_first"):
            best = 0
            for nb in range(0, 41):
                bm = []
                while len(bm) < 12 * nb: bm += badm
                bm = bm[:12 * nb] if nb else []
                seq = (bm + G) if order == "bad_first" else (G + bm)
                rc = [0.0] * len(seq); me = [True] * len(seq)
                r = sim(rc, seq, seq, mode, 0.10, me)
                if r["P"][-1] >= 1.0: best = nb
                else: break
            out[f"{mode}_{order}_max_bad_years_covered_by_1_good"] = best
    # how many good years needed to cover the 4 actual bad years 2016-2019 (bad first), mode H/A/B
    for mode in ("H", "A", "B"):
        need = None
        for ng in range(0, 21):
            seq = badm + G * ng; r = sim([0.0] * len(seq), seq, seq, mode, 0.10, [True] * len(seq))
            if r["P"][-1] >= 1.0: need = ng; break
        out[f"{mode}_good_years_needed_after_2016_2019"] = need
    return out
if __name__ == "__main__":
    out = {"prereg_addendum_sha": sha("/workspace/t298b/out/PREREG_t298b_addendum.md"), "script_sha": sha(__file__), "live_input_sha": sha("/workspace/t298b/in/cmp_live_months.json"),
           "live_monthly_returns": live_r, "label": "limited (account months)"}
    out["full"] = evaluate("2020-01-01", "2026-10-31")
    out["live_only"] = evaluate("2025-11-01", "2026-10-31")
    out["ex_live"] = evaluate("2020-01-01", "2025-10-31")
    full_pass = {m: [int(w*100) for w in W if not out["full"]["fails"][f"{m}{int(w*100)}"]] for m in ("A", "B")}
    out["one_year_flag"] = {m: {w: bool(out["ex_live"]["fails"][f"{m}{w}"]) for w in ws} for m, ws in full_pass.items()}
    out["sensitivity"] = sensitivity()
    json.dump(out, open("/workspace/t298b/out/t298b_stageB_results.json", "w"), ensure_ascii=False, indent=1, default=float)
    for k in ("full", "live_only", "ex_live"):
        pd.DataFrame(out[k]["table"]).to_csv(f"/workspace/t298b/out/t298b_stageB_{k}.csv", index=False)
        print("==", k, out[k]["pick"], out[k]["pick_summary"])
        print(pd.DataFrame(out[k]["table"])[["cfg", "CAGR", "dCAGR", "MDD_close", "MDD_worst", "ES5_m", "BD_share", "P_MDD_gt25", "MDD_p95", "fails", "summary_pass"]].round(2).to_string())
    print("one_year_flag", out["one_year_flag"]); print(json.dumps(out["sensitivity"], indent=1, default=float))
