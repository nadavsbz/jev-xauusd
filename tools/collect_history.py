"""Read-only export of one account's full deal and order history from MT5.

Safety, in order of importance:
  * Never sends, modifies or cancels anything: the only MT5 calls are
    initialize, account_info, history_deals_get, history_orders_get, shutdown.
  * Refuses to run if the account allows trading, i.e. if the password given
    is a master password and not an investor one.
  * Needs an explicit --terminal path, so it can never attach to whatever
    terminal happens to be running (a bare initialize() did that once).
  * Verifies the logged-in account is the one asked for before reading.
  * Credentials are read from a file outside the repo and never printed;
    output is written under data/ (gitignored) with a sha256 manifest.

Usage:
    python tools/collect_history.py --accounts PATH --name "Black Dragon 1" \
        --terminal "C:\MT5_JEV_RO\terminal64.exe" --since 2025-10-01
"""
import argparse
import csv
import hashlib
import json
import os
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
    p.add_argument("--since", default="2025-10-01")
    args = p.parse_args()

    if not os.path.isfile(args.terminal):
        sys.exit("terminal path does not exist")
    acc = load_account(args.accounts, args.name)
    login = int(acc["login"])

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
        deals = mt5.history_deals_get(since, now) or ()
        orders = mt5.history_orders_get(since, now) or ()

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
