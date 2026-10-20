"""Registered selection of docs/BTC_CAP_SWEEP_PLAN.md, written before any result was read: 12 counted combinations
(MaxLot 0.1/0.2/0.5 x Martin 1.1/1.2 x 15/25 levels, Buy = Sell; MaxLot 1.0 is the original's reference only).
Pass = not wiped, equity DD <= 30%, annual >= 50% (19 months); best = highest annual; else the lowest-DD survivor
(marked as a failure). Usage: python research/bd_cap/btc_select.py"""
import json, os, sys
EV, DEP, MONTHS = "docs/evidence", 24895.0, 19.0
num = lambda x: float(str(x).replace(" ", "").replace(",", "").replace("%", ""))
rows = []
for f in ("btccap_opt_sel.json", "btccap_opt_sel_05.json"):
    p = os.path.join(EV, f)
    if not os.path.exists(p):
        sys.exit(f"missing {p}")
    for r in json.load(open(p, encoding="utf-8"))["passes"]:
        ml, b, s = num(r["MaxLot_"]), num(r["MaxOrdersBuy"]), num(r["MaxOrdersSell"])
        if b != s:
            continue
        net, dd = num(r["Profit"]), num(r["Equity DD %"])
        wiped = net <= -0.9 * DEP or dd >= 90
        ann = ((1 + net / DEP) ** (12 / MONTHS) - 1) * 100 if net > -DEP else -100.0
        rows.append({"MaxLot_": ml, "Martin_": num(r["Martin_"]), "MaxOrders": int(b), "net": net, "equity_dd_pct": dd,
                     "annual_pct": ann, "wiped": wiped, "counted": ml != 1.0,
                     "passes": ml != 1.0 and not wiped and dd <= 30 and ann >= 50})
counted = [r for r in rows if r["counted"]]
if len(counted) != 12:
    sys.exit(f"expected 12 counted combinations, found {len(counted)}")
ok = [r for r in counted if r["passes"]]
if ok:
    best, verdict = max(ok, key=lambda r: (r["annual_pct"], -r["equity_dd_pct"])), "pass"
else:
    alive = [r for r in counted if not r["wiped"]]
    best = min(alive, key=lambda r: r["equity_dd_pct"]) if alive else None
    verdict = "no combination passes" + ("" if best else "; every counted combination wiped")
json.dump({"rows": rows, "chosen": best, "verdict": verdict}, open(os.path.join(EV, "btccap_selection.json"), "w"), indent=1)
for r in sorted(rows, key=lambda r: (r["MaxLot_"], r["Martin_"], r["MaxOrders"])):
    print({k: (round(v, 1) if isinstance(v, float) else v) for k, v in r.items()})
print("CHOSEN:", best, "|", verdict)
