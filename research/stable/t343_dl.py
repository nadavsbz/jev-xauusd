"""t343 data: Binance public BTCUSDT 1m klines (data.binance.vision, no registration) 2020-01 .. 2026-11-20 into data/raw/binance/.
Usage: py -3.12 research/stable/t343_dl.py"""
import os, time, urllib.request
import pandas as pd
OUT = "data/raw/binance"; os.makedirs(OUT, exist_ok=True)
B = "https://data.binance.vision/data/spot"
urls = [f"{B}/monthly/klines/BTCUSDT/1m/BTCUSDT-1m-{m:%Y-%m}.zip" for m in pd.date_range("2020-01-01", "2026-10-01", freq="MS")]
urls += [f"{B}/daily/klines/BTCUSDT/1m/BTCUSDT-1m-{d:%Y-%m-%d}.zip" for d in pd.date_range("2026-11-01", "2026-11-20")]
for u in urls:
    f = f"{OUT}/{os.path.basename(u)}"
    if os.path.exists(f): continue
    for k in range(5):
        try:
            open(f, "wb").write(urllib.request.urlopen(u, timeout=120).read()); break
        except Exception as e:
            print("retry", u, e, flush=True); time.sleep(10 * (k + 1))
print("done", len(os.listdir(OUT)))
