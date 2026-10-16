"""Month-by-month view of directional blocking, asked for by the user AFTER stage B ended in
NO-GO. Descriptive only: it shows every month, including Jun-Oct, for a few combinations, so it
is NOT the pre-registered test (docs/DIRECTION_BLOCK_PLAN.md) and is no evidence for a rule."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import direction_block as db  # noqa: E402

COMBOS = [None, (1, 1.0), (2, 0.5), (2, 0.3)]


def per_basket(h=None, x=None):
    o, p = db.o, db.p
    blocked = np.zeros(len(p), bool) if h is None else (db.move_pct(h) * p.sgn.values <= -x)
    q = p.assign(blk=blocked); keep = q[~q.blk]
    r, tr, rb, ru = [a.copy() / 100 for a in (o.pnl_pct.values, o.mae_pct.values, o.runup_before_pct.values, o.runup_pct.values)]
    for c in set(q.cid[q.blk]):
        g = keep[keep.cid == c]; k = int(np.where(o.cid.values == c)[0][0])
        r[k], tr[k], rb[k], ru[k] = (0.0, 0.0, 0.0, 0.0) if len(g) == 0 else db.reprice(g, o.bal0.values[k])
    return r, tr, rb, ru


month = pd.to_datetime(db.o.t0, unit="s").dt.to_period("M").values
cols = {}
for c in COMBOS:
    r, tr, rb, ru = per_basket(*(c or (None, None)))
    name = "actual" if c is None else f"H{c[0]} X{c[1]}"
    rows = {}
    for m in sorted(set(month)):
        s = month == m
        eq, dd = db.max_drawdown(r[s], tr[s], rb[s], ru[s])
        rows[str(m)] = f"{(eq[-1] - 1) * 100:+.0f}% / {dd:.0f}%"
    eq, dd = db.max_drawdown(r, tr, rb, ru)
    rows["all"] = f"x{eq[-1]:.2f} / {dd:.0f}%"
    cols[name] = rows
print(pd.DataFrame(cols).to_string())
