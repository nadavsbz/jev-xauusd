"""Read-only nightly read of the real ProCent C1 account (investor login, git-ignored secrets).
Usage: py -3.12 research/stable/procent_read.py YYYYMMDD
Refuses unless trade_allowed is False. Prints no login/server. Writes data/derived/procent/*_<tag>.csv."""
import os, sys, json, subprocess
from datetime import datetime, timezone
import pandas as pd
import MetaTrader5 as mt5
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
from collect_history import assert_clean_terminal, wait_for_history

TERM = r"C:\MT5_JEV_RO\terminal64.exe"
SINCE = datetime(2026, 11, 20, tzinfo=timezone.utc)


def main(tag):
    a = json.load(open("secrets/procent_investor.json", encoding="utf-8"))
    assert_clean_terminal(TERM)
    ok = mt5.initialize(path=TERM, portable=True, login=int(a["login"]), password=a["password"], server=a["server"], timeout=120000)
    if not ok:
        sys.exit(f"initialize failed: {mt5.last_error()[0]}")
    try:
        ai = mt5.account_info()
        if ai is None or ai.trade_allowed:
            sys.exit("REFUSED: trading is allowed on this login - not reading")
        now = datetime.now(timezone.utc)
        wait_for_history(SINCE, now)
        D = mt5.history_deals_get(SINCE, now) or ()
        P = mt5.positions_get() or ()
        os.makedirs("data/derived/procent", exist_ok=True)
        cols = ["ticket", "order", "time", "time_msc", "type", "entry", "magic", "position_id", "volume", "price", "commission", "swap", "profit", "symbol", "comment"]
        d = pd.DataFrame([x._asdict() for x in D])
        if len(d): d = d[[c for c in cols if c in d.columns]]; d.to_csv(f"data/derived/procent/deals_{tag}.csv", index=False)
        p = pd.DataFrame([x._asdict() for x in P])
        pc = ["ticket", "time", "type", "magic", "identifier", "volume", "price_open", "price_current", "swap", "profit", "symbol"]
        if len(p): p = p[pc]; p.to_csv(f"data/derived/procent/positions_{tag}.csv", index=False)
        print(json.dumps(dict(currency=ai.currency, balance=ai.balance, equity=ai.equity, server_time_last=str(pd.to_datetime(d.time.max(), unit="s")) if len(d) else None,
                              n_deals=int(len(d)), n_trade_deals=int((d.type <= 1).sum()) if len(d) else 0,
                              positions=[dict(sym=r.symbol, side="buy" if r.type == 0 else "sell", vol=r.volume, open=str(pd.to_datetime(r.time, unit="s")), px=r.price_open, magic=int(r.magic), pnl=r.profit) for r in p.itertuples()] if len(p) else []), indent=1))
    finally:
        mt5.shutdown()
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Get-Process terminal64 -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq 'C:\\MT5_JEV_RO\\terminal64.exe' } | Stop-Process -Force"], capture_output=True)


if __name__ == "__main__":
    main(sys.argv[1])
