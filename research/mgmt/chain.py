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


def path(pos, bt, lo, hi, ask_add, capital, cl=None):
    """Equity path of one run. The whole book is valued twice per minute, once with the price at the bar's LOW and
    once at its HIGH (sells at the ASK = price + the bar's spread), and only then the worse/better total is taken:
    the price cannot be at the low and the high at once (review PR #31, rounds 3 and 4). Also returns the open
    volume per minute (closing commission)."""
    a0 = np.searchsorted(bt, pos.t0.min(), "left"); a1 = np.searchsorted(bt, pos.t1.max(), "right")
    tt = bt[a0:a1]; at_lo = np.zeros(len(tt)); at_hi = np.zeros(len(tt)); real = np.zeros(len(tt)); vol = np.zeros(len(tt))
    at_cl = np.zeros(len(tt)); C = cl[a0:a1] if cl is not None else None
    L, H, A = lo[a0:a1], hi[a0:a1], ask_add[a0:a1]
    for r in pos.itertuples():
        i = max(np.searchsorted(tt, r.t0, "right") - 1, 0); j = np.searchsorted(tt, r.t1, "left")
        acc = r.cost_in + r.swap * (np.arange(j - i) + 1) / max(j - i, 1) if j > i else 0.0
        sgn, add = (1, 0.0) if r.side == "buy" else (-1, A[i:j])
        at_lo[i:j] += sgn * r.vol * (L[i:j] + add - r.p0) * K + acc
        at_hi[i:j] += sgn * r.vol * (H[i:j] + add - r.p0) * K + acc
        if C is not None:
            at_cl[i:j] += sgn * r.vol * (C[i:j] + add - r.p0) * K + acc
        vol[i:j] += r.vol
        real[np.searchsorted(tt, r.t1, "left"):] += r.net
    lo_t, hi_t = capital + real + np.minimum(at_lo, at_hi), capital + real + np.maximum(at_lo, at_hi)
    if C is not None:                                   # the equity at the bar's CLOSE (daily close-to-close returns)
        return tt, lo_t, hi_t, vol, capital + real + at_cl
    return tt, lo_t, hi_t, vol


def window(cfg, B, start, end, eq, lot, level, peak, safe, flat_after=None):
    """One tester run from a flat account. -> dict with the equity at the end (or at the protection touch, after
    the closing commission), hit time, the new running peak of the TOTAL (account + safe base, intra-run peak
    included, review PR #31) and the worst drawdown of the total against that running peak.
    flat_after (a date): the user changes the lot only when NO position is open (user, 20.10.2026), so the run is
    cut at the first minute on/after that date with nothing open; 'flat' gives that time. If the book is never
    flat before the run ends, the tester's end-of-test close is used and 'forced_end' is set (ASSUMED rare)."""
    bt, lo, hi, ask_add = B[:4]
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
    f = None
    if flat_after is not None:
        # the tester's own end-of-test closes are NOT a natural flat moment (review PR #34): every minute from
        # the first such close on is excluded. They carry the comment "end of test"; as a fallback, exits at
        # the run's very last deal time on its final day are treated the same way.
        outs = d[d.dir == "out"]
        eot = outs[outs.comment.str.contains("end of test", case=False, na=False)]
        last_t = int(d.t.max()) if len(d) else 0
        end_ts = int(dt.datetime.combine(end, dt.time()).replace(tzinfo=dt.timezone.utc).timestamp())
        if eot.empty and len(outs) and last_t >= end_ts - 86400:
            eot = outs[outs.t == last_t]
        cut = int(eot.t.min()) if len(eot) else None
        tb = int(dt.datetime.combine(flat_after, dt.time()).replace(tzinfo=dt.timezone.utc).timestamp())
        natural = (tt >= tb) & (vol == 0)
        if cut is not None:
            natural &= tt < cut
        cand = np.nonzero(natural)[0]
        if len(cand):
            f = int(cand[0])
        elif cut is None and tt[-1] >= tb:
            f = len(tt) - 1                       # flat after the last (natural) exit of the run
    if len(hit) and (f is None or hit[0] <= f):
        k = hit[0] + 1
    elif f is not None:
        k = f + 1; hit = []
    else:
        k = len(tt)
    runpk = np.maximum.accumulate(np.maximum(e_hi[:k] + safe, peak))
    dd = float(((e_close[:k] + safe - runpk) / runpk).min())
    if len(hit):
        e1 = float(e_close[hit[0]]); res["hit"] = str(dt.datetime.utcfromtimestamp(int(tt[hit[0]])))
    elif f is not None:
        e1 = float(e_close[f]); res["flat"] = str(dt.datetime.utcfromtimestamp(int(tt[f])))
    else:
        e1 = float(d.balance.iloc[-1]); res["forced_end"] = flat_after is not None
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
    return b.time.values.astype(np.int64), b.low.values, b.high.values, b.spread.values * point, b.close.values


def replay(cfg, B):
    """Validation mode (MASTER_PLAN 4.3): each row of the user's real schedule starts from the REAL equity and lot of
    that row (anchored) and runs to the next row's date. After a protection touch the account restarts the next
    trading day with the same lot per equity and the same protection ratio (ASSUMED), until the next row
    (review PR #31). The end is compared with the next row's real equity plus what was moved out in between."""
    rows = json.load(open(os.path.join(ROOT, cfg["schedule"]), encoding="utf-8"))
    # what the user moved out (withdrawn_cum) is the safe base: it stays in the total, so a withdrawal is not a
    # drawdown (review PR #31, round 4)
    out = []; peak = rows[0]["eq"] + rows[0]["withdrawn_cum"]; worst = 0.0
    for r, n in zip(rows[:-1], rows[1:]):
        start, stop = dt.date.fromisoformat(r["date"]), dt.date.fromisoformat(n["date"])
        eq = r["eq"]; safe = r["withdrawn_cum"]; peak = max(peak, eq + safe); hits = []
        ratio = r["level"] / r["eq"] if r["level"] else 0.0
        while start < stop and eq > 0:
            lot = max(0.01, round(r["lot"] * eq / r["eq"], 2))
            w = window(cfg, B, start, stop, eq, lot, ratio * eq, peak, safe)
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
        boundary = next_monday(start)
        if boundary >= stop:
            boundary, end = None, stop
        else:
            end = min(boundary + dt.timedelta(days=14), stop)   # room to reach a flat moment after the boundary
        lot = max(0.01, round(eq / cfg["divisor"], 2))
        w = window(cfg, B, start, end, eq, lot, cfg["protect"] * eq, peak, safe, flat_after=boundary)
        tries = 1
        while w.get("forced_end") and end < stop and tries < 6:     # no natural flat yet: run longer (review PR #34)
            end = min(end + dt.timedelta(days=14), stop); tries += 1
            w = window(cfg, B, start, end, eq, lot, cfg["protect"] * eq, peak, safe, flat_after=boundary)
        e1 = w["eq_end"]; gain = e1 - eq
        if gain > 0 and cfg.get("sweep", 0) > 0:
            s = gain * cfg["sweep"]; safe += s; e1 -= s
        w.update(eq_end=round(e1, 2), safe=round(safe, 2), total=round(e1 + safe, 2),
                 next_start=str(min(next_day(w["hit"] or w.get("flat") or str(end)), stop))
                 if (w["hit"] or w.get("flat")) else str(end))   # ASSUMED: the next run starts the day after
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
