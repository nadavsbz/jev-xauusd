"""BD + a small Trend Catcher weight, realised daily P&L of existing tester runs (docs/PORTFOLIO_BD_TC_PLAN.md)."""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
from guardian_sim import deals

T = "C:/MT5_JEV_TEST/"
PERIODS = {"y2022": ("bdanti_2022_orig", "tc_y2022"), "sel24": ("bd_robo_orig_bigdep", "tc_sel24"), "acc1": ("bd_cal_full", "tc_acc1")}
CAP, WS = 8000.0, (0, 0.1, 0.2, 0.3, 0.5)


def daily(rep):
    d = deals(T + rep + ".htm"); d = d[d.dir != ""]
    v = d.profit.fillna(0) + d.commission.fillna(0) + d.swap.fillna(0)
    s = v.groupby(pd.to_datetime(d.t, unit="s").dt.normalize()).sum()
    lot0 = d.volume[d.dir == "in"].min()
    return s / (lot0 / 0.01), float(lot0)                        # P&L per 0.01 starting lot


res = {}
for p, (bd, tc) in PERIODS.items():
    b, lb = daily(bd); t, lt = daily(tc)
    idx = b.index.union(t.index); b = b.reindex(idx, fill_value=0); t = t.reindex(idx, fill_value=0)
    res[p] = {"bd_lot0": lb, "tc_lot0": lt}
    for w in WS:
        eq = CAP + (b + w * t).cumsum()
        dd = float((eq / eq.cummax() - 1).min()); res[p][str(w)] = dict(profit_pct=round(float(eq.iloc[-1] / CAP - 1) * 100, 1),
                                                                     max_dd_realised_pct=round(dd * 100, 1), min_eq_pct=round(float(eq.min() / CAP) * 100, 1))
    res[p]["corr_daily"] = round(float(np.corrcoef(b, t)[0, 1]), 3)
    print(p, json.dumps(res[p]))
base = {p: res[p]["0"] for p in res}
ok = [w for w in WS[1:] if all(res[p][str(w)]["max_dd_realised_pct"] > base[p]["max_dd_realised_pct"] and
                               res[p][str(w)]["profit_pct"] >= base[p]["profit_pct"] * 0.9 for p in res)]
res["passing"] = ok; res["chosen"] = min(ok) if ok else None
print("passing", ok)
json.dump(res, open("docs/evidence/portfolio_bd_tc.json", "w"), indent=1)
