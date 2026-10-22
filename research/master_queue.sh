#!/usr/bin/env bash
# one sequential tester queue (20.10.2026, user: more purposeful work): the indicator signals first, then the rest
cd "$(dirname "$0")/.."
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
S="$TEMP/claude/D--Claude-jev/ae818c4a-c247-4ec4-a56e-b6097a32d869/scratchpad"
COMMON="$APPDATA/MetaQuotes/Terminal/Common/Files"
# 1) let the running Umbrella balanced 2024-25 run finish, then stop the old Umbrella queue
until grep -q '"umb_bal_sel24"' data/derived/umbrella_test.jsonl 2>/dev/null; do sleep 60; done  # (already true on a restart)
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -match 'queue_umbrella' } | ForEach-Object { taskkill /PID \$_.ProcessId /T /F }" >/dev/null 2>&1
sleep 10
powershell -NoProfile -Command "Get-Process terminal64,metatester64 -ErrorAction SilentlyContinue | Where-Object { \$_.Path -like 'C:\MT5_JEV_TEST\*' } | Stop-Process -Force" >/dev/null 2>&1
echo "umbrella paused after bal_sel24"
# 2) indicator exports (Trend AI, Trend Catcher; M15, both periods), each validated
for r in $($PY -c "import json;print(' '.join(j['report'] for j in json.load(open('research/crash/queue_exports.json'))))"); do
  csv=$($PY -c "import json;print([j['csv'] for j in json.load(open('research/crash/queue_exports.json')) if j['report']=='$r'][0])")
  [ -f "data/derived/indicators/$csv" ] && { echo "$r already exported"; continue; }
  rm -f "$COMMON/$csv" "docs/evidence/$r.json"
  $PY -c "import json;json.dump([j for j in json.load(open('research/crash/queue_exports.json')) if j['report']=='$r'],open('data/derived/one_export.json','w'))"
  $PY tools/run_queue.py data/derived/one_export.json data/derived/exports.jsonl >/dev/null 2>&1
  if [ -f "$COMMON/$csv" ] && grep -q "^#valid_values=[1-9]" "$COMMON/$csv"; then mkdir -p data/derived/indicators; cp "$COMMON/$csv" data/derived/indicators/; echo "$r ok"; else echo "$r FAILED"; fi
done
echo "exports finished"
# 2b) Flag_Use_hedge=false (docs/BD_HEDGE_PLAN.md): 80% of account 1's deep baskets were two-sided
$PY tools/run_queue.py research/bd_cap/queue_hedge.json data/derived/hedge_test.jsonl >/dev/null 2>&1; echo "hedge finished"
# 3) management layer: validation on account 1, the fixed rule, the sizing sweep
for c in bd_acc1_valid bd_sel24 bd_sel24_d900 bd_sel24_d1200 bd_sel24_p90 bd_acc1_rule; do
  $PY research/mgmt/chain.py research/mgmt/$c.json > "$S/mgmt_$c.log" 2>&1 && echo "$c done" || echo "$c FAILED"
done
# 4) the rest: Umbrella (remaining), Trend Catcher EA + Trend AI calibration, Strong_Support export
$PY tools/run_queue.py research/other_bots/queue_umbrella.json data/derived/umbrella_test.jsonl >/dev/null 2>&1; echo "umbrella finished"
$PY tools/run_queue.py research/other_bots/queue_trendcatcher.json data/derived/trendcatcher_test.jsonl >/dev/null 2>&1; echo "tc finished"
bash research/crash/queue_indexport.sh; echo "all finished"
