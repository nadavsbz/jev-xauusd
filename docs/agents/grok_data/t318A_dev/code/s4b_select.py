import pandas as pd, numpy as np, json, glob
from zoneinfo import ZoneInfo
from cfg import D, FIRST, LAST
ET=ZoneInfo('America/New_York')
cal=[c['date'] for c in json.load(open(D+'calendar.json')) if FIRST<=c['date']<=LAST]
raw=pd.read_parquet(D+'daily_raw.parquet'); adj=pd.read_parquet(D+'daily_split.parquet')
fx=raw.merge(adj,on=['symbol','date'],suffixes=('','_a')); fx['f']=fx.c/fx.c_a
fx=fx.set_index(['symbol','date']).f
F=pd.read_parquet(D+'daily_filter.parquet'); F=F[F['pass']]
rows=[]
for d in cal:
    b=pd.read_parquet(D+f'open5/{d}.parquet')
    if len(b)==0: continue
    b['et']=pd.to_datetime(b.t).dt.tz_convert(ET); b['m']=b.et.dt.hour*60+b.et.dt.minute-570
    b=b[(b.m>=0)&(b.m<5)].sort_values(['symbol','m'])
    g=b.groupby('symbol')
    a=pd.DataFrame({'vol5':g.v.sum(),'n5':g.m.nunique(),
        'o5':g.o.first(),'h5':g.h.max(),'l5':g.l.min(),'c5':g.c.last(),'last_m':g.m.max()})
    b0=b[b.m==0].set_index('symbol')
    a['vol1']=b0.v; a['o1']=b0.o; a['h1']=b0.h; a['l1']=b0.l; a['c1']=b0.c
    a['date']=d; rows.append(a.reset_index())
O=pd.concat(rows)
O['f']=[fx.get((s,d),np.nan) for s,d in zip(O.symbol,O.date)]
O.to_parquet(D+'open_agg.parquet')
# history matrix of opening volumes in adjusted (today-basis via f) terms: vol_adj = vol_raw * f_d
O['v5a']=O.vol5*O.f; O['v1a']=O.vol1.fillna(0)*O.f
V5=O.pivot(index='date',columns='symbol',values='v5a').reindex(cal).fillna(0)
V1=O.pivot(index='date',columns='symbol',values='v1a').reindex(cal).fillna(0)
H5=V5.shift(1).rolling(14).mean(); H1=V1.shift(1).rolling(14).mean()
Oi=O.set_index(['date','symbol'])
sel=[]; stats=[]
for d in sorted(F.date.unique()):
    fd=F[F.date==d].set_index('symbol')
    for ortype in (5,1):
        H=H5 if ortype==5 else H1; Vt=V5 if ortype==5 else V1
        syms=[s for s in fd.index if s in Vt.columns]
        if not syms: continue
        rv=(Vt.loc[d,syms]/H.loc[d,syms]).replace([np.inf],np.nan)
        df=pd.DataFrame({'relvol':rv}); df.index.name=None; df['symbol']=df.index
        idx=[(d,s) for s in df.symbol]
        x=Oi.reindex(idx); x.index=df.index
        if ortype==5: ok=(x.n5==5); O_,Hh,Ll,C_=x.o5,x.h5,x.l5,x.c5
        else: ok=x.o1.notna(); O_,Hh,Ll,C_=x.o1,x.h1,x.l1,x.c1
        df['ok']=ok.fillna(False); df['oro']=O_; df['orh']=Hh; df['orl']=Ll; df['orc']=C_
        n_rv=(df.relvol>=1).sum(); n_bad=((df.relvol>=1)&~df.ok).sum()
        top=df[(df.relvol>=1)&df.ok].sort_values(['relvol','symbol'],ascending=[False,True]).head(20).copy()
        top['rank']=range(1,len(top)+1)
        top['dir']=np.sign(top.orc-top.oro)
        top=top[top.dir!=0]
        top['N']=len(top); top['ortype']=ortype; top['date']=d
        top['atr']=fd.loc[top.symbol,'atr'].values
        sel.append(top.reset_index(drop=True))
        stats.append((d,ortype,len(fd),int(n_rv),int(n_bad),len(top)))
S=pd.concat(sel); S.to_parquet(D+'selected.parquet')
st=pd.DataFrame(stats,columns=['date','ortype','n_filter','n_relvol_ge1','n_or_missing_excluded','n_selected_nondoji'])
st.to_csv(D+'select_stats.csv',index=False)
print(st.groupby('ortype')[['n_filter','n_relvol_ge1','n_or_missing_excluded','n_selected_nondoji']].agg(['mean','sum']))
print('S4B_DONE symbol-days',len(S),'unique sym-days',S[['date','symbol']].drop_duplicates().shape[0])
