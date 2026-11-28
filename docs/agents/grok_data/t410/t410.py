#!/usr/bin/env python3
"""t410 - pre-rule screen VR(H6) / TrendPersistence. Frozen with PREREG_t410.md.
Order is enforced in code: (1) cost screen, (2) controls BTC+ETH, STOP if any control fails,
(3) only then the cost-passing test instruments."""
import json, sys, hashlib
import numpy as np, pandas as pd

SEED = 410; B = 2000; QS = (4, 12, 28); YEARS = list(range(2021, 2026))
ALPHA = 0.05; COST_CAP_BP = 2.0
SERVER_TZ = "Europe/Athens"   # RF server = EET/EEST (EU DST), OBSERVED via US/EU DST-mismatch weeks
CONTROLS = {
  "BTCUSD": "/workspace/research_new_component/data/cfd_h1/BTCUSD.csv",
  "ETHUSD": "/workspace/research_new_component/data/cfd_h1/ETHUSD.csv",
}
# EffectiveCostSide = spread/2 + commission per side, bp of price (RoboForex ECN); sources in PREREG s.4
TESTS = {  # half_abs = half of full RT cash width in price units (needs ref price); *_bp already in bp of price
  "XAUUSD":      dict(path="/workspace/t405/data/bars/XAUUSD_H1.csv",      half_abs=0.31/2, comm_side_bp=0.0),   # RF ECN RT $0.31/oz incl. commission
  "XAGUSD":      dict(path="/workspace/t295/in/XAGUSD_H1.csv",             half_abs=0.012/2, comm_side_bp=0.20), # width $0.012/oz + ECN 20/mio/side
  ".USTECHCash": dict(path="/workspace/t405/data/bars/.USTECHCash_H1.csv", half_bp=0.54/2,  comm_side_bp=0.0),   # 0.54bp RT incl. comm (prescreen)
  ".DE40Cash":   dict(path="/workspace/t405/data/bars/.DE40Cash_H1.csv",   half_bp=0.84/2,  comm_side_bp=0.0),   # 0.84bp RT incl. comm (prescreen)
  "BRENT":       dict(path="/workspace/t295/in/BRENT_H1.csv",              half_bp=3.8333/2, comm_side_bp=0.0),  # WTI 3.83bp RT proxy (ASSUMED)
}

def ref_price(path):
    """median close over the measurement years (price LEVEL only, no returns)."""
    d = pd.read_csv(path, usecols=["time", "close"]); y = pd.to_datetime(d["time"], unit="s").dt.year
    return float(d.loc[(y >= YEARS[0]) & (y <= YEARS[-1]), "close"].median())

def h6_returns(path):
    d = pd.read_csv(path, usecols=["time", "close"])
    srv = pd.to_datetime(d["time"], unit="s")             # naive server wall-clock
    utc = srv.dt.tz_localize(SERVER_TZ, ambiguous="NaT", nonexistent="NaT").dt.tz_convert("UTC")
    d = d.assign(utc=utc).dropna(subset=["utc"]).sort_values("utc")
    d = d[d["close"] > 0]
    d["b"] = d["utc"].dt.floor("6h")                       # H6 buckets at UTC 00/06/12/18
    h6 = d.groupby("b")["close"].last()
    r = np.log(h6).diff().dropna()                         # return between consecutive existing H6 buckets
    r = r[(r.index.year >= YEARS[0]) & (r.index.year <= YEARS[-1])]
    return r

def vr(x, q):
    x = np.asarray(x, float); n = (len(x) // q) * q
    if n < 2 * q: return np.nan
    s = x[:n].reshape(-1, q).sum(1)                        # non-overlapping q-sums
    return s.var(ddof=1) / (q * x.var(ddof=1))

def tp(x):
    return float(np.median([vr(x, q) for q in QS]))

def measure(name, r, rng):
    out = {"n_h6": int(len(r)), "first": str(r.index[0]), "last": str(r.index[-1])}
    out.update({f"VR{q}": vr(r.values, q) for q in QS}); out["TP"] = tp(r.values)
    out["VR12_by_year"] = {str(y): vr(r[r.index.year == y].values, 12) for y in YEARS}
    out["years_VR12_gt1"] = int(sum(v > 1 for v in out["VR12_by_year"].values()))
    wk = r.index.tz_convert(None).to_period("W-SUN")     # weekly blocks (Mon-Sun UTC)
    blocks = [g.values for _, g in r.groupby(wk)]
    nb = len(blocks); boots = np.empty(B)
    for b in range(B):
        idx = rng.integers(0, nb, nb)
        boots[b] = tp(np.concatenate([blocks[i] for i in idx]))
    out["n_weeks"] = nb
    out["TP_lo95_onesided"] = float(np.quantile(boots, ALPHA))
    out["p_boot_TP_le_1"] = float((1 + np.sum(boots <= 1.0)) / (B + 1))
    return out

def main():
    res = {"task": "t410", "seed": SEED, "B": B, "qs": QS, "years": YEARS, "server_tz": SERVER_TZ}
    # (1) cost screen - before any VR
    cost = {}
    for k, v in TESTS.items():
        if "half_abs" in v:
            px = ref_price(v["path"]); half = v["half_abs"] / px * 1e4
        else:
            px = None; half = v["half_bp"]
        c = half + v["comm_side_bp"]
        cost[k] = {"ref_price": px, "half_spread_bp": round(half, 4), "comm_side_bp": v["comm_side_bp"],
                   "EffectiveCostSide_bp": round(c, 4), "excluded": bool(c > COST_CAP_BP)}
    res["cost_screen"] = cost
    passing = [k for k in TESTS if not cost[k]["excluded"]]
    res["cost_pass"] = passing
    rng = np.random.default_rng(SEED)
    # (2) controls first
    ctrl = {}
    for k, p in CONTROLS.items():
        m = measure(k, h6_returns(p), rng)
        m["screen_pass"] = bool(m["TP_lo95_onesided"] > 1 and m["years_VR12_gt1"] >= 4)
        ctrl[k] = m
    res["controls"] = ctrl
    if not all(m["screen_pass"] for m in ctrl.values()):
        res["verdict"] = "INVALID_METRIC_CONTROL_FAIL"; res["tests"] = "NOT_COMPUTED"
    elif not passing:
        res["verdict"] = "NO_INSTRUMENT_PASSES_COST"; res["tests"] = "NOT_COMPUTED"
    else:
        tests = {k: measure(k, h6_returns(TESTS[k]["path"]), rng) for k in passing}
        # Holm across cost-passing test instruments on bootstrap p-values
        order = sorted(passing, key=lambda k: tests[k]["p_boot_TP_le_1"]); m = len(order); stop = False
        for i, k in enumerate(order):
            thr = ALPHA / (m - i); rej = (not stop) and tests[k]["p_boot_TP_le_1"] <= thr
            if not rej: stop = True
            tests[k]["holm_threshold"] = thr; tests[k]["holm_reject"] = bool(rej)
        for k in passing:
            t = tests[k]; t["screen_pass"] = bool(t["holm_reject"] and t["years_VR12_gt1"] >= 4)
        res["tests"] = tests
        res["passers"] = [k for k in passing if tests[k]["screen_pass"]]
        res["verdict"] = "PASSERS_FOUND" if res["passers"] else "ZERO_PASS"
    json.dump(res, open("/workspace/t410/RESULTS_t410.json", "w"), indent=2, default=float)
    print(json.dumps(res, indent=1, default=float)[:6000])

if __name__ == "__main__":
    main()
