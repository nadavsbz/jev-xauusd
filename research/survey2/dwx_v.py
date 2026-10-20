import re, json, html, sys, datetime as dt, os, glob
sys.stdout.reconfigure(encoding='utf-8')
rows=[]
for p in glob.glob('dwx/pages/*.html'):
    s=open(p,encoding='utf-8').read()
    m=re.search(r'"ALL":\s*(\[\[.*?\]\])',s,re.S)
    if not m: continue
    ts=[(dt.datetime.utcfromtimestamp(a/1000),v) for a,v in json.loads(m.group(1))]
    tx=re.sub(r'<script.*?</script>|<style.*?</style>',' ',s,flags=re.S); tx=re.sub(r'<[^>]+>',' ',tx); tx=re.sub(r'\s+',' ',html.unescape(tx))
    g=lambda pat:(re.search(pat,tx).group(1) if re.search(pat,tx) else '')
    since=g(r'trading with Darwinex since (\d\d/\d\d/\d{4})')
    inv=g(r'investable since (\d\d/\d\d/\d{4})')
    d0=dt.datetime.strptime(since,'%d/%m/%Y') if since else ts[0][0]
    sub=[x for x in ts if x[0]>=d0]
    if len(sub)<2: continue
    yrs=(sub[-1][0]-sub[0][0]).days/365.25
    cagr=(sub[-1][1]/sub[0][1])**(1/yrs)-1 if yrs>0.2 else 0
    pk=0;mdd=0;md=None
    for d,v in sub:
        pk=max(pk,v); dd=v/pk-1
        if dd<mdd: mdd,md=dd,d
    c2=sub[-1][0]-dt.timedelta(days=730); s2=[x for x in sub if x[0]>=c2]
    r2=((s2[-1][1]/s2[0][1])**0.5-1)*100 if yrs>=2 else None
    c1=sub[-1][0]-dt.timedelta(days=365); s1=[x for x in sub if x[0]>=c1]; r1=(s1[-1][1]/s1[0][1]-1)*100
    # flat check: last 90 days unchanged
    c9=sub[-1][0]-dt.timedelta(days=90); s9=[x[1] for x in sub if x[0]>=c9]; flat=max(s9)-min(s9)<0.01
    rows.append(dict(t=os.path.basename(p)[:-5],since=since,inv=inv,first=str(ts[0][0].date()),yrs=round(yrs,1),cagr=round(cagr*100,1),mdd=round(mdd*100,1),mdd_date=str(md.date()) if md else '',r2=round(r2,1) if r2 is not None else None,r1=round(r1,1),flat=flat,
        ann_page=g(r'Annualized ([\-\d\.]+) %'),ret5=g(r'Return (\d+ years?) ([\-\d\.,]+) %'),investors=g(r'Join (\d[\d,]*) investors'),aum=g(r'total of \$ ([\d,]+)'),dxcap=g(r'Darwinex Invested Capital ([\d,\.]+) €'),assets=g(r'Invest [A-Z]+ (.{0,50}?CFDs)'),provider=g(r'Provided by (\S+)')))
rows.sort(key=lambda r:-(r['cagr']/abs(r['mdd'])) if r['mdd'] else 0)
for r in rows:
    if r['yrs']>=2: print(json.dumps(r,ensure_ascii=False))
json.dump(rows,open('dwx/verified.json','w'),indent=1)
