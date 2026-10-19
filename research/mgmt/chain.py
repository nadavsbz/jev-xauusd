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
from guardian_sim import deals, pair  # noqa: E402

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


K = 100.0          # contract size of XAUUSD / XAUUSDc (pairing error 0.005 on the EGlobal report, VERIFIED)


def path(pos, bt, lo, hi, ask_add, capital):
    """Equity path of one run, the conservative side of every minute (review PR #31): buys at the bar low, sells
    closed at the ASK (bar high + the bar's spread). Also returns the open volume per minute (closing commission)."""
    a0 = np.searchsorted(bt, pos.t0.min(), "left"); a1 = np.searchsorted(bt, pos.t1.max(), "right")
    tt = bt[a0:a1]; worst = np.zeros(len(tt)); best = np.zeros(len(tt)); real = np.zeros(len(tt)); vol = np.zeros(len(tt))
    L, H, A = lo[a0:a1], hi[a0:a1], ask_add[a0:a1]
    for r in pos.itertuples():
        i = max(np.searchsorted(tt, r.t0, "right") - 1, 0); j = np.searchsorted(tt, r.t1, "left")
        acc = r.cost_in + r.swap * (np.arange(j - i) + 1) / max(j - i, 1) if j > i else 0.0
        if r.side == "buy":
            worst[i:j] += r.vol * (L[i:j] - r.p0) * K + acc; best[i:j] += r.vol * (H[i:j] - r.p0) * K + acc
        else:
            worst[i:j] += -r.vol * (H[i:j] + A[i:j] - r.p0) * K + acc; best[i:j] += -r.vol * (L[i:j] + A[i:j] - r.p0) * K + acc
        vol[i:j] += r.vol
        real[np.searchsorted(tt, r.t1, "left"):] += r.net
    return tt, capital + real + worst, capital + real + best, vol


def window(cfg, B, start, end, eq, lot, level, peak, safe):
    """One tester run from a flat account. -> dict with the equity at the end (or at the protection touch, after
    the closing commission), hit time, the new running peak of the TOTAL (account + safe base, intra-run peak
    included, review PR #31) and the worst drawdown of the total against that running peak."""
    bt, lo, hi, ask_add = B
    d = deals(run(cfg, start, end, eq, lot, f"mgmt_{cfg['tag']}"))
    res = dict(start=str(start), end=str(end), eq_start=round(eq, 2), lot=lot, level=round(level, 2), hit=None)
    pos = pair(d)[0] if len(d) else []
    if not len(pos):
        e1 = float(d.balance.iloc[-1]) if len(d) else eq
        pk = max(peak, e1 + safe)
        res.update(eq_end=round(e1, 2), min_eq=round(min(eq, e1), 2), peak=pk, dd=min(0.0, (min(eq, e1) + safe - pk) / pk))
        return res
    outs = d[d.dir == "out"]
    cpl = float(outs.commission.sum() / outs.volume.sum()) if outs.volume.sum() else 0.0   # commission per lot, <= 0
    tt, e_lo, e_hi, vol = path(pos, bt, lo, hi, ask_add, eq)
    e_close = e_lo + vol * cpl
    hit = np.nonzero(e_close <= level)[0] if level > 0 else []
    k = hit[0] + 1 if len(hit) else len(tt)
    runpk = np.maximum.accumulate(np.maximum(e_hi[:k] + safe, peak))
    dd = float(((e_close[:k] + safe - runpk) / runpk).min())
    if len(hit):
        e1 = float(e_close[hit[0]]); res["hit"] = str(dt.datetime.utcfromtimestamp(int(tt[hit[0]])))
    else:
        e1 = float(d.balance.iloc[-1])
    pk = max(float(runpk[-1]), e1 + safe)
    res.update(eq_end=round(e1, 2), min_eq=round(float(e_close[:k].min()), 2), peak=pk, dd=round(min(dd, 0.0), 5))
    return res


def next_day(ts):
    d = dt.datetime.fromisoformat(ts).date() + dt.timedelta(days=1)
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def load_bars(cfg):
    b = pd.read_csv(os.path.join(ROOT, cfg["bars"]))
    point = 0.001 if cfg["symbol"].endswith("c") else 0.01          # XAUUSDc 3 digits, XAUUSD 2 digits
    return b.time.values.astype(np.int64), b.low.values, b.high.values, b.spread.values * point


