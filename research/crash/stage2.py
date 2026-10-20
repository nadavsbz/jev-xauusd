"""Stage 2 of docs/CRASH_DETECT_PLAN.md, run on the user's approval (descriptive only): account 1 opens
no new entry on a day whose S5 (GVZ percentile of the previous observation, stage-1 definition,
threshold 0.90) is flagged; the rest of each basket stays as it was (direction_block.py re-pricing).
Usage: python research/crash/stage2.py GVZCLS_CSV"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import direction_block as db  # noqa: E402

g = pd.read_csv(sys.argv[1], parse_dates=["observation_date"], na_values=".").set_index("observation_date").GVZCLS.dropna()
import gvz_pub  # noqa: E402
pub = gvz_pub.published(gvz_pub.percentile(g))
# entry time: account 1 server clock (Central European) -> UTC; each entry gets the S5 value already
# published at that moment (review: same timing as stage1.py)
t_utc = (pd.to_datetime(db.p.time.values, unit="s").tz_localize("Europe/Berlin", ambiguous="NaT", nonexistent="shift_forward")
         .tz_convert("UTC").tz_localize(None))
v, _ = gvz_pub.at(t_utc, pub)
blocked = np.nan_to_num(v, nan=0.0) >= 0.90
flag_day = pd.Series(pub.values >= 0.90, index=pub.index.normalize())
# the rule blocks OPENING a basket (review PR #28): decided at each basket's first entry, the whole basket
# is kept or removed; levels added to an open basket after a flag stay
q = db.p.assign(blk=blocked)
first_blk = q.sort_values("time").groupby("cid").blk.first()
q["blk"] = q.cid.map(first_blk).values; blocked = q.blk.values; keep = q[~q.blk]
o = db.o
r, tr, rb, ru = [a.copy() / 100 for a in (o.pnl_pct.values, o.mae_pct.values, o.runup_before_pct.values, o.runup_pct.values)]
for c in set(q.cid[q.blk]):
    gg = keep[keep.cid == c]; i = int(np.where(o.cid.values == c)[0][0])
    r[i], tr[i], rb[i], ru[i] = (0.0, 0.0, 0.0, 0.0) if len(gg) == 0 else db.reprice(gg, o.bal0.values[i])
base = db.run()[0]
deep = o.mae_pct.values <= -10
print("flagged days in the period:", int(flag_day[(flag_day.index >= "2025-11-11") & (flag_day.index <= "2026-10-14")].sum()))
print("blocked baskets:", int(first_blk.sum()), "of", len(first_blk), "| their entries:", int(blocked.sum()), "of", len(blocked), "| deep baskets touched:", int(np.isin(o.cid.values[deep], list(set(q.cid[q.blk]))).sum()), "of", int(deep.sum()))
for name, m in (("nov_may", o.t0.values < db.SPLIT), ("jun_oct", o.t0.values >= db.SPLIT), ("all", np.ones(len(o), bool))):
    eq, dd = db.max_drawdown(r[m], tr[m], rb[m], ru[m])
    b = base.get(name) if name in base else None
    print(f"{name}: with S5 block x{eq[-1]:.2f} / {dd:.1f}%" + (f" | actual x{b[0]} / {b[1]}%" if b else ""))
