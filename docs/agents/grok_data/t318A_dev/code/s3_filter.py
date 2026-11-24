import pandas as pd, numpy as np, json
from cfg import D, FIRST, LAST
cal=[c['date'] for c in json.load(open(D+'calendar.json')) if FIRST<=c['date']<=LAST]
raw=pd.read_parquet(D+'daily_raw.parquet'); adj=pd.read_parquet(D+'daily_split.parquet')
m=raw.merge(adj,on=['symbol','date'],suffixes=('','_a')); del raw, adj
m=m[m.date.isin(cal)].copy()
m['f']=m.c/m.c_a
out=[]
for s,g in m.groupby('symbol',sort=False):
    g=g.set_index('date').reindex(cal)
    pc=g.c_a.shift(1)
    tr=np.maximum(g.h_a,pc)-np.minimum(g.l_a,pc)
    have=g.c_a.notna().astype(float)
    n14=have.shift(1).rolling(14).sum()
    atr=tr.shift(1).rolling(14).mean()
    av=g.v_a.shift(1).rolling(14).mean()
    f=g.f
    d=pd.DataFrame({'symbol':s,'o':g.o,'f':f,'atr':atr*f,'avgvol':av/f,'n14':n14})
    d=d[g.o.notna()]
    out.append(d.reset_index().rename(columns={'index':'date'}))
F=pd.concat(out)
F['pass']=(F.o>5)&(F.avgvol>=1e6)&(F.atr>0.5)&(F.n14==14)
F.to_parquet(D+'daily_filter.parquet')
P=F[F['pass']]
print('rows',len(F),'pass rows',len(P),'symbols passing>=1',P.symbol.nunique(),'per day mean',P.groupby('date').size().mean(),flush=True)
json.dump(sorted(P.symbol.unique().tolist()),open(D+'cand_symbols.json','w'))
