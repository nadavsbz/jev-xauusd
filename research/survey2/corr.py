import csv,json,re,sys,datetime as dt,math
sys.stdout.reconfigure(encoding='utf-8')
g={}
for row in csv.DictReader(open('D:/Claude/jev/data/raw/black_dragon_1/rates_XAUUSDc_M1_20261016T110437Z/bars.csv')):
    d=dt.datetime.utcfromtimestamp(int(row['time'])).date(); g[d]=float(row['close'])
gd=sorted(g); gr={gd[i]:g[gd[i]]/g[gd[i-1]]-1 for i in range(1,len(gd))}
def ser(t):
    s=open(f'dwx/pages/{t}.html',encoding='utf-8').read()
    data=json.loads(re.search(r'"ALL":\s*(\[\[.*?\]\])',s,re.S).group(1))
    v={}
    for a,q in data: v[dt.datetime.utcfromtimestamp(a/1000).date()]=q
    return v
worst=sorted(gr,key=lambda d:gr[d])[:10]; best=sorted(gr,key=lambda d:-gr[d])[:10]
print('gold days',len(gr),gd[0],gd[-1]); print('worst gold days',[(str(d),round(gr[d]*100,1)) for d in worst])
for t in sys.argv[1:]:
    v=ser(t); vd=sorted(v); vr={vd[i]:v[vd[i]]/v[vd[i-1]]-1 for i in range(1,len(vd))}
    common=[d for d in gr if d in vr]
    x=[gr[d] for d in common]; y=[vr[d] for d in common]
    n=len(x); mx=sum(x)/n; my=sum(y)/n
    c=sum((a-mx)*(b-my) for a,b in zip(x,y))/math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y)+1e-18)
    w=[vr[d]*100 for d in worst if d in vr]; b=[vr[d]*100 for d in best if d in vr]
    print(t,'n',n,'corr %.2f'%c,'| avg on 10 worst gold days %.2f%% (min %.2f%%)'%(sum(w)/max(len(w),1),min(w) if w else 0),'| avg on 10 best gold days %.2f%%'%(sum(b)/max(len(b),1)))
