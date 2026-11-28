# Alpaca client. Keys loaded from ~/.secure/alpaca_paper.env; never printed/logged.
import os, time, requests, threading
def _load():
    p=os.path.expanduser('~/.secure/alpaca_paper.env'); d={}
    for line in open(p):
        line=line.strip()
        if '=' in line and not line.startswith('#'):
            k,v=line.split('=',1); d[k.strip()]=v.strip().strip('"').strip("'")
    return d['ALPACA_KEY_ID'], d['ALPACA_SECRET_KEY']
_K,_S=_load()
H={'APCA-API-KEY-ID':_K,'APCA-API-SECRET-KEY':_S}
S=requests.Session(); S.headers.update(H)
_lock=threading.Lock(); _times=[]
MAXPM=180
def _throttle():
    with _lock:
        now=time.time()
        while _times and now-_times[0]>60: _times.pop(0)
        if len(_times)>=MAXPM:
            time.sleep(60-(now-_times[0])+0.05)
        _times.append(time.time())
def get(url, params=None, tries=8):
    for i in range(tries):
        _throttle()
        try:
            r=S.get(url, params=params, timeout=60)
        except Exception as e:
            time.sleep(2+2*i); continue
        if r.status_code==429: time.sleep(10+5*i); continue
        if r.status_code>=500: time.sleep(3+3*i); continue
        r.raise_for_status(); return r.json()
    raise RuntimeError('failed %s'%url)
def bars(symbols, timeframe, start, end, adjustment='raw', feed='sip'):
    url='https://data.alpaca.markets/v2/stocks/bars'
    out={}; tok=None
    while True:
        p={'symbols':','.join(symbols),'timeframe':timeframe,'start':start,'end':end,'limit':10000,'adjustment':adjustment,'feed':feed,'asof':'-'}
        if tok: p['page_token']=tok
        j=get(url,p)
        for s,b in (j.get('bars') or {}).items(): out.setdefault(s,[]).extend(b)
        tok=j.get('next_page_token')
        if not tok: return out
