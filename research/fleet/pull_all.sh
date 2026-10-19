#!/usr/bin/env bash
# MASTER_PLAN step A4: read-only history pull (investor passwords) of the live fleet, one account at a time
# on the collector terminal C:\MT5_JEV_RO. Account 7 is excluded by the registered rule (MASTER_PLAN 4.3).
# Every attempt is logged per account; the script exits non-zero if any account failed (review PR #31).
set -o pipefail
cd "$(dirname "$0")/../../tools"
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
STATUS=../data/derived/fleet_pull_status.jsonl   # one line per attempt: the three-attempts rule counts these
# names on the command line (a retry) or the whole fleet
[ $# -gt 0 ] && names=("$@") || names=("Black Dragon 2" "Black Dragon 3" "BTC Bot 4" "Black Dragon 5" "Black Dragon 6" "Black Dragon 8")
fail=0
for n in "${names[@]}"; do
  echo "== $n"
  if $PY collect_history.py --accounts ../accounts.json --name "$n" --terminal 'C:\MT5_JEV_RO\terminal64.exe' 2>&1 | { grep -v Warning || true; } | tail -2; then
    st=ok
  else
    st=fail; fail=1
  fi
  echo "{\"account\": \"$n\", \"status\": \"$st\", \"at\": \"$(date -u +%FT%TZ)\"}" >> "$STATUS"
done
[ $fail -eq 0 ] && echo "fleet pull done" || { echo "fleet pull: some accounts FAILED (see $STATUS)"; exit 1; }
