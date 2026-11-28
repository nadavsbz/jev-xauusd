#!/usr/bin/env python3
"""t368 prices (run only after PREREG hashed). Keys from ~/.secure/alpaca_paper.env; never printed/written."""
import os, time, sys, json
from pathlib import Path
import requests, pandas as pd
def _load():
    d={}
    for l in (Path.home()/'.secure/alpaca_paper.env').read_text().splitlines():
        l=l.strip()
        if '=' in l and not l.startswith('#'): k,v=l.split('=',1); d[k.strip()]=v.strip().strip('"').strip("'")
    return d['ALPACA_KEY_ID'], d['ALPACA_SECRET_KEY']
K,S=_load(); H={'APCA-API-KEY-ID':K,'APCA-API-SECRET-KEY':S}
OUT=Path('/workspace/t368/data')
def get(url, params):
    for i in range(8):
        r=requests.get(url,params=params,headers=H,timeout=60)
        if r.status_code==429: time.sleep(10+5*i); continue
        if r.status_code>=500: time.sleep(5); continue
        if r.status_code!=200: sys.exit(f'HTTP {r.status_code} {r.text[:150].replace(K,"x").replace(S,"x")}')
        time.sleep(0.4); return r.json()
    raise RuntimeError('retries')
def bars(url, symbols, tf, start, end, extra):
    out={s:[] for s in symbols}; tok=None
    while True:
        p=dict(symbols=','.join(symbols),timeframe=tf,start=start,end=end,limit=10000,**extra)
        if tok: p['page_token']=tok
        j=get(url,p)
        for s,v in (j.get('bars') or {}).items(): out[s]+=v
        tok=j.get('next_page_token')
        if not tok: break
    return out
SURL='https://data.alpaca.markets/v2/stocks/bars'
d=bars(SURL,['SPY','QQQ'],'1Day','2024-12-01','2026-11-21',dict(feed='sip',adjustment='all',asof='-'))
for s,v in d.items():
    df=pd.DataFrame(v); df['date']=pd.to_datetime(df.t).dt.tz_convert('America/New_York').dt.date
    df[['date','o','h','l','c','v']].to_csv(OUT/f'{s}_daily.csv',index=False); print(s,len(df),df.date.min(),df.date.max())
c=bars('https://data.alpaca.markets/v1beta3/crypto/us/bars',['BTC/USD'],'1Hour','2024-12-01T00:00:00Z','2026-11-21T00:00:00Z',{})
b=pd.DataFrame(c['BTC/USD']); b['t_et']=pd.to_datetime(b.t).dt.tz_convert('America/New_York')
b[['t','t_et','o','h','l','c','v']].to_csv(OUT/'BTC_1h_alpaca.csv',index=False); print('BTC',len(b),b.t.min(),b.t.max())
# 1-min for RTH events
ev=pd.read_csv(OUT/'EVENTS_PRIMARY_locked.csv'); cal=pd.DataFrame(json.load(open(OUT/'calendar_2025_2026.json')))
cal=cal.set_index('date')
rows=[]
for _,e in ev.iterrows():
    ts=pd.Timestamp(e.first_ts_et); d=str(ts.date())
    if d in cal.index and str(pd.Timestamp(e.day1).date())==d:
        o=pd.Timestamp(d+' '+cal.loc[d,'open']); cl=pd.Timestamp(d+' '+cal.loc[d,'close'])
        if o<=ts<cl: rows.append(d)
print('RTH events',len(rows))
allm=[]
for d in sorted(set(rows)):
    st=pd.Timestamp(d+' 09:30',tz='America/New_York').tz_convert('UTC').isoformat(); en=pd.Timestamp(d+' 16:01',tz='America/New_York').tz_convert('UTC').isoformat()
    m=bars(SURL,['SPY','QQQ'],'1Min',st,en,dict(feed='sip',adjustment='all',asof='-'))
    for s,v in m.items():
        x=pd.DataFrame(v); x['sym']=s; allm.append(x)
M=pd.concat(allm); M['t_et']=pd.to_datetime(M.t).dt.tz_convert('America/New_York'); M[['sym','t','t_et','o','h','l','c','v']].to_csv(OUT/'SPY_QQQ_1m_rth_events.csv',index=False); print('1m rows',len(M))
