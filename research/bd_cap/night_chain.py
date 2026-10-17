"""Overnight chain, one tester run at a time (docs/BD_CAP_SWEEP_PLAN.md, docs/BD_TIME_FILTER_PLAN.md):
1. wait for the cap-sweep optimization (bdcap_opt_ml05_10) to finish;
2. apply the pre-registered selection (select.py), build and run the ONE EGlobal test (run_queue);
3. run the RoboForex set on account 1's period (queue_after_sweep.json, docs/BD1_CRASH_CAUSE.md);
4. build and run the trading-hours optimization with the chosen cap combination (selection period only).
Each step writes its own evidence; a failed step is logged and the chain goes on with the next one.
Usage: python research/bd_cap/night_chain.py"""
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = sys.executable
EV = os.path.join(ROOT, "docs", "evidence")


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def run(args):
    r = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log(f"{args[0]} rc={r.returncode} | {(r.stdout + r.stderr)[-600:]}")
    return r.returncode


def tester_busy():
    """Only the dedicated tester install counts (other terminals on this machine are not ours)."""
    cmd = ("Get-Process terminal64,metatester64 -ErrorAction SilentlyContinue | "
           "Where-Object { $_.Path -like 'C:\MT5_JEV_TEST\*' } | Measure-Object | Select-Object -ExpandProperty Count")
    out = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, errors="replace").stdout
    try:
        return int(out.strip() or 0) > 0
    except ValueError:
        return True


def main():
    target = os.path.join(EV, "bdcap_opt_ml05_10.json")
    while not (os.path.exists(target) or os.path.exists(target + ".invalid")):
        if not tester_busy():
            time.sleep(120)
            if not tester_busy() and not os.path.exists(target):
                log("the cap optimization is not running and left no evidence - stopping the chain")
                return
        time.sleep(60)
    log("cap sweep finished")
    while tester_busy():
        time.sleep(30)
    if run(["research/bd_cap/select.py"]) == 0 and run(["research/bd_cap/make_test_job.py"]) == 0:
        run(["tools/run_queue.py", "research/bd_cap/queue_test.json", "data/derived/bdcap_test.jsonl"])
    run(["tools/run_queue.py", "research/bd_cap/queue_after_sweep.json", "data/derived/bd_robo_accperiod.jsonl"])
    # trading hours, with the chosen cap combination (or the original set when none was chosen)
    fixed = {}
    sel = os.path.join(EV, "bdcap_selection.json")
    if os.path.exists(sel):
        c = json.load(open(sel, encoding="utf-8")).get("chosen")
        if c:
            mo = str(c["MaxOrders"])
            fixed = {"MaxLot_": str(c["MaxLot_"]), "Martin_": str(c["Martin_"]), "MaxOrdersBuy": mo, "MaxOrdersSell": mo}
    job = {"report": "bdtime_opt_sel", "base_set": "bd2afterpoint_l001_sp50.set", "fixed": fixed,
           "ranges": {"Start_Hour": [0, 2, 6], "End_Hour": [17, 2, 23]},
           "name": "Black Dragon 3", "expert": "BD\\EA Black Dragon.ex5", "symbol": "XAUUSD", "period": "M15",
           "from": "2024.04.01", "to": "2025.10.31", "deposit": 24895, "leverage": 1000}
    path = os.path.join(ROOT, "research", "bd_cap", "opt_time.json")
    json.dump(job, open(path, "w"), indent=1)
    run(["tools/run_opt.py", "research/bd_cap/opt_time.json"])
    log("chain done")


if __name__ == "__main__":
    main()
