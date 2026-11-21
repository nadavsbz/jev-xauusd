"""Download M5 bars from the ECN demo used by the tester (read-only: initialize, account_info, symbol_select, copy_rates_range).
Writes data/derived/scan/m5/<symbol>.csv. Usage: python research/scan/get_m5.py .USTECHCash [from_year]"""
import os, sys
from datetime import datetime
import pandas as pd
import MetaTrader5 as mt5

TERM = r"C:\MT5_JEV_TEST\terminal64.exe"
OUT = "data/derived/scan/m5"
sym = sys.argv[1]; y0 = int(sys.argv[2]) if len(sys.argv) > 2 else 2017
sys.path.insert(0, "tools")
from collect_history import load_account
acc = load_account("accounts.json", "Bots ECN demo")       # demo account; credentials are never printed
if not mt5.initialize(path=TERM, login=int(acc["login"]), password=acc["password"], server=acc["server"], timeout=240000, portable=True):
    sys.exit(f"initialize failed {mt5.last_error()}")
if mt5.account_info().trade_mode != 0: mt5.shutdown(); sys.exit("not a demo account - stop")
mt5.symbol_select(sym, True)
os.makedirs(OUT, exist_ok=True)
parts = []
for y in range(y0, datetime.now().year + 1):          # year by year, so the server sends the history in chunks
    r = mt5.copy_rates_range(sym, mt5.TIMEFRAME_M5, datetime(y, 1, 1), datetime(y + 1, 1, 1))
    n = 0 if r is None else len(r); print(y, n, mt5.last_error() if not n else "")
    if n: parts.append(pd.DataFrame(r)[["time", "open", "high", "low", "close", "tick_volume", "spread"]])
mt5.shutdown()
if parts:
    d = pd.concat(parts).drop_duplicates("time").sort_values("time")
    d.to_csv(f"{OUT}/{sym.lstrip('.')}.csv", index=False)
    print(f"{sym}: {len(d)} bars {pd.to_datetime(d.time.iloc[0], unit='s'):%Y-%m-%d} -> {pd.to_datetime(d.time.iloc[-1], unit='s'):%Y-%m-%d}")
