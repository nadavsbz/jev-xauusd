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
           ("2025.04.01", "2025.12.31", "2026.01.01", "2026.03.31"), ("2025.07.01", "2026.03.31", "2026.04.01", "2026.06.30"),
           ("2025.10.01", "2026.06.30", "2026.07.01", "2026.09.30")]
RANGES = {"Fix_Distance": [300, 200, 500], "Distance_multiplier": [1.2, 0.3, 1.5], "TP_": [200, 100, 300],
          "OverlapOrderNumber": [5, 2, 7]}


def log(m):
    print(time.strftime("%m-%d %H:%M:%S"), m, flush=True)


def run(args):
    r = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log(f"{args[0]} {args[1] if len(args) > 1 else ''} rc={r.returncode} | {(r.stdout + r.stderr)[-400:]}")
    return r.returncode


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


def single(report, overrides, frm, to, base_set=None, name=None, symbol=None):
    job = [dict(BASE, report=report, overrides=overrides, **{"from": frm, "to": to})]
    if base_set:
        job[0].update(base_set=base_set, name=name, symbol=symbol)
    path = os.path.join(ROOT, "research", "bd_wf", f"q_{report}.json")
    json.dump(job, open(path, "w"), indent=1)
    run(["tools/run_queue.py", os.path.relpath(path, ROOT), "data/derived/bd_wf_runs.jsonl"])


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
    # spot check (review PR #22): bdcap_opt_ml02.json has no MaxLot_ column; one single pass of the chosen
    # combination on the same period must reproduce its optimization profit to verify that 0.2 was applied
    single("bdcap_spotcheck_ml02", {"MaxLot_": "0.2", "Martin_": "1.3", "MaxOrdersBuy": "10", "MaxOrdersSell": "10"},
           "2024.04.01", "2025.10.31")
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
    fixed = dict(cap, **hours)
    # 2. walk-forward
    for i, (a, b, c, d) in enumerate(WINDOWS, 1):
        rep = f"bdwf_w{i}_opt"
        job = dict(BASE, report=rep, fixed=fixed, ranges=RANGES, **{"from": a, "to": b})
        path = os.path.join(ROOT, "research", "bd_wf", f"{rep}.json"); json.dump(job, open(path, "w"), indent=1)
        run(["tools/run_opt.py", os.path.relpath(path, ROOT)])
        ev = os.path.join(EV, rep + ".json")
        if not os.path.exists(ev):
            log(f"window {i}: no valid optimization - skipped"); continue
        best, passed = choose(json.load(open(ev, encoding="utf-8"))["passes"], 9)
        if best is None:
            log(f"window {i}: every combination wiped"); continue
        params = {k: (str(int(num(best[k]))) if k != "Distance_multiplier" else str(num(best[k]))) for k in RANGES}
        json.dump({"window": i, "chosen": params, "eligible": passed}, open(os.path.join(EV, f"bdwf_w{i}_choice.json"), "w"), indent=1)
        single(f"bdwf_w{i}_test", dict(fixed, **params), c, d)
        single(f"bdwf_w{i}_base", dict(fixed), c, d)        # the original file (with cap and hours) on the same window
    log("walk-forward done")


if __name__ == "__main__":
    main()
