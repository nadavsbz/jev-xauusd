"""Execution-delay experiment (docs/MGMT_LAYER_PLAN.md, registered 21.10.2026): closing stats of
bd_cal_full vs the two delay runs, and the worst basket float on 21.4 and 28.5 (% of balance).
Simple basket = one side, 1-3 positions, all closed at the same second, in profit.
Usage: python research/bd1/delay_check.py RATES_DIR REPORT.htm [REPORT.htm ...]"""
import os, sys, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guardian_sim as g  # noqa: E402
from vol_lot_map import baskets  # noqa: E402

bars = pd.read_csv(os.path.join(sys.argv[1], "bars.csv"))
bt = bars.time.to_numpy(); lo = bars.low.to_numpy(); hi = bars.high.to_numpy()
out = {}
for rep in sys.argv[2:]:
    d = g.deals(rep); pos, _ = g.pair(d); pos = baskets(pos)
    bal = d[["t", "balance"]].dropna()
    st = {}
    simple = []
    for b, x in pos.groupby("basket"):
        sgn = 1 if x.side.iloc[0] == "buy" else -1
        if len(x) <= 3 and x.t1.nunique() == 1 and x.net.sum() > 0:
            avg = (x.vol * x.p0).sum() / x.vol.sum()
            simple.append(dict(n=len(x), gain=sgn * (x.p1.iloc[0] - avg), hold=(x.t1.iloc[0] - x.t0.min()) / 60))
    s = pd.DataFrame(simple)
    one = s[s.n == 1]
    st["median_gain_1"] = round(float(one.gain.median()), 3)
    st["median_hold_1_min"] = round(float(one.hold.median()), 2)
    st["n3_closed_together"] = int((s.n == 3).sum())
    # worst floating basket loss per day, % of the balance before the basket opened
    worst = {}
    for b, x in pos.groupby("basket"):
        sgn = 1 if x.side.iloc[0] == "buy" else -1
        t0, t1 = x.t0.min(), x.t1.max()
        i0, i1 = np.searchsorted(bt, t0 - 59), np.searchsorted(bt, t1)
        if i1 <= i0:
            continue
        px = lo[i0:i1] if sgn == 1 else hi[i0:i1]
        fl = np.zeros(i1 - i0)
        for r in x.itertuples():
            act = (bt[i0:i1] >= r.t0 - 59) & (bt[i0:i1] < r.t1)
            fl += np.where(act, sgn * (px - r.p0) * g.K * r.vol, 0)
        b0 = bal[bal.t <= t0].balance
        b0 = float(b0.iloc[-1]) if len(b0) else float(bal.balance.iloc[0])
        k = int(np.argmin(fl)); day = str(pd.to_datetime(bt[i0 + k], unit="s").date())
        worst[day] = min(worst.get(day, 0), fl[k] / b0 * 100)
    st["worst_float_pct"] = {dd: round(worst.get(dd, 0), 1) for dd in ("2026-04-21", "2026-04-28", "2026-04-30", "2026-05-28")}
    st["days_below_15"] = sorted(k for k, v in worst.items() if v <= -15)
    out[os.path.basename(rep)] = st
print(json.dumps(out, indent=1, ensure_ascii=False))
json.dump(out, open("docs/evidence/bd_delay_check.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
