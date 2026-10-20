import re, sys, os, time, json, html, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'mql')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
def get(url,fn):
    p=os.path.join(D,fn)
    if os.path.exists(p): return open(p,encoding='utf-8').read()
    s=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=40).read().decode('utf-8','replace')
    open(p,'w',encoding='utf-8').write(s); time.sleep(1.0); return s
def num(x):
    x=html.unescape(x).replace('\xa0','').replace(' ','').replace('%','')
    m=re.match(r'(-?[\d\.]+)([KM]?)',x)
    if not m: return None
    v=float(m.group(1)); return v*(1e3 if m.group(2)=='K' else 1e6 if m.group(2)=='M' else 1)
rows=[]
for mt in ('mt5','mt4'):
    for pg in range(1,80):
        url=f'https://www.mql5.com/en/signals/{mt}/list' + (f'/page{pg}' if pg>1 else '')
        try: s=get(url,f'{mt}_p{pg}.html')
        except Exception as e: print('ERR',url,e); break
        cards=s.split('<div class="row signal">')[1:]
        if not cards: break
        for c in cards:
            g=lambda cls: (re.search(r'class="%s[^"]*"[^>]*>(.*?)</div>'%cls,c,re.S) or [None,''])[1]
            idm=re.search(r'/en/signals/(\d+)',c); 
            if not idm: continue
            rows.append(dict(mt=mt,id=idm.group(1),name=html.unescape((re.search(r'class="name">(.*?)<',c) or [0,''])[1]),
               real='Real Account' in c, price=re.sub(r'<[^>]+>','',g('col-price')).strip(),
               growth=num(re.sub(r'<[^>]+>','',g('col-growth'))), subs=num(g('col-subscribers')), weeks=num(g('col-weeks')),
               balance=re.sub(r'<[^>]+>|\s+',' ',g('col-balance')).strip(), algo=num(g('col-experts')), trades=num(g('col-trades')),
               win=num(g('col-plus')), pf=num(g('col-pf')), dd=num(re.sub(r'<[^>]+>','',g('col-drawdown'))), lev=g('col-leverage').strip()))
        print(mt,pg,len(cards),file=sys.stderr)
json.dump(rows,open(os.path.join(D,'all.json'),'w'),indent=0)
print(len(rows))
