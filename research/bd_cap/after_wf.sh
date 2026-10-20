#!/usr/bin/env bash
# waits for the walk-forward runner, then: Black Dragon anti-crash sweep (docs/BD_ANTICRASH_PLAN.md),
# then the BTC Bot cap sweep (docs/BTC_CAP_SWEEP_PLAN.md)
cd "$(dirname "$0")/../.."
LOG="$1"
until grep -q "walk-forward done\|walk-forward PARTIAL\|walk-forward is not run\|dependent steps stop" "$LOG" 2>/dev/null; do sleep 120; done
PY=/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe
$PY tools/run_opt.py research/bd_cap/anti_opt.json
echo "anti-crash sweep done"
$PY tools/run_opt.py research/bd_cap/btc_opt_a.json
$PY tools/run_opt.py research/bd_cap/btc_opt_b.json
echo "btc cap sweep done"
