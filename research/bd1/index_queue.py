"""'Profitable every year' round 8 (docs/BD_EVERYYEAR_PLAN.md, pre-registered 2.11.2026): the clone (v11, all new flags off = v7)
on the Nasdaq (.USTECHCash) of RoboForex-ECN - never tested: RF-Pro has no indices. Measured 2024 (data/derived/symspec_ecn.csv):
spread ~0.04% of the median daily range vs 0.56% for gold on RF-Pro, and an index drifts up, so the buy side of the grid works
WITH the drift (round 7: sell-only on gold helped but failed). Scaling from gold as research/bd1/assets_queue.py: every price
distance keeps its size in median daily ranges; Autolotsize_/MaxLot_ keep the dollars at risk per daily range of gold at 0.01
per 6,000; MaxSpred at least 2.5x the median spread.
Usage: python research/bd1/index_queue.py -> research/bd1/q_every8.json"""
import json
import pandas as pd
from everyyear_queue import YEARS, job

GOLD = {"Fix_Distance": 300, "Dynamic_distance_start": 200, "iTS": 60, "iTD": 10, "TP_": 200, "MaxSpred": 50}   # dcv11_2d.set
g = pd.read_csv("data/derived/symspec.csv").drop_duplicates("symbol", keep="last").set_index("symbol").loc["XAUUSD"]
s = pd.read_csv("data/derived/symspec_ecn.csv").set_index("symbol").loc[".USTECHCash"]
o = {k: max(1, round(v * g.point / g.median_day_range * s.median_day_range / s.point)) for k, v in GOLD.items()}
o["MaxSpred"] = max(o["MaxSpred"], round(2.5 * s.median_spread_pts))
risk = (s.median_day_range / s.tick_size * s.tick_value) / (g.median_day_range / g.tick_size * g.tick_value)
o["Autolotsize_"] = round(6000 * risk); o["MaxLot_"] = round(5 / risk, 2)
SC = {k: str(v) for k, v in o.items()}

CFG8 = {
    "nq": {},                                                                   # both sides, as the frozen gold base
    "nq_bo": {"Flag_Trade_Sell_": "false"},                                     # buy baskets only (with the index drift)
    "nq_bo_dd5q": {"Flag_Trade_Sell_": "false", "DDScalePct": "5", "DDScaleMult": "0.25"},
}

if __name__ == "__main__":
    print("scaled", SC)
    q = []
    for tag, extra in CFG8.items():
        for yr in YEARS:
            j = job(*yr, tag, {**SC, **extra}, "4")          # "4" -> v11 + dcv11_2d.set
            j.update(symbol=".USTECHCash", name="Robo ECN demo", leverage=100, report=f"ev8_rf{yr[0]}_{tag}")
            q.append(j)
    json.dump(q, open("research/bd1/q_every8.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(q), "jobs")
