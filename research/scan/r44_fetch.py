"""Round 44: fetch RF real ticks around each pre-registered USD release (T-10s..T+16min), 4 majors, cached per event.
Read-only demo terminal. Resumable. Usage: py -3.12 research/scan/r44_fetch.py"""
import os, sys, datetime as dt
import pandas as pd, MetaTrader5 as mt5
sys.path.insert(0, "tools")
from collect_history import load_account
FAM = ["Nonfarm Payrolls", "CPI m/m", "Core CPI m/m", "Initial Jobless Claims", "PPI m/m", "Retail Sales m/m", "ISM Manufacturing PMI",
       "ISM Non-Manufacturing PMI", "JOLTS Job Openings", "Fed Interest Rate Decision", "GDP q/q", "Core PCE Price Index m/m",
       "ADP Nonfarm Employment Change", "Durable Goods Orders m/m"]
SYMS = ("EURUSD", "GBPUSD", "USDJPY", "AUDUSD")
OUT = "data/derived/scan/news_ticks"
def events():
    c = pd.read_csv("data/derived/news/mt5_calendar_usd.csv"); c = c[(c.importance == 3) & c.event.isin(FAM)]
    t = pd.to_datetime(c.time, unit="s").drop_duplicates().sort_values()
    return t[(t >= "2019-01-01") & (t < pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(hours=1))]
if __name__ == "__main__":
    ev = events(); print("events", len(ev), flush=True)
    acc = load_account("accounts.json", "Bots ECN demo")
    if not mt5.initialize(path=r"C:\MT5_JEV_TEST\terminal64.exe", login=int(acc["login"]), password=acc["password"], server=acc["server"], timeout=240000, portable=True):
        sys.exit(f"init failed {mt5.last_error()}")
    if mt5.account_info().trade_mode != 0: mt5.shutdown(); sys.exit("not demo")
    off = 0
    for s in SYMS: mt5.symbol_select(s, True)
    for n, T in enumerate(ev):
        for s in SYMS:
            f = f"{OUT}/{s}_{int(T.timestamp())}.csv"
            if os.path.exists(f): continue
            # tick times from the terminal are server time (UTC+2/+3 = NY+7); request in server time
            et = T.tz_localize("UTC").tz_convert("America/New_York").tz_localize(None); srv = et + pd.Timedelta(hours=7)
            a = (srv - pd.Timedelta(seconds=10)).to_pydatetime().replace(tzinfo=dt.timezone.utc); b = (srv + pd.Timedelta(minutes=16)).to_pydatetime().replace(tzinfo=dt.timezone.utc)
            k = mt5.copy_ticks_range(s, a, b, mt5.COPY_TICKS_INFO)
            d = pd.DataFrame(k) if k is not None and len(k) else pd.DataFrame(columns=["time_msc", "bid", "ask"])
            d["srv_T"] = srv; d[["time_msc", "bid", "ask", "srv_T"]].to_csv(f, index=False)
        if n % 50 == 0: print(n, T, flush=True)
    mt5.shutdown()
