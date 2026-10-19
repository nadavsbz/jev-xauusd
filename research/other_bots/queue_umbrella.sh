#!/usr/bin/env bash
# Umbrella profiles test (docs/OTHER_BOTS_TEST_PLAN.md): starts after the Overlap-off optimization with 6 levels
cd "$(dirname "$0")/../.."
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
until [ -f docs/evidence/bdovl_sel_mo6.json ] || [ -f docs/evidence/bdovl_sel_mo6.json.invalid ]; do sleep 120; done
while tasklist | grep -qi metatester64; do sleep 60; done
$PY tools/run_queue.py research/other_bots/queue_umbrella.json data/derived/umbrella_test.jsonl && echo "umbrella done" || echo "umbrella FAILED"
