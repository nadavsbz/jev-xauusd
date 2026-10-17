"""Who realised the loss on account 1's crash days (docs/BD1_CRASH_CAUSE.md): exit deals of positions
opened by the robot (magic 5555), split by the exit deal's magic/reason, summed per server-time day.
Also the lot-to-balance ratio before each of the worst days.
Usage (snapshot through JEV_DEALS_SNAPSHOT): python research/bd1/crash_who_closed.py"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inputs import load, START, MAGIC  # noqa: E402

REASON = {0: "outside:desktop", 1: "outside:mobile", 2: "outside:web", 3: "outside:expert", 4: "outside:SL",
          6: "outside:stopout"}

d, _ = load()
d = d.sort_values("time").copy()
d["day"] = pd.to_datetime(d.time, unit="s").dt.normalize()
d["bal"] = (d.profit + d.commission + d.swap + d.fee).cumsum()
d = d[d.time >= START]
robot = set(d[(d.entry == 0) & (d.magic == MAGIC)].position_id)
x = d[(d.entry != 0) & d.position_id.isin(robot)].copy()
x["net"] = x.profit + x.commission + x.swap + x.fee
x["who"] = x.reason.map(REASON).fillna("outside:other").where(x.magic != MAGIC, "robot")
day = x.pivot_table(index="day", columns="who", values="net", aggfunc="sum", fill_value=0)
day["total"] = day.sum(axis=1)
worst = day.sort_values("total").head(10)
print(worst.round(0).to_string())
print("robot exits net:", round(x[x.magic == MAGIC].net.sum()), "| outside exits net:", round(x[x.magic != MAGIC].net.sum()))
print("days where the robot's own exits net < 0:", int((day.get("robot", 0) < 0).sum()))
e = d[(d.entry == 0) & (d.magic == MAGIC)]
for dd in worst[worst.total < -1000].index:
    prev = d[d.day < dd].bal.iloc[-1]; lot = e[e.day <= dd].tail(200).volume.min()
    print(dd.date(), "balance before", round(prev), "base lot", lot, "cents per 0.01:", round(prev / (lot / 0.01)))
worst.round(2).to_csv("docs/evidence/bd1_crash_days_who_closed.csv")
