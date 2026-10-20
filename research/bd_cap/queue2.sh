#!/usr/bin/env bash
# after the anti-crash and BTC sweeps: the original set on RoboForex with a very large deposit (never wiped),
# the selection data for docs/DEPTH_HEDGE_PLAN.md
cd "$(dirname "$0")/../.."
until grep -q "btc cap sweep done" "$1" 2>/dev/null; do sleep 120; done
/c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe tools/run_queue.py research/bd_cap/queue_hedge_data.json data/derived/hedge_data.jsonl
echo "hedge data done"
