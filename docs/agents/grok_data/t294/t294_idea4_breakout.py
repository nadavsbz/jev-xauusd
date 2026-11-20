#!/usr/bin/env python3
"""t294 idea 4 (Grok): standalone daily 24h-range breakout on gold H1 (PREREG_t294_idea4.md sha256 14b6fb96...ef54).
Read-only. Usage: python t294_idea4_breakout.py H1.csv D1.csv REPORTDIR FLEET_BASKETS_CSV OUT.json"""
import sys, os, json, csv, statistics, datetime, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t294_common import *
PREREG = "14b6fb963af7b52271f150b8fc083de07447aedde4ffb0b810949414d558ef54"
CAP = 120000.0; RISK = 0.0025 * CAP; COST = 0.40; STRESS = 0.10
def simulate(h1, days, atr):
    T = []; traded = set(); n = len(h1)
    for i in range(24, n - 1):
        t, o, h, l, c = h1[i]; d = t // DAY; hr = (t % DAY) // 3600
        if d in traded or not (1 <= hr <= 20): continue
        if h1[i+1][0] // DAY != d: continue
        hi = max(b[2] for b in h1[i-24:i]); lo = min(b[3] for b in h1[i-24:i])
        s = 1 if c > hi else (-1 if c < lo else 0)
        if not s: continue
        k, a = atr_before(days, atr, d)
        if a is None: continue
        traded.add(d); te, e = h1[i+1][0], h1[i+1][1]; sl = e - s * a; ex = None; tx = None; why = "time"
        j = i + 1
        while j < n and h1[j][0] // DAY == d and (h1[j][0] % DAY) // 3600 <= 22:
            tj, oj, hj, lj, cj = h1[j]
            if j > i + 1 and (oj - sl) * s <= 0: ex, tx, why = oj, tj, "sl_gap"; break
            if (lj if s > 0 else hj) * s <= sl * s: ex, tx, why = sl, tj + 1800, "sl"; break
            ex, tx = cj, tj + 3600
            if (tj % DAY) // 3600 == 22: break
            j += 1
        g = (ex - e) * s; u = RISK / a
        T.append(dict(day=d, year=datetime.datetime.utcfromtimestamp(d * DAY).year, side=s, t_in=te, t_out=tx, entry=e, exit=ex, atr=a, why=why,
                      gross=g, net=g - COST, net_stress=g - COST - STRESS, net_10bp=g - 0.001 * e,
                      usd=u * (g - COST), usd_stress=u * (g - COST - STRESS), usd_10bp=u * (g - 0.001 * e), R=(g - COST) / a,
                      bp=(g - COST) / e * 1e4, hold_min=(tx - te) / 60))
    return T
def dd_usd(daily):
    eq = 0; pk = 0; dd = 0
    for d in sorted(daily): eq += daily[d]; pk = max(pk, eq); dd = max(dd, pk - eq)
    return dd
