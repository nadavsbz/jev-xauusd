"""BD settings search on the last year (docs/BD_OPT_PLAN.md, pre-registered 26.10.2026): one factor at a time around the frozen
d24ntop configuration (frozen/bd_v7_d24ntop_20261026), EGlobal 12/2025-10/2026 only (development); the 4 RoboForex years stay
untouched for validation. Distances in EGlobal points (XAUUSDc, 3 digits: 3000 = $3).
Usage: python research/bd1/opt_queue.py ROUND -> research/bd1/q_opt<ROUND>.json"""
import json, sys
sys.path.insert(0, "research/bd1"); from v7_queue import job

BASE = {"DayOffMask": "24", "NewsFile": "news_top_{b}.txt"}
STEPS = {
 "fix": ("Fix_Distance", ["2000", "2500", "3500", "4500"]),
 "dyn": ("Dynamic_distance_start", ["1500", "3000"]),
 "dmul": ("Distance_multiplier", ["1.0", "1.4"]),
 "mart": ("Martin_", ["1.3", "1.4", "1.6"]),
 "maxo": ("MaxOrdersBuy", ["7", "13"]),
 "its": ("iTS", ["400", "900"]),
 "itd": ("iTD", ["50", "200"]),
 "tp": ("TP_", ["1500", "3000"]),
 "ovn": ("OverlapOrderNumber", ["5", "9"]),
 "ovp": ("OverlapPercent", ["1", "5"]),
 "alot": ("Autolotsize_", ["4000", "9000"]),
 "mlot": ("MaxLot_", ["2", "10"]),
 "hrs": (("Start_Hour", "End_Hour"), [("3", "20"), ("1", "22")]),
 "spr": ("MaxSpred", ["100", "400"]),
}

def jobs1():
    q = [job("eg2526", "opt_base", BASE)]
    for tag, (k, vals) in STEPS.items():
        for v in vals:
            o = dict(BASE)
            if isinstance(k, tuple): o.update(dict(zip(k, v))); t = f"{tag}{v[0]}_{v[1]}"
            else:
                o[k] = v; t = f"{tag}{v.replace('.', '')}"
                if k == "MaxOrdersBuy": o["MaxOrdersSell"] = v
            q.append(job("eg2526", "opt_" + t, o))
    for j in q: j["report"] = j["report"].replace("v7_eg2526_", "opt1_")
    return q

if __name__ == "__main__":
    q = {"1": jobs1}[sys.argv[1]]()
    json.dump(q, open(f"research/bd1/q_opt{sys.argv[1]}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(q), "jobs")
