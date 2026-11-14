"""Download daily OHLC of the four indices from Yahoo's public chart API (docs/THIRD_COMPONENT_PLAN.md).
Saves data/raw/yahoo/<name>.csv (date, open, high, low, close). Read-only, no login.
Usage: python research/third/fetch_yahoo.py"""
import csv, json, os, time, urllib.request

TICKERS = {"NDX": "%5ENDX", "SPX": "%5EGSPC", "DAX": "%5EGDAXI", "N225": "%5EN225"}
OUT = "data/raw/yahoo"

def fetch(sym):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=946684800&period2={int(time.time())}&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research script)"})
    return json.load(urllib.request.urlopen(req, timeout=60))["chart"]["result"][0]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, sym in TICKERS.items():
        r = fetch(sym); q = r["indicators"]["quote"][0]; n = 0
        with open(f"{OUT}/{name}.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["date", "open", "high", "low", "close"])
            for t, o, h, l, c in zip(r["timestamp"], q["open"], q["high"], q["low"], q["close"]):
                if c is None: continue
                w.writerow([time.strftime("%Y-%m-%d", time.gmtime(t + r["meta"].get("gmtoffset", 0))), o, h, l, c]); n += 1
        print(name, n, "days")
