#!/usr/bin/env bash
# MGMT_LAYER_PLAN stage 3 (sizing sweep): after the stage 1-2 chains, before Trend Catcher
cd "$(dirname "$0")/../.."
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
S="$TEMP/claude/D--Claude-jev/ae818c4a-c247-4ec4-a56e-b6097a32d869/scratchpad"
until grep -q "bd_acc1_rule done\|bd_acc1_rule FAILED" "$S/mgmtq.log" 2>/dev/null; do sleep 120; done
while tasklist | grep -qi metatester64; do sleep 60; done
for c in bd_sel24_d900 bd_sel24_d1200 bd_sel24_p90; do $PY research/mgmt/chain.py research/mgmt/$c.json > "$S/mgmt_$c.log" 2>&1 && echo "$c done" || echo "$c FAILED"; done
echo "sizing finished"
