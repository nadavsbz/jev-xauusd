"""MASTER_PLAN step A3: the user's management layer run INSIDE the tester, as a chain of runs
(review PR #31: a protection close resets the grid, so the path cannot be derived from one long run).

Rule (the user's own, manual_report.xlsx):
  * every week (Monday) the account restarts flat with Lot_Init_ = round(equity / DIVISOR, 2), min 0.01;
    ASSUMED: open positions are closed at the weekly update (the tester closes them at the end of the run);
  * protection = PROTECT x equity at the start of the week; when the minute-bar equity (worse of low/high,
    floating included) touches it, everything is closed at that minute and the account waits for the next
    day, then restarts with the new lot (ASSUMED: next trading day, as in the report's restarts);
  * optional sweep: SWEEP x the week's profit leaves the account to a safe base (not traded).
Each run: tools/run_tester.py on C:\\MT5_JEV_TEST; the equity path is rebuilt from the report's deals and the
broker's M1 bars (research/btc/guardian_sim.py functions).

Usage: python research/mgmt/chain.py CONFIG_JSON
CONFIG: {"tag": "bd_lars_sel24", "base_set": "...", "name": "Black Dragon 3", "expert": "BD\\\\EA Black Dragon.ex5",
         "symbol": "XAUUSD", "period": "M15", "model": 4, "from": "2024-04-01", "to": "2025-11-01",
         "deposit": 50000, "divisor": 600000, "protect": 0.85, "sweep": 0.0, "bars": "data/raw/.../bars.csv"}
Writes data/derived/mgmt/<tag>.jsonl (one line per run, restartable) and docs/evidence/mgmt_<tag>.json."""
import datetime as dt, json, os, subprocess, sys
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "research", "btc"))
from run_queue import write_set, TERM          # noqa: E402
from guardian_sim import deals, pair, equity_path  # noqa: E402

PY = sys.executable


def next_monday(d):
    return d + dt.timedelta(days=(7 - d.weekday()) % 7 or 7)


def run(cfg, start, end, deposit, lot, rep):
    write_set(cfg["base_set"], {"Lot_Init_": f"{lot:.2f}"}, rep + ".set")
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-Process terminal64,metatester64 -ErrorAction SilentlyContinue | "
                    "Where-Object { $_.Path -like 'C:\\MT5_JEV_TEST\\*' } | Stop-Process -Force"])
    cmd = [PY, "run_tester.py", "--accounts", "../accounts.json", "--name", cfg["name"], "--terminal", TERM,
           "--expert", cfg["expert"], "--set", rep + ".set", "--symbol", cfg["symbol"], "--period", cfg["period"],
           "--model", str(cfg.get("model", 4)), "--from", start.strftime("%Y.%m.%d"), "--to", end.strftime("%Y.%m.%d"),
           "--deposit", str(int(round(deposit))), "--leverage", "1000", "--report", rep, "--timeout", "3600"]
    r = subprocess.run(cmd, cwd=os.path.join(ROOT, "tools"), capture_output=True, text=True)
    htm = os.path.join(os.path.dirname(TERM), rep + ".htm")
    if r.returncode != 0 or not os.path.exists(htm):
        raise SystemExit(f"tester run failed {start}..{end}: {r.stdout[-300:]} {r.stderr[-300:]}")
    txt = open(htm, "rb").read().decode("utf-16")
    if f"Lot_Init_={lot:.2f}" not in txt and f"Lot_Init_={lot:g}" not in txt:
        raise SystemExit(f"report {rep} does not carry Lot_Init_={lot:.2f}: input ignored")
    return htm


def segment_end(cfg, htm, eq, level, bt, lo, hi):
    """-> (equity at the end of the run or at the protection touch, hit time or None, minimum equity)."""
    d = deals(htm)
    if not len(d):
        return eq, None, eq
    pos, _ = pair(d)
    if not len(pos):
        return float(d.balance.iloc[-1]), None, eq
    tt, e_lo, _ = equity_path(pos, bt, lo, hi, eq)
    hit = np.nonzero(e_lo <= level)[0] if level > 0 else []
    if len(hit):
        return float(e_lo[hit[0]]), int(tt[hit[0]]), float(e_lo[hit[0]])
    return float(d.balance.iloc[-1]), None, float(e_lo.min())


