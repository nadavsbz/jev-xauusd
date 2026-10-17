"""Stage 2 of docs/CRASH_DETECT_PLAN.md, run on the user's approval (descriptive only): account 1 opens
no new entry on a day whose S5 (GVZ percentile of the previous observation, stage-1 definition,
threshold 0.90) is flagged; the rest of each basket stays as it was (direction_block.py re-pricing).
Usage: python research/crash/stage2.py GVZCLS_CSV"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import direction_block as db  # noqa: E402

g = pd.read_csv(sys.argv[1], parse_dates=["observation_date"], na_values=".").set_index("observation_date").GVZCLS.dropna()
s5 = g.rolling(250, min_periods=125).rank(pct=True).shift(1)                      # stage1.py
# entry time: account 1 server clock (Central European) -> UTC calendar day
t_utc = (pd.to_datetime(db.p.time.values, unit="s").tz_localize("Europe/Berlin", ambiguous="NaT", nonexistent="shift_forward")
         .tz_convert("UTC").tz_localize(None).normalize())
flag_day = s5.reindex(pd.date_range(s5.index.min(), t_utc.max()), method="ffill") >= 0.90
blocked = flag_day.reindex(t_utc).fillna(False).values
q = db.p.assign(blk=blocked); keep = q[~q.blk]
o = db.o
r, tr, rb, ru = [a.copy() / 100 for a in (o.pnl_pct.values, o.mae_pct.values, o.runup_before_pct.values, o.runup_pct.values)]
for c in set(q.cid[q.blk]):
    gg = keep[keep.cid == c]; i = int(np.where(o.cid.values == c)[0][0])
    r[i], tr[i], rb[i], ru[i] = (0.0, 0.0, 0.0, 0.0) if len(gg) == 0 else db.reprice(gg, o.bal0.values[i])
base = db.run()[0]
deep = o.mae_pct.values <= -10
print("flagged days in the period:", int(flag_day[(flag_day.index >= "2025-11-11") & (flag_day.index <= "2026-10-14")].sum()))
print("blocked entries:", int(blocked.sum()), "of", len(blocked), "| deep baskets touched:", int(np.isin(o.cid.values[deep], list(set(q.cid[q.blk]))).sum()), "of", int(deep.sum()))
for name, m in (("nov_may", o.t0.values < db.SPLIT), ("jun_oct", o.t0.values >= db.SPLIT), ("all", np.ones(len(o), bool))):
    eq, dd = db.max_drawdown(r[m], tr[m], rb[m], ru[m])
    b = base.get(name) if name in base else None
    print(f"{name}: with S5 block x{eq[-1]:.2f} / {dd:.1f}%" + (f" | actual x{b[0]} / {b[1]}%" if b else ""))
