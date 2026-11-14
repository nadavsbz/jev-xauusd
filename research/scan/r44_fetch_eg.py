"""Round 44/46 diagnostic: the same release-window ticks as r44_fetch.py, from EGlobal (EGlobalTrade-Classic, cent symbols 'c'),
read-only. Uses the dedicated read-only terminal C:\\MT5_JEV_RO and refuses unless the login cannot trade (investor password).
EGlobal clock = UTC+2 all year (research/bd1/news_files.py). Output data/derived/scan/news_ticks_eg/{SYM}_{T}.csv, same columns.
Usage: py -3.12 research/scan/r44_fetch_eg.py"""
import os, sys, datetime as dt
import pandas as pd, MetaTrader5 as mt5
sys.path.insert(0, "research/scan"); sys.path.insert(0, "tools")
from r44_fetch import events, SYMS
from collect_history import load_account
OUT = "data/derived/scan/news_ticks_eg"; TERM = r"C:\MT5_JEV_RO\terminal64.exe"
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ev = events(); ev = ev[ev >= "2025-03-26"]; print("events", len(ev), flush=True)  # EG keeps ticks from 2025-03-25 only
    acc = load_account("accounts.json", "Black Dragon 1")
    if not mt5.initialize(path=TERM, login=int(acc["login"]), password=acc["password"], server=acc["server"], timeout=240000, portable=True):
        sys.exit(f"init failed {mt5.last_error()}")
    ai = mt5.account_info()
    if ai is None or ai.trade_allowed or ai.login != int(acc["login"]): mt5.shutdown(); sys.exit("refusing: login can trade or wrong account")
    for s in SYMS: mt5.symbol_select(s + "c", True)
    for n, T in enumerate(ev):
        srv = T + pd.Timedelta(hours=2)
        for s in SYMS:
            f = f"{OUT}/{s}_{int(T.timestamp())}.csv"
            if os.path.exists(f): continue
            a = (srv - pd.Timedelta(seconds=10)).to_pydatetime().replace(tzinfo=dt.timezone.utc); b = (srv + pd.Timedelta(minutes=16)).to_pydatetime().replace(tzinfo=dt.timezone.utc)
            k = mt5.copy_ticks_range(s + "c", a, b, mt5.COPY_TICKS_INFO)
            d = pd.DataFrame(k) if k is not None and len(k) else pd.DataFrame(columns=["time_msc", "bid", "ask"])
            d["srv_T"] = srv; d[["time_msc", "bid", "ask", "srv_T"]].to_csv(f, index=False)
        if n % 100 == 0: print(n, T, flush=True)
    mt5.shutdown()
