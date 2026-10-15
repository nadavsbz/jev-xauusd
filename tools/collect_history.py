"""Read-only export of one account's full deal and order history from MT5.

Safety, in order of importance:
  * Never sends, modifies or cancels anything: the only MT5 calls are
    initialize, account_info, history_deals_get, history_orders_get, shutdown.
  * Refuses to run if the account allows trading, i.e. if the password given
    is a master password and not an investor one.
  * Needs an explicit --terminal path, so it can never attach to whatever
    terminal happens to be running (a bare initialize() did that once).
  * Before logging in, demands a clean dedicated terminal: not already
    running, no compiled program under MQL5/Experts, Scripts or Services, no
    auto-start entry (Script=/Expert=/Service=) in config/*.ini, and no saved
    chart with an EA attached. So even if a master password slipped in, there is
    nothing in that terminal that could trade during the moments before the
    trade_allowed check runs.
  * A failed history call aborts; it is never written out as "no trades".
  * Verifies the logged-in account is the one asked for before reading.
  * Credentials are read from a file outside the repo and never printed;
    output is written under data/ (gitignored) with a sha256 manifest.

Usage:
    python tools/collect_history.py --accounts PATH --name "Black Dragon 1" \
        --terminal "C:\MT5_JEV_RO\terminal64.exe" --since 2025-10-01
"""
import argparse
import codecs
import csv
import glob
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import MetaTrader5 as mt5

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_account(path, name):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    accounts = data if isinstance(data, list) else next(
        v for v in data.values() if isinstance(v, list))
    matches = [a for a in accounts if str(a.get("name", "")).strip() == name]
    if len(matches) != 1:
        sys.exit(f"expected exactly one account named {name!r}, found {len(matches)}")
    return matches[0]


def assert_clean_terminal(terminal):
    """Fail closed unless the terminal cannot run anything that trades."""
    root = os.path.dirname(os.path.abspath(terminal))
    for kind in ("Experts", "Scripts", "Services"):
        found = glob.glob(os.path.join(root, "MQL5", kind, "**", "*.ex5"), recursive=True)
        if found:
            sys.exit(f"terminal is not clean: {len(found)} compiled program(s) under MQL5/{kind}")
    for ini in glob.glob(os.path.join(root, "config", "*.ini")):
        with open(ini, "rb") as f:
            raw = f.read()
        text = raw.decode("utf-16", errors="ignore") if raw.startswith(codecs.BOM_UTF16_LE) else raw.decode("utf-8", errors="ignore")
        for line in text.lower().splitlines():
            key = line.split("=", 1)[0].strip()
            if "=" in line and key in ("script", "expert", "service") and line.split("=", 1)[1].strip():
                sys.exit(f"terminal is not clean: {os.path.basename(ini)} auto-starts a program ({key}=)")
    for chart in glob.glob(os.path.join(root, "MQL5", "Profiles", "**", "*.chr"), recursive=True):
        with open(chart, "rb") as f:
            raw = f.read()
        text = raw.decode("utf-16", errors="ignore") if raw.startswith(codecs.BOM_UTF16_LE) else raw.decode("utf-8", errors="ignore")
        if "<expert>" in text.lower():
            sys.exit("terminal is not clean: a saved chart has an EA attached")
    ps = ("Get-CimInstance Win32_Process -Filter \"Name='terminal64.exe'\" | "
          "ForEach-Object { $_.ExecutablePath }")
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                             capture_output=True, text=True, timeout=60, check=True).stdout
    except Exception as e:
        sys.exit(f"cannot verify running terminals ({e.__class__.__name__}) - aborting")
    running = {os.path.normcase(os.path.abspath(x.strip())) for x in out.splitlines() if x.strip()}
    if os.path.normcase(os.path.abspath(terminal)) in running:
        sys.exit("this terminal is already running - close it first so the login is not switched under it")


def write_csv(path, rows):
    if not rows:
        open(path, "w").close()
        return 0
    fields = list(rows[0]._asdict().keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for r in rows:
            w.writerow(r)
    return len(rows)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--accounts", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--terminal", required=True)
    p.add_argument("--since", default="2000-01-01",
                   help="UTC start date; the default covers the account's whole life")
    args = p.parse_args()

    if not os.path.isfile(args.terminal):
        sys.exit("terminal path does not exist")
    acc = load_account(args.accounts, args.name)
    login = int(acc["login"])
    assert_clean_terminal(args.terminal)

    if not mt5.initialize(path=args.terminal, login=login, password=acc["password"],
                          server=acc["server"], portable=True, timeout=60000):
        sys.exit(f"initialize failed: {mt5.last_error()}")
    try:
        info = mt5.account_info()
        if info is None or info.login != login:
            sys.exit("connected to the wrong account - aborting")
        if info.trade_allowed:
            sys.exit("account allows trading (master password?) - refusing, investor only")

        since = datetime.strptime(args.since, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        deals = mt5.history_deals_get(since, now)
        if deals is None:
            sys.exit(f"history_deals_get failed: {mt5.last_error()} - nothing written")
        orders = mt5.history_orders_get(since, now)
        if orders is None:
            sys.exit(f"history_orders_get failed: {mt5.last_error()} - nothing written")

        stamp = now.strftime("%Y%m%dT%H%M%SZ")
        slug = args.name.lower().replace(" ", "_")
        out = os.path.join(ROOT, "data", "raw", slug, stamp)
        os.makedirs(out, exist_ok=True)
        files = {
            "deals.csv": write_csv(os.path.join(out, "deals.csv"), deals),
            "orders.csv": write_csv(os.path.join(out, "orders.csv"), orders),
        }
        manifest = {
            "account_name": args.name,
            "server": acc["server"],
            "currency": info.currency,
            "balance": info.balance,
            "equity": info.equity,
            "leverage": info.leverage,
            "trade_allowed": info.trade_allowed,
            "since_utc": since.isoformat(),
            "pulled_utc": now.isoformat(),
            "time_note": "MT5 deal times are broker server time, not UTC",
            "files": {k: {"rows": n, "sha256": sha256(os.path.join(out, k))}
                      for k, n in files.items()},
        }
        with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"ok: {files['deals.csv']} deals, {files['orders.csv']} orders -> {out}")
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()
