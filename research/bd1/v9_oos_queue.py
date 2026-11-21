"""v9 vs the frozen d24ntop on three RoboForex years never used for any decision: 2019, 2020, 2021 (user request 29.10.2026,
pre-registered in docs/BD_REGIME2_PLAN.md before the runs). Same jobs as the 2022-2025 rounds: real ticks, 120K deposit,
0.01 lot per 6000, floor guard 15%/14 days from the start of each year, Thu+Fri off, top-news pause (news_top_rf.txt, now from 12/2018).
Usage: python research/bd1/v9_oos_queue.py -> research/bd1/q_v9_oos.json"""
import json

YEARS = [("rf2019", "2019.01.02", "2020.01.01", "20190101"), ("rf2020", "2020.01.02", "2021.01.01", "20200101"),
         ("rf2021", "2021.01.04", "2022.01.01", "20210101")]

def job(p, f, t, ff, v9):
    o = {"Autolot_": "true", "Autolotsize_": "6000", "G_FloorPct": "15", "G_FloorDays": "14", "P_At": "0", "G_FloorFrom": ff,
         "DayOffMask": "24", "NewsFile": "news_top_rf.txt"}
    if v9: o["RegimeRangePct"] = "2.0"
    return {"name": "Black Dragon 3", "symbol": "XAUUSD", "period": "M15", "deposit": 120000, "leverage": 1000,
            "base_set": "dcv9_2d.set" if v9 else "dcv7_2d.set", "from": f, "to": t,
            "expert": r"Jev\DragonClone_v9.ex5" if v9 else r"Jev\DragonClone_v7.ex5",
            "report": f"v9_{p}_reg20" if v9 else f"v7_{p}_d24ntop", "overrides": o}

if __name__ == "__main__":
    q = [job(*y, v9) for y in YEARS for v9 in (True, False)]
    json.dump(q, open("research/bd1/q_v9_oos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(q), "jobs")
