"""Round 103 data: Alpaca market data (read-only, key from git-ignored alpaca_key.json, never printed).
Stages (resumable, cached in data/raw/alpaca/):
  assets  -> assets.json (us_equity, status=all: active + inactive/delisted)
  daily   -> daily/<batch>.csv.gz  raw daily bars 2015-11-01..today for all tradable-class symbols
  or5     -> or5/<YYYY-MM-DD>.csv.gz  09:30 ET 5Min bar for the day's filter candidates
  m1      -> m1/<YYYY-MM-DD>.csv.gz   1Min bars 09:30-16:00 ET for the day's top-20 RV stocks
Usage: py -3.12 research/orb/alpaca_dl.py assets|daily|or5|m1"""
import json, os, sys, time, urllib.request, urllib.parse, urllib.error
import pandas as pd
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
K = json.load(open("alpaca_key.json")); H = {"APCA-API-KEY-ID": K["key_id"], "APCA-API-SECRET-KEY": K["secret"]}
RAW = "data/raw/alpaca"; os.makedirs(RAW, exist_ok=True)
DATA = "https://data.alpaca.markets/v2/stocks/bars"
last = [0.0]

def get(url):
    for k in range(8):
        wait = 0.31 - (time.time() - last[0])                      # free plan: 200 requests/min
        if wait > 0: time.sleep(wait)
        last[0] = time.time()
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=60))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504): time.sleep(5 * (k + 1)); continue
            raise
        except Exception:
            time.sleep(5 * (k + 1))
    raise RuntimeError("giving up on a request")

def bars(symbols, tf, start, end):
    out, tok, symbols = [], None, list(symbols)
    while symbols:
        q = dict(symbols=",".join(symbols), timeframe=tf, start=start, end=end, feed="sip", adjustment="raw", limit=10000)
        if tok: q["page_token"] = tok
        try:
            d = get(DATA + "?" + urllib.parse.urlencode(q))
        except urllib.error.HTTPError as e:
            m = e.read().decode(errors="ignore")
            if e.code == 400 and "invalid symbol:" in m:                      # drop the bad ticker and restart this batch
                bad = m.split("invalid symbol:")[1].split('"')[0].strip(); symbols.remove(bad); out, tok = [], None; continue
            raise
        for s, bl in (d.get("bars") or {}).items():
            for b in bl: b["s"] = s; out.append(b)
        tok = d.get("next_page_token")
        if not tok: break
    return pd.DataFrame(out)

stage = sys.argv[1]
if stage == "assets":
    A = json.load(urllib.request.urlopen(urllib.request.Request("https://paper-api.alpaca.markets/v2/assets?asset_class=us_equity&status=all", headers=H), timeout=120))
    json.dump(A, open(f"{RAW}/assets.json", "w"))
    print(len(A), "assets;", sum(a["status"] == "active" for a in A), "active")

elif stage == "daily":
    A = json.load(open(f"{RAW}/assets.json"))
    import re
    syms = sorted({a["symbol"] for a in A if a["exchange"] in ("NYSE", "NASDAQ", "ARCA", "AMEX", "BATS") and re.fullmatch(r"[A-Z]{1,5}", a["symbol"])})
    print(len(syms), "symbols", flush=True)
    os.makedirs(f"{RAW}/daily", exist_ok=True)
    B = 100
    for i in range(0, len(syms), B):
        f = f"{RAW}/daily/{i // B:04d}.csv.gz"
        if os.path.exists(f): continue
        df = bars(syms[i:i + B], "1Day", "2015-11-01", (pd.Timestamp.now() - pd.Timedelta(days=2)).strftime("%Y-%m-%d"))
        df.to_csv(f, index=False) if len(df) else pd.DataFrame({"s": []}).to_csv(f, index=False)
        print(f"daily batch {i // B + 1}/{(len(syms) + B - 1) // B}: {len(df)} bars", flush=True)

def daily_all():
    D = pd.concat([pd.read_csv(f) for f in sorted(__import__("glob").glob(f"{RAW}/daily/*.csv.gz"))], ignore_index=True)
    D = D.dropna(subset=["t"]); D["d"] = pd.to_datetime(D.t).dt.tz_convert("America/New_York").dt.tz_localize(None).dt.normalize()
    return D.sort_values(["s", "d"])

