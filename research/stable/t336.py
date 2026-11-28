"""t336 (docs/prereg/research_t336.md): fade an extreme 10-min US index open (|z|>=2 vs prior 252 days), 09:45->11:30 ET.
Usage: py -3.12 research/stable/t336.py density|dev|holdout"""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/stable")
from scan import tcost, E
from scan2 import mismatch
TD = pd.Timedelta

def opens(s):
    m = pd.read_csv(f"data/derived/scan/m5/{s}.csv"); m.index = pd.to_datetime(m.time, unit="s"); m = m[~m.index.duplicated()]
    tc = tcost(s, m.resample("1h").last().dropna()); pt = E.loc["." + s, "point"]
    P = m.open; S = (m.spread * pt / m.open)
    rows = []
    for d in sorted(set(m.index.normalize())):
        if d.dayofweek > 4: continue
        O = d + TD(hours=10) if s == "DE40Cash" else d + TD(hours=9 + (6 if mismatch(d) else 7), minutes=30)
        t = [O, O + TD(minutes=10), O + TD(minutes=15), O + TD(hours=2)]
        if not all(x in P.index for x in t): continue
        rows.append(dict(d=d, r=P[t[1]] / P[t[0]] - 1, g=P[t[3]] / P[t[2]] - 1, c=max(tc, S[t[2]]) + max(tc, S[t[3]])))
    D = pd.DataFrame(rows).set_index("d")
    mu = D.r.rolling(252).mean().shift(1); sd = D.r.rolling(252).std().shift(1)
    D["z"] = (D.r - mu) / sd
    D["sig"] = np.where(D.z >= 2, -1, np.where(D.z <= -2, 1, 0))
    return D

def evaluate(D, lo, hi, cmul=1.0):
    X = D[lo:hi]; T = X[X.sig != 0]
    net = T.sig * T.g - T.c * cmul
    yr = net.groupby(net.index.year).sum()
    return dict(n=int(len(T)), per_year=T.groupby(T.index.year).size().to_dict(),
                mean_bp=round(float(net.mean() * 1e4), 2), t=round(float(net.mean() / net.std() * np.sqrt(len(net))), 2) if len(net) > 1 else None,
                net_sum_pct=round(float(net.sum() * 100), 2), cost_sum_pct=round(float((T.c * cmul).sum() * 100), 2),
                by_year_pct=(yr * 100).round(2).to_dict(), pos_years=f"{int((yr > 0).sum())}/{len(yr)}"), net

if __name__ == "__main__":
    part = sys.argv[1]
    if part == "density":
        for s in ("US500Cash", "USTECHCash", "US30Cash", "DE40Cash"):
            D = opens(s); print(s, D.groupby(D.index.year).size().to_dict())
        sys.exit()
    lo, hi = ("2018-01-01", "2022-12-31") if part == "dev" else ("2023-01-01", "2026-11-20")
    out = {}
    D = opens("US500Cash")
    out["US500_base"], net = evaluate(D, lo, hi)
    out["US500_2x_cost"], _ = evaluate(D, lo, hi, 2.0)
    try:
        from book_tester import i2_daily
        i2 = i2_daily(); x = net.groupby(net.index.normalize()).sum()
        out["corr_I2_trade_days"] = round(float(x.corr(i2.reindex(x.index).fillna(0))), 2)
        c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.resample("D").last().pct_change()
        out["corr_C1_trade_days"] = round(float(x.corr(c1.reindex(x.index))), 2)
    except Exception as e:
        out["corr_err"] = str(e)[:100]
    for s in ("USTECHCash", "US30Cash", "DE40Cash"):
        out[s + "_info_only"], _ = evaluate(opens(s), lo, hi)
    print(json.dumps(out, indent=1, ensure_ascii=False, default=str))
