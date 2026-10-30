"""Read-only list of the server's symbols through an investor login (docs/STABLE_SYSTEM_PLAN.md: which asset classes exist).
Same safety as collect_daily.py: clean terminal, investor only (refuses an account that allows trading), no credentials printed,
calls only initialize, account_info, symbols_get and shutdown. Prints name, path, digits, swap mode, long and short swap, contract size, current spread and point for every symbol.
Usage (from tools/): python list_symbols.py --accounts ../accounts.json --name NAME --terminal PATH"""
import argparse, os, sys, time
import MetaTrader5 as mt5
from collect_history import assert_clean_terminal, load_account
from collect_rates import _kill_by_path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--accounts", required=True); p.add_argument("--name", required=True); p.add_argument("--terminal", required=True)
    a = p.parse_args()
    if os.path.basename(a.terminal).lower() != "terminal64.exe" or not os.path.isfile(a.terminal):
        sys.exit("a valid terminal64.exe path is required")
    acc = load_account(a.accounts, a.name); login = int(acc["login"])
    assert_clean_terminal(a.terminal)
    try:
        if not mt5.initialize(path=a.terminal, login=login, password=acc["password"], server=acc["server"], portable=True, timeout=240000):
            sys.exit(f"initialize failed: {mt5.last_error()}")
        info = mt5.account_info()
        for _ in range(12):
            if info is not None and info.login == login: break
            time.sleep(5); info = mt5.account_info()
        if info is None or info.login != login: sys.exit("connected to the wrong account - aborting")
        if info.trade_allowed: sys.exit("account allows trading (master password?) - refusing, investor only")
        for s in mt5.symbols_get() or []:
            print(s.name, s.path, s.digits, s.swap_mode, s.swap_long, s.swap_short, s.trade_contract_size, s.spread, s.point, sep="\t")
    finally:
        mt5.shutdown(); _kill_by_path(a.terminal)

if __name__ == "__main__":
    main()
