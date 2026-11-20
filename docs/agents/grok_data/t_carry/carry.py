import pandas as pd, numpy as np, io
D='data/'; C=['EUR','JPY','GBP','CHF','AUD','NZD','CAD']
fx={'EUR':('DEXUSEU',1),'JPY':('DEXJPUS',-1),'GBP':('DEXUSUK',1),'CHF':('DEXSZUS',-1),'AUD':('DEXUSAL',1),'NZD':('DEXUSNZ',1),'CAD':('DEXCAUS',-1)}
ir={'USD':'US','EUR':'EZ','JPY':'JP','GBP':'GB','CHF':'CH','AUD':'AU','NZD':'NZ','CAD':'CA'}
def rd(p): s=pd.read_csv(p,index_col=0,parse_dates=True).iloc[:,0]; return pd.to_numeric(s,errors='coerce')
# USD value of 1 unit currency
px=pd.DataFrame({c:(rd(D+f'{fx[c][0]}.csv') if fx[c][1]==1 else 1/rd(D+f'{fx[c][0]}.csv')) for c in C}).ffill().dropna()
R=pd.DataFrame({c:rd(D+f'IR3TIB01{ir[c]}M156N.csv') for c in ir})
R.loc[R.index<'2002-04-01','JPY']=R.loc[R.index<'2002-04-01','JPY'].fillna(0.10)
# publication lag 1 month
R=R.shift(1)
# markup from RF table
sw=pd.read_csv('rf_swaps.csv'); sw=sw[sw.swap_mode==1]
R26=pd.DataFrame({c:rd('data26/'+f'IR3TIB01{ir[c]}M156N.csv') for c in ir}).ffill().iloc[-1]
p26=pd.DataFrame({c:(rd('data26/'+f'{fx[c][0]}.csv') if fx[c][1]==1 else 1/rd('data26/'+f'{fx[c][0]}.csv')) for c in C}).ffill().iloc[-1]; p26['USD']=1.0
mL=[];mS=[]
for r in sw.itertuples():
    b,q=r.symbol[:3],r.symbol[3:]; price=p26[b]/p26[q]
    aL=r.swap_long*r.point*365/price*100; aS=r.swap_short*r.point*365/price*100
    d=R26[b]-R26[q]; mL.append(d-aL); mS.append(-d-aS)
m=(np.mean(mL)+np.mean(mS))/2
print(f'markup long {np.mean(mL):.2f}%/y short {np.mean(mS):.2f}%/y avg m={m:.2f}%/y')
ret=px.pct_change().dropna(); ret['USD']=0.0
days=ret.index
Rd=R.reindex(days,method='ffill')
vix=rd(D+'VIXCLS.csv').reindex(days).ffill()
def run(filt=True,mk=m):
    vol=ret.rolling(60).std()
    w=pd.DataFrame(0.0,index=days,columns=ret.columns); cur=None
    me=days.to_series().groupby(days.to_period('M')).max()
    for t in days:
        if t in me.values or cur is None:
            if pd.isna(Rd.loc[t]).any() or vol.loc[t].isna().any(): continue
            rk=Rd.loc[t].sort_values(); lo,hi=rk.index[:3],rk.index[-3:]
            iv=1/vol.loc[t].replace(0,np.nan).fillna(vol.loc[t][vol.loc[t]>0].mean())
            cur=pd.Series(0.0,index=ret.columns); cur[hi]=iv[hi]/iv[hi].sum(); cur[lo]=-iv[lo]/iv[lo].sum()
        if cur is not None: w.loc[t]=cur
    w=w.shift(1).fillna(0)  # trade at close, earn next day
    gross=(w*ret).sum(1)
    carry=(w*Rd/100/365).sum(1)*(days.to_series().diff().dt.days.fillna(1))  # calendar days
    pv=gross.rolling(60).std()*np.sqrt(252); lev=(0.08/pv).clip(upper=5).shift(1).fillna(0)
    to=w.diff().abs().sum(1)
    r=lev*(gross+carry-(mk/100/365)*days.to_series().diff().dt.days.fillna(1)*1.0)-lev*to*0.0002
    if filt:
        sig=r.rolling(250).std()*np.sqrt(20); r20=r.rolling(20).sum()
        trig=((vix>25)|(r20<-2*sig)).shift(1).fillna(False)
        flat=pd.Series(False,index=days); on=False; mon=None
        for t in days:
            if mon is not None and t.to_period('M')!=mon: on=False
            if trig[t] and not on: on=True; mon=t.to_period('M')
            flat[t]=on
        r=r.where(~flat,0.0)
    return r
def stats(r,a,b):
    x=r[a:b]; eq=(1+x).cumprod(); mdd=(eq/eq.cummax()-1).min()
    mo=(eq.iloc[-1])**(1/(len(x)/21))-1; sh=x.mean()/x.std()*np.sqrt(252)
    yr=x.groupby(x.index.year).apply(lambda s:(1+s).prod()-1)
    return dict(mo_pct=round(mo*100,2),sharpe=round(sh,2),mdd_pct=round(mdd*100,1),pos_years=f'{(yr>0).sum()}/{len(yr)}',worst_yr=round(yr.min()*100,1))
out={}
for name,kw in {'filter':dict(filt=True),'nofilter':dict(filt=False),'filter_stress_m+1':dict(filt=True,mk=m+1),'filter_stress_2m':dict(filt=True,mk=2*m),'filter_zero_markup(gross)':dict(filt=True,mk=0)}.items():
    r=run(**kw); out[name]=r
    print(name,'DEV',stats(r,'2000','2012'),'| HOLDOUT',stats(r,'2013','2025'))
r=out['filter']; r['2013':'2025'].to_csv('carry_daily_holdout_filter.csv')
print('holdout yearly (filter):',(r['2013':'2025'].groupby(r['2013':'2025'].index.year).apply(lambda s:(1+s).prod()-1)*100).round(1).to_dict())
