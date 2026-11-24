import re,glob,csv,html
prior=set(open('_prior_ids.txt').read().split())
rows={}
def num(s):
    s=s.replace('\xa0','').replace(' ','').replace(',','')
    m=re.match(r'-?[\d.]+',s); 
    if not m: return None
    v=float(m.group()); 
    if 'K' in s: v*=1e3
    if 'M' in s: v*=1e6
    return v
for f in glob.glob('raw/list/*.html')+glob.glob('raw/list2/*.html'):
    h=open(f,encoding='utf8',errors='ignore').read()
    for blk in h.split('<div class="row signal">')[1:]:
        m=re.search(r'/signals/(\d+)"',blk); 
        if not m: continue
        sid=m.group(1)
        g=lambda c: (re.search(r'class="%s[^"]*"[^>]*>(.*?)</div>'%c,blk,re.S) or [None,''])[1]
        name=html.unescape(re.search(r'<span class="name">(.*?)</span>',blk).group(1))
        pm=re.search(r'Profit/Month: (-?[\d.]+)%',blk)
        real='Real Account' in blk
        r=dict(id=sid,name=name,mt=f.split('/')[-1][:3],real=real,
          growth=num(re.sub('<.*?>','',g('col-growth'))),pm=float(pm.group(1)) if pm else None,
          subs=num(g('col-subscribers')),weeks=num(g('col-weeks')),ea=g('col-experts'),
          trades=num(g('col-trades')),win=g('col-plus'),pf=num(g('col-pf')),
          dd=num(re.sub('<.*?>','',g('col-drawdown'))),lev=g('col-leverage'),prior=sid in prior)
        rows[sid]=r
w=csv.DictWriter(open('list_parsed.csv','w'),fieldnames=list(next(iter(rows.values())).keys()))
w.writeheader(); [w.writerow(r) for r in rows.values()]
print('total',len(rows))
c=[r for r in rows.values() if r['weeks'] and r['weeks']>=78 and r['dd'] is not None and r['dd']<=25 and r['pm'] and r['pm']>=3]
print('screen',len(c),'new',sum(not r['prior'] for r in c))
for r in sorted(c,key=lambda r:-r['pm']):
    print(r['id'],r['mt'],'P' if r['prior'] else 'N',r['real'],r['name'][:30],r['pm'],r['growth'],r['weeks'],r['dd'],r['trades'],r['ea'],r['pf'])
