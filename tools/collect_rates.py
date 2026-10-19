"""Read-only download of M1 bars for one symbol through an investor login.

Reuses the safety checks of collect_history.py (clean terminal, investor
only, no credentials printed). Calls only initialize, account_info,
symbol_select, copy_rates_range and shutdown - nothing that can trade.
Bars are fetched month by month and each month is re-fetched until two
consecutive pulls are byte-identical (the terminal downloads history
asynchronously); the whole range is then checked day by day against
the expected trading calendar (tools/market_calendar.py).
"""

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone

import MetaTrader5 as mt5

from collect_history import ROOT, assert_clean_terminal, load_account
from market_calendar import check_trading_days

FIELDS = ("time", "open", "high", "low", "close", "tick_volume", "spread", "real_volume")


def month_starts(since, until):
    cur = since.replace(day=1)
    while cur < until:
        nxt = cur.replace(year=cur.year + cur.month // 12, month=cur.month % 12 + 1)
        yield max(cur, since), min(nxt, until)
        cur = nxt


def fetch_stable(symbol, start, end, tries=12, poll=5):
    """Re-fetch until two consecutive pulls are byte-identical (same bars,
    same values). Completeness is checked day by day in main()."""
    prev = None
    for _ in range(tries):
        bars = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, start, end)
        if bars is not None:
            # copy_rates_range includes `end`; keep [start, end) so months do not overlap
            bars = bars[bars["time"] < int(end.timestamp())]
        digest = None if bars is None or len(bars) == 0 else hashlib.sha256(bars.tobytes()).hexdigest()
        if digest and digest == prev:
            return bars
        prev = digest
        time.sleep(poll)
    sys.exit(f"{symbol} {start:%Y-%m}: two identical pulls never arrived - nothing written")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--accounts", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--terminal", required=True)
    p.add_argument("--symbol", required=True)
    p.add_argument("--since", required=True, help="UTC date YYYY-MM-DD")
    p.add_argument("--accept-short-days", action="store_true",
                   help="write even if some days fail the calendar check (e.g. a broker's US-holiday early closes); "
                        "the failing days are listed in the manifest")
    args = p.parse_args()

    if os.path.basename(args.terminal).lower() != "terminal64.exe" or not os.path.isfile(args.terminal):
        sys.exit("a valid terminal64.exe path is required")
    acc = load_account(args.accounts, args.name)
    login = int(acc["login"])
    assert_clean_terminal(args.terminal)

    try:
        # initialize inside try (review PR #29): a failed login can still have started the terminal
        if not mt5.initialize(path=args.terminal, login=login, password=acc["password"],
                              server=acc["server"], portable=True, timeout=240000):
            sys.exit(f"initialize failed: {mt5.last_error()}")
        info = mt5.account_info()
        for _ in range(12):  # the login switch can lag behind initialize()
            if info is not None and info.login == login:
                break
            time.sleep(5)
            info = mt5.account_info()
        if info is None or info.login != login:
            sys.exit("connected to the wrong account - aborting")
        if info.trade_allowed:
            sys.exit("account allows trading (master password?) - refusing, investor only")
        if not mt5.symbol_select(args.symbol, True):
            sys.exit(f"symbol {args.symbol} not available")

        since = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        rows, months = [], []
        for start, end in month_starts(since, now):
            bars = fetch_stable(args.symbol, start, end)
            months.append({"month": f"{start:%Y-%m}", "bars": len(bars)})
            rows.extend(bars.tolist())
            print(f"{start:%Y-%m}: {len(bars)} bars", flush=True)
        times = [r[0] for r in rows]
        if times != sorted(set(times)):
            sys.exit("duplicate or unsorted bar times - nothing written")
        # every weekday up to yesterday must be a full trading day unless it is a listed holiday
        last_full = (now - timedelta(days=1)).date()
        problems = check_trading_days(times, since.date(), last_full)
        if args.accept_short_days:
            # only a short session (800+ bars) or a closed day on a fixed market holiday is accepted;
            # gaps, missing ranges and other closed days still fail
            def short_ok(msg):
                m = re.match(r"(\d{4}-\d\d-\d\d): (\d+) bars, expected", msg)
                if not m:
                    return False
                day, n = m.group(1), int(m.group(2))
                # a reduced count is accepted only on a date listed as short in tools/market_calendar.py (review)
                from market_calendar import SHORT
                short_day = date.fromisoformat(day) in SHORT
                return (n >= 800 and short_day) or (n == 0 and (day[5:] in ("12-25", "01-01") or day in ("2025-04-18", "2026-04-03")))   # + Good Fridays
            hard = [x for x in problems if not short_ok(x)]
            if hard:
                sys.exit("incomplete bars - nothing written: " + "; ".join(hard))
        elif problems:
            sys.exit("incomplete bars - nothing written: " + "; ".join(problems))

        stamp = now.strftime("%Y%m%dT%H%M%SZ")
        slug = re.sub(r"[^a-z0-9_-]+", "_", args.name.lower()).strip("_") or "account"
        base = os.path.realpath(os.path.join(ROOT, "data", "raw"))
        out = os.path.realpath(os.path.join(base, slug, f"rates_{args.symbol}_M1_{stamp}"))
        if os.path.commonpath([base, out]) != base:
            sys.exit("output path escaped data/raw")
        os.makedirs(out)
        path = os.path.join(out, "bars.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(FIELDS)
            w.writerows(rows)
        with open(path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        manifest = {
            "account_name": args.name, "server": info.server, "symbol": args.symbol,
            "timeframe": "M1", "time_note": "bar open, server time as epoch seconds",
            "since_utc": since.isoformat(), "pulled_utc": now.isoformat(),
            "rows": len(rows), "months": months, "sha256": digest,
            "completeness": f"every weekday {since.date()}..{last_full} checked against tools/market_calendar.py",
            "accepted_calendar_problems": problems if args.accept_short_days else [],
        }
        with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        print(f"ok: {len(rows)} bars -> {out}")
    finally:
        mt5.shutdown()
        _kill_by_path(args.terminal)


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
