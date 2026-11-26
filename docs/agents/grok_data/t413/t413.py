#!/usr/bin/env python3
"""t413 - BTC fade of the FOMC/CPI announcement-hour move, exit 4h later.
Frozen with PREREG_t413.md. Usage: python3 t413.py dev | holdout
holdout refuses to run unless RESULTS_t413_dev.json exists with dev_verdict == PASS.
"""
import sys, json, csv, math, hashlib
from datetime import datetime, timedelta, time, timezone
from zoneinfo import ZoneInfo
import numpy as np

DATA = "/workspace/research_new_component/data/binance/BTCUSDT_1h.csv"
DATA_SHA = "90f638adf57cc0d019ad3558976c53c732ab73263d0dac5f77fdd2d75d8b11e8"
FOMC = "/workspace/t413/src/scheduled_statement_dates.csv"
CPI = "/workspace/t413/src/cpi_release_dates_2021_2026.csv"
ET = ZoneInfo("America/New_York")
UTC = timezone.utc
PERIODS = {"dev": ("2021-01-01", "2023-12-31"), "holdout": ("2024-01-01", "2026-11-09")}
RT_BP = 2.84            # RF BTC ECN round trip (spread+commission)
ENTRY_SPREAD_ADD_BP = 0.84  # +1 full normal spread at entry (entry spread = 2x normal)
SWAP_BP = 1.30          # per rollover, both sides pay
ROLL_ET = time(17, 0)   # RF server midnight = 17:00 New York
HOLD_H = 4
B, SEED, ALPHA = 10000, 413, 0.10
N_TRIALS_DSR = 4600     # LEDGER.md conservative cumulative N

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def load_bars():
    assert sha(DATA) == DATA_SHA, "data sha mismatch"
    bars = {}
    with open(DATA) as f:
        for r in csv.DictReader(f):
            t = datetime.fromtimestamp(int(r["open_time_ms"]) / 1000, UTC)
            bars[t] = (float(r["open"]), float(r["close"]))
    return bars

def events(lo, hi):
    ev = []
    for r in csv.DictReader(open(FOMC)):
        d = r["date"]
        if lo <= d <= hi: ev.append((d, "FOMC", time(14, 0)))
    for r in csv.DictReader(open(CPI)):
        d = r["date"]
        if lo <= d <= hi: ev.append((d, "CPI", time(8, 30)))
    out = []
    for d, kind, t in ev:
        ann_et = datetime.combine(datetime.strptime(d, "%Y-%m-%d").date(), t, ET)
        ann_utc = ann_et.astimezone(UTC)
        out.append((ann_utc, d, kind))
    return sorted(out)

def rollovers(t0, t1):
    """count RF rollovers (17:00 ET) in (t0, t1]; Friday rollover counts x3"""
    n = 0.0
    day = t0.astimezone(ET).date() - timedelta(days=1)
    while True:
        r = datetime.combine(day, ROLL_ET, ET).astimezone(UTC)
        if r > t1: break
        if r > t0:
            n += 3 if day.weekday() == 4 else 1
        day += timedelta(days=1)
    return n

def run_period(name):
    lo, hi = PERIODS[name]
    bars = load_bars()
    trades, skipped = [], []
    busy_until = None
    for ann_utc, d, kind in events(lo, hi):
        a_bar = ann_utc.replace(minute=0, second=0, microsecond=0)  # H1 bar containing the announcement
        e_bar = a_bar + timedelta(hours=1)                           # first bar AFTER announcement bar
        x_bar = e_bar + timedelta(hours=HOLD_H)                      # exit at open of this bar
        need = [a_bar, e_bar, x_bar]
        if any(b not in bars for b in need):
            skipped.append((d, kind, "missing bar")); continue
        if busy_until is not None and e_bar < busy_until:
            skipped.append((d, kind, "overlap")); continue
        ao, ac = bars[a_bar]
        ann_ret = ac / ao - 1
        if ann_ret == 0:
            skipped.append((d, kind, "zero ann return")); continue
        direction = -1 if ann_ret > 0 else 1
        entry = bars[e_bar][0]; exitp = bars[x_bar][0]
        gross = direction * (exitp / entry - 1) * 1e4
        nroll = rollovers(e_bar, x_bar)
        cost = RT_BP + ENTRY_SPREAD_ADD_BP + SWAP_BP * nroll
        trades.append(dict(date=d, kind=kind, ann_bar_utc=a_bar.isoformat(), entry_utc=e_bar.isoformat(),
                           exit_utc=x_bar.isoformat(), ann_ret_bp=round(ann_ret * 1e4, 3), dir=direction,
                           gross_bp=round(gross, 4), rollovers=nroll, cost_bp=round(cost, 4), net_bp=round(gross - cost, 4)))
        busy_until = x_bar
    return trades, skipped

