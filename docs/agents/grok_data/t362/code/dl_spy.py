# t362: download SPY 1-min SIP bars from Alpaca, monthly chunks, cached as compressed parquet.
# Keys are read from ~/.secure/alpaca_paper.env into memory only; never printed/logged/written.
import os, time, requests, pandas as pd, sys
def _load():
    d={}
    for line in open(os.path.expanduser('~/.secure/alpaca_paper.env')):
        line=line.strip()
        if '=' in line and not line.startswith('#'):
            k,v=line.split('=',1); d[k.strip()]=v.strip().strip('"').strip("'")
    return d['ALPACA_KEY_ID'], d['ALPACA_SECRET_KEY']
K,S_=_load()
S=requests.Session(); S.headers.update({'APCA-API-KEY-ID':K,'APCA-API-SECRET-KEY':S_})
URL='https://data.alpaca.markets/v2/stocks/bars'
MIN_INTERVAL=1.2   # <=50 req/min, well under 150/min shared budget
_last=[0.0]
def get(p):
    for i in range(10):
        dt=time.time()-_last[0]
        if dt<MIN_INTERVAL: time.sleep(MIN_INTERVAL-dt)
        _last[0]=time.time()
        try: r=S.get(URL,params=p,timeout=60)
        except Exception as e: time.sleep(3+3*i); continue
        if r.status_code==429: time.sleep(15+10*i); continue
        if r.status_code>=500: time.sleep(5+5*i); continue
        if r.status_code!=200:
            print('HTTP',r.status_code,r.text[:200]); sys.exit(1)
        return r.json()
    raise RuntimeError('failed')
OUT='/workspace/t362/data'
months=pd.date_range('2019-01-01','2026-10-01',freq='MS')
nreq=0
for a,b in zip(months[:-1],months[1:]):
    fn=f'{OUT}/SPY_1m_{a:%Y-%m}.parquet'
    if os.path.exists(fn): continue
    rows=[]; tok=None
    while True:
        p={'symbols':'SPY','timeframe':'1Min','start':a.strftime('%Y-%m-%dT00:00:00Z'),'end':b.strftime('%Y-%m-%dT00:00:00Z'),
           'limit':10000,'adjustment':'all','feed':'sip'}
        if tok: p['page_token']=tok
        j=get(p); nreq+=1
        rows.extend((j.get('bars') or {}).get('SPY',[]))
        tok=j.get('next_page_token')
        if not tok: break
    df=pd.DataFrame(rows)
    df.to_parquet(fn+'.tmp',compression='zstd'); os.replace(fn+'.tmp',fn)
    print(a.strftime('%Y-%m'),len(df),'req',nreq,flush=True)
print('DONE',nreq)
