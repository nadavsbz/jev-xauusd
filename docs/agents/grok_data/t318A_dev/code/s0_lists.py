# DEV universe sources (PREREG §3): Wayback snapshots of nasdaqtrader symbol files 2015-07..2021-12 (all available
# snapshots, max one per calendar month per file) + FINRA CNMS daily short-volume files (from 08.2018), every 5th trading day.
import requests, os, time, json, alp
D='/workspace/t318A_dev/data/'
def cal():
    fn=D+'calendar.json'
    if not os.path.exists(fn):
        r=alp.S.get('https://paper-api.alpaca.markets/v2/calendar',params={'start':'2015-11-01','end':'2021-12-31'},timeout=60); r.raise_for_status()
        json.dump(r.json(),open(fn,'w'))
    return json.load(open(fn))
C=cal(); print('calendar',len(C),C[0]['date'],C[-1]['date'],flush=True)
def get(url,tries=6):
    for i in range(tries):
        try:
            r=requests.get(url,timeout=120)
            if r.status_code==200: return r.content
        except Exception: pass
        time.sleep(3+3*i)
    return None
for f in ['nasdaqlisted','otherlisted','nasdaqtraded']:
    cdx=get(f'https://web.archive.org/cdx/search/cdx?url=nasdaqtrader.com/dynamic/symdir/{f}.txt&from=201507&to=202112&filter=statuscode:200&fl=timestamp&collapse=timestamp:6')
    ts=cdx.decode().split()
    for t in ts:
        fn=D+f'symlists/{f}_{t}.txt'
        if os.path.exists(fn): continue
        b=get(f'https://web.archive.org/web/{t}id_/http://www.nasdaqtrader.com/dynamic/SymDir/{f}.txt')
        if b and b'|' in b[:300]: open(fn,'wb').write(b); print('ok',f,t,len(b),flush=True)
        else: print('FAIL',f,t,flush=True)
days=[c['date'] for c in C if c['date']>='2018-08-01']
for d in days[::5]:
    fn=D+f"finra/CNMSshvol{d.replace('-','')}.txt"
    if os.path.exists(fn): continue
    b=get(f"https://cdn.finra.org/equity/regsho/daily/CNMSshvol{d.replace('-','')}.txt")
    if b: open(fn,'wb').write(b)
    else: print('FAIL finra',d,flush=True)
print('S0_DONE',len(os.listdir(D+'symlists')),len(os.listdir(D+'finra')),flush=True)
