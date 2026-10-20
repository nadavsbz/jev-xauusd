#!/usr/bin/env bash
# Trend Catcher test (docs/OTHER_BOTS_TEST_PLAN.md): after the management-layer chains
cd "$(dirname "$0")/../.."
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
S="$TEMP/claude/D--Claude-jev/ae818c4a-c247-4ec4-a56e-b6097a32d869/scratchpad"
until grep -q "bd_acc1_rule done\|bd_acc1_rule FAILED" "$S/mgmtq.log" 2>/dev/null; do sleep 120; done
while tasklist | grep -qi metatester64; do sleep 60; done
$PY tools/run_queue.py research/other_bots/queue_trendcatcher.json data/derived/trendcatcher_test.jsonl && echo "tc done" || echo "tc FAILED"
