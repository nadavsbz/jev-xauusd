"""t338 data: Alpaca SIP daily bars, adjustment=all (splits+dividends), same symbol list/batches as research/orb/alpaca_dl.py daily.
Resumable; writes data/raw/alpaca/daily_adj/<batch>.csv.gz. Key from git-ignored alpaca_key.json (never printed).
Usage: py -3.12 research/stable/t338_dl.py"""
import json, os, re, sys, time, urllib.request, urllib.parse, urllib.error
import pandas as pd
K = json.load(open("alpaca_key.json")); H = {"APCA-API-KEY-ID": K["key_id"], "APCA-API-SECRET-KEY": K["secret"]}
RAW = "data/raw/alpaca"; OUT = f"{RAW}/daily_adj"; os.makedirs(OUT, exist_ok=True)
last = [0.0]

def get(url):
    for k in range(8):
        w = 0.31 - (time.time() - last[0])
        if w > 0: time.sleep(w)
        last[0] = time.time()
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504): time.sleep(5 * (k + 1)); continue
            raise
        except Exception:
            time.sleep(5 * (k + 1))
    raise RuntimeError("giving up")

def bars(symbols, start, end):
    out, tok, symbols = [], None, list(symbols)
    while symbols:
        q = dict(symbols=",".join(symbols), timeframe="1Day", start=start, end=end, feed="sip", adjustment="all", limit=10000)
        if tok: q["page_token"] = tok
        try:
            d = get("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q))
        except urllib.error.HTTPError as e:
            m = e.read().decode(errors="ignore")
            if e.code == 400 and "invalid symbol:" in m:
                symbols.remove(m.split("invalid symbol:")[1].split('"')[0].strip()); out, tok = [], None; continue
            raise
        for s, bl in (d.get("bars") or {}).items():
            for b in bl: out.append(dict(s=s, t=b["t"][:10], o=b["o"], h=b["h"], l=b["l"], c=b["c"]))
        tok = d.get("next_page_token")
        if not tok: break
    return pd.DataFrame(out)

A = json.load(open(f"{RAW}/assets.json"))
syms = sorted({a["symbol"] for a in A if a["exchange"] in ("NYSE", "NASDAQ", "ARCA", "AMEX", "BATS") and re.fullmatch(r"[A-Z]{1,5}", a["symbol"])})
B = 100; n = (len(syms) + B - 1) // B
for i in range(0, len(syms), B):
    f = f"{OUT}/{i // B:04d}.csv.gz"
    if os.path.exists(f): continue
    df = bars(syms[i:i + B], "2015-11-01", "2026-11-20")
    (df if len(df) else pd.DataFrame({"s": []})).to_csv(f, index=False)
    if (i // B) % 10 == 0: print(f"batch {i // B + 1}/{n}: {len(df)} bars", flush=True)
print("done")
