#!/usr/bin/env bash
# after the stochastic levels sweep: the two Overlap-off optimizations (docs/TELEGRAM_FINDINGS.md)
cd "$(dirname "$0")/../.."
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
while tasklist | grep -qi "run_opt\|metatester64" || pgrep -f "stoch_lv_opt" >/dev/null 2>&1; do sleep 120; done
until [ -f docs/evidence/bdstoch_lv_sel.json ] || [ -f docs/evidence/bdstoch_lv_sel.json.invalid ]; do sleep 120; done
for n in 10 6; do $PY tools/run_opt.py research/bd_cap/ovl_opt_mo$n.json && echo "ovl mo$n done" || echo "ovl mo$n FAILED"; done
