"""The Black Dragon clone (v7, flags off, the user's floor guard) on other RoboForex symbols (docs/BD_V7_PLAN.md, part 4).
Scaling from gold, measured in 2024 by mql5/SymSpec.mq5 (Common\\Files\\symspec.csv -> data/derived/symspec.csv):
  - every price distance of the gold set (grid, trailing, TP) keeps its size in units of the median daily range;
  - Autolotsize_ and MaxLot_ keep the same dollars at risk per daily range as gold at 0.01 per 6,000;
  - MaxSpred: the gold value in daily-range units, but at least 2.5x the symbol's median spread (else it never trades).
Usage: python research/bd1/assets_queue.py -> research/bd1/q_assets.json, and prints the scaling table."""
import json
import pandas as pd

GOLD = {"Fix_Distance": 300, "Dynamic_distance_start": 200, "iTS": 60, "iTD": 10, "TP_": 200, "MaxSpred": 50}   # dcv7_2d.set, points of 0.01
YEARS = [("2022", "2022.01.03", "2023.01.01"), ("2023", "2023.01.02", "2024.01.01"), ("2024", "2024.01.02", "2025.01.01"), ("2025", "2025.01.02", "2025.10.24")]

s = pd.read_csv("data/derived/symspec.csv").drop_duplicates("symbol", keep="last").set_index("symbol")
s["usd_per_lot_adr"] = s.median_day_range / s.tick_size * s.tick_value
s["spread_adr_pct"] = s.median_spread_pts * s.point / s.median_day_range * 100
g = s.loc["XAUUSD"]
rows, q = [], []
for sym, r in s.iterrows():
    if sym == "XAUUSD": continue
    o = {}
    for k, v in GOLD.items():
        frac = v * g.point / g.median_day_range                   # gold distance in daily ranges
        o[k] = max(1, round(frac * r.median_day_range / r.point))
    o["MaxSpred"] = max(o["MaxSpred"], round(2.5 * r.median_spread_pts))
    risk = r.usd_per_lot_adr / g.usd_per_lot_adr
    o["Autolotsize_"] = round(6000 * risk)
    o["MaxLot_"] = round(5 / risk, 2)
    rows.append({"symbol": sym, "spread_%adr": round(r.spread_adr_pct, 2), **o})
    for y, f, t in YEARS:
        ov = {"Autolot_": "true", "G_FloorPct": "15", "G_FloorDays": "14", "G_FloorFrom": f"{y}0101", "P_At": "0", **{k: str(v) for k, v in o.items()}}
        q.append({"name": "Black Dragon 3", "symbol": sym, "period": "M15", "deposit": 120000, "leverage": 1000, "base_set": "dcv7_2d.set",
                  "from": f, "to": t, "expert": "Jev\\DragonClone_v7.ex5", "report": f"as_{sym}_{y}", "overrides": ov})
t = pd.DataFrame(rows).sort_values("spread_%adr")
print(f"gold spread {g.spread_adr_pct:.2f}% of the daily range"); print(t.to_string(index=False))
order = {sym: i for i, sym in enumerate(t.symbol)}          # cheapest spreads first
q.sort(key=lambda j: (order[j["symbol"]], j["from"]))
json.dump(q, open("research/bd1/q_assets.json", "w"), indent=1); print(len(q), "jobs")
