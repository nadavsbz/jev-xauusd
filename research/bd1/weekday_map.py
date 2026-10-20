"""Day-of-week map of Black Dragon chains (docs/BD_TIME_FILTER_PLAN.md, part 2; descriptive, no selection):
on the calibrated tester run, each chain (one side, from the first entry while that side is flat until it is
flat again) is grouped by the weekday of its first entry (server day): number of chains, net, worst chain,
and how many reached 10 levels or more.
Usage: python research/bd1/weekday_map.py REPORT.htm OUT_CSV"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guardian_sim as g  # noqa: E402
from vol_lot_map import baskets  # noqa: E402

pos, _ = g.pair(g.deals(sys.argv[1])); pos = baskets(pos)
ch = pos.groupby("basket").agg(t0=("t0", "min"), net=("net", "sum"), levels=("t0", "size"), maxlot=("vol", "max"))
ch["weekday"] = pd.to_datetime(ch.t0, unit="s").dt.day_name()
out = ch.groupby("weekday").agg(chains=("net", "size"), net=("net", "sum"), worst=("net", "min"),
                                deep10=("levels", lambda x: int((x >= 10).sum())), maxlot=("maxlot", "max"))
out = out.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]).round(0)
print(out.to_string()); out.to_csv(sys.argv[2])
