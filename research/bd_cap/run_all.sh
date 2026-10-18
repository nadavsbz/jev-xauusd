#!/usr/bin/env bash
# the three optimization runs of the cap sweep, one after another (each one uses all local agents)
cd "$(dirname "$0")/../.."
for f in research/bd_cap/opt_ml02.json research/bd_cap/opt_ml05_10.json; do   # 0.5 and 1.0 in one run (review PR #22)
  /c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe tools/run_opt.py "$f"
done
