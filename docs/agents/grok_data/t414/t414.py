#!/usr/bin/env python3
"""t414 - US spot BTC ETF aggregate net flow (Farside) >= P75 of prior 60 trading days -> long BTC 24h.
Frozen with PREREG_t414.md. Usage:
  python3 t414.py pubtime   # measures Farside publication times from Wayback snapshots (no returns)
  python3 t414.py dev       # requires data/pubtime.csv sha listed in SHA256SUMS_prereg.txt
  python3 t414.py holdout   # only if RESULTS_t414_dev.json dev_verdict == PASS; once only
"""
import sys, os, json, csv, math, hashlib, re, time as _time, urllib.request
from datetime import datetime, timedelta, time, timezone, date
from zoneinfo import ZoneInfo
import numpy as np

ROOT = "/workspace/t414"
DATA = "/workspace/research_new_component/data/binance/BTCUSDT_1h.csv"
DATA_SHA = "90f638adf57cc0d019ad3558976c53c732ab73263d0dac5f77fdd2d75d8b11e8"
FLOWS = ROOT + "/data/farside_btc_flows.csv"
FLOWS_SHA = "6c230fc4f4a9baaf7bb27a3261231c448d3c49ac78da829c94814307a399d7eb"
CDX = [ROOT + "/data/cdx_farside_co_uk_btc_.txt", ROOT + "/data/cdx_farside_co_uk_bitcoin-etf-flow-all-data_.txt"]
CDX_URL = {CDX[0]: "farside.co.uk/btc/", CDX[1]: "farside.co.uk/bitcoin-etf-flow-all-data/"}
PUBTIME = ROOT + "/data/pubtime.csv"
SNAPDIR = ROOT + "/data/snapshots"
ET = ZoneInfo("America/New_York"); UTC = timezone.utc
DEV = (datetime(2024, 1, 11, tzinfo=UTC), datetime(2025, 7, 1, tzinfo=UTC))        # entry time in [lo, hi)
HOLD = (datetime(2025, 7, 1, tzinfo=UTC), datetime(2026, 11, 10, tzinfo=UTC))
LOOKBACK, PCTL = 60, 75.0
ENTRY_HOUR = 14; HOLD_H = 24
RT_BP = 2.84; SWAP_BP = 1.30; ROLL_ET = time(17, 0)
B, SEED, ALPHA = 10000, 414, 0.10
N_TRIALS_DSR = 4600

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

def load_flows():
    assert sha(FLOWS) == FLOWS_SHA, "flow sha mismatch"
    out = []
    for r in csv.DictReader(open(FLOWS)):
        if r["all_dash_nontrading"] == "1": continue
        out.append((date.fromisoformat(r["date"]), float(r["total_usd_m"])))
    return out

def parse_num(s):
    s = s.strip()
    if s in ("-", ""): return None
    neg = s.startswith("("); v = float(s.strip("()").replace(",", ""))
    return -v if neg else v

def snapshot_total(html, d):
    """return Total for date d found in a Farside snapshot html, else None"""
    lab = d.strftime("%d %b %Y")
    for m in re.finditer(re.escape(lab), html):
        i = html.rfind("<tr", 0, m.start()); j = html.find("</tr>", m.start())
        if i < 0 or j < 0: continue
        cells = re.findall(r"<td[^>]*>(.*?)</td>", html[i:j], flags=re.S)
        cells = [re.sub(r"<[^>]+>", "", c).replace("&nbsp;", "").strip() for c in cells]
        if not cells or cells[0] != lab or len(cells) < 3: continue
        try: return parse_num(cells[-1])
        except ValueError: continue
    return None

def fetch(url, tries=3):
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 research (read-only)"})
            raw = urllib.request.urlopen(req, timeout=90).read()
            if raw[:2] == b"\x1f\x8b":
                import gzip; raw = gzip.decompress(raw)
            return raw.decode("utf-8", "replace")
        except Exception as e:
            _time.sleep(5 * (a + 1)); err = e
    return None

