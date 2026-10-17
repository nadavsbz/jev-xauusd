#!/usr/bin/env bash
# the three optimization runs of the cap sweep, one after another (each one uses all local agents)
cd "$(dirname "$0")/../.."
for f in research/bd_cap/opt_ml02.json research/bd_cap/opt_ml05.json research/bd_cap/opt_ml10.json; do
  /c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe tools/run_opt.py "$f"
done