def months(y0, m0, y1, m1): return (y1 - y0) * 12 + (m1 - m0) + 1
def stats(T, nmonths, label):
    if not T: return dict(n=0)
    daily = {}
    for x in T: daily[x["day"]] = daily.get(x["day"], 0) + x["usd"]
    net = sum(x["usd"] for x in T); dd = dd_usd(daily) / CAP * 100; mret = net / CAP * 100 / nmonths
    top10 = sum(sorted(daily.values(), reverse=True)[:10]); yrs = {}
    for x in T: yrs[x["year"]] = yrs.get(x["year"], 0) + x["usd"]
    maxshare = max(v for v in yrs.values()) / net if net > 0 else None
    scaled = mret / dd * 25 if dd > 0 else None; risk_req = 0.25 * 25 / dd if dd > 0 else None
    r = dict(period=label, n=len(T), net_usd=round(net, 2), net_pct=round(net / CAP * 100, 2), monthly_pct=round(mret, 3),
             mean_bp=round(statistics.mean(x["bp"] for x in T), 2), mean_R=round(statistics.mean(x["R"] for x in T), 4),
             win=round(sum(x["usd"] > 0 for x in T) / len(T) * 100, 1), median_hold_min=statistics.median(x["hold_min"] for x in T),
             sl_rate=round(sum(x["why"] != "time" for x in T) / len(T) * 100, 1), maxdd_pct_of_120k=round(dd, 2),
             net_stress=round(sum(x["usd_stress"] for x in T), 2), net_10bp=round(sum(x["usd_10bp"] for x in T), 2),
             net_ex_top10days=round(net - top10, 2), year_net={y: round(v, 2) for y, v in sorted(yrs.items())},
             max_year_share=round(maxshare, 3) if maxshare is not None else None,
             scaled_monthly_at_dd25=round(scaled, 3) if scaled is not None else None, risk_per_trade_needed_pct=round(risk_req, 3) if risk_req else None,
             long=dict(n=sum(x["side"] > 0 for x in T), usd=round(sum(x["usd"] for x in T if x["side"] > 0), 2)),
             short=dict(n=sum(x["side"] < 0 for x in T), usd=round(sum(x["usd"] for x in T if x["side"] < 0), 2)))
    r["crit"] = dict(c1_net_pos=net > 0, c2_mean_ge_10bp=r["mean_bp"] >= 10, c3_stress_pos=r["net_stress"] > 0,
                     c4_hard_sl_and_hold=r["median_hold_min"] >= 15, c5_gate=(scaled or 0) >= 3 and (risk_req or 99) <= 2,
                     c6_not_concentrated=(net - top10) > 0 and maxshare is not None and maxshare <= 0.6)
    r["PASS_A"] = all(r["crit"].values()); return r
