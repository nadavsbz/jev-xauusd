"""Queue for the out-of-sample Thursday test on RoboForex real ticks 2019-2021 (docs/CRASH_LINK_PLAN.md):
DragonClone_v6day with the user's guard, DayOffMask 0 / 8 / 24, same settings as research/bd1/q_dayoff.json.
With any argument: the control days Mon / Tue / Wed (1 / 2 / 4) into q_thu_placebo.json."""
import json, sys
MAIN = (("base", "0"), ("thu", "8"), ("thufri", "24")); PLACEBO = (("mon", "1"), ("tue", "2"), ("wed", "4"))
J = []
for y, f, t in (("2019", "2019.01.02", "2020.01.01"), ("2020", "2020.01.02", "2021.01.01"), ("2021", "2021.01.04", "2022.01.01")):
    for nm, m in (MAIN if len(sys.argv) < 2 else PLACEBO):
        J.append({"name": "Black Dragon 3", "symbol": "XAUUSD", "period": "M15", "deposit": 120000, "leverage": 1000,
                  "base_set": "dcv5_2d.set", "from": f, "to": t, "expert": r"Jev\DragonClone_v6day.ex5", "report": f"d6t_rf{y}_{nm}",
                  "overrides": {"Autolot_": "true", "Autolotsize_": "6000", "G_FloorPct": "15", "G_FloorDays": "14",
                                "G_FloorFrom": y + "0101", "P_At": "0", "DayOffMask": m}})
json.dump(J, open("research/bd1/q_thu_oos.json" if len(sys.argv) < 2 else "research/bd1/q_thu_placebo.json", "w"), indent=1)
