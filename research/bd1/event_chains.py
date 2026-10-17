"""Do the deepest Black Dragon chains start on scheduled-event days? (docs/BD_TIME_FILTER_PLAN.md; descriptive)
Calibrated tester run: chains as in vol_lot_map.baskets; an event day = the server day (Europe/Berlin clock,
as account 1's server, VERIFIED) of an NFP or FOMC release in docs/evidence/events_actual_nfp.csv.
Usage: python research/bd1/event_chains.py REPORT.htm"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guardian_sim as g  # noqa: E402
from vol_lot_map import baskets  # noqa: E402

ev = pd.read_csv("docs/evidence/events_actual_nfp.csv")
ev_day = set(pd.to_datetime(ev.utc).dt.tz_localize("UTC").dt.tz_convert("Europe/Berlin").dt.tz_localize(None).dt.normalize())
pos, _ = g.pair(g.deals(sys.argv[1])); pos = baskets(pos)
ch = pos.groupby("basket").agg(t0=("t0", "min"), t1=("t1", "max"), levels=("t0", "size"), maxlot=("vol", "max"))
ch["day"] = pd.to_datetime(ch.t0, unit="s").dt.normalize()
# a chain "touches" an event day if any day between its first entry and its last exit is an event day
ch["touch"] = [any(d in ev_day for d in pd.date_range(a, pd.to_datetime(b, unit="s").normalize()))
               for a, b in zip(ch.day, ch.t1)]
days = ch.day.nunique(); evd = ch[ch.day.isin(ev_day)].day.nunique()
for name, m in (("all chains", ch.levels >= 1), ("10+ levels", ch.levels >= 10), ("max lot >= 1.0", ch.maxlot >= 1.0)):
    sub = ch[m]
    print(f"{name}: {len(sub)} | start on an event day {int(sub.day.isin(ev_day).sum())} | touch an event day {int(sub.touch.sum())}")
print(f"event days among trading days: {evd} of {days} ({evd / days:.1%})")
