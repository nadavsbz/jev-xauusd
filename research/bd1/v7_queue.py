"""Queues of DragonClone_v7 on the 5 real-tick periods (docs/BD_V7_PLAN.md).
Same engine as the lot-ratio scan (lr3_*_6k): the user's floor guard, 0.01 per 6,000, deposit 120K.
Usage: python research/bd1/v7_queue.py ROUND  -> research/bd1/q_v7_<ROUND>.json"""
import json, sys

PERIODS = [("rf2022", "2022.01.03", "2023.01.01", "20220101"), ("rf2023", "2023.01.02", "2024.01.01", "20230101"),
           ("rf2024", "2024.01.02", "2025.01.01", "20240101"), ("rf2025", "2025.01.02", "2025.10.24", "20250101"),
           ("eg2526", "2025.12.01", "2026.10.24", None)]   # EGlobal: the guard from 3.4.2026, like account 1

def job(period, tag, extra):
    p, f, t, ff = next(x for x in PERIODS if x[0] == period)
    rf = p.startswith("rf")
    o = {"Autolot_": "true", "Autolotsize_": "6000", "G_FloorPct": "15", "G_FloorDays": "14", "P_At": "0"}
    if ff: o["G_FloorFrom"] = ff
    o.update({k: v.replace("{b}", "rf" if rf else "eg") for k, v in extra.items()})
    return {"name": "Black Dragon 3" if rf else "Black Dragon 1", "symbol": "XAUUSD" if rf else "XAUUSDc", "period": "M15",
            "deposit": 120000, "leverage": 1000, "base_set": "dcv7_2d.set" if rf else "dcv7_base.set", "from": f, "to": t,
            "expert": "Jev\\DragonClone_v7.ex5", "report": f"v7_{p}_{tag}", "overrides": o}

ROUNDS = {
 # round 1: sanity (all flags off = lr3_rf2022_6k), lot after Overlap (user, 30.7), lot cap scaled to the balance
 "r1": [("rf2022", "off", {})]
     + [(p[0], f"lao{m}", {"LotAfterOverlap": str(m)}) for m in (4, 3, 1) for p in PERIODS]
     + [(p[0], f"ml{k}", {"MaxLot_": "100", "MaxLotMult": str(k)}) for k in (6, 10, 15) for p in PERIODS]
     + [(p[0], "mlnone", {"MaxLot_": "100"}) for p in PERIODS],
 # round 1b: the v7 baseline on every period, and a determinism check (v7_rf2022_off came out -95.7K vs lr3_rf2022_6k -90.8K,
 # first different deal 10.1.2022 01:00): the same v7 run again, and the lr3 job (v5b) again
 "r1b": [("rf2022", "off2", {})] + [(p[0], "off", {}) for p in PERIODS[1:]],
 # round 2: days, scheduled news (MT5 calendar, broker clock), unscheduled moves (G_Crash), and the user's lot flag with days
 "r2": [(p[0], t, o) for t, o in [("day24", {"DayOffMask": "24"}),
                                  ("ntop", {"NewsFile": "news_top_{b}.txt"}),
                                  ("nhigh", {"NewsFile": "news_high_{b}.txt"}),
                                  ("ntopw", {"NewsFile": "news_top_{b}.txt", "NewsBeforeMin": "60", "NewsAfterMin": "240"}),
                                  ("crash", {"G_Crash": "true"}),
                                  ("d24lao4", {"DayOffMask": "24", "LotAfterOverlap": "4"}),
                                  ("d24ntop", {"DayOffMask": "24", "NewsFile": "news_top_{b}.txt"})] for p in PERIODS],
 # round 3 (robustness of day24, docs/BD_V7_PLAN.md): Thu+Fri came from earlier analysis of the same years, so every other
 # 2-day pair and Thu / Fri alone must NOT do as well if the effect is real; and day24 with the wide news window / G_Crash
 "r3": [(p[0], f"day{m}", {"DayOffMask": str(m)}) for m in (8, 16, 3, 5, 9, 17, 6, 10, 18, 12, 20) for p in PERIODS]
     + [(p[0], t, o) for t, o in [("d24ntopw", {"DayOffMask": "24", "NewsFile": "news_top_{b}.txt", "NewsBeforeMin": "60", "NewsAfterMin": "240"}),
                                  ("d24ntc", {"DayOffMask": "24", "NewsFile": "news_top_{b}.txt", "G_Crash": "true"})] for p in PERIODS],
 # after the Codex PR 41 fixes (swap via tick value, NewsFile checked in OnInit, RandDayPct): the fixed build must reproduce
 # the old results on gold exactly, then the exposure-matched control: no new baskets on 40% of weekdays drawn at random
 "fixcheck": [(p, f"{t}_fx", o) for p, t, o in [("rf2022", "off", {}), ("eg2526", "off", {}), ("rf2024", "d24ntop", {"DayOffMask": "24", "NewsFile": "news_top_{b}.txt"}),
                                                   ("rf2022", "off0", {"RandDayPct": "0", "RandSeed": "1"})]],   # the new set inputs, at their defaults
 "r4": [(p[0], f"rnd{k}", {"RandDayPct": "40", "RandSeed": str(k)}) for k in range(1, 11) for p in PERIODS]
     # Codex PR 39 (P1): v4/v5 state is now also cleared when a basket closes inside OnTick; the user's lot flag reruns with the fix
     + [(p[0], "lao4_fx", {"LotAfterOverlap": "4"}) for p in PERIODS],
}

if __name__ == "__main__":
    r = sys.argv[1]
    q = [job(*x) for x in ROUNDS[r]]
    if r == "r1b":
        import copy; j = copy.deepcopy(q[0]); j.update(base_set="dcv5_2d.set", expert="Jev\\DragonClone_v5b.ex5", report="v7_rf2022_lr3again"); q.insert(1, j)
    json.dump(q, open(f"research/bd1/q_v7_{r}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(q), "jobs")
