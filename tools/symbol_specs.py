"""Read-only dump of symbol specifications (digits, point, contract size,
volume step, commission-free fields only) through an investor login, as an
evidence file. Calls only initialize, account_info, symbol_select,
symbol_info and shutdown. No login or account number is written."""
import argparse, datetime as dt, json, os, sys, time

import MetaTrader5 as mt5
from collect_history import load_account, assert_clean_terminal

FIELDS = ["name", "description", "digits", "point", "trade_contract_size", "volume_min", "volume_step",
          "volume_max", "currency_base", "currency_profit", "currency_margin", "trade_tick_size", "trade_tick_value"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--accounts", required=True); p.add_argument("--name", required=True)
    p.add_argument("--terminal", required=True); p.add_argument("--out", required=True)
    p.add_argument("symbols", nargs="+")
    a = p.parse_args()
    acc = load_account(a.accounts, a.name); login = int(acc["login"])
    assert_clean_terminal(a.terminal)
    try:
        # initialize inside try (review PR #29): a failed login can still have started the terminal
        if not mt5.initialize(path=a.terminal, login=login, password=acc["password"], server=acc["server"],
                              portable=True, timeout=240000):
            sys.exit(f"initialize failed: {mt5.last_error()}")
        info = None
        for _ in range(12):
            info = mt5.account_info()
            if info is not None and info.login == login:
                break
            time.sleep(5)
        if info is None or info.login != login:
            sys.exit("connected to the wrong account")
        if info.trade_allowed:
            sys.exit("account allows trading - refusing, investor only")
        out = {"server": acc["server"], "account_currency": info.currency,
               "pulled_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "symbols": {}}
        for s in a.symbols:
            mt5.symbol_select(s, True)
            si = mt5.symbol_info(s)
            out["symbols"][s] = None if si is None else {f: getattr(si, f) for f in FIELDS}
    finally:
        mt5.shutdown()
        _kill_by_path(a.terminal)
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False)[:600])


def _kill_by_path(terminal):
    """Close the terminal this tool started (exact path), also when initialize failed (review PR #29)."""
    import subprocess
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-Process terminal64 -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq '%s' } | "
                          "ForEach-Object { $_.Id }" % os.path.abspath(terminal)], capture_output=True, text=True).stdout
    for pid in out.split():
        subprocess.run(["taskkill", "/PID", pid, "/F"], capture_output=True)


if __name__ == "__main__":
    main()