def replay(cfg, bt, lo, hi):
    """Validation mode: every row of the user's real schedule is one run that starts from the REAL equity and lot
    of that row (anchored), with the row's protection level; its end is compared with the next row's real
    equity plus what was moved out in between. Measures tester+reconstruction fidelity, not the rule."""
    rows = json.load(open(os.path.join(ROOT, cfg["schedule"]), encoding="utf-8"))
    out = []
    for r, n in zip(rows[:-1], rows[1:]):
        htm = run(cfg, dt.date.fromisoformat(r["date"]), dt.date.fromisoformat(n["date"]), r["eq"], r["lot"], f"mgmt_{cfg['tag']}")
        e1, th, mn = segment_end(cfg, htm, r["eq"], r["level"], bt, lo, hi)
        real = (n["eq"] + n["withdrawn_cum"] - r["withdrawn_cum"]) / r["eq"]
        row = dict(start=r["date"], end=n["date"], lot=r["lot"], level=r["level"], sim_growth=round(e1 / r["eq"], 4),
                   real_growth=round(real, 4), hit=None if th is None else str(dt.datetime.utcfromtimestamp(th)),
                   min_eq=round(mn, 2))
        out.append(row); print(row, flush=True)
    sim = float(np.prod([o["sim_growth"] for o in out])); real = float(np.prod([o["real_growth"] for o in out]))
    summ = dict(config=cfg, segments=out, sim_multiple=round(sim, 3), real_multiple=round(real, 3),
                ratio=round(sim / real, 3))
    json.dump(summ, open(os.path.join(ROOT, "docs", "evidence", f"mgmt_{cfg['tag']}.json"), "w", encoding="utf-8"), indent=1)
    print(summ["sim_multiple"], summ["real_multiple"], summ["ratio"])


def main():
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    if "schedule" in cfg:
        b = pd.read_csv(os.path.join(ROOT, cfg["bars"]))
        return replay(cfg, b.time.values.astype(np.int64), b.low.values, b.high.values)
    tag = cfg["tag"]; out = os.path.join(ROOT, "data", "derived", "mgmt", tag + ".jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    b = pd.read_csv(os.path.join(ROOT, cfg["bars"]))
    bt, lo, hi = b.time.values.astype(np.int64), b.low.values, b.high.values
    done = [json.loads(l) for l in open(out, encoding="utf-8")] if os.path.exists(out) else []
    if done:                                     # restart after the last finished run
        last = done[-1]; eq, safe = last["eq_end"], last["safe"]
        start = dt.date.fromisoformat(last["next_start"])
    else:
        eq, safe = float(cfg["deposit"]), 0.0
        start = dt.date.fromisoformat(cfg["from"])
    stop = dt.date.fromisoformat(cfg["to"])
    while start < stop and eq > 0:
        end = min(next_monday(start), stop)
        lot = max(0.01, round(eq / cfg["divisor"], 2)); level = cfg["protect"] * eq
        rep = f"mgmt_{tag}"
        htm = run(cfg, start, end, eq, lot, rep)
        d = deals(htm)
        row = dict(start=str(start), end=str(end), eq_start=round(eq, 2), lot=lot, level=round(level, 2))
        if len(d):
            pos, unpaired = pair(d)
            tt, e_lo, _ = equity_path(pos, bt, lo, hi, eq) if len(pos) else (np.array([]), np.array([]), None)
            hit = np.nonzero(e_lo <= level)[0]
            if len(hit):
                th = int(tt[hit[0]]); eq_end = float(e_lo[hit[0]])
                hd = dt.datetime.utcfromtimestamp(th).date()
                nxt = hd + dt.timedelta(days=1)
                while nxt.weekday() >= 5:
                    nxt += dt.timedelta(days=1)
                row.update(hit=True, hit_time=str(dt.datetime.utcfromtimestamp(th)), eq_end=round(eq_end, 2),
                           min_eq=round(eq_end, 2), next_start=str(min(nxt, stop)), unpaired=unpaired)
            else:
                eq_end = float(d.balance.iloc[-1])
                row.update(hit=False, eq_end=round(eq_end, 2),
                           min_eq=round(float(e_lo.min()) if len(e_lo) else eq, 2), next_start=str(end), unpaired=unpaired)
        else:
            eq_end = eq
            row.update(hit=False, eq_end=round(eq, 2), min_eq=round(eq, 2), next_start=str(end), unpaired=0)
        gain = eq_end - eq
        if gain > 0 and cfg.get("sweep", 0) > 0:
            s = gain * cfg["sweep"]; safe += s; eq_end -= s; row["eq_end"] = round(eq_end, 2)
        row["safe"] = round(safe, 2); row["total"] = round(eq_end + safe, 2)
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        print(row, flush=True)
        eq = eq_end; start = dt.date.fromisoformat(row["next_start"])
        if start >= stop:
            break
    rows = [json.loads(l) for l in open(out, encoding="utf-8")]
    tot = np.array([r["total"] for r in rows]); worst = np.array([r["min_eq"] + r["safe"] for r in rows])
    peak = np.maximum.accumulate(np.concatenate([[cfg["deposit"]], tot]))[:-1]
    dd = float(((worst - peak) / peak).min()) if len(rows) else 0.0
    years = (dt.date.fromisoformat(rows[-1]["end"]) - dt.date.fromisoformat(cfg["from"])).days / 365.25
    summ = dict(config=cfg, runs=len(rows), hits=sum(r["hit"] for r in rows), final_total=tot[-1],
                multiple=round(tot[-1] / cfg["deposit"], 3), cagr=round((tot[-1] / cfg["deposit"]) ** (1 / years) - 1, 4),
                max_dd_total=round(dd, 4), safe=rows[-1]["safe"])
    json.dump(summ, open(os.path.join(ROOT, "docs", "evidence", f"mgmt_{tag}.json"), "w", encoding="utf-8"), indent=1)
    print(summ)


if __name__ == "__main__":
    main()
