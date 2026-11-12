"""Download public Binance 1h klines (no account) to data/raw/binance/<SYM>.csv. Usage: python research/scan/get_binance.py XRPUSDT ..."""
import sys, time, json, urllib.request
import pandas as pd
URL = "https://data-api.binance.vision/api/v3/klines?symbol={s}&interval=1h&startTime={t}&limit=1000"
for s in sys.argv[1:]:
    t, rows = 1514764800000, []
    while True:
        k = json.load(urllib.request.urlopen(URL.format(s=s, t=t), timeout=30))
        if not k: break
        rows += [(r[0] // 1000, float(r[1]), float(r[2]), float(r[3]), float(r[4])) for r in k]
        t = k[-1][0] + 3600000
        if len(k) < 1000: break
        time.sleep(0.1)
    pd.DataFrame(rows, columns=["time", "open", "high", "low", "close"]).to_csv(f"data/raw/binance/{s}.csv", index=False)
    print(s, len(rows), pd.to_datetime(rows[0][0], unit="s"), pd.to_datetime(rows[-1][0], unit="s"))
