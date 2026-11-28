"""t355 data: Alpaca SIP 5-min bars (adjustment=all) for 30 fixed large caps + SPY, 2019-01-01..2026-11-20, RTH only.
Resumable per symbol -> data/raw/alpaca/m5_t355/<SYM>.csv.gz. Key from git-ignored alpaca_key.json (never printed)."""
import json, os, sys, time, urllib.request, urllib.parse, urllib.error
import pandas as pd
sys.path.insert(0, "research/stable")
K = json.load(open("alpaca_key.json")); H = {"APCA-API-KEY-ID": K["key_id"], "APCA-API-SECRET-KEY": K["secret"]}
OUT = "data/raw/alpaca/m5_t355"; os.makedirs(OUT, exist_ok=True)
SYMS = ["SPY", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "BRK.B", "JNJ", "JPM", "XOM", "V", "PG", "UNH", "HD", "MA", "INTC", "VZ", "T", "CVX", "PFE",
        "MRK", "BAC", "KO", "CSCO", "PEP", "WFC", "CMCSA", "DIS", "ORCL", "ABT", "NFLX"]
last = [0.0]


def get(url):
    for k in range(8):
        w = 0.31 - (time.time() - last[0])
        if w > 0: time.sleep(w)
        last[0] = time.time()
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504): time.sleep(5 * (k + 1)); continue
            raise
        except Exception: time.sleep(5 * (k + 1))
    raise RuntimeError("giving up")


for s in SYMS:
    f = f"{OUT}/{s}.csv.gz"
    if os.path.exists(f): continue
    out, tok = [], None
    while True:
        q = dict(symbols=s, timeframe="5Min", start="2019-01-01", end="2026-11-21", feed="sip", adjustment="all", limit=10000)
        if tok: q["page_token"] = tok
        d = get("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q))
        for b in (d.get("bars") or {}).get(s, []): out.append((b["t"], b["o"], b["c"]))
        tok = d.get("next_page_token")
        if not tok: break
    df = pd.DataFrame(out, columns=["t", "o", "c"]); df["t"] = pd.to_datetime(df.t, utc=True).dt.tz_convert("America/New_York")
    df = df[(df.t.dt.time >= pd.Timestamp("09:30").time()) & (df.t.dt.time < pd.Timestamp("16:00").time())]
    df.to_csv(f, index=False); print(s, len(df), flush=True)
print("done")
