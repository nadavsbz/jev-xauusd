import os,requests,json
d={}
for l in open(os.path.expanduser('~/.secure/alpaca_paper.env')):
    l=l.strip()
    if '=' in l and not l.startswith('#'): k,v=l.split('=',1); d[k.strip()]=v.strip().strip('"').strip("'")
r=requests.get('https://paper-api.alpaca.markets/v2/calendar',params={'start':'2018-12-01','end':'2026-10-01'},
  headers={'APCA-API-KEY-ID':d['ALPACA_KEY_ID'],'APCA-API-SECRET-KEY':d['ALPACA_SECRET_KEY']},timeout=60)
print(r.status_code); c=r.json(); json.dump(c,open('/workspace/t362/data/calendar.json','w')); print(len(c),c[0],c[-1])
print([x for x in c if x['close']!='16:00'][:5])
