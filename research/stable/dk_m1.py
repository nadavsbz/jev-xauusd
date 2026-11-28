"""Download Dukascopy M1 BID candles (one bi5 file per day) for FX pairs, for t312 (FX fix reversal, Grok t307 #1).
Files: data/raw/dukascopy/<PAIR>/m1/YYYY-MM-DD.bi5 (git-ignored). Months in the URL are 0-based. Skips existing files and Saturdays.
Polite: one request at a time, 0.7s pause, long back-off on 429. Usage: py -3.12 research/stable/dk_m1.py EURUSD,GBPUSD 2010 2026"""
import os, sys, time, urllib.error, urllib.request
from datetime import date, timedelta


def one(pair, d):
    p = os.path.join("data", "raw", "dukascopy", pair, "m1", f"{d}.bi5")
    if os.path.exists(p): return 0
    url = f"https://datafeed.dukascopy.com/datafeed/{pair}/{d.year}/{d.month - 1:02d}/{d.day:02d}/BID_candles_min_1.bi5"
    for k in range(12):
        try:
            b = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
            os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "wb").write(b); time.sleep(0.7); return len(b)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "wb").close(); return 0
            time.sleep(120 * (k + 1) if e.code == 429 else 1 + k)
        except Exception:
            time.sleep(1 + k)
    print("FAILED", url, flush=True); return -1


if __name__ == "__main__":
    pairs = sys.argv[1].split(","); y0, y1 = int(sys.argv[2]), int(sys.argv[3])
    end = min(date(y1 + 1, 1, 1), date.today() - timedelta(days=1))
    for pair in pairs:
        d, n, tot = date(y0, 1, 1), 0, 0
        while d < end:
            if d.weekday() != 5:
                tot += max(one(pair, d), 0); n += 1
                if n % 250 == 0: print(pair, d, n, f"{tot / 1e6:.0f}MB", flush=True)
            d += timedelta(days=1)
        print("done", pair, n, flush=True)
