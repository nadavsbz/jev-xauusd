"""Read-only check of Nasdaq symbol specs on a RoboForex cent account (investor login, clean terminal, as collect_history).
Prints only account currency / trade mode and symbol specs; never the login, password or server address.
Usage: python research/scan/cent_spec.py "<account name in accounts.json>" """
import sys
import MetaTrader5 as mt5
sys.path.insert(0, "tools")
from collect_history import load_account, assert_clean_terminal

TERM = r"C:\MT5_JEV_RO\terminal64.exe"
assert_clean_terminal(TERM)
acc = load_account("accounts.json", sys.argv[1])
pw = acc.get("password")   # investor password expected; refused below if trading is allowed
if not pw: sys.exit("no investor password for this account - stop")
if not mt5.initialize(path=TERM, login=int(acc["login"]), password=pw, server=acc["server"], timeout=240000, portable=True):
    sys.exit(f"initialize failed {mt5.last_error()}")
a = mt5.account_info()
print("currency", a.currency, "| trade_allowed", a.trade_allowed, "| trade_mode", a.trade_mode, "| leverage", a.leverage)
if a.trade_allowed: mt5.shutdown(); sys.exit("trading allowed = not an investor login - stop")
print("all:", " ".join(s.name for s in mt5.symbols_get()))
syms = [s for s in mt5.symbols_get() if any(k in s.name.upper() for k in ("TECH", "US100", "NAS", "NDX", "US500", "US30", "DE40"))]
print("symbols found:", len(syms), "| total symbols:", mt5.symbols_total())
for s in syms:
    mt5.symbol_select(s.name, True); t = mt5.symbol_info_tick(s.name); i = mt5.symbol_info(s.name)
    sp = (t.ask - t.bid) / t.bid * 100 if t and t.bid else float("nan")
    print(f"{i.name:14s} contract {i.trade_contract_size} profit_ccy {i.currency_profit} tick_value {i.trade_tick_value:.5f} tick_size {i.trade_tick_size} "
          f"vol_min {i.volume_min} step {i.volume_step} digits {i.digits} trade_mode {i.trade_mode} spread_now {sp:.4f}% "
          f"swap_l {i.swap_long} swap_s {i.swap_short} swap_mode {i.swap_mode} path {i.path}")
mt5.shutdown()
