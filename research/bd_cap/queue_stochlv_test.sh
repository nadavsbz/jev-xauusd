#!/usr/bin/env bash
# after the stochastic levels sweep: its pre-registered selection and two single test runs
# (docs/BD_STOCH_LEVELS_PLAN.md), then the two Overlap-off optimizations (docs/TELEGRAM_FINDINGS.md).
# One tester run at a time.
cd "$(dirname "$0")/../.."
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
until [ -f docs/evidence/bdstoch_lv_sel.json ] || [ -f docs/evidence/bdstoch_lv_sel.json.invalid ]; do sleep 120; done
while tasklist | grep -qi metatester64; do sleep 60; done
if [ -f docs/evidence/bdstoch_lv_sel.json ]; then
  if $PY research/bd_cap/stoch_lv_select.py; then
    $PY tools/run_queue.py research/bd_cap/queue_stochlv_test.json data/derived/bdstochlv_test.jsonl && echo "stochlv tests done" || echo "stochlv tests FAILED"
  else echo "no surviving combination"; fi
else echo "sweep evidence invalid: no selection"; fi
for n in 10 6; do $PY tools/run_opt.py research/bd_cap/ovl_opt_mo$n.json && echo "ovl mo$n done" || echo "ovl mo$n FAILED"; done