def main():
    h1p, d1p, rd, fp, outp = sys.argv[1:6]
    h1 = load_h1(h1p); days, atr, lastd = load_d1(d1p, h1)
    R = dict(prereg_sha256=PREREG, inputs={os.path.basename(p): sha(p) for p in (h1p, d1p, fp)})
    T = simulate(h1, days, atr)
    dev = [x for x in T if 2016 <= x["year"] <= 2021]; ho = [x for x in T if x["year"] >= 2022]
    R["DEV"] = stats(dev, 72, "2016-2021"); R["HOLDOUT"] = stats(ho, months(2022, 1, 2026, 10), "2022-01..2026-10-30")
    R["ALL_2015"] = stats([x for x in T if x["year"] == 2015], 12, "2015 (warmup year, info only)")
    # base17
    allB, deps, shas = load_base17(rd, range(2016, 2026)); R["base17_report_sha256"] = shas
    botday = {}
    for x in T: botday[x["day"]] = botday.get(x["day"], 0) + x["usd"]
    tradedays = sorted({b[0] // DAY for b in h1 if datetime.datetime.utcfromtimestamp(b[0]).weekday() < 5})
    def hedge(ys):
        bdday = {}; cutdays = set(); bdcut = 0.0; ncut = 0
        for y in ys:
            for b in allB[y]:
                d1 = b["t1"] // DAY; bdday[d1] = bdday.get(d1, 0) + b["net"]
                if b["net_pct"] <= -8:
                    ncut += 1; bdcut += b["net"]
                    for d in range(b["t0"] // DAY, b["t1"] // DAY + 1): cutdays.add(d)
        D = [d for d in tradedays if datetime.datetime.utcfromtimestamp(d * DAY).year in ys]
        bo = [botday.get(d, 0) for d in D]; bd = [bdday.get(d, 0) for d in D]
        sbo = statistics.pstdev(bo); sbd = statistics.pstdev(bd); k = sbd / sbo if sbo else 0
        mb = statistics.mean(bo); mbd = statistics.mean(bd)
        corr = sum((a - mb) * (c - mbd) for a, c in zip(bo, bd)) / (len(D) * sbo * sbd) if sbo and sbd else None
        cd = [d for d in D if d in cutdays]; botcut = sum(botday.get(d, 0) for d in cd)
        Tc = [x for x in T if x["day"] in cutdays and x["year"] in ys]
        return dict(years=f"{ys[0]}-{ys[-1]}", n_cut_baskets=ncut, n_cut_days=len(cd), bd_cut_loss_usd=round(bdcut, 2),
                    bot_usd_on_cut_days_at_0p25risk=round(botcut, 2), bot_trades_on_cut_days=len(Tc),
                    bot_mean_R_on_cut_days=round(statistics.mean(x["R"] for x in Tc), 4) if Tc else None,
                    bot_mean_R_all=round(statistics.mean(x["R"] for x in T if x["year"] in ys), 4),
                    equal_risk_scale_k=round(k, 3), bot_usd_on_cut_days_equal_risk=round(k * botcut, 2),
                    hedge_ratio=round(k * botcut / abs(bdcut), 4) if bdcut else None, daily_corr_bot_vs_base17=round(corr, 4) if corr is not None else None,
                    PASS_B=(k * botcut / abs(bdcut) >= 0.20) if bdcut else False)
    R["hedge_DEV"] = hedge(list(range(2016, 2022))); R["hedge_HOLDOUT"] = hedge(list(range(2022, 2026)))
    R["hedge_DEV"]["PASS_B"] = R["hedge_DEV"]["PASS_B"] and R["DEV"]["net_usd"] > 0
    # fleet (description only)
    F = load_fleet(fp); lastday = h1[-1][0] // DAY
    fcd = set(); nf = 0
    for x in F:
        if x["cut"] and x["t1s"] // DAY <= lastday:
            nf += 1
            for d in range(x["t0s"] // DAY, x["t1s"] // DAY + 1): fcd.add(d)
    f0 = min(x["t0s"] for x in F) // DAY
    Tw = [x for x in T if f0 <= x["day"] <= lastday]; Tc = [x for x in Tw if x["day"] in fcd]
    R["fleet_cut_days"] = dict(window=f"{datetime.datetime.utcfromtimestamp(f0*DAY).date()}..{datetime.datetime.utcfromtimestamp(lastday*DAY).date()}",
                               n_cuts_covered=nf, n_cuts_total=sum(x["cut"] for x in F), n_cut_days=len(fcd), bot_trades_on_cut_days=len(Tc),
                               bot_usd_on_cut_days=round(sum(x["usd"] for x in Tc), 2), bot_sum_R_cut_days=round(sum(x["R"] for x in Tc), 3),
                               bot_mean_R_cut_days=round(statistics.mean(x["R"] for x in Tc), 4) if Tc else None,
                               bot_mean_R_window=round(statistics.mean(x["R"] for x in Tw), 4) if Tw else None, bot_trades_window=len(Tw),
                               bot_usd_window=round(sum(x["usd"] for x in Tw), 2), fleet_cut_pnl=round(sum(x["pnl"] for x in F if x["cut"]), 2))
    R["VERDICT"] = dict(standalone_DEV=R["DEV"]["PASS_A"], standalone_HOLDOUT=R["HOLDOUT"]["PASS_A"],
                        hedge_DEV=R["hedge_DEV"]["PASS_B"], hedge_HOLDOUT=R["hedge_HOLDOUT"]["PASS_B"],
                        FINDING=(R["DEV"]["PASS_A"] and R["HOLDOUT"]["PASS_A"]) or (R["hedge_DEV"]["PASS_B"] and R["hedge_HOLDOUT"]["PASS_B"]))
    json.dump(R, open(outp, "w"), indent=1)
    with open(outp.replace(".json", "_trades.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, list(T[0].keys())); w.writeheader(); w.writerows(T)
    print(json.dumps({k: v for k, v in R.items() if k not in ("inputs",)}, indent=1))
main()
