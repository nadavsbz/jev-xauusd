#!/usr/bin/env python3
"""t363: download SPY/QQQ daily (2024-2026) and 1-min windows from Alpaca.
SIP for historical; IEX only for today's 'recent' bars (SIP subscription blocks recent SIP).
Keys from ~/.secure/alpaca_paper.env; never printed/logged/written.
"""
import os, time, sys
from pathlib import Path
import requests
import pandas as pd

def _load():
    d = {}
    p = Path.home() / ".secure/alpaca_paper.env"
    for line in p.read_text().splitlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    kid, sec = d["ALPACA_KEY_ID"], d["ALPACA_SECRET_KEY"]
    if not kid or not sec:
        sys.exit("missing alpaca keys")
    print(f"keys_loaded names=ALPACA_KEY_ID,ALPACA_SECRET_KEY lens={len(kid)},{len(sec)}", flush=True)
    return kid, sec

K, S_ = _load()
SESS = requests.Session()
SESS.headers.update({"APCA-API-KEY-ID": K, "APCA-API-SECRET-KEY": S_})
URL = "https://data.alpaca.markets/v2/stocks/bars"
MIN_INTERVAL = 1.2
_last = [0.0]
OUT = Path("/workspace/t363/data")
OUT.mkdir(parents=True, exist_ok=True)
nreq = [0]

def get(params):
    for i in range(10):
        dt = time.time() - _last[0]
        if dt < MIN_INTERVAL:
            time.sleep(MIN_INTERVAL - dt)
        _last[0] = time.time()
        try:
            r = SESS.get(URL, params=params, timeout=60)
        except Exception as e:
            print("net_err", type(e).__name__, flush=True)
            time.sleep(3 + 3 * i)
            continue
        if r.status_code == 429:
            print("rate_limited, backoff", flush=True)
            time.sleep(15 + 10 * i)
            continue
        if r.status_code >= 500:
            print("http", r.status_code, "retry", flush=True)
            time.sleep(5 + 5 * i)
            continue
        if r.status_code != 200:
            body = r.text[:180].replace(K, "[redacted]").replace(S_, "[redacted]")
            print("HTTP", r.status_code, "body_len", len(r.text), "body_head", body)
            sys.exit(1)
        nreq[0] += 1
        return r.json()
    raise RuntimeError("failed after retries")

def fetch_bars(symbols, timeframe, start, end, feed="sip", adjustment="all"):
    rows_by = {s: [] for s in symbols}
    tok = None
    while True:
        p = {
            "symbols": ",".join(symbols),
            "timeframe": timeframe,
            "start": start,
            "end": end,
            "limit": 10000,
            "adjustment": adjustment,
            "feed": feed,
        }
        if tok:
            p["page_token"] = tok
        j = get(p)
        bars = j.get("bars") or {}
        for s in symbols:
            rows_by[s].extend(bars.get(s, []))
        tok = j.get("next_page_token")
        if not tok:
            break
    return rows_by

def to_df(rows):
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["t"] = pd.to_datetime(df["t"], utc=True)
    df = df.sort_values("t").drop_duplicates("t")
    return df

print("fetch daily SPY,QQQ SIP through 2026-11-20", flush=True)
daily = fetch_bars(["SPY", "QQQ"], "1Day", "2024-01-01T00:00:00Z", "2026-11-21T00:00:00Z", feed="sip")
for s, rows in daily.items():
    df = to_df(rows)
    path = OUT / f"{s}_daily_2024_2026.csv"
    df.to_csv(path, index=False)
    print(s, "daily", len(df), "first", None if df.empty else str(df["t"].iloc[0]), "last", None if df.empty else str(df["t"].iloc[-1]), flush=True)

# Try IEX daily including today (may be empty until close)
print("fetch daily IEX including today (may be incomplete)", flush=True)
daily_iex = fetch_bars(["SPY", "QQQ"], "1Day", "2026-11-20T00:00:00Z", "2026-11-24T00:00:00Z", feed="iex")
for s, rows in daily_iex.items():
    df = to_df(rows)
    path = OUT / f"{s}_daily_iex_recent.csv"
    df.to_csv(path, index=False)
    print(s, "iex_daily_recent", len(df), "last", None if df.empty else str(df["t"].iloc[-1]), flush=True)

windows = [
    ("E1", "2026-11-03T00:00:00-05:00", "2026-11-07T00:00:00-05:00", "sip"),
    ("E2", "2026-11-16T00:00:00-05:00", "2026-11-20T00:00:00-05:00", "sip"),
    ("E3_fri", "2026-11-20T00:00:00-05:00", "2026-11-21T00:00:00-05:00", "sip"),
    ("E3_mon", "2026-11-23T00:00:00-05:00", "2026-11-24T00:00:00-05:00", "iex"),
]
for name, start, end, feed in windows:
    print("fetch 1min", name, feed, flush=True)
    mm = fetch_bars(["SPY", "QQQ"], "1Min", start, end, feed=feed)
    for s, rows in mm.items():
        df = to_df(rows)
        path = OUT / f"{s}_1m_{name}.csv"
        df.to_csv(path, index=False)
        print(s, name, "bars", len(df), "first", None if df.empty else str(df["t"].iloc[0]), "last", None if df.empty else str(df["t"].iloc[-1]), flush=True)

print("DONE requests", nreq[0], flush=True)
