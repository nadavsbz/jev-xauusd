"""Runs docs/BD_TIME_FILTER_PLAN.md (hours: choose + one EGlobal test) and docs/BD_WF_PLAN.md (walk-forward),
one tester run at a time, after the night chain (research/bd_cap/night_chain.py) has finished.
Every rule here is the registered one; nothing is chosen by hand.
Usage: python research/bd_wf/run_wf.py"""
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = sys.executable
EV = os.path.join(ROOT, "docs", "evidence")
DEP = 24895
BASE = {"name": "Black Dragon 3", "expert": "BD\\EA Black Dragon.ex5", "symbol": "XAUUSD", "period": "M15",
        "deposit": DEP, "leverage": 1000, "base_set": "bd2afterpoint_l001_sp50.set"}
WINDOWS = [("2024.04.01", "2024.12.31", "2025.01.01", "2025.03.31"), ("2024.07.01", "2025.03.31", "2025.04.01", "2025.06.30"),
           ("2024.10.01", "2025.06.30", "2025.07.01", "2025.09.30"), ("2025.01.01", "2025.09.30", "2025.10.01", "2025.12.31"),
           # ToDate is EXCLUSIVE in the tester (review PR #25): windows end on the 1st of the next month. Window 5's
           # selection keeps 2025.12.31 (its optimization was already running; 31.12 excluded - documented)
           ("2025.04.01", "2025.12.31", "2026.01.01", "2026.04.01"), ("2025.07.01", "2026.04.01", "2026.04.01", "2026.07.01"),
           ("2025.10.01", "2026.07.01", "2026.07.01", "2026.10.01")]
MISSING = []
RANGES = {"Fix_Distance": [300, 200, 500], "Distance_multiplier": [1.2, 0.3, 1.5], "TP_": [200, 100, 300],
          "OverlapOrderNumber": [5, 2, 7]}


def log(m):
    print(time.strftime("%m-%d %H:%M:%S"), m, flush=True)


def run(args):
    r = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log(f"{args[0]} {args[1] if len(args) > 1 else ''} rc={r.returncode} | {(r.stdout + r.stderr)[-400:]}")
    return r.returncode


def tester_busy():
    cmd = ("Get-Process terminal64,metatester64 -ErrorAction SilentlyContinue | "
           "Where-Object { $_.Path -like 'C:\\MT5_JEV_TEST\\*' } | Measure-Object | Select-Object -ExpandProperty Count")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, errors="replace").stdout
    try:
        return int(out.strip() or 0) > 0
    except ValueError:
        return True


def num(x):
    return float(str(x).replace(" ", "").replace(",", "").replace("%", ""))


def choose(passes, months, need_annual=None):
    """Registered rule: eligible = not wiped and equity DD <= 30% (and annual >= need_annual when given);
    best = highest profit; else the lowest-DD survivor."""
    rows = []
    for p in passes:
        net, dd = num(p["Profit"]), num(p["Equity DD %"])
        wiped = net <= -0.9 * DEP or dd >= 90.0
        ann = ((1 + net / DEP) ** (12 / months) - 1) * 100 if net > -DEP else -100.0
        ok = (not wiped) and dd <= 30.0 and (need_annual is None or ann >= need_annual)
        rows.append((p, net, dd, wiped, ok))
    good = [r for r in rows if r[4]]
    if good:
        return max(good, key=lambda r: (r[1], -r[2]))[0], True
    alive = [r for r in rows if not r[3]]
    return (min(alive, key=lambda r: r[2])[0], False) if alive else (None, False)


def chosen_cap():
    p = os.path.join(EV, "bdcap_selection.json")
    c = json.load(open(p, encoding="utf-8")).get("chosen") if os.path.exists(p) else None
    if not c:
        return {}
    mo = str(c["MaxOrders"])
    return {"MaxLot_": str(c["MaxLot_"]), "Martin_": str(c["Martin_"]), "MaxOrdersBuy": mo, "MaxOrdersSell": mo}