def stats(x):
    x = np.asarray(x, float); n = len(x)
    m = x.mean(); s = x.std(ddof=1)
    return n, m, s, (m / (s / math.sqrt(n)) if s > 0 else float("nan"))

def boot_lb(x):
    rng = np.random.default_rng(SEED)
    x = np.asarray(x, float)
    idx = rng.integers(0, len(x), size=(B, len(x)))
    means = x[idx].mean(axis=1)
    return float(np.quantile(means, ALPHA))  # one-sided 90% lower bound

def dsr(x, N=N_TRIALS_DSR):
    from statistics import NormalDist
    nd = NormalDist()
    x = np.asarray(x, float); n = len(x)
    sr = x.mean() / x.std(ddof=1)
    g3 = float(((x - x.mean()) ** 3).mean() / x.std(ddof=0) ** 3)
    g4 = float(((x - x.mean()) ** 4).mean() / x.std(ddof=0) ** 4)
    V = 1.0 / (n - 1)
    gam = 0.5772156649
    sr0 = math.sqrt(V) * ((1 - gam) * nd.inv_cdf(1 - 1 / N) + gam * nd.inv_cdf(1 - 1 / (N * math.e)))
    den = math.sqrt(max(1e-12, 1 - g3 * sr + (g4 - 1) / 4 * sr ** 2))
    return dict(sr_per_trade=sr, sr0=sr0, skew=g3, kurt=g4, N=N, dsr=nd.cdf((sr - sr0) * math.sqrt(n - 1) / den))

def summarize(trades):
    g = [t["gross_bp"] for t in trades]; ne = [t["net_bp"] for t in trades]
    n, mg, sg, tg = stats(g); _, mn, sn, tn = stats(ne)
    out = dict(n=n, gross_mean_bp=mg, gross_t=tg, net_mean_bp=mn, net_sd_bp=sn, net_t=tn,
               net_boot_lb90=boot_lb(ne), hit_rate=float(np.mean(np.array(ne) > 0)),
               cost_mean_bp=float(np.mean([t["cost_bp"] for t in trades])), dsr=dsr(ne))
    by = {}
    for k in ("FOMC", "CPI"):  # descriptive only
        sub = [t["net_bp"] for t in trades if t["kind"] == k]
        if len(sub) > 2:
            a, b, c, d = stats(sub); by[k] = dict(n=a, net_mean_bp=b, net_t=d)
    out["by_kind_descriptive"] = by
    yrs = {}
    for t in trades: yrs.setdefault(t["date"][:4], []).append(t["net_bp"])
    out["by_year_net_mean_bp"] = {y: float(np.mean(v)) for y, v in sorted(yrs.items())}
    return out

def main():
    phase = sys.argv[1]
    meta = dict(script_sha=sha(__file__), data=DATA, data_sha=DATA_SHA, fomc_sha=sha(FOMC), cpi_sha=sha(CPI),
                run_utc=datetime.now(UTC).isoformat())
    if phase == "dev":
        tr, sk = run_period("dev")
        s = summarize(tr)
        if s["gross_mean_bp"] <= 0: verdict = "KILL"
        elif s["net_mean_bp"] > 0 and s["net_t"] >= 1.5 and s["net_boot_lb90"] > 0: verdict = "PASS"
        else: verdict = "FAIL"
        res = dict(meta=meta, phase="dev", period=PERIODS["dev"], summary=s, dev_verdict=verdict, skipped=sk, trades=tr)
        json.dump(res, open("/workspace/t413/RESULTS_t413_dev.json", "w"), indent=1, default=float)
    elif phase == "holdout":
        dv = json.load(open("/workspace/t413/RESULTS_t413_dev.json"))
        assert dv["dev_verdict"] == "PASS", "dev did not pass - holdout locked"
        import os
        assert not os.path.exists("/workspace/t413/RESULTS_t413_holdout.json"), "holdout already run once"
        tr, sk = run_period("holdout")
        s = summarize(tr)
        verdict = "PASS" if s["net_mean_bp"] > 0 else "FAIL"
        alltr = dv["trades"] + tr
        full = summarize(alltr)
        res = dict(meta=meta, phase="holdout", period=PERIODS["holdout"], summary=s, holdout_verdict=verdict,
                   full_sample=full, dsr_go=bool(full["dsr"]["dsr"] >= 0.95), skipped=sk, trades=tr)
        json.dump(res, open("/workspace/t413/RESULTS_t413_holdout.json", "w"), indent=1, default=float)
    print(json.dumps({k: v for k, v in res.items() if k not in ("trades",)}, indent=1, default=float))

if __name__ == "__main__":
    main()
