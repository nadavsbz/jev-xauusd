"""Replay the user's real guard levels (manual_report, local schedule data/derived/fleet/guard_schedule.json) on each
account's real baskets at the real lot: does the basket model reproduce the real result? (docs/FLEET_LOTGUARD_PLAN.md)
Window: first guard entry to 20.7.2026 (the report ends 16.7)."""
import json, sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fleet_lotguard import Acc, DIRS

SCHED = json.load(open("data/derived/fleet/guard_schedule.json", encoding="utf-8"))
END = pd.Timestamp("2026-07-20").timestamp()


def levels(sheet):
    rows = [(pd.to_datetime(d.replace(".206", ".2026"), dayfirst=True).timestamp(), lv) for d, lv in SCHED[sheet]]
    return sorted(rows)


def replay(acc, sched, slip=1.3, scale=1.0, widen=0.0):
    o = acc.o; base = np.fmin(np.where(np.isnan(acc.pmin), o.mae_pct.values, acc.pmin), o.mae_pct.values)
    ts = np.array([t for t, _ in sched]); lv = np.array([l for _, l in sched], float)
    m = (o.t0.values >= ts[0]) & (o.t1.values <= END)
    r_real = o.pnl_pct.values[m] / 100; r = []; trig = 0
    for i in np.where(m)[0]:
        L = lv[np.searchsorted(ts, o.t0[i], side="right") - 1]
        thr = (L / o.bal0[i] - 1) * 100 - widen                      # floating % of the balance that hits the level
        worst = scale * base[i]
        if o.guard[i] and o.cid[i] in acc.ag.index:
            worst = min(worst, scale * acc.ag.loc[o.cid[i]].worst_lower)
        if worst <= thr:
            r.append(slip * thr / 100); trig += 1
        elif o.guard[i] and o.cid[i] in acc.ag.index:
            g = acc.ag.loc[o.cid[i]]; r.append(0.0 if g.recovered else scale * g.worst_lower / 100)
        else:
            r.append(scale * o.pnl_pct[i] / 100)
    return dict(n=int(m.sum()), real_x=round(float(np.prod(1 + r_real)), 3), model_x=round(float(np.prod(1 + np.array(r))), 3),
                real_guards=int(o.guard.values[m].sum()), model_trig=trig)


if __name__ == "__main__":
    out = {}
    for k, sheet in [("1", "#1"), ("2", "#2"), ("3", "#3"), ("5", "#5"), ("6", "#6"), ("8", "#8")]:
        a = Acc(DIRS[k]); out[k] = replay(a, levels(sheet)); print(k, out[k])
    json.dump(out, open("docs/evidence/fleet_guard_replay.json", "w"), indent=1)