def candidates(D):
    """paper filters, all known before the open of day d except the open price itself (open > $5)."""
    g = D.groupby("s")
    pc = g.c.shift(1)
    tr = pd.concat([D.h - D.l, (D.h - pc).abs(), (D.l - pc).abs()], axis=1).max(axis=1)
    D = D.assign(atr=tr.groupby(D.s).transform(lambda x: x.rolling(14).mean().shift(1)),
                 av=g.v.transform(lambda x: x.rolling(14).mean().shift(1)))
    return D[(D.o > 5) & (D.av >= 1_000_000) & (D.atr > 0.5)][["s", "d", "o", "atr"]]

def et(d, hh, mm):
    return pd.Timestamp(d).replace(hour=hh, minute=mm).tz_localize("America/New_York").tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")

if stage in ("or5", "m1", "cand"):
    C = candidates(daily_all()); C.to_csv(f"{RAW}/candidates.csv.gz", index=False)
    days = sorted(C.d.unique()); print(len(C), "candidate rows over", len(days), "days", flush=True)

if stage == "or5":
    os.makedirs(f"{RAW}/or5", exist_ok=True)
    byday = C.groupby("d").s.apply(set)
    for i, d in enumerate(days):
        f = f"{RAW}/or5/{pd.Timestamp(d):%Y-%m-%d}.csv.gz"
        if os.path.exists(f): continue
        need = set().union(*[byday.get(x, set()) for x in days[i:i + 15]])      # candidates today or in the next 14 days (RV denominators)
        need = sorted(need); parts = []
        for j in range(0, len(need), 200):
            b = bars(need[j:j + 200], "5Min", et(d, 9, 30), et(d, 9, 34))
            if len(b): parts.append(b)
        (pd.concat(parts) if parts else pd.DataFrame({"s": []})).to_csv(f, index=False)
        if i % 50 == 0: print(f"or5 {i + 1}/{len(days)} {pd.Timestamp(d):%Y-%m-%d} symbols {len(need)}", flush=True)

def selection():
    """top-20 relative volume per day among the day's candidates (RV >= 1). RV = today's 09:30 5Min volume / mean of the previous 14 days' (2-sided data, past only)."""
    import glob
    O = pd.concat([pd.read_csv(f).assign(d=pd.Timestamp(os.path.basename(f)[:10])) for f in sorted(glob.glob(f"{RAW}/or5/*.csv.gz")) if os.path.getsize(f) > 30], ignore_index=True)
    O = O.sort_values(["s", "d"]); O["den"] = O.groupby("s").v.transform(lambda x: x.rolling(14).mean().shift(1))
    # the previous 14 entries must be the previous 14 trading days: require the 14th-previous row to be at most 21 calendar-trading days back
    O["gap"] = O.groupby("s").d.diff(14).dt.days
    O = O[(O.gap <= 22)]
    O["rv"] = O.v / O.den
    S = C.merge(O[["s", "d", "o", "h", "l", "c", "v", "rv"]].rename(columns={"o": "oo", "h": "oh", "l": "ol", "c": "oc"}), on=["s", "d"])
    S = S[S.rv >= 1.0].sort_values(["d", "rv"], ascending=[True, False]).groupby("d").head(20)
    return S

if stage == "m1":
    S = selection(); S.to_csv(f"{RAW}/selection.csv.gz", index=False)
    os.makedirs(f"{RAW}/m1", exist_ok=True)
    for i, (d, g) in enumerate(S.groupby("d")):
        f = f"{RAW}/m1/{pd.Timestamp(d):%Y-%m-%d}.csv.gz"
        if os.path.exists(f): continue
        b = bars(sorted(g.s), "1Min", et(d, 9, 30), et(d, 15, 59))
        b.to_csv(f, index=False)
        if i % 100 == 0: print(f"m1 {i + 1}/{S.d.nunique()} {pd.Timestamp(d):%Y-%m-%d}", flush=True)
