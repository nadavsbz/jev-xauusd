"""Lars set on the original EA Black Dragon (docs/CRASH_LINK_PLAN.md, pre-registration 7.11.2026).
The user's account-1 set (bots/bd/bd.set, git-ignored, from Lars) is written for 3-digit gold; RoboForex in the tester is
2-digit, so every distance in points is divided by 10 (the same scaling as frozen/bd_v7_d24ntop_20261026/bd_v7_d24ntop_robo.set).
Sizing: Autolot 0.01 per 6,000 of balance on a 50,000 deposit, as in the earlier every-year rounds, so results are comparable.
One switch per variant, 7 years each 2019-2025 on RoboForex real ticks, M15. Writes lars_2d.set into the tester's
Profiles\\Tester and research/bd1/q_lars.json for tools/run_queue.py.
Usage: python research/bd1/mk_lars.py"""
import json, os, re

SRC = os.path.join("bots", "bd", "bd.set")
SETS = r"C:\MT5_JEV_TEST\MQL5\Profiles\Tester"
SCALE = ("MaxSpred", "TP_", "iTS", "iTD", "Fix_Distance", "Dynamic_distance_start")
Y = (("2019", "2019.01.02", "2020.01.01"), ("2020", "2020.01.02", "2021.01.01"), ("2021", "2021.01.04", "2022.01.01"),
     ("2022", "2022.01.03", "2023.01.01"), ("2023", "2023.01.02", "2024.01.01"), ("2024", "2024.01.02", "2025.01.01"),
     ("2025", "2025.01.02", "2025.10.24"))
V = {"base": {},
     "m135": {"Martin_": "1.35"},
     "nc0": {"NewCycle_": "false"},
     "mo8": {"MaxOrdersBuy": "8", "MaxOrdersSell": "8"},
     "a12k": {"Autolotsize_": "12000"}}

b = open(SRC, "rb").read()
t = b.decode("utf-16") if b[:2] in (b"\xff\xfe", b"\xfe\xff") else b.decode("utf-8-sig")
def fix(m):
    k, v = m.group(1), m.group(2)
    if k in SCALE: v = str(int(float(v)) // 10)
    if k == "Autolot_": v = "true"
    if k == "Autolotsize_": v = "6000"
    if k == "Lot_Init_": v = "0.01"
    return f"{k}={v}"
t = re.sub(r"(?m)^([A-Za-z_]\w*)=([^|\r\n]*)", fix, t)
open(os.path.join(SETS, "lars_2d.set"), "wb").write(b"\xff\xfe" + t.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-16-le"))

J = [{"name": "Black Dragon 3", "symbol": "XAUUSD", "period": "M15", "deposit": 50000, "leverage": 1000,
      "base_set": "lars_2d.set", "from": f, "to": to, "expert": r"BD\EA Black Dragon.ex5",
      "report": f"lars_{v}_{y}", "overrides": o} for v, o in V.items() for y, f, to in Y]
json.dump(J, open("research/bd1/q_lars.json", "w"), indent=1)
print(len(J), "runs")
