"""t300: run chain.py for seeds 1..N sequentially (one tester at a time). Usage: py -3.12 research/mgmt/t300_mc.py N"""
import json, os, subprocess, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
base = {"expert": "Jev\DragonClone.ex5", "period": "M15", "model": 4, "divisor": 600000, "protect": 0.85, "sweep": 0.0,
        "base_set": "dc3r_bd_3digit_cal.set", "name": "Black Dragon 1", "symbol": "XAUUSDc",
        "from": "2025-11-11", "to": "2026-10-15", "deposit": 25559,
        "bars": "data/raw/black_dragon_1/rates_XAUUSDc_M1_20261019T211852Z/bars.csv",
        "overrides": {"MaxSpred": "350", "TrailBySL": "false", "EntryRetrySpread": "false"},
        "delay_choices": [0, 2, 5, 10, 15, 20, 30, 40, 60, 80]}
os.makedirs(os.path.join(ROOT, "research", "mgmt", "t300"), exist_ok=True)
for seed in range(1, int(sys.argv[1]) + 1):
    cfg = dict(base, tag=f"t300_p{seed:02d}", seed=seed)
    p = os.path.join(ROOT, "research", "mgmt", "t300", f"p{seed:02d}.json")
    json.dump(cfg, open(p, "w"), indent=1)
    t = time.time()
    r = subprocess.run([sys.executable, os.path.join(ROOT, "research", "mgmt", "chain.py"), p], capture_output=True, text=True)
    print(f"seed {seed} rc {r.returncode} {time.time()-t:.0f}s {r.stdout[-200:]!r} {r.stderr[-300:]!r}", flush=True)
