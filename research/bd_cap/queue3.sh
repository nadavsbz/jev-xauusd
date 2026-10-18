#!/usr/bin/env bash
# after the BTC sweep: the ONE registered test of the anti-crash choice (docs/BD_ANTICRASH_PLAN.md), then the
# hedge data run (docs/DEPTH_HEDGE_PLAN.md)
cd "$(dirname "$0")/../.."
until grep -q "btc cap sweep done" "$1" 2>/dev/null; do sleep 120; done
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
$PY tools/run_queue.py research/bd_cap/queue_anti_test.json data/derived/bdanti_test.jsonl
echo "anti test done"
$PY tools/run_queue.py research/bd_cap/queue_hedge_data.json data/derived/hedge_data.jsonl
echo "hedge data done"
