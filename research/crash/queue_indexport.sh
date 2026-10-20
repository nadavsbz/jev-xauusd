#!/usr/bin/env bash
# Strong_Support export (docs/CRASH_DETECT_PLAN.md, T7): after the Trend Catcher queue
cd "$(dirname "$0")/../.."
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
S="$TEMP/claude/D--Claude-jev/ae818c4a-c247-4ec4-a56e-b6097a32d869/scratchpad"
until grep -q "tc done\|tc FAILED" "$S/tc.log" 2>/dev/null; do sleep 120; done
while tasklist | grep -qi metatester64; do sleep 60; done
CSV="$APPDATA/MetaQuotes/Terminal/Common/Files/strong_support_xauusd_h1.csv"
rm -f "$CSV"                                   # a stale export must never pass as this run's (review PR #34)
$PY tools/run_queue.py research/crash/queue_indexport.json data/derived/indexport.jsonl || { echo "export FAILED (tester)"; exit 1; }
# the run counts only if the new CSV exists, has rows and at least one buffer value was read
if [ -f "$CSV" ] && [ "$(wc -l < "$CSV")" -gt 100 ] && grep -q "^#valid_values=[1-9]" "$CSV"; then
  mkdir -p data/derived/indicators && cp "$CSV" data/derived/indicators/ && echo "export done"
else
  echo "export FAILED (no valid buffer values)"; exit 1
fi
