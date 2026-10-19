#!/usr/bin/env bash
# MASTER_PLAN step A4: read-only history pull (investor passwords) of the live fleet, one account at a time
# on the collector terminal C:\MT5_JEV_RO. Account 7 was closed by the user and is skipped.
cd "$(dirname "$0")/../../tools"
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
for n in "Black Dragon 2" "Black Dragon 3" "BTC Bot 4" "Black Dragon 5" "Black Dragon 6" "Black Dragon 8"; do
  echo "== $n"
  $PY collect_history.py --accounts ../accounts.json --name "$n" --terminal 'C:\MT5_JEV_RO\terminal64.exe' 2>&1 | { grep -v Warning || true; } | tail -2
done
echo "fleet pull done"
