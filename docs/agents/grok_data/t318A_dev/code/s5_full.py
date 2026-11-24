# full RTH 1Min bars for selected symbol-days (union of 5m and 1m Top-20 lists)
import alp, json, os, pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from cfg import D
O=D+'full/'; os.makedirs(O,exist_ok=True)
ET=ZoneInfo('America/New_York'); UTC=ZoneInfo('UTC')
sel=pd.read_parquet(D+'selected.parquet')
def iso(d,hm):
    return datetime.fromisoformat(d+'T'+hm).replace(tzinfo=ET).astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
def job(a):
    d,g=a
    fn=O+d+'.parquet'
    if os.path.exists(fn): return
    S=sorted(g.symbol.unique()); rows=[]
    b=alp.bars(S,'1Min',iso(d,'09:30:00'),iso(d,'15:59:59'))
    for s,bs in b.items():
        for x in bs: rows.append((s,x['t'],x['o'],x['h'],x['l'],x['c'],x['v']))
    df=pd.DataFrame(rows,columns=['symbol','t','o','h','l','c','v'])
    df.to_parquet(fn+'.tmp'); os.replace(fn+'.tmp',fn)
    print('full',d,len(S),len(df),flush=True)

from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(5) as ex: list(ex.map(job,list(sel.groupby('date'))))

print('S5_DONE',flush=True)
