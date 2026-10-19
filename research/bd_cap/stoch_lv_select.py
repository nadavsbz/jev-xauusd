"""Registered selection of docs/BD_STOCH_LEVELS_PLAN.md, computed from the optimization evidence
(bdstoch_lv_sel.json): pass = not wiped and equity DD <= 40%; best = highest profit; no pass -> no choice.
Writes bdstoch_lv_selection.json (with the evidence's canonical sha256) and, when a combination is chosen,
the two pre-registered test jobs (EGlobal account-1 period; RoboForex 2022..3/2024 OHLC M1) to
research/bd_cap/queue_stochlv_test.json. Exits 0 only when a combination is chosen.
Usage: python research/bd_cap/stoch_lv_select.py"""
import hashlib, json, sys
p = "docs/evidence/bdstoch_lv_sel.json"
d = json.loads(open(p, "rb").read())
num = lambda x: float(str(x).replace(" ", "").replace(",", "").replace("%", ""))
# the registered grid only (review of the run 19.10.2026): MT5 expands an enum range into EVERY timeframe
# between start and stop, so the optimization also ran M1..M30; those passes are reported but never chosen
sys.path.insert(0, "tools")
from run_opt import values
grid = {k: {int(v) for v in values(*d["job"]["ranges"][k])} for k in ("Up_Level", "Down_Level", "TF_Stoh")}
rows = []
for r in d["passes"]:
    net, dd = num(r["Profit"]), num(r["Equity DD %"])
    rows.append({"Up_Level": int(num(r["Up_Level"])), "Down_Level": int(num(r["Down_Level"])),
                 "TF_Stoh": int(num(r["TF_Stoh"])), "profit": net, "dd": dd,
                 "wiped": net <= -0.9 * 24895 or dd >= 90})
for r in rows:
    r["registered"] = all(r[k] in grid[k] for k in grid)
ok = sorted([r for r in rows if r["registered"] and not r["wiped"] and r["dd"] <= 40], key=lambda r: -r["profit"])
canon = json.dumps(d, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
c = ok[0] if ok else None
json.dump({"source": p, "source_canonical_sha256": hashlib.sha256(canon).hexdigest(), "job": d["job"],
           "grid": {k: sorted(v) for k, v in grid.items()}, "rows": rows, "chosen": c}, open("docs/evidence/bdstoch_lv_selection.json", "w"), indent=1)
print("chosen:", c)
if c is None:
    sys.exit(1)
ov = {"Use_Stoh": "true", "Up_Level": str(c["Up_Level"]), "Down_Level": str(c["Down_Level"]), "TF_Stoh": str(c["TF_Stoh"])}
jobs = [{"report": "bdstochlv_test_eglobal", "base_set": "bd_3digit_cal.set", "overrides": ov,
         "name": "Black Dragon 1", "expert": "BD\EA Black Dragon.ex5", "symbol": "XAUUSDc", "period": "M15",
         "from": "2025.11.11", "to": "2026.10.15", "deposit": 24895, "leverage": 1000},
        {"report": "bdstochlv_test_2022", "base_set": "bd2afterpoint_l001_sp50.set", "overrides": ov,
         "name": "Black Dragon 3", "expert": "BD\EA Black Dragon.ex5", "symbol": "XAUUSD", "period": "M15",
         "from": "2022.01.01", "to": "2024.04.01", "deposit": 24895, "leverage": 1000, "model": 1}]
json.dump(jobs, open("research/bd_cap/queue_stochlv_test.json", "w"), indent=1)
sys.exit(0)
