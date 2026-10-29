"""'Profitable every year' round 1 (docs/BD_EVERYYEAR_PLAN.md, pre-registered 29.10.2026). Diagnosis (research/bd1/oos_diag.py):
on RoboForex 2019-2025 the frozen d24ntop is positive only in 2024 and 2025; its normal closes earn +46%..+200% of the deposit a
year, and 5-16 floor cuts of ~15% a year take it all back. Round 1: settings that should make the grid reach the floor less often
(less money per point, fewer or wider levels, a softer martingale) and the floor level itself, one at a time, on all 7 RF years.
EGlobal 12/2025-10/2026 is NOT run in this round (holdout, with the demo).
Round 2: logic flags already in the code (D1 EMA context, basket stop, crash pause, one side at a time).
Usage: python research/bd1/everyyear_queue.py [ROUND=1] -> research/bd1/q_every<ROUND>.json"""
import sys
import json

YEARS = [(y, f"{y}.01.0{2 if y != 2021 else 4}", f"{y + 1}.01.01" if y < 2025 else "2025.10.24", f"{y}0101") for y in range(2019, 2026)]
YEARS = [(y, "2022.01.03" if y == 2022 else f, t, ff) for y, f, t, ff in YEARS]
CFG = {
    "alot12k": {"Autolotsize_": "12000"},
    "alot24k": {"Autolotsize_": "24000"},
    "maxo7": {"MaxOrdersBuy": "7", "MaxOrdersSell": "7"},
    "mart13": {"Martin_": "1.3"},
    "dist15": {"Fix_Distance": "450", "Dynamic_distance_start": "300"},
    "dist2": {"Fix_Distance": "600", "Dynamic_distance_start": "400"},
    "wideall": {"iTS": "90", "Fix_Distance": "350", "Dynamic_distance_start": "150", "Distance_multiplier": "1.0"},
    "floor8": {"G_FloorPct": "8"},
    "floor25": {"G_FloorPct": "25"},
    "alot12k_maxo7": {"Autolotsize_": "12000", "MaxOrdersBuy": "7", "MaxOrdersSell": "7"},
}

CFG2 = {
    "ctx20": {"G_Context": "true", "G_ContextEma": "20"},
    "ctx50": {"G_Context": "true", "G_ContextEma": "50"},
    "ctx200": {"G_Context": "true", "G_ContextEma": "200"},
    "bstop5": {"G_BasketStopPct": "5"},
    "bstop8": {"G_BasketStopPct": "8"},
    "crash": {"G_Crash": "true"},
    "nohedge": {"Flag_Use_hedge": "false"},
    "ctx50_alot24k": {"G_Context": "true", "G_ContextEma": "50", "Autolotsize_": "24000"},
}

def job(y, f, t, ff, tag, extra, r="1"):
    o = {"Autolot_": "true", "Autolotsize_": "6000", "G_FloorPct": "15", "G_FloorDays": "14", "P_At": "0", "G_FloorFrom": ff,
         "DayOffMask": "24", "NewsFile": "news_top_rf.txt", **extra}
    return {"name": "Black Dragon 3", "symbol": "XAUUSD", "period": "M15", "deposit": 120000, "leverage": 1000,
            "base_set": "dcv7_2d.set", "from": f, "to": t, "expert": r"Jev\DragonClone_v7.ex5",
            "report": f"ev{r}_rf{y}_{tag}", "overrides": o}

if __name__ == "__main__":
    r = sys.argv[1] if len(sys.argv) > 1 else "1"
    q = [job(*yr, tag, o, r) for tag, o in {"1": CFG, "2": CFG2}[r].items() for yr in YEARS]
    json.dump(q, open(f"research/bd1/q_every{r}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(q), "jobs", [(j["report"], j["from"], j["to"]) for j in q[:7]])
