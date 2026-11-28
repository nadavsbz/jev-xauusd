"""t365 downloader: Binance USD-M public data (data.binance.vision). 5m OI metrics (daily files) + 5m klines (monthly files).
Usage: py -3.12 research/stable/t365_dl.py"""
import os, time, urllib.request
import pandas as pd
B = "https://data.binance.vision/data/futures/um"; OUT = "data/raw/binance"
for s in ("BTCUSDT", "ETHUSDT"):
    for sub in ("metrics", "klines5m"):
        os.makedirs(f"{OUT}/{sub}/{s}", exist_ok=True)


def get(url, f):
    if os.path.exists(f): return True
    for k in range(4):
        try:
            b = urllib.request.urlopen(url, timeout=60).read(); open(f, "wb").write(b); time.sleep(0.05); return True
        except urllib.error.HTTPError as e:
            if e.code == 404: return False
            time.sleep(2 * (k + 1))
        except Exception:
            time.sleep(2 * (k + 1))
    return False


miss = []
for s in ("BTCUSDT", "ETHUSDT"):
    for m in pd.period_range("2021-12", "2026-10", freq="M"):
        if not get(f"{B}/monthly/klines/{s}/5m/{s}-5m-{m}.zip", f"{OUT}/klines5m/{s}/{s}-5m-{m}.zip"): miss.append(f"k {s} {m}")
    for d in pd.date_range("2021-12-01", "2026-10-31"):
        d = d.strftime("%Y-%m-%d")
        if not get(f"{B}/daily/metrics/{s}/{s}-metrics-{d}.zip", f"{OUT}/metrics/{s}/{s}-metrics-{d}.zip"): miss.append(f"m {s} {d}")
    print(s, "done; missing so far", len(miss), flush=True)
print("missing", len(miss), miss[:20])
