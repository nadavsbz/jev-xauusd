"""Queue for the trading-hours test (docs/CRASH_LINK_PLAN.md): DragonClone_v6day, new baskets only inside a server-time window,
RoboForex real ticks 2019-2025, same settings as research/bd1/q_thu_oos.json.
No argument: the pre-registered window 12-18 into q_hours.json. 'control': the equal-length windows 2-8, 6-12, 15-21 and a
v6day all-hours 2022 run (must equal lr3_rf2022_6k) into q_hours_ctl.json."""
import json, sys
Y = (("2019", "2019.01.02", "2020.01.01"), ("2020", "2020.01.02", "2021.01.01"), ("2021", "2021.01.04", "2022.01.01"),
     ("2022", "2022.01.03", "2023.01.01"), ("2023", "2023.01.02", "2024.01.01"), ("2024", "2024.01.02", "2025.01.01"),
     ("2025", "2025.01.02", "2025.10.24"))
def job(y, f, t, a, b):
    return {"name": "Black Dragon 3", "symbol": "XAUUSD", "period": "M15", "deposit": 120000, "leverage": 1000, "base_set": "dcv5_2d.set",
            "from": f, "to": t, "expert": r"Jev\DragonClone_v6day.ex5", "report": f"d6h_rf{y}_h{a}_{b}",
            "overrides": {"Autolot_": "true", "Autolotsize_": "6000", "G_FloorPct": "15", "G_FloorDays": "14", "G_FloorFrom": y + "0101",
                          "P_At": "0", "DayOffMask": "0", "Start_Hour": str(a), "End_Hour": str(b)}}
if len(sys.argv) < 2:
    json.dump([job(y, f, t, 12, 18) for y, f, t in Y], open("research/bd1/q_hours.json", "w"), indent=1)
else:
    J = [job(*Y[3], 2, 21)] + [job(y, f, t, a, b) for a, b in ((2, 8), (6, 12), (15, 21)) for y, f, t in Y]
    json.dump(J, open("research/bd1/q_hours_ctl.json", "w"), indent=1)
