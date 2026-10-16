import json,sys,os,re,time,urllib.request,datetime as dt
sys.stdout.reconfigure(encoding='utf-8')
rows={r['t']:r for r in json.load(open('dwx/verified.json'))}
out=[]
for t in sys.argv[1:]:
    p=f'dwx/bi_{t}.json'
    if not os.path.exists(p):
        s=urllib.request.urlopen(urllib.request.Request(f'https://www.darwinexzero.com/api/products/{t}/basic-info',headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read().decode()
        open(p,'w').write(s); time.sleep(0.5)
    b=json.load(open(p)); ta=b.get('tradingAccount',{}); pr=b.get('product',{})
    acc=dt.datetime.utcfromtimestamp(ta.get('creationDate',0)/1000)
    s=open(f'dwx/pages/{t}.html',encoding='utf-8').read()
    data=json.loads(re.search(r'"ALL":\s*(\[\[.*?\]\])',s,re.S).group(1))
    ts=[(dt.datetime.utcfromtimestamp(a/1000),v) for a,v in data]
    sub=[x for x in ts if x[0]>=acc]
    yrs=(sub[-1][0]-sub[0][0]).days/365.25
    cagr=((sub[-1][1]/sub[0][1])**(1/yrs)-1)*100
    pk=0;mdd=0
    for d,v in sub:
        pk=max(pk,v); mdd=min(mdd,v/pk-1)
    # yearly returns (calendar) on verified part
    yr={}
    for d,v in sub: yr.setdefault(d.year,[v,v]); yr[d.year][1]=v
    prev=None; ys=[]
    for y in sorted(yr):
        st=prev or yr[y][0]; ys.append(f"{y}:{(yr[y][1]/st-1)*100:+.0f}%"); prev=yr[y][1]
    r=rows.get(t,{})
    print(t, ta.get('connectionType'), ta.get('accountType'), ta.get('assetFamilyType'), 'acc', acc.date(), 'quote_from', ts[0][0].date(), '| verified yrs %.1f cagr %.1f mdd %.1f'%(yrs,cagr,mdd*100), '| r1', r.get('r1'), '| inv', r.get('investors'), 'aum', r.get('aum'), 'dx', r.get('dxcap'), '|', ' '.join(ys))
