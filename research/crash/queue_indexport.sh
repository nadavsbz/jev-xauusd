#!/usr/bin/env bash
# Strong_Support export (docs/CRASH_DETECT_PLAN.md, T7): after the Trend Catcher queue
cd "$(dirname "$0")/../.."
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
S="$TEMP/claude/D--Claude-jev/ae818c4a-c247-4ec4-a56e-b6097a32d869/scratchpad"
until grep -q "tc done\|tc FAILED" "$S/tc.log" 2>/dev/null; do sleep 120; done
while tasklist | grep -qi metatester64; do sleep 60; done
$PY tools/run_queue.py research/crash/queue_indexport.json data/derived/indexport.jsonl && echo "export done" || echo "export FAILED"