def replay(cfg, B):
    """Validation mode (MASTER_PLAN 4.3): each row of the user's real schedule starts from the REAL equity and lot of
    that row (anchored) and runs to the next row's date. After a protection touch the account restarts the next
    trading day with the same lot per equity and the same protection ratio (ASSUMED), until the next row
    (review PR #31). The end is compared with the next row's real equity plus what was moved out in between."""
    rows = json.load(open(os.path.join(ROOT, cfg["schedule"]), encoding="utf-8"))
    out = []; peak = rows[0]["eq"]; worst = 0.0
    for r, n in zip(rows[:-1], rows[1:]):
        start, stop = dt.date.fromisoformat(r["date"]), dt.date.fromisoformat(n["date"])
        eq = r["eq"]; peak = max(peak, eq); hits = []; ratio = r["level"] / r["eq"] if r["level"] else 0.0
        while start < stop and eq > 0:
            lot = max(0.01, round(r["lot"] * eq / r["eq"], 2))
            w = window(cfg, B, start, stop, eq, lot, ratio * eq, peak, 0.0)
            peak = w["peak"]; worst = min(worst, w["dd"]); eq = w["eq_end"]
            if not w["hit"]:
                break
            hits.append(w["hit"]); start = next_day(w["hit"])
        real = (n["eq"] + n["withdrawn_cum"] - r["withdrawn_cum"]) / r["eq"]
        row = dict(start=r["date"], end=n["date"], lot=r["lot"], level=r["level"], sim_growth=round(eq / r["eq"], 4),
                   real_growth=round(real, 4), hits=hits)
        out.append(row); print(row, flush=True)
    sim = float(np.prod([o["sim_growth"] for o in out])); real = float(np.prod([o["real_growth"] for o in out]))
    err = [abs(o["sim_growth"] - o["real_growth"]) for o in out]
    summ = dict(config=cfg, segments=out, sim_multiple=round(sim, 3), real_multiple=round(real, 3), ratio=round(sim / real, 3),
                median_abs_gap_pp=round(100 * float(np.median(err)), 2), sim_max_dd=round(worst, 4))
    json.dump(summ, open(os.path.join(ROOT, "docs", "evidence", f"mgmt_{cfg['tag']}.json"), "w", encoding="utf-8"), indent=1)
    print(summ["sim_multiple"], summ["real_multiple"], summ["ratio"], summ["median_abs_gap_pp"], summ["sim_max_dd"])


def main():
    cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    B = load_bars(cfg)
    if "schedule" in cfg:
        return replay(cfg, B)
    tag = cfg["tag"]; out = os.path.join(ROOT, "data", "derived", "mgmt", tag + ".jsonl")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    done = [json.loads(l) for l in open(out, encoding="utf-8")] if os.path.exists(out) else []
    if done:                                     # restart after the last finished run
        last = done[-1]; eq, safe, peak = last["eq_end"], last["safe"], last["peak"]
        start = dt.date.fromisoformat(last["next_start"])
    else:
        eq, safe = float(cfg["deposit"]), 0.0; peak = eq
        start = dt.date.fromisoformat(cfg["from"])
    stop = dt.date.fromisoformat(cfg["to"])
    while start < stop and eq > 0:
        end = min(next_monday(start), stop)
        lot = max(0.01, round(eq / cfg["divisor"], 2))
        w = window(cfg, B, start, end, eq, lot, cfg["protect"] * eq, peak, safe)
        e1 = w["eq_end"]; gain = e1 - eq
        if gain > 0 and cfg.get("sweep", 0) > 0:
            s = gain * cfg["sweep"]; safe += s; e1 -= s
        w.update(eq_end=round(e1, 2), safe=round(safe, 2), total=round(e1 + safe, 2),
                 next_start=str(min(next_day(w["hit"]), stop)) if w["hit"] else str(end))
        peak = w["peak"]
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(w) + "\n")
        print(w, flush=True)
        eq = e1; start = dt.date.fromisoformat(w["next_start"])
    rows = [json.loads(l) for l in open(out, encoding="utf-8")]
    years = (dt.date.fromisoformat(rows[-1]["end"]) - dt.date.fromisoformat(cfg["from"])).days / 365.25
    fin = rows[-1]["total"]
    summ = dict(config=cfg, runs=len(rows), hits=sum(bool(r["hit"]) for r in rows), final_total=fin,
                multiple=round(fin / cfg["deposit"], 3), cagr=round((fin / cfg["deposit"]) ** (1 / years) - 1, 4),
                max_dd_total=round(min(r["dd"] for r in rows), 4), safe=rows[-1]["safe"])
    json.dump(summ, open(os.path.join(ROOT, "docs", "evidence", f"mgmt_{tag}.json"), "w", encoding="utf-8"), indent=1)
    print(summ)


if __name__ == "__main__":
    main()
