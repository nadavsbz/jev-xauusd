import sys,json,time,csv,urllib.request
from datetime import date,datetime,timezone,timedelta
sys.path.insert(0,'/workspace/research_new_component/code')
import download_data as D
from pathlib import Path
OUT=Path('data')
# SGE
req=urllib.request.Request("https://www.sge.com.cn/graph/Dailyhq",data=b"instid=Au99.99",headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/x-www-form-urlencoded"},method="POST")
(OUT/'sge_au9999.json').write_bytes(urllib.request.urlopen(req,timeout=60).read()); print('sge ok',flush=True)
# Yahoo CNY=X
raw=D.fetch("https://query1.finance.yahoo.com/v8/finance/chart/CNY=X?period1=1451606400&period2=1795000000&interval=1d")
(OUT/'yahoo_CNYX.json').write_bytes(raw); print('cny ok',flush=True)
# Dukascopy XAUUSD H1
sc=D.probe_scale('XAUUSD',date(2024,1,15),2030.0)
D.download_dukascopy_h1('XAUUSD',date(2016,10,1),date(2026,11,10),sc,OUT/'XAUUSD_1h.csv')
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
