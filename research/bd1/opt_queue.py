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
    # code round (v8): grid distances widen with volatility; K = 0 must reproduce opt_base exactly
    for t, o in [("v8k0", {"AtrDistK": "0"}), ("v8k05", {"AtrDistK": "0.5"}), ("v8k1", {"AtrDistK": "1"}),
                 ("v8k15", {"AtrDistK": "1.5"}), ("v8k1m2", {"AtrDistK": "1", "AtrDistMax": "2"})]:
        j = job("eg2526", "opt_" + t, {**BASE, **o}); j.update(expert=r"Jev\DragonClone_v8.ex5", base_set="dcv8_base.set"); q.append(j)
    for j in q: j["report"] = j["report"].replace("v7_eg2526_", "opt1_")
    return q

# round 2 (docs/BD_OPT_PLAN.md): the 5 promising values with the best net/DD per parameter, in order of improvement, and their
# combination; robustness: base, each value and the combo also from two shifted starts (15.12.2025, 5.1.2026); then the combo and
# the base on the 4 RoboForex years (conditional historical comparison), mapped per parameter (price params x RF base / EG base)
PICK = {"iTS": "900", "Fix_Distance": "3500", "Martin_": "1.6", "Distance_multiplier": "1.0", "Dynamic_distance_start": "1500"}
EG_BASE = {"iTS": 600, "Fix_Distance": 3000, "Dynamic_distance_start": 2000}
RF_BASE = {"iTS": 60, "Fix_Distance": 300, "Dynamic_distance_start": 200}
SHIFTS = [("s1215", "2025.12.15"), ("s0105", "2026.01.05")]

def jobs2():
    q = []
    cfgs = [("base", {})] + [(f"{k}{v}".replace(".", ""), {k: v}) for k, v in PICK.items()] + [("combo", dict(PICK))]
    for t, o in cfgs:
        if t == "combo": q.append(job("eg2526", "opt_combo", {**BASE, **o}))
        for sn, d in SHIFTS:
            j = job("eg2526", f"opt_{t}_{sn}", {**BASE, **o}); j["from"] = d; q.append(j)
    rf = {k: (str(round(RF_BASE[k] * float(v) / EG_BASE[k])) if k in EG_BASE else v) for k, v in PICK.items()}
    for p in ("rf2022", "rf2023", "rf2024", "rf2025"):
        q.append(job(p, "opt_combo", {**BASE, **rf}))
    for j in q: j["report"] = j["report"].replace("v7_eg2526_", "opt2_").replace("v7_rf", "opt2_rf")
    return q

# round 3: Martin_ 1.6 failed the start-date sensitivity rule (5.1.2026: +58% vs base +90%), so by the registered rule the combination
# is the other four values; the same dev runs (full + 2 shifts) and the 4 RoboForex years
PICK3 = {k: v for k, v in PICK.items() if k != "Martin_"}

def jobs3():
    q = [job("eg2526", "opt_combo4", {**BASE, **PICK3})]
    for sn, d in SHIFTS:
        j = job("eg2526", f"opt_combo4_{sn}", {**BASE, **PICK3}); j["from"] = d; q.append(j)
    rf = {k: (str(round(RF_BASE[k] * float(v) / EG_BASE[k])) if k in EG_BASE else v) for k, v in PICK3.items()}
    for p in ("rf2022", "rf2023", "rf2024", "rf2025"):
        q.append(job(p, "opt_combo4", {**BASE, **rf}))
    for j in q: j["report"] = j["report"].replace("v7_eg2526_", "opt3_").replace("v7_rf", "opt3_rf")
    return q

if __name__ == "__main__":
    q = {"1": jobs1, "2": jobs2, "3": jobs3}[sys.argv[1]]()
    json.dump(q, open(f"research/bd1/q_opt{sys.argv[1]}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(q), "jobs")
