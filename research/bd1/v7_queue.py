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
    o.update(extra)
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
}

if __name__ == "__main__":
    r = sys.argv[1]
    q = [job(*x) for x in ROUNDS[r]]
    if r == "r1b":
        import copy; j = copy.deepcopy(q[0]); j.update(base_set="dcv5_2d.set", expert="Jev\\DragonClone_v5b.ex5", report="v7_rf2022_lr3again"); q.insert(1, j)
    json.dump(q, open(f"research/bd1/q_v7_{r}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(q), "jobs")