def single(report, overrides, frm, to, base_set=None, name=None, symbol=None, period="M15"):
    job = [dict(BASE, report=report, overrides=overrides, period=period, **{"from": frm, "to": to})]
    if base_set:
        job[0].update(base_set=base_set, name=name, symbol=symbol)
    path = os.path.join(ROOT, "research", "bd_wf", f"q_{report}.json")
    json.dump(job, open(path, "w"), indent=1)
    run(["tools/run_queue.py", os.path.relpath(path, ROOT), "data/derived/bd_wf_runs.jsonl"])
    ok = os.path.exists(os.path.join(EV, report + ".json"))      # run_queue writes evidence only for a valid run
    if not ok:
        MISSING.append(report); log(f"{report}: NO valid evidence")
    return ok


def main():
    chain_log = os.environ.get("CHAIN_LOG", "")
    if not chain_log:
        sys.exit("CHAIN_LOG (the night chain's log file) is required")
    while True:                                   # wait for research/bd_cap/night_chain.py to finish
        txt = open(chain_log, encoding="utf-8", errors="replace").read() if os.path.exists(chain_log) else ""
        if "chain done" in txt or "stopping the chain" in txt:
            break
        time.sleep(120)
    log("night chain done")
    while tester_busy():          # a restart must never start a second tester run beside a running one
        time.sleep(60)
    # spot check (review PR #22): bdcap_opt_ml02.json has no MaxLot_ column; one single pass of the chosen
    # combination on the same period must reproduce its optimization profit to verify that 0.2 was applied
    single("bdcap_spotcheck_ml02", {"MaxLot_": "0.2", "Martin_": "1.3", "MaxOrdersBuy": "10", "MaxOrdersSell": "10"},
           "2024.04.01", "2025.10.31")
    # the spot check must reproduce the optimization's profit, or 0.2 was not what ran there (review PR #23)
    sc = os.path.join(EV, "bdcap_spotcheck_ml02.json")
    if not os.path.exists(sc):
        log("spot check has no valid evidence - every step that depends on the cap choice stops"); return
    got = num(json.load(open(sc, encoding="utf-8"))["summary_from_report"]["סך רווח נקי"])
    json.dump({"expected": 12735.63, "got": got, "match": abs(got - 12735.63) <= 1.0},
              open(os.path.join(EV, "bdcap_spotcheck_result.json"), "w"), indent=1)
    if abs(got - 12735.63) > 1.0:
        log(f"spot check MISMATCH: {got} vs 12735.63 - the 0.2 sweep result is not verified; dependent steps stop"); return
    # timeframes (docs/BD_TF_PLAN.md): BD-A on M5, M30, H1 (M15 = the spot check above), then the rule
    bda = {"MaxLot_": "0.2", "Martin_": "1.3", "MaxOrdersBuy": "10", "MaxOrdersSell": "10"}
    for tf in ("M5", "M30", "H1"):
        single(f"bdtf_sel_{tf}", bda, "2024.04.01", "2025.10.31", period=tf)
    tf_rows = {}
    for tf, rep in (("M15", "bdcap_spotcheck_ml02"), ("M5", "bdtf_sel_M5"), ("M30", "bdtf_sel_M30"), ("H1", "bdtf_sel_H1")):
        p = os.path.join(EV, rep + ".json")
        if os.path.exists(p):
            sm = json.load(open(p, encoding="utf-8"))["summary_from_report"]
            tf_rows[tf] = {"Profit": sm["סך רווח נקי"], "Equity DD %": sm["שווי הפסד מקסימלי"].split("(")[1].rstrip(")%")}
    if len(tf_rows) == 4:
        best, passed = choose([dict(v, tf=k) for k, v in tf_rows.items()], 19, need_annual=50.0)
        json.dump({"rows": tf_rows, "chosen": best and best["tf"], "passes_rule": passed},
                  open(os.path.join(EV, "bdtf_selection.json"), "w"), indent=1, ensure_ascii=False)
        if best and best["tf"] != "M15":
            single(f"bdtf_test_eglobal_{best['tf']}", bda, "2025.11.11", "2026.10.14",
                   base_set="bd_3digit_cal.set", name="Black Dragon 1", symbol="XAUUSDc", period=best["tf"])
    else:
        MISSING.append("timeframe selection")
    cap = chosen_cap()
    # 1. hours: registered choice on the selection period, then ONE test on EGlobal (account 1's period)
    hours = {}
    tp = os.path.join(EV, "bdtime_opt_sel.json")
    if not os.path.exists(tp) and os.path.exists(tp + ".invalid"):      # written by the older check (review PR #22)
        run(["tools/run_opt.py", "research/bd_cap/opt_time.json", "--revalidate"])
    if os.path.exists(tp):
        best, passed = choose(json.load(open(tp, encoding="utf-8"))["passes"], 19, need_annual=50.0)
        if best:
            hours = {"Start_Hour": str(int(num(best["Start_Hour"]))), "End_Hour": str(int(num(best["End_Hour"])))}
            json.dump({"chosen": hours, "passes_rule": passed}, open(os.path.join(EV, "bdtime_selection.json"), "w"), indent=1)
            single("bdtime_test_eglobal", dict(cap, **hours), "2025.11.11", "2026.10.14",
                   base_set="bd_3digit_cal.set", name="Black Dragon 1", symbol="XAUUSDc")
    if not hours:            # the registered walk-forward runs WITH the chosen hours (review PR #22)
        log("no valid trading-hours choice - the walk-forward is not run"); return
    fixed = dict(cap, **hours)
    # 2. walk-forward
    # only windows whose test period is after the cap/hours selection period (ends 31.10.2025) are out of sample
    # (review PR #25): windows 5-7; windows 1-4 are not run
    for i, (a, b, c, d) in enumerate(WINDOWS, 1):
        if i < 5:
            continue
        rep = f"bdwf_w{i}_opt"
        job = dict(BASE, report=rep, fixed=fixed, ranges=RANGES, **{"from": a, "to": b})
        path = os.path.join(ROOT, "research", "bd_wf", f"{rep}.json"); json.dump(job, open(path, "w"), indent=1)
        run(["tools/run_opt.py", os.path.relpath(path, ROOT)])
        ev = os.path.join(EV, rep + ".json")
        if not os.path.exists(ev):
            MISSING.append(rep); log(f"window {i}: no valid optimization - skipped"); continue
        best, passed = choose(json.load(open(ev, encoding="utf-8"))["passes"], 9)
        if best is None:
            MISSING.append(rep + " (all wiped)"); log(f"window {i}: every combination wiped"); continue
        params = {k: (str(int(num(best[k]))) if k != "Distance_multiplier" else str(num(best[k]))) for k in RANGES}
        json.dump({"window": i, "chosen": params, "eligible": passed}, open(os.path.join(EV, f"bdwf_w{i}_choice.json"), "w"), indent=1)
        single(f"bdwf_w{i}_test", dict(fixed, **params), c, d)
        single(f"bdwf_w{i}_base", dict(fixed), c, d)        # the original file (with cap and hours) on the same window
    # the registered verdict: chained balance, drawdown, simple annual return, comparison with the base
    bars3 = [d for d in sorted(os.listdir(os.path.join(ROOT, "data", "raw", "black_dragon_3"))) if d.startswith("rates_XAUUSD_M1_")]
    if bars3:
        if run(["research/bd_wf/aggregate.py", os.path.join("data", "raw", "black_dragon_3", bars3[-1], "bars.csv")]) != 0:
            MISSING.append("verdict (incomplete aggregation)")
    else:
        MISSING.append("verdict (no RoboForex M1 bars snapshot)")     # review PR #26
    if MISSING:
        log("walk-forward PARTIAL - missing valid evidence: " + ", ".join(MISSING))
        json.dump({"missing": MISSING}, open(os.path.join(EV, "bdwf_partial.json"), "w"), indent=1)
    else:
        log("walk-forward done")


if __name__ == "__main__":
    main()
