"""Gate for round 11 (docs/CRASH_LINK_PLAN.md): v13 (Close/Close stochastic) must match the original EA, same_bar >= 0.80 in
2021 and 2020 for the reading StochRule 1 / StochBar 1. Exit 0 = passed, 1 = failed. Prints the match table.
Usage: python research/bd1/v13_gate.py"""
import json, subprocess, sys
ok = True
for y, f, t in (("2021", "2021-01-04", "2022-01-01"), ("2020", "2020-01-02", "2021-01-01")):
    out = subprocess.run([sys.executable, "-X", "utf8", "research/bd1/clone_vs_ref.py", f"lars_stoh_{y}", f, t,
                          f"v13val2_r1b1_{y}", f"v13val2_r1b0_{y}"], capture_output=True, text=True, encoding="utf-8").stdout
    r = json.loads(out); print(y, json.dumps(r))
    ok &= r[f"v13val2_r1b1_{y}"]["same_bar"] >= 0.80
print("gate", "PASSED" if ok else "FAILED")
sys.exit(0 if ok else 1)
