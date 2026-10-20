"""Build the single pre-registered test job (EGlobal, account 1's period) for the chosen combination.
Usage: python research/bd_cap/make_test_job.py  -> research/bd_cap/queue_test.json (run with tools/run_queue.py)"""
import json

c = json.load(open("docs/evidence/bdcap_selection.json", encoding="utf-8"))["chosen"]
if c is None:
    raise SystemExit("no surviving combination: nothing to test")
mo = str(c["MaxOrders"])
job = [{"report": "bdcap_test_eglobal", "base_set": "bd_3digit_cal.set",
        "overrides": {"MaxLot_": str(c["MaxLot_"]), "Martin_": str(c["Martin_"]), "MaxOrdersBuy": mo, "MaxOrdersSell": mo},
        "name": "Black Dragon 1", "expert": "BD\EA Black Dragon.ex5", "symbol": "XAUUSDc", "period": "M15",
        "from": "2025.11.11", "to": "2026.10.14", "deposit": 24895, "leverage": 1000}]
json.dump(job, open("research/bd_cap/queue_test.json", "w"), indent=1)
print(job)
