"""Clone v13 (Use_Stoh implemented) against the original EA Black Dragon on the Lars set (docs/CRASH_LINK_PLAN.md, 7.11.2026).
The clone's set is dcv12_2d.set made equal to lars_2d.set (MaxSpred 20, Autolot 0.01 per 6000), floor guard, day mask and news off,
so the clone runs what the original ran in research/bd1/mk_lars.py. Two years (2021, 2020), 50,000 deposit, M15:
base (Use_Stoh off) against lars_base_*, and four readings of BD's Stochastic rule against lars_stoh_*:
StochRule 1 (EMA side AND stochastic edge) or 2 (stochastic edge alone) x StochBar 1 (closed bar) or 0 (opening bar).
The reading with the best same-bar basket match in 2021 is the one used later; 2020 checks it out of sample.
Usage: python research/bd1/mk_v13val.py"""
import json, os, re
S = r"C:\MT5_JEV_TEST\MQL5\Profiles\Tester"
t = open(os.path.join(S, "dcv12_2d.set"), "rb").read().decode("utf-16")
fix = {"MaxSpred": "20", "Autolot_": "true", "Autolotsize_": "6000", "Lot_Init_": "0.01", "G_FloorPct": "0", "DayOffMask": "0", "NewsFile": ""}
t = re.sub(r"(?m)^([A-Za-z_]\w*)=([^\r\n]*)", lambda m: f"{m.group(1)}={fix.get(m.group(1), m.group(2))}", t)
t = t.rstrip("\r\n") + "\r\nStochRule=1\r\nStochBar=1\r\n"
open(os.path.join(S, "dcv13_lars.set"), "wb").write(b"\xff\xfe" + t.encode("utf-16-le"))
ST = {"Use_Stoh": "true", "TF_Stoh": "0", "Up_Level": "80", "Down_Level": "20", "KPeriod": "7"}   # the lars_stoh overrides
V = {"base": {}, "r1b1": {**ST}, "r1b0": {**ST, "StochBar": "0"}, "r2b1": {**ST, "StochRule": "2"}, "r2b0": {**ST, "StochRule": "2", "StochBar": "0"}}
Y = (("2021", "2021.01.04", "2022.01.01"), ("2020", "2020.01.02", "2021.01.01"))
J = [{"name": "Black Dragon 3", "symbol": "XAUUSD", "period": "M15", "deposit": 50000, "leverage": 1000, "base_set": "dcv13_lars.set",
      "from": f, "to": to, "expert": r"Jev\DragonClone_v13.ex5", "report": f"v13val_{v}_{y}", "overrides": o} for y, f, to in Y for v, o in V.items()]
json.dump(J, open("research/bd1/q_v13val.json", "w"), indent=1)
print(len(J), "runs")
