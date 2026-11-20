import json,time,csv,urllib.request
from datetime import datetime,timezone,timedelta
from pathlib import Path
OUT=Path("data")
# Coinbase H1
rows={}
t=datetime(2017,8,1,tzinfo=timezone.utc); end=datetime(2026,11,10,tzinfo=timezone.utc)
while t<end:
    t2=min(t+timedelta(hours=300),end)
    u=f"https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=3600&start={t.strftime('%Y-%m-%dT%H:%M:%SZ')}&end={t2.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    for k in range(5):
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read(); break
        except Exception as e:
            time.sleep(2*(k+1)); r=b'[]'
    for c in json.loads(r): rows[c[0]]=c
    t=t2; time.sleep(0.35)
with open(OUT/'coinbase_BTCUSD_1h.csv','w') as f:
    w=csv.writer(f); w.writerow(['time','low','high','open','close','volume'])
    for k in sorted(rows): w.writerow(rows[k])
print('coinbase',len(rows),flush=True)
