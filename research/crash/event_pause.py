"""Event pause on account 1 (docs/EVENT_PAUSE_PLAN.md): no new entry from 4 hours before a scheduled
NFP/FOMC release until the release. Uses direction_block.py's re-pricing. Run once.
Usage: python research/crash/event_pause.py EVENTS_CSV"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import direction_block as db  # noqa: E402

ev = pd.to_datetime(pd.read_csv(sys.argv[1]).utc).dt.tz_localize("UTC").dt.tz_convert("Europe/Berlin")
ev = np.sort(ev.dt.tz_localize(None).astype("int64").values // 10**9)       # account 1 server clock as epoch
t = db.p.time.values
k = np.searchsorted(ev, t, side="left")                                    # first release at or after the entry
nxt = np.where(k < len(ev), ev[np.minimum(k, len(ev) - 1)], np.iinfo(np.int64).max)
blocked = (nxt - t) <= 4 * 3600
q = db.p.assign(blk=blocked); keep = q[~q.blk]
o = db.o
r, tr, rb, ru = [a.copy() / 100 for a in (o.pnl_pct.values, o.mae_pct.values, o.runup_before_pct.values, o.runup_pct.values)]
for c in set(q.cid[q.blk]):
    g = keep[keep.cid == c]; i = int(np.where(o.cid.values == c)[0][0])
    r[i], tr[i], rb[i], ru[i] = (0.0, 0.0, 0.0, 0.0) if len(g) == 0 else db.reprice(g, o.bal0.values[i])
base = db.run()[0]
for name, m in (("nov_may", o.t0.values < db.SPLIT), ("jun_oct", o.t0.values >= db.SPLIT)):
    eq, dd = db.max_drawdown(r[m], tr[m], rb[m], ru[m])
    print(f"{name}: actual x{base[name][0]} / {base[name][1]}% | with pause x{eq[-1]:.2f} / {dd:.1f}%")
print("blocked entries:", int(blocked.sum()), "in", len(set(q.cid[q.blk])), "baskets")
