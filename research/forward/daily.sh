#!/usr/bin/env bash
# Daily forward pull + comparison for account 1 (read-only investor login, collector terminal only).
set -e
cd "$(dirname "$0")/../.."
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
RAW=data/raw/black_dragon_1
kill_ro() { powershell -NoProfile -Command "Get-Process terminal64 -ErrorAction SilentlyContinue | Where-Object { \$_.Path -eq 'C:\MT5_JEV_RO\terminal64.exe' } | Stop-Process -Force" >/dev/null 2>&1 || true; sleep 3; }
kill_ro
(cd tools && $PY collect_history.py --accounts ../accounts.json --name "Black Dragon 1" --terminal 'C:\MT5_JEV_RO\terminal64.exe' 2>&1 | grep -v Warning | tail -2)
kill_ro
(cd tools && $PY collect_rates.py --accounts ../accounts.json --name "Black Dragon 1" --terminal 'C:\MT5_JEV_RO\terminal64.exe' --symbol XAUUSDc --since 2025-09-01 2>&1 | grep -v Warning | tail -2)
kill_ro
export JEV_DEALS_SNAPSHOT=$(ls $RAW | grep -E '^[0-9]{8}T' | sort | tail -1)
export JEV_RATES_SNAPSHOT=$(ls $RAW | grep -E '^rates_XAUUSDc_M1_' | sort | tail -1)
export JEV_DERIVED=data/derived/bd1_forward
echo "snapshots: $JEV_DEALS_SNAPSHOT $JEV_RATES_SNAPSHOT"
python research/bd1/clusters.py --strict | tail -1
python research/forward/compare.py data/derived/bd1_forward/compare.json
python research/forward/crash_signal.py data/derived/bd1_forward/crash_signal.csv
