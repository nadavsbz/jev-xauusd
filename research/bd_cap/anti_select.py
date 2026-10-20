"""Registered selection of docs/BD_ANTICRASH_PLAN.md, computed from the CURRENT optimization evidence
(bdanti_opt_sel.json, its job and passes): pass = not wiped and equity DD <= 40%; best = highest profit.
Writes bdanti_selection.json with the evidence's sha256, and exits 0 only when a combination is chosen.
Usage: python research/bd_cap/anti_select.py"""
import hashlib, json, sys
p = "docs/evidence/bdanti_opt_sel.json"
raw = open(p, "rb").read(); d = json.loads(raw)
num = lambda x: float(str(x).replace(" ", "").replace(",", "").replace("%", ""))
rows = []
for r in d["passes"]:
    net, dd = num(r["Profit"]), num(r["Equity DD %"])
    rows.append((str(r["Use_Stoh"]).lower(), num(r["Fix_Distance"]), num(r["Distance_multiplier"]), net, dd,
                 net <= -0.9 * 24895 or dd >= 90))
ok = sorted([r for r in rows if not r[5] and r[4] <= 40], key=lambda r: -r[3])
# hash of the CANONICAL JSON content (review PR #27): line-ending changes by git must not break the link
canon = json.dumps(d, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
out = {"source": p, "source_canonical_sha256": hashlib.sha256(canon).hexdigest(), "job": d["job"], "rows": rows,
       "chosen": ok[0] if ok else None}
json.dump(out, open("docs/evidence/bdanti_selection.json", "w"), indent=1)
print("chosen:", out["chosen"])
sys.exit(0 if ok else 1)
