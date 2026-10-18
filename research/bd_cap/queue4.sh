#!/usr/bin/env bash
# after queue3: the registered 2022-2024 check of the stochastic filter (docs/BD_ANTICRASH_PLAN.md, M1 OHLC model)
cd "$(dirname "$0")/../.."
until grep -q "hedge data done\|hedge data FAILED" "$1" 2>/dev/null; do sleep 120; done
if /c/Users/Benza/AppData/Local/Programs/Python/Python312/python.exe tools/run_queue.py research/bd_cap/queue_anti_2022.json data/derived/bdanti_2022.jsonl; then
  echo "anti 2022 done"
else
  echo "anti 2022 FAILED for some runs"
fi
