"""Read-only download of D1 bars for many symbols through an investor login (docs/HYBRID_PLAN.md, step 1: multi-asset trend).
Same safety as collect_rates.py: clean terminal, investor only (refuses an account that allows trading), no credentials printed,
calls only initialize, account_info, symbol_select, copy_rates_range and shutdown. Writes data/derived/daily/<SYM>_D1.csv.
Usage (from tools/): python collect_daily.py --accounts ../accounts.json --name NAME --terminal PATH --since 2010-01-01 [--tf H1] SYM [SYM ...]
--tf H1/H4 writes data/derived/intraday/<SYM>_<TF>.csv (docs/STABLE_SYSTEM_PLAN.md: intraday crypto trend)."""
import argparse, csv, os, sys, time
from datetime import datetime, timezone
import MetaTrader5 as mt5
from collect_history import ROOT, assert_clean_terminal, load_account
from collect_rates import _kill_by_path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--accounts", required=True); p.add_argument("--name", required=True)
    p.add_argument("--terminal", required=True); p.add_argument("--since", required=True)
    p.add_argument("--tf", default="D1", choices=["D1", "H4", "H1"])
    p.add_argument("symbols", nargs="+")
    a = p.parse_args()
    if os.path.basename(a.terminal).lower() != "terminal64.exe" or not os.path.isfile(a.terminal):
        sys.exit("a valid terminal64.exe path is required")
    acc = load_account(a.accounts, a.name); login = int(acc["login"])
    assert_clean_terminal(a.terminal)
    out = os.path.join(ROOT, "data", "derived", "daily" if a.tf == "D1" else "intraday"); tf = getattr(mt5, "TIMEFRAME_" + a.tf); os.makedirs(out, exist_ok=True)
    try:
        if not mt5.initialize(path=a.terminal, login=login, password=acc["password"], server=acc["server"], portable=True, timeout=240000):
            sys.exit(f"initialize failed: {mt5.last_error()}")
        info = mt5.account_info()
        for _ in range(12):
            if info is not None and info.login == login: break
            time.sleep(5); info = mt5.account_info()
        if info is None or info.login != login: sys.exit("connected to the wrong account - aborting")
        if info.trade_allowed: sys.exit("account allows trading (master password?) - refusing, investor only")
        since = datetime.strptime(a.since, "%Y-%m-%d").replace(tzinfo=timezone.utc); now = datetime.now(timezone.utc)
        for s in a.symbols:
            if not mt5.symbol_select(s, True): print(s, "not available", flush=True); continue
            prev = None
            for _ in range(6):   # history arrives asynchronously: re-fetch until two pulls agree
                r = mt5.copy_rates_range(s, tf, since, now)
                n = 0 if r is None else len(r)
                if prev is not None and n == prev and n > 0: break
                prev = n; time.sleep(3)
            if r is None or len(r) == 0: print(s, "no bars", flush=True); continue
            with open(os.path.join(out, f"{s}_{a.tf}.csv"), "w", newline="") as f:
                w = csv.writer(f); w.writerow(["time", "open", "high", "low", "close", "tick_volume", "spread"])
                for x in r: w.writerow([int(x["time"]), x["open"], x["high"], x["low"], x["close"], int(x["tick_volume"]), int(x["spread"])])
            print(s, len(r), datetime.fromtimestamp(int(r[0]["time"]), timezone.utc).date(), flush=True)
    finally:
        mt5.shutdown(); _kill_by_path(a.terminal)

if __name__ == "__main__":
    main()
