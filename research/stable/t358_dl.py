"""t358 data: all inactive (delisted) NYSE/NASDAQ/AMEX symbols from Alpaca /v2/assets?status=inactive. Based on t353: Alpaca serves history for delisted symbols when asked by symbol; our bulk download used only the current asset list.
Fetch raw (c,v) and adjusted (o,c) daily bars 2017-10..2026-11-20 for every t353 event symbol missing from data/raw/alpaca/daily.
Writes data/raw/alpaca/daily_extra/<n>.csv.gz (raw) and daily_adj_extra/<n>.csv.gz. Key from git-ignored alpaca_key.json (never printed)."""
import glob, json, os, re, time, urllib.request, urllib.parse, urllib.error
import pandas as pd
K = json.load(open("alpaca_key.json")); H = {"APCA-API-KEY-ID": K["key_id"], "APCA-API-SECRET-KEY": K["secret"]}
R = "data/raw/alpaca"; os.makedirs(f"{R}/daily_extra", exist_ok=True); os.makedirs(f"{R}/daily_adj_extra", exist_ok=True)
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


def bars(symbols, adj):
    out, tok, symbols = [], None, list(symbols)
    while symbols:
        q = dict(symbols=",".join(symbols), timeframe="1Day", start="2017-10-01", end="2026-11-21", feed="sip", adjustment=adj, limit=10000)
        if tok: q["page_token"] = tok
        try: d = get("https://data.alpaca.markets/v2/stocks/bars?" + urllib.parse.urlencode(q))
        except urllib.error.HTTPError as e:
            m = e.read().decode(errors="ignore")
            if e.code == 400 and "invalid symbol:" in m:
                symbols.remove(m.split("invalid symbol:")[1].split('"')[0].strip()); out, tok = [], None; continue
            raise
        for s, bl in (d.get("bars") or {}).items():
            for b in bl: out.append(dict(s=s, t=b["t"], o=b["o"], h=b["h"], l=b["l"], c=b["c"], v=b["v"]))
        tok = d.get("next_page_token")
        if not tok: break
    return pd.DataFrame(out)


have = set()
for f in glob.glob(f"{R}/daily/*.csv.gz") + glob.glob(f"{R}/daily_extra/*.csv.gz"): have |= set(pd.read_csv(f, usecols=["s"]).s)
A = json.load(open(f"{R}/assets_inactive.json"))
syms = sorted({a["symbol"] for a in A if a["exchange"] in ("NYSE", "NASDAQ", "AMEX") and re.fullmatch(r"[A-Z]{1,5}", a["symbol"])} - have)
print("missing symbols to fetch", len(syms), flush=True)
B = 50
for i in range(0, len(syms), B):
    n = i // B; fr, fa = f"{R}/daily_extra/i{n:04d}.csv.gz", f"{R}/daily_adj_extra/i{n:04d}.csv.gz"
    if os.path.exists(fr) and os.path.exists(fa): continue
    raw = bars(syms[i:i + B], "raw"); raw.to_csv(fr, index=False)
    adj = bars(syms[i:i + B], "all")
    if len(adj): adj["t"] = adj.t.str[:10]
    adj.to_csv(fa, index=False)
    print(n, len(raw), len(adj), flush=True)
print("done")
