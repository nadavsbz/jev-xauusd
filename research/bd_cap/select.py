"""The pre-registered selection rule of docs/BD_CAP_SWEEP_PLAN.md, written before any result was seen.
Reads the three optimization evidence files, keeps only the 12 registered combinations (Buy = Sell),
applies the rule exactly and prints the chosen combination and the full table.
Usage: python research/bd_cap/select.py"""
import json, os, sys

EV = "docs/evidence"
FILES = ["bdcap_opt_ml02.json", "bdcap_opt_ml05.json", "bdcap_opt_ml10.json"]
DEPOSIT, MONTHS = 24895.0, 19.0          # 1.4.2024 - 31.10.2025


def num(x):
    return float(str(x).replace(" ", "").replace(",", "").replace("%", ""))


def main():
    rows = []
    for f in FILES:
        p = os.path.join(EV, f)
        if not os.path.exists(p):
            sys.exit(f"missing {p} (or only .invalid): the sweep is not complete")
        d = json.load(open(p, encoding="utf-8")); ml = d["job"]["fixed"]["MaxLot_"]
        for r in d["passes"]:
            b, s = num(r["MaxOrdersBuy"]), num(r["MaxOrdersSell"])
            if b != s:
                continue                                    # mixed combinations are not counted
            net = num(r["Profit"]); dd = num(r["Equity DD %"])
            wiped = net <= -0.9 * DEPOSIT or dd >= 90.0
            ann = ((1 + net / DEPOSIT) ** (12 / MONTHS) - 1) * 100 if net > -DEPOSIT else -100.0
            rows.append({"MaxLot_": ml, "Martin_": num(r["Martin_"]), "MaxOrders": int(b), "net": net,
                         "equity_dd_pct": dd, "annual_pct": round(ann, 1), "wiped": wiped,
                         "passes": (not wiped) and dd <= 30.0 and ann >= 50.0})
    if len(rows) != 12:
        sys.exit(f"expected 12 registered combinations, found {len(rows)}")
    rows.sort(key=lambda r: (r["MaxLot_"], r["Martin_"], r["MaxOrders"]))
    for r in rows:
        print(r)
    ok = [r for r in rows if r["passes"]]
    if ok:
        best = sorted(ok, key=lambda r: (-r["annual_pct"], r["equity_dd_pct"]))[0]; verdict = "pass"
    else:
        alive = [r for r in rows if not r["wiped"]]
        best = sorted(alive, key=lambda r: r["equity_dd_pct"])[0] if alive else None
        verdict = "no combination passes (the lowest-drawdown survivor is tested, marked as a failure)"
    out = {"rows": rows, "chosen": best, "verdict": verdict}
    json.dump(out, open(os.path.join(EV, "bdcap_selection.json"), "w", encoding="utf-8"), indent=1)
    print("CHOSEN:", best, "|", verdict)


if __name__ == "__main__":
    main()
