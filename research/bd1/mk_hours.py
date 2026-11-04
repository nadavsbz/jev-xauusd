"""Queue for the trading-hours test (docs/CRASH_LINK_PLAN.md): DragonClone_v6day, new baskets only 12:00-17:59 server time,
RoboForex real ticks 2019-2025, same settings as research/bd1/q_thu_oos.json."""
import json
Y = (("2019", "2019.01.02", "2020.01.01"), ("2020", "2020.01.02", "2021.01.01"), ("2021", "2021.01.04", "2022.01.01"),
     ("2022", "2022.01.03", "2023.01.01"), ("2023", "2023.01.02", "2024.01.01"), ("2024", "2024.01.02", "2025.01.01"),
     ("2025", "2025.01.02", "2025.10.24"))
J = [{"name": "Black Dragon 3", "symbol": "XAUUSD", "period": "M15", "deposit": 120000, "leverage": 1000, "base_set": "dcv5_2d.set",
      "from": f, "to": t, "expert": r"Jev\DragonClone_v6day.ex5", "report": f"d6h_rf{y}_h12_18",
      "overrides": {"Autolot_": "true", "Autolotsize_": "6000", "G_FloorPct": "15", "G_FloorDays": "14", "G_FloorFrom": y + "0101",
                    "P_At": "0", "DayOffMask": "0", "Start_Hour": "12", "End_Hour": "18"}} for y, f, t in Y]
json.dump(J, open("research/bd1/q_hours.json", "w"), indent=1)
