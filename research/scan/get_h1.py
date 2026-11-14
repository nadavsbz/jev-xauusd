"""Download H1 bars of the RoboForex-ECN universe (stocks, indices, crypto) from the demo terminal used by the tester.
Read-only: initialize, account_info, symbol_select, copy_rates_from_pos, shutdown. Writes data/derived/scan/h1/<symbol>.csv.
Usage: python research/scan/get_h1.py"""
import os, sys
import pandas as pd
import MetaTrader5 as mt5

TERM = r"C:\MT5_JEV_TEST\terminal64.exe"
OUT = "data/derived/scan/h1"
SKIP_FX = 31   # the first 31 rows of ecn_costs are FX and metals

syms = sys.argv[1:] or pd.read_csv("data/derived/ecn_costs_20261030.csv").symbol.tolist()[SKIP_FX:]   # optional: symbols on the command line
sys.path.insert(0, "tools")
from collect_history import load_account
acc = load_account("accounts.json", "Bots ECN demo")       # demo account; credentials are never printed
if not mt5.initialize(path=TERM, login=int(acc["login"]), password=acc["password"], server=acc["server"], timeout=240000, portable=True):
    sys.exit(f"initialize failed {mt5.last_error()}")
a = mt5.account_info()
print("server", a.server, "trade_mode", a.trade_mode)   # 0 = demo
if a.trade_mode != 0: mt5.shutdown(); sys.exit("not a demo account - stop")
os.makedirs(OUT, exist_ok=True)
for s in syms:
    mt5.symbol_select(s, True)
    r = None
    for n in (100000, 50000, 20000):
        r = mt5.copy_rates_from_pos(s, mt5.TIMEFRAME_H1, 0, n)
        if r is not None and len(r): break
    if r is None or not len(r): print(s, "no data", mt5.last_error()); continue
    d = pd.DataFrame(r)[["time", "open", "high", "low", "close", "tick_volume", "spread"]]
    d.to_csv(f"{OUT}/{s.lstrip('.')}.csv", index=False)
    print(f"{s:12s} {len(d):6d} bars {pd.to_datetime(d.time.iloc[0], unit='s'):%Y-%m-%d} -> {pd.to_datetime(d.time.iloc[-1], unit='s'):%Y-%m-%d}")
mt5.shutdown()
