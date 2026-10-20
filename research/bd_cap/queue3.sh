#!/usr/bin/env bash
# after the BTC sweep (ordering only): the ONE registered test of the anti-crash choice (docs/BD_ANTICRASH_PLAN.md),
# run only when its selection evidence is valid and names a combination (review PR #27); then the hedge data run
cd "$(dirname "$0")/../.."
until grep -q "btc cap sweep done" "$1" 2>/dev/null; do sleep 120; done
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
# the choice is recomputed from the CURRENT optimization evidence (review PR #27) and must be the one the test job runs
if $PY research/bd_cap/anti_select.py && $PY -c "import json,sys; c=json.load(open('docs/evidence/bdanti_selection.json'))['chosen']; sys.exit(0 if c[0]=='true' and c[1]==300.0 and c[2]==1.2 else 1)"; then
  if $PY tools/run_queue.py research/bd_cap/queue_anti_test.json data/derived/bdanti_test.jsonl; then
    echo "anti test done"
  else
    echo "anti test FAILED: no valid evidence"
  fi
else
  echo "anti test NOT run: selection evidence missing or not the registered choice"
fi
if $PY tools/run_queue.py research/bd_cap/queue_hedge_data.json data/derived/hedge_data.jsonl; then
  echo "hedge data done"
else
  echo "hedge data FAILED: no valid evidence"
fi
