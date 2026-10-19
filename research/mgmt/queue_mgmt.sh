#!/usr/bin/env bash
# A3 chains (docs/MGMT_LAYER_PLAN.md): after the Umbrella queue
cd "$(dirname "$0")/../.."
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
S="$TEMP/claude/D--Claude-jev/ae818c4a-c247-4ec4-a56e-b6097a32d869/scratchpad"
until grep -q "umbrella done\|umbrella FAILED" "$S/umb.log" 2>/dev/null; do sleep 120; done
while tasklist | grep -qi metatester64; do sleep 60; done
for c in bd_acc1_valid bd_sel24; do $PY research/mgmt/chain.py research/mgmt/$c.json > "$S/mgmt_$c.log" 2>&1 && echo "$c done" || echo "$c FAILED"; done
