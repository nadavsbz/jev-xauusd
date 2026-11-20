#!/usr/bin/env python3
"""t294 idea 3 (Grok): base lot x0.5 when ATR(D1,20)/median(ATR20, 250d) > 1.5 (PREREG_t294_idea3.md sha256 ab8b6280...b752).
Static, read-only. Usage: python t294_idea3_volregime.py H1.csv D1.csv REPORTDIR FLEET_BASKETS_CSV OUT.json"""
import sys, os, json, csv, statistics, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t294_common import *
PREREG = "ab8b6280cc36b20dac0a753f77719f4935d701927a0f943efaf7820e6b6db752"
def ratio_fn(days, atr):
    cache = {}
    def R(d):
        if d in cache: return cache[d]
        i = bisect.bisect_left(days, d) - 1; v = None
        if i >= 0 and atr[i] is not None:
            w = [a for a in atr[max(0, i - 249):i + 1] if a is not None]
            if len(w) == 250: v = atr[i] / statistics.median(w)
        cache[d] = v; return v
    return R
def maxdd(Bk, mult, dep):
    eq = dep; pk = dep; dd = 0.0
    for b, mm in sorted(zip(Bk, mult), key=lambda x: x[0]["t1"]):
        eq += mm * b["net"]; pk = max(pk, eq); dd = max(dd, (pk - eq) / pk * 100)
    return dd
