"""Fleet deep baskets vs scheduled US news, and BD's own news pause (docs/NEWS_PAUSE_PLAN.md, registered 21.10.2026)."""
import json, os
import numpy as np, pandas as pd

DIRS = {"1": "data/derived/bd1_rescue", "2": "data/derived/fleet/bd2", "3": "data/derived/fleet/bd3",
        "5": "data/derived/fleet/bd5", "6": "data/derived/fleet/bd6", "8": "data/derived/fleet/bd8"}
NFP = "2026-01-09 2026-02-11 2026-03-06 2026-04-03 2026-05-08 2026-06-05 2026-07-02 2026-08-07 2026-09-04 2026-10-02"
CPI = "2026-01-13 2026-02-13 2026-03-11 2026-04-10 2026-05-12 2026-06-10 2026-07-14 2026-08-12 2026-09-11 2026-10-14"
FOMC = "2026-01-28 2026-03-18 2026-04-29 2026-06-17 2026-07-29 2026-09-16"
EV = sorted([pd.Timestamp(d + " 15:30").timestamp() for d in (NFP + " " + CPI).split()] +
            [pd.Timestamp(d + " 21:00").timestamp() for d in FOMC.split()])
EV = np.array(EV); T0, T1 = pd.Timestamp("2026-01-01").timestamp(), pd.Timestamp("2026-10-17").timestamp()


def near(o):
    mt = o.mae_t.values
    a = np.searchsorted(EV, mt + 3600)                        # first event after mae_t - (-1h) ...
    by_mae = np.zeros(len(o), bool)
    for i, t in enumerate(mt):
        k = np.searchsorted(EV, t - 6 * 3600)                 # events in [t-6h, t+1h]
        by_mae[i] = k < len(EV) and EV[k] <= t + 3600
    k0 = np.searchsorted(EV, o.t0.values); open_at = (k0 < len(EV)) & (EV[np.minimum(k0, len(EV) - 1)] <= o.t1.values)
    return by_mae | open_at


res = {"accounts": {}}
saved = lost = 0.0; ok = 0
for k, d in DIRS.items():
    o = pd.read_csv(os.path.join(d, "clusters_strict.csv")).sort_values("t0")
    o = o[(o.t0 >= T0) & (o.t1 <= T1)].reset_index(drop=True)
    nn = near(o); deep = o.mae_pct <= -10
    k0 = np.searchsorted(EV, o.t0.values - 3600)
    blocked = (k0 < len(EV)) & (np.abs(EV[np.minimum(k0, len(EV) - 1)] - o.t0.values) <= 3600)
    x_all = float(np.prod(1 + o.pnl_pct / 100)); x_rule = float(np.prod(1 + o.pnl_pct[~blocked] / 100))
    b = o[blocked]
    s, l = float(-b.pnl_pct[b.pnl_pct < 0].sum()), float(b.pnl_pct[b.pnl_pct > 0].sum())
    saved += s; lost += l; ok += x_rule >= x_all
    res["accounts"][k] = dict(baskets=len(o), deep=int(deep.sum()), deep_near_news=int((deep & nn).sum()),
                              share_all_near_news=round(float(nn.mean()), 3),
                              share_deep_near_news=round(float(nn[deep].mean()), 3) if deep.any() else None,
                              blocked=int(blocked.sum()), blocked_deep=int((blocked & deep).sum()),
                              x_actual=round(x_all, 3), x_rule=round(x_rule, 3), saved_pct=round(s, 2), lost_pct=round(l, 2))
    print(k, res["accounts"][k])
res["fleet"] = dict(saved_pct_sum=round(saved, 2), lost_pct_sum=round(lost, 2), accounts_not_worse=ok,
                    passes=bool(saved > lost and ok >= 4))
print(res["fleet"])
json.dump(res, open("docs/evidence/news_pause.json", "w"), indent=1)
