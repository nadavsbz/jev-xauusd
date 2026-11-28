"""Grok t391 request: RF XAUUSD real-tick bid/ask around each live timestamp (ts_server +-5 s), read-only.
Uses the read-only terminal C:\\MT5_JEV_RO with the fleet investor login ("Black Dragon 3" in accounts.json, the same RF
server the tester uses). Refuses if trading is allowed. Writes docs/agents/grok_data/t391_tester_spread/ticks.csv.gz.
MT5 tick times are server-clock seconds stored as epoch; ts_server is passed the same way.
Usage: py -3.12 research/fleet/t391_tick_export.py"""
import os, sys, subprocess
from datetime import timedelta, timezone
import pandas as pd
import MetaTrader5 as mt5
sys.path.insert(0, "tools"); from collect_history import assert_clean_terminal, load_account

TERM = r"C:\MT5_JEV_RO\terminal64.exe"; OUT = "docs/agents/grok_data/t391_tester_spread"


def main():
    T = pd.read_csv("docs/agents/grok_data/t391/t391_timestamps.csv")
    a = load_account("accounts.json", "Black Dragon 3"); assert_clean_terminal(TERM)
    try:
        if not mt5.initialize(path=TERM, portable=True, login=int(a["login"]), password=a["password"], server=a["server"], timeout=120000):
            sys.exit(f"initialize failed: {mt5.last_error()[0]}")
        ai = mt5.account_info()
        if ai is None or ai.login != int(a["login"]) or ai.trade_allowed: sys.exit("REFUSED: not a read-only login")
        mt5.symbol_select("XAUUSD", True); pt = mt5.symbol_info("XAUUSD").point; rows = []
        for i, r in T.iterrows():
            t = pd.Timestamp(r.ts_server).tz_localize(timezone.utc)
            tk = mt5.copy_ticks_from("XAUUSD", (t - timedelta(seconds=5)).to_pydatetime(), 3000, mt5.COPY_TICKS_INFO)   # copy_ticks_range returns 0 for old, uncached days
            d = pd.DataFrame(tk) if tk is not None else pd.DataFrame(columns=["time_msc", "bid", "ask"])
            hi = int((t + timedelta(seconds=5)).timestamp() * 1000); lo = int((t - timedelta(seconds=5)).timestamp() * 1000)
            d = d[(d.time_msc >= lo) & (d.time_msc <= hi)] if len(d) else d
            if not len(d): rows.append(pd.DataFrame([dict(row=i, time_msc=None)])); continue
            d = d[["time_msc", "bid", "ask"]].copy(); d["spread_points"] = ((d.ask - d.bid) / pt).round().astype(int); d.insert(0, "row", i)
            rows.append(d)
        os.makedirs(OUT, exist_ok=True)
        D = pd.concat(rows); D.to_csv(f"{OUT}/ticks.csv.gz", index=False)
        print("rows", len(T), "ticks", int(D.time_msc.notna().sum()), "rows without ticks", int(D.groupby("row").time_msc.count().eq(0).sum()), "point", pt)
    finally:
        mt5.shutdown()
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Get-Process terminal64 -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq 'C:\\MT5_JEV_RO\\terminal64.exe' } | Stop-Process -Force"], capture_output=True)


if __name__ == "__main__":
    main()
