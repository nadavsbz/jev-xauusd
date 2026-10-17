"""Read-only pull of H1 bars through an investor login into stage-1 CSVs (docs/CRASH_DETECT_PLAN.md).
Server time is converted to UTC with the 'New York + 7h' rule (ASSUMED for RoboForex: the
last bar at pull time matched UTC+3 while New York was on daylight time).
Usage: python research/crash/pull_h1.py ACCOUNT_NAME SYMBOL OUT_PREFIX OUT_DIR [--list PATTERN]"""
import sys, time, os, subprocess, datetime as dt
from zoneinfo import ZoneInfo
import MetaTrader5 as mt5
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from collect_history import load_account, assert_clean_terminal  # noqa: E402

TERM = r"C:\MT5_JEV_RO\terminal64.exe"
NY = ZoneInfo("America/New_York")


def to_utc(server_epoch):
    ny_wall = dt.datetime.utcfromtimestamp(server_epoch) - dt.timedelta(hours=7)
    return ny_wall.replace(tzinfo=NY).astimezone(dt.timezone.utc)


def main():
    name, sym, prefix, out = sys.argv[1:5]
    assert_clean_terminal(TERM)
    acc = load_account(os.path.join(os.path.dirname(__file__), "..", "..", "accounts.json"), name)
    login = int(acc["login"])
    if not mt5.initialize(path=TERM, login=login, password=acc["password"], server=acc["server"], portable=True, timeout=240000):
        sys.exit(f"init failed {mt5.last_error()}")
    try:
        for _ in range(12):
            i = mt5.account_info()
            if i and i.login == login:
                break
            time.sleep(5)
        if not i or i.login != login or i.trade_allowed:
            sys.exit("not the investor login asked for")
        if "--list" in sys.argv:
            pat = sys.argv[sys.argv.index("--list") + 1].upper()
            print([s.name for s in mt5.symbols_get() if pat in s.name.upper() or pat in s.description.upper()])
            return
        mt5.symbol_select(sym, True)
        prev = None
        r = None
        for _ in range(40):                       # history arrives asynchronously: pull until stable
            r = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_H1, 0, 200000)
            if r is not None and len(r) and prev is not None and len(r) == len(prev):
                break
            prev = r if r is not None and len(r) else None
            time.sleep(6)
        if r is None or not len(r):
            sys.exit(f"{sym}: no bars ({mt5.last_error()})")
        d = pd.DataFrame(r)
        d["utc"] = [to_utc(int(t)) for t in d.time]
        d["timestamp"] = [int(u.timestamp() * 1000) for u in d.utc]
        d = d[d.utc >= pd.Timestamp("2015-01-01", tz="UTC")]
        os.makedirs(out, exist_ok=True)
        for y, g in d.groupby(d.utc.dt.year):
            g[["timestamp", "open", "high", "low", "close"]].to_csv(os.path.join(out, f"{prefix}_h1_{y}.csv"), index=False)
        print(sym, len(d), "bars", d.utc.iloc[0], "->", d.utc.iloc[-1])
    finally:
        mt5.shutdown()
        # close this collector terminal again (exact path only), so the next pull starts clean
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Get-Process terminal64 -ErrorAction SilentlyContinue | "
                        f"Where-Object {{ $_.Path -eq '{TERM}' }} | Stop-Process -Force"], capture_output=True)
        time.sleep(3)


if __name__ == "__main__":
    main()
