"""Fleet sentinel (docs/NEWS_PAUSE_PLAN.md stage 2, registered 21.10.2026): once any basket in the fleet is at -5%,
no account opens a new basket on the same side for 12 hours."""
import json, os
import numpy as np, pandas as pd
DIRS = {"1": "data/derived/bd1_rescue", "2": "data/derived/fleet/bd2", "3": "data/derived/fleet/bd3",
        "5": "data/derived/fleet/bd5", "6": "data/derived/fleet/bd6", "8": "data/derived/fleet/bd8"}
T0, T1 = pd.Timestamp("2026-01-01").timestamp(), pd.Timestamp("2026-10-17").timestamp()   # as news_pause.py

ALERT, HOLD = -5.0, 12 * 3600
acc, alerts = {}, []
for k, d in DIRS.items():
    o = pd.read_csv(os.path.join(d, "clusters_strict.csv")).sort_values("t0")
    o = o[(o.t0 >= T0) & (o.t1 <= T1)].reset_index(drop=True); acc[k] = o
    P = dict(np.load(os.path.join(d, "paths_strict.npz")))
    for r in o.itertuples():
        a = P.get(str(r.cid))
        if a is None:
            continue
        a = a[a[:, 0] + 60 <= r.t1]; j = np.where(a[:, 1] <= ALERT)[0]
        if len(j):
            alerts.append((a[j[0], 0], r.side))
alerts = sorted(alerts)
res = {"alerts": len(alerts), "accounts": {}}; saved = lost = 0.0; ok = 0
for k, o in acc.items():
    blk = np.zeros(len(o), bool)
    for t, s in alerts:
        blk |= (o.side.values == s) & (o.t0.values > t) & (o.t0.values <= t + HOLD)
    xa, xr = float(np.prod(1 + o.pnl_pct / 100)), float(np.prod(1 + o.pnl_pct[~blk] / 100))
    b = o[blk]; s_, l_ = float(-b.pnl_pct[b.pnl_pct < 0].sum()), float(b.pnl_pct[b.pnl_pct > 0].sum())
    saved += s_; lost += l_; ok += xr >= xa
    res["accounts"][k] = dict(baskets=len(o), blocked=int(blk.sum()), blocked_deep=int((blk & (o.mae_pct <= -10)).sum()),
                              deep=int((o.mae_pct <= -10).sum()), x_actual=round(xa, 3), x_rule=round(xr, 3),
                              saved_pct=round(s_, 2), lost_pct=round(l_, 2))
    print(k, res["accounts"][k])
res["fleet"] = dict(saved=round(saved, 2), lost=round(lost, 2), accounts_not_worse=ok, passes=bool(saved > lost and ok >= 4))
print(res["alerts"], res["fleet"])
json.dump(res, open("docs/evidence/fleet_sentinel.json", "w"), indent=1)
