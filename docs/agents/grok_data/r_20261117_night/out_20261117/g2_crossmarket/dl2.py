import sys,csv,time
from datetime import date,datetime,timezone
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,'/workspace/research_new_component/code')
import download_data as D
ms=list(D.months(date(2016,10,1),date(2026,10,31)))
def job(ym):
    y,m=ym; t0=time.time()
    raw=D.fetch(D._duka_hour_url('XAUUSD',y,m),tries=4,timeout=60)
    return ym, (D._decode_candles(raw,datetime(y,m,1),1000.0) if raw else []), time.time()-t0
rows={}
with ThreadPoolExecutor(8) as ex:
    for ym,recs,dt in ex.map(job,ms):
        print(ym,len(recs),round(dt,1),flush=True)
        for r in recs: rows[r[0]]=r
with open('data/XAUUSD_1h.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(["open_time_ms","open","high","low","close","volume","utc"])
    for k in sorted(rows):
        ts,o,h,l,c,v=rows[k]; w.writerow([ts,o,h,l,c,v,datetime.fromtimestamp(ts/1000,tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")])
print('done',len(rows))