def main():
    h1p, d1p, rd, fp, outp = sys.argv[1:6]
    h1 = load_h1(h1p); days, atr, lastd = load_d1(d1p, h1); Rf = ratio_fn(days, atr)
    allB, deps, shas = load_base17(rd, range(2016, 2026))
    R = dict(prereg_sha256=PREREG, inputs={os.path.basename(p): sha(p) for p in (h1p, d1p, fp)}, base17_report_sha256=shas, years={}, grid={})
    def run(th, m, keep=False):
        res = {}; rows = []
        for y in allB:
            Bk = allB[y]; dep = deps[y]; mult = []; nores = 0
            for b in Bk:
                r = Rf(b["t0"] // DAY)
                if r is None: nores += 1
                mult.append(m if (r is not None and r > th) else 1.0)
                if keep: rows.append(dict(year=y, side=b["side"], t0=b["t0"], t1=b["t1"], levels=b["levels"], net=round(b["net"], 2), net_pct=round(b["net_pct"], 3), R=round(r, 4) if r else None, mult=mult[-1]))
            yd = [d for d in days if datetime.datetime.utcfromtimestamp(d * DAY).year == y]
            trig = sum(1 for d in yd if (Rf(d) or 0) > th)
            dlt = sum((mm - 1) * b["net"] for b, mm in zip(Bk, mult)); dc = sum((mm - 1) * b["net"] for b, mm in zip(Bk, mult) if b["net_pct"] <= -8)
            inw = [b for b, mm in zip(Bk, mult) if mm != 1]; outw = [b for b, mm in zip(Bk, mult) if mm == 1]
            base = sum(b["net"] for b in Bk)
            res[y] = dict(trigger_days=trig, n_scaled=len(inw), n_baskets=len(Bk), no_ratio=nores, base_net=round(base, 2), rule_net=round(base + dlt, 2),
                          base_pct=round(base / dep * 100, 2), rule_pct=round((base + dlt) / dep * 100, 2),
                          delta=round(dlt, 2), delta_pct=round(dlt / dep * 100, 2), delta_cut=round(dc, 2), delta_noncut=round(dlt - dc, 2),
                          dd_base=round(maxdd(Bk, [1] * len(Bk), dep), 2), dd_rule=round(maxdd(Bk, mult, dep), 2),
                          cutrate_in=f'{sum(b["net_pct"] <= -8 for b in inw)}/{len(inw)}', cutrate_out=f'{sum(b["net_pct"] <= -8 for b in outw)}/{len(outw)}',
                          mean_pct_in=round(statistics.mean(b["net_pct"] for b in inw), 3) if inw else None,
                          mean_pct_out=round(statistics.mean(b["net_pct"] for b in outw), 3) if outw else None)
        return res, rows
    def verdict(res, ys, mintrig=None):
        ty = [y for y in ys if res[y]["n_scaled"] > 0]
        c1 = sum(res[y]["delta"] for y in ys) > 0
        c2 = (sum(res[y]["delta"] >= 0 for y in ty) >= 0.6 * len(ty)) if ty else False
        c3 = all(res[y]["dd_rule"] <= res[y]["dd_base"] + 1 for y in ys) and sum(res[y]["dd_rule"] for y in ys) < sum(res[y]["dd_base"] for y in ys)
        nt = sum(res[y]["trigger_days"] for y in ys); c4 = nt >= mintrig if mintrig else True
        return dict(c1_sum_delta_pos=c1, c2_60pct_years=c2, c3_dd=c3, c4_trigger_days=c4, trigger_days=nt, scaled_baskets=sum(res[y]["n_scaled"] for y in ys),
                    sum_delta=round(sum(res[y]["delta"] for y in ys), 2), sum_delta_cut=round(sum(res[y]["delta_cut"] for y in ys), 2),
                    sum_delta_noncut=round(sum(res[y]["delta_noncut"] for y in ys), 2),
                    cuts_in=sum(int(res[y]["cutrate_in"].split("/")[0]) for y in ys), cuts_total=sum(int(res[y]["cutrate_in"].split("/")[0]) + int(res[y]["cutrate_out"].split("/")[0]) for y in ys),
                    PASS=c1 and c2 and c3 and c4)
    DEV = list(range(2016, 2022)); HO = list(range(2022, 2026))
    res, rows = run(1.5, 0.5, True)
    R["main"] = dict(per_year=res, DEV=verdict(res, DEV, 20), HOLDOUT_A=verdict(res, HO))
    for th in (1.25, 1.5, 1.75, 2.0):
        for m in (0.0, 0.25, 0.5):
            r2, _ = run(th, m); R["grid"][f"th{th}_m{m}"] = dict(DEV=verdict(r2, DEV)["sum_delta"], HO=verdict(r2, HO)["sum_delta"],
                                                                 DEV_cut=verdict(r2, DEV)["sum_delta_cut"], HO_cut=verdict(r2, HO)["sum_delta_cut"])
    # fleet
    F = load_fleet(fp); n = 0; d = 0.0; dc = 0.0; ncut_in = 0; nores = 0
    for x in F:
        r = Rf(x["t0s"] // DAY)
        if r is None: nores += 1; continue
        if r > 1.5:
            n += 1; d += -0.5 * x["pnl"]
            if x["cut"]: dc += -0.5 * x["pnl"]; ncut_in += 1
    fl_days = sorted({x["t0s"] // DAY for x in F}); trig_days = sum(1 for dd in fl_days if (Rf(dd) or 0) > 1.5)
    Rvals = [Rf(dd) for dd in fl_days if Rf(dd) is not None]
    R["fleet"] = dict(n_baskets=len(F), excluded_no_ratio=nores, trigger_days=trig_days, R_max=round(max(Rvals), 3) if Rvals else None,
                      R_median=round(statistics.median(Rvals), 3) if Rvals else None, n_scaled=n, cuts_in_regime=ncut_in, n_cuts=sum(x["cut"] for x in F),
                      delta=round(d, 2), delta_cut=round(dc, 2), delta_noncut=round(d - dc, 2))
    R["fleet"]["verdict"] = "undecidable" if n == 0 else ("PASS" if d > 0 and dc > 0 else "FAIL")
    # gate for base vs rule (per year)
    R["gate_by_year"] = {y: dict(base_monthly=round(res[y]["base_pct"] / 12, 2), rule_monthly=round(res[y]["rule_pct"] / 12, 2), dd_base=res[y]["dd_base"], dd_rule=res[y]["dd_rule"]) for y in res}
    R["VERDICT"] = dict(DEV=R["main"]["DEV"]["PASS"], HOLDOUT_A=R["main"]["HOLDOUT_A"]["PASS"], HOLDOUT_B=R["fleet"]["verdict"],
                        FINDING=R["main"]["DEV"]["PASS"] and R["main"]["HOLDOUT_A"]["PASS"] and R["fleet"]["verdict"] != "FAIL")
    json.dump(R, open(outp, "w"), indent=1)
    with open(outp.replace(".json", "_rows.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(json.dumps({k: v for k, v in R.items() if k not in ("inputs", "base17_report_sha256")}, indent=1))
main()
