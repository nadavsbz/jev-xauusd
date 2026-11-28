# 1Min 09:30-09:34 ET. Per day d we request every symbol that passes the daily filter on any of days d..d+14
# (exactly the set whose RelVol uses day d's opening volume); results identical to pulling all candidates every day.
import alp, json, os, pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from cfg import D, FIRST, LAST
O=D+'open5/'; os.makedirs(O,exist_ok=True)
ET=ZoneInfo('America/New_York'); UTC=ZoneInfo('UTC')
cal=[c['date'] for c in json.load(open(D+'calendar.json')) if FIRST<=c['date']<=LAST]
F=pd.read_parquet(D+'daily_filter.parquet',columns=['date','symbol','pass']); F=F[F['pass']]
byday=F.groupby('date').symbol.apply(set).to_dict()
need={}
for i,d in enumerate(cal):
    s=set()
    for dd in cal[i:i+15]: s|=byday.get(dd,set())
    need[d]=sorted(s)
def iso(d,hm): return datetime.fromisoformat(d+'T'+hm).replace(tzinfo=ET).astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
def job(d):
    fn=O+d+'.parquet'
    if os.path.exists(fn): return
    S=need[d]; rows=[]
    for i in range(0,len(S),400):
        b=alp.bars(S[i:i+400],'1Min',iso(d,'09:30:00'),iso(d,'09:34:59'))
        for s,bs in b.items():
            for x in bs: rows.append((s,x['t'],x['o'],x['h'],x['l'],x['c'],x['v']))
    df=pd.DataFrame(rows,columns=['symbol','t','o','h','l','c','v'])
    df.to_parquet(fn+'.tmp'); os.replace(fn+'.tmp',fn)
    print('open5',d,len(S),len(df),flush=True)
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(5) as ex: list(ex.map(job,cal))
print('S4_DONE',flush=True)
