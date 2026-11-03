"""Download Dukascopy XAUUSD tick files (bi5, one per hour) for docs/CRASH_LINK_PLAN.md into data/raw/dukascopy/XAUUSD/YYYY/MM/DD/HHh_ticks.bi5
(git-ignored). Months in the URL are 0-based. Skips files already present; weekends skipped. Usage: python dk_download.py 2016 2022"""
import os, sys, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

ROOT = os.path.join("data", "raw", "dukascopy", "XAUUSD")

def one(d, h):
    p = os.path.join(ROOT, f"{d.year}", f"{d.month:02d}", f"{d.day:02d}", f"{h:02d}h_ticks.bi5")
    if os.path.exists(p): return 0
    url = f"https://datafeed.dukascopy.com/datafeed/XAUUSD/{d.year}/{d.month - 1:02d}/{d.day:02d}/{h:02d}h_ticks.bi5"
    for k in range(12):
        try:
            b = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
            os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "wb").write(b); return len(b)
        except urllib.error.HTTPError as e:
            if e.code == 404:                                       # no file for a closed hour: store it empty
                os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "wb").close(); return 0
            time.sleep(30 * (k + 1) if e.code == 429 else 1 + k)   # 429 = rate limited: back off
        except Exception:
            time.sleep(1 + k)
    print("FAILED", url, flush=True); return -1

if __name__ == "__main__":
    y0, y1 = int(sys.argv[1]), int(sys.argv[2])
    d = date(y0, 1, 1); jobs = []
    while d < date(y1 + 1, 1, 1):
        if d.weekday() != 5: jobs += [(d, h) for h in range(24)]
        d += timedelta(days=1)
    with ThreadPoolExecutor(3) as ex:
        tot = 0
        for i, n in enumerate(ex.map(lambda a: one(*a), jobs)):
            tot += max(n, 0)
            if i % 500 == 0: print(f"{i}/{len(jobs)} {tot / 1e6:.0f}MB", flush=True)
    print("done", len(jobs), f"{tot / 1e6:.0f}MB")
