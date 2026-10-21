"""Fleet sentinel (docs/NEWS_PAUSE_PLAN.md stage 2, registered 21.10.2026): once any basket in the fleet is at -5%,
no account opens a new basket on the same side for 12 hours.
v2 after the review of PR 36: (1) events are processed in time order and only baskets that were NOT blocked can
raise an alert; (2) a basket's side is the side of its FIRST entry (positions_strict.csv), not the union of sides;
(3) the alert is stamped at the END of the minute whose low/high crossed the level; (4) the result is measured in
money (each account compounds from its own starting balance), not by adding percentages of different balances."""
import json, os, sys
import numpy as np, pandas as pd

DIRS = {"1": "data/derived/bd1_rescue", "2": "data/derived/fleet/bd2", "3": "data/derived/fleet/bd3",
        "5": "data/derived/fleet/bd5", "6": "data/derived/fleet/bd6", "8": "data/derived/fleet/bd8"}
T0, T1 = pd.Timestamp("2026-01-01").timestamp(), pd.Timestamp("2026-10-17").timestamp()   # as news_pause.py
ALERT, HOLD = -5.0, 12 * 3600


def load():
    ev = []
    for k, d in DIRS.items():
        o = pd.read_csv(os.path.join(d, "clusters_strict.csv")).sort_values("t0")
        o = o[(o.t0 >= T0) & (o.t1 <= T1)].reset_index(drop=True)
        pos = pd.read_csv(os.path.join(d, "positions_strict.csv"))
        first = pos.sort_values("t0_msc").groupby("cid").sgn.first()
        o["side1"] = o.cid.map(first).fillna(0).astype(int)
        P = dict(np.load(os.path.join(d, "paths_strict.npz")))
        al = np.full(len(o), np.nan)
        for i, r in enumerate(o.itertuples()):
            a = P.get(str(r.cid))
            if a is None:
                continue
            a = a[a[:, 0] + 60 <= r.t1]; j = np.where(a[:, 1] <= ALERT)[0]
            if len(j):
                al[i] = a[j[0], 0] + 60                      # known at the end of that minute
        o["alert_t"] = al; o["acc"] = k
        ev.append(o)
    return pd.concat(ev, ignore_index=True)


def run(f, alert=ALERT, hold=HOLD):
    f = f.sort_values("t0").reset_index(drop=True)
    blocked = np.zeros(len(f), bool); live_alerts = []             # (time, side) of alerts from baskets that exist
    pending = []                                                   # alerts of open, non-blocked baskets, by time
    for i, r in enumerate(f.itertuples()):
        while pending and pending[0][0] <= r.t0:
            live_alerts.append(pending.pop(0))
        if any(s == r.side1 and t < r.t0 <= t + hold for t, s in live_alerts):
            blocked[i] = True; continue
        if not np.isnan(r.alert_t):
            pending.append((r.alert_t, r.side1)); pending.sort()
    f["blocked"] = blocked
    return f


if __name__ == "__main__":
    f = run(load()); res = {"accounts": {}}; ok = 0; tot_a = tot_r = 0.0
    for k, o in f.groupby("acc"):
        b0 = o.bal0.iloc[0] / 100
        xa, xr = float(np.prod(1 + o.pnl_pct / 100)), float(np.prod(1 + o.pnl_pct[~o.blocked] / 100))
        ok += xr >= xa; tot_a += b0 * (xa - 1); tot_r += b0 * (xr - 1)
        res["accounts"][k] = dict(baskets=len(o), blocked=int(o.blocked.sum()), x_actual=round(xa, 3), x_rule=round(xr, 3),
                                  gain_actual_usd=round(b0 * (xa - 1)), gain_rule_usd=round(b0 * (xr - 1)))
        print(k, res["accounts"][k])
    res["fleet"] = dict(gain_actual_usd=round(tot_a), gain_rule_usd=round(tot_r), accounts_not_worse=ok,
                        passes=bool(tot_r > tot_a and ok >= 4))
    print(res["fleet"])
    if "--sens" in sys.argv:
        f0 = load.__wrapped__ if hasattr(load, "__wrapped__") else None
    json.dump(res, open("docs/evidence/fleet_sentinel.json", "w"), indent=1)