def phase_pubtime():
    flows = load_flows()
    snaps = []
    for f in CDX:
        for l in open(f):
            p = l.split()
            if len(p) >= 2 and p[1] == "200":
                snaps.append((datetime.strptime(p[0], "%Y%m%d%H%M%S").replace(tzinfo=UTC), p[0], CDX_URL[f]))
    snaps.sort()
    os.makedirs(SNAPDIR, exist_ok=True)
    rows = []
    for i, (d, tot) in enumerate(flows):
        if i + 1 >= len(flows): break
        d1 = flows[i + 1][0]
        deadline = datetime.combine(d1, time(ENTRY_HOUR), UTC)
        start = datetime.combine(d, time(0), UTC)
        cand = [s for s in snaps if start <= s[0] < deadline]
        status, snap_ts, snap_val = "UNMEASURED_NO_SNAPSHOT", "", ""
        if cand:
            s = cand[-1]  # latest snapshot before deadline
            fn = os.path.join(SNAPDIR, s[1] + "_" + s[2].replace("/", "_") + ".html")
            if os.path.exists(fn): html = open(fn, encoding="utf-8").read()
            else:
                html = fetch(f"https://web.archive.org/web/{s[1]}id_/https://{s[2]}")
                if html is not None: open(fn, "w", encoding="utf-8").write(html)
                _time.sleep(1.0)
            if html is None: status = "UNMEASURED_FETCH_FAIL"
            else:
                v = snapshot_total(html, d)
                snap_ts = s[0].isoformat(); snap_val = "" if v is None else v
                if v is not None and abs(v - tot) <= 0.05: status = "VERIFIED_BEFORE_T1_1400"
                elif v is None: status = "ROW_ABSENT_IN_LAST_SNAPSHOT"
                else: status = "ROW_PRESENT_VALUE_DIFFERS"
        rows.append(dict(date=d.isoformat(), total=tot, next_td=d1.isoformat(), deadline_utc=deadline.isoformat(),
                         last_snapshot_utc=snap_ts, snapshot_total=snap_val, status=status))
        if i % 25 == 0: print(i, d, status, flush=True)
    with open(PUBTIME, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("pubtime written", sha(PUBTIME))

def load_bars():
    assert sha(DATA) == DATA_SHA, "data sha mismatch"
    bars = {}
    with open(DATA) as f:
        for r in csv.DictReader(f):
            bars[datetime.fromtimestamp(int(r["open_time_ms"]) / 1000, UTC)] = float(r["open"])
    return bars

def rollovers(t0, t1):
    n = 0.0; day = t0.astimezone(ET).date() - timedelta(days=1)
    while True:
        r = datetime.combine(day, ROLL_ET, ET).astimezone(UTC)
        if r > t1: break
        if r > t0: n += 3 if day.weekday() == 4 else 1
        day += timedelta(days=1)
    return n

def check_pubtime_frozen():
    s = sha(PUBTIME)
    assert s in open(ROOT + "/SHA256SUMS_prereg.txt").read(), "pubtime.csv not frozen in SHA256SUMS_prereg.txt"
    return s

def signals():
    flows = load_flows()
    pub = {r["date"]: r["status"] for r in csv.DictReader(open(PUBTIME))}
    sig = []
    for i in range(LOOKBACK, len(flows)):
        d, v = flows[i]
        prior = np.array([x[1] for x in flows[i - LOOKBACK:i]])
        thr = float(np.percentile(prior, PCTL))
        if v < thr: continue
        verified = pub.get(d.isoformat()) == "VERIFIED_BEFORE_T1_1400"
        lag = 1 if verified else 2
        if i + lag >= len(flows): continue
        ed = flows[i + lag][0]
        sig.append(dict(date=d.isoformat(), flow=v, thr=thr, pub_status=pub.get(d.isoformat(), "NONE"), lag=lag,
                        entry=datetime.combine(ed, time(ENTRY_HOUR), UTC)))
    return sorted(sig, key=lambda s: (s["entry"], s["date"]))

def run_period(lo, hi, bars):
    trades, skipped = [], []; busy = None
    for s in signals():
        e = s["entry"]
        if not (lo <= e < hi): continue
        x = e + timedelta(hours=HOLD_H)
        if e not in bars or x not in bars: skipped.append((s["date"], "missing bar")); continue
        if busy is not None and e < busy: skipped.append((s["date"], "overlap")); continue
        gross = (bars[x] / bars[e] - 1) * 1e4
        nr = rollovers(e, x); cost = RT_BP + SWAP_BP * nr
        trades.append(dict(date=s["date"], flow_usd_m=s["flow"], thr=round(s["thr"], 2), pub_status=s["pub_status"],
                           lag=s["lag"], entry_utc=e.isoformat(), exit_utc=x.isoformat(), gross_bp=round(gross, 4),
                           rollovers=nr, cost_bp=round(cost, 4), net_bp=round(gross - cost, 4)))
        busy = x
    return trades, skipped

def stats(x):
    x = np.asarray(x, float); n = len(x); m = x.mean(); s = x.std(ddof=1)
    return n, m, s, (m / (s / math.sqrt(n)) if s > 0 else float("nan"))

def boot_lb(x):
    rng = np.random.default_rng(SEED); x = np.asarray(x, float)
    idx = rng.integers(0, len(x), size=(B, len(x)))
    return float(np.quantile(x[idx].mean(axis=1), ALPHA))

def dsr(x, N=N_TRIALS_DSR):
    from statistics import NormalDist
    nd = NormalDist(); x = np.asarray(x, float); n = len(x)
    sr = x.mean() / x.std(ddof=1)
    g3 = float(((x - x.mean()) ** 3).mean() / x.std(ddof=0) ** 3)
    g4 = float(((x - x.mean()) ** 4).mean() / x.std(ddof=0) ** 4)
    V = 1.0 / (n - 1); gam = 0.5772156649
    sr0 = math.sqrt(V) * ((1 - gam) * nd.inv_cdf(1 - 1 / N) + gam * nd.inv_cdf(1 - 1 / (N * math.e)))
    den = math.sqrt(max(1e-12, 1 - g3 * sr + (g4 - 1) / 4 * sr ** 2))
    return dict(sr_per_trade=sr, sr0=sr0, skew=g3, kurt=g4, N=N, dsr=nd.cdf((sr - sr0) * math.sqrt(n - 1) / den))

def summarize(trades):
    g = [t["gross_bp"] for t in trades]; ne = [t["net_bp"] for t in trades]
    n, mg, sg, tg = stats(g); _, mn, sn, tn = stats(ne)
    out = dict(n=n, gross_mean_bp=mg, gross_t=tg, net_mean_bp=mn, net_sd_bp=sn, net_t=tn, net_boot_lb90=boot_lb(ne),
               hit_rate=float(np.mean(np.array(ne) > 0)), cost_mean_bp=float(np.mean([t["cost_bp"] for t in trades])),
               dsr=dsr(ne), n_lag1=sum(t["lag"] == 1 for t in trades), n_lag2=sum(t["lag"] == 2 for t in trades))
    for L in (1, 2):  # descriptive only
        sub = [t["net_bp"] for t in trades if t["lag"] == L]
        if len(sub) > 2:
            a, b, c, d = stats(sub); out[f"lag{L}_descriptive"] = dict(n=a, net_mean_bp=b, net_t=d)
    yrs = {}
    for t in trades: yrs.setdefault(t["entry_utc"][:4], []).append(t["net_bp"])
    out["by_year_net_mean_bp"] = {y: float(np.mean(v)) for y, v in sorted(yrs.items())}
    return out

def main():
    phase = sys.argv[1]
    if phase == "pubtime": return phase_pubtime()
    meta = dict(script_sha=sha(__file__), data_sha=DATA_SHA, flows_sha=FLOWS_SHA, pubtime_sha=check_pubtime_frozen(),
                run_utc=datetime.now(UTC).isoformat())
    bars = load_bars()
    if phase == "dev":
        tr, sk = run_period(*DEV, bars); s = summarize(tr)
        if s["gross_mean_bp"] <= 0: v = "KILL"
        elif s["net_mean_bp"] > 0 and s["net_t"] >= 1.5 and s["net_boot_lb90"] > 0: v = "PASS"
        else: v = "FAIL"
        res = dict(meta=meta, phase="dev", summary=s, dev_verdict=v, skipped=sk, trades=tr)
        json.dump(res, open(ROOT + "/RESULTS_t414_dev.json", "w"), indent=1, default=str)
    elif phase == "holdout":
        dv = json.load(open(ROOT + "/RESULTS_t414_dev.json"))
        assert dv["dev_verdict"] == "PASS", "dev did not pass - holdout locked"
        assert not os.path.exists(ROOT + "/RESULTS_t414_holdout.json"), "holdout already run once"
        tr, sk = run_period(*HOLD, bars); s = summarize(tr)
        v = "PASS" if s["net_mean_bp"] > 0 else "FAIL"
        full = summarize(dv["trades"] + tr)
        res = dict(meta=meta, phase="holdout", summary=s, holdout_verdict=v, full_sample=full,
                   dsr_go=bool(full["dsr"]["dsr"] >= 0.95), skipped=sk, trades=tr)
        json.dump(res, open(ROOT + "/RESULTS_t414_holdout.json", "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in res.items() if k != "trades"}, indent=1, default=str))

if __name__ == "__main__":
    main()
