import pandas as pd, numpy as np, glob, sys
sys.path.insert(0,'/workspace/t384_m2')
SP=pd.read_csv('in/t391_tester_spread/t391_spread.csv.gz').drop_duplicates(['time_msc','bid','ask']).sort_values('time_msc').reset_index(drop=True)
TM=SP.time_msc.values; BID=SP.bid.values; ASK=SP.ask.values; SPD=SP.spread_points.values
def asof(ms):
    j=np.searchsorted(TM,ms,side='right')-1
    ok=(j>=0)&(ms-TM[np.clip(j,0,None)]<=5000)
    return np.where(ok,j,-1)
# ---- b20 entries
def episodes(d):
    d=d.copy(); d['lvl']=0
    for side in ['buy','sell']:
        vol=0.0; L=0
        for i in d.index[d.side==side]:
            q=d.at[i,'vol_per_100k']
            if d.at[i,'dir']=='in':
                if vol<1e-9: L=0
                L+=1; d.at[i,'lvl']=L; vol+=q
            else: vol-=q
            if vol<1e-9: vol=0.0
    return d
rows=[]
for f in sorted(glob.glob('/workspace/t389/in/t384_tester/*_b.csv.gz')):
    seg=f.split('/')[-1][:11]; d=pd.read_csv(f,parse_dates=['ts'])
    d['side']=np.where(((d.dir=='in')&(d.type=='buy'))|((d.dir!='in')&(d.type=='sell')),'buy','sell')
    d=episodes(d); e=d[d.dir=='in'].copy(); e['seg']=seg; rows.append(e)
B=pd.concat(rows); B['ms']=(B.ts-pd.Timestamp('1970-01-01')).dt.total_seconds().astype(np.int64)*1000
B=B.drop_duplicates(['ts','type','price','lvl'])  # same entry may appear in overlapping segments
for nm,off in (('reg',0),('sens',999)):
    j=asof(B.ms.values+off); B[f'sp_{nm}']=np.where(j>=0,SPD[np.clip(j,0,None)],np.nan)
# exact fill-tick match within [ms, ms+999]
ex=[]
for ms,typ,p in zip(B.ms.values,B.type.values,B.price.values):
    a=np.searchsorted(TM,ms,side='left'); b=np.searchsorted(TM,ms+999,side='right')
    q=ASK[a:b] if typ=='buy' else BID[a:b]; k=np.where(np.abs(q-p)<0.005)[0]
    ex.append(SPD[a+k[0]] if len(k) else np.nan)
B['sp_exact']=ex
def dist(s):
    s=s.dropna(); return dict(n=len(s),med=s.median(),p95=s.quantile(.95),mx=s.max(),gt20=round((s>20).mean(),3),gt50=round((s>50).mean(),3),gt200=int((s>200).sum()))
out=[]
for pop,m in (('b20_first',B.lvl==1),('b20_adds',B.lvl>=2)):
    for c in ['sp_reg','sp_sens','sp_exact']: out.append(dict(pop=pop,quote=c,**dist(B.loc[m,c])))
# ---- live records
L=pd.read_csv('/workspace/t391/t391_timestamps.csv')
L['ms']=(pd.to_datetime(L.ts_server)-pd.Timestamp('1970-01-01')).dt.total_seconds().mul(1000).round().astype(np.int64)
j=asof(L.ms.values); ok=j>=0; jj=np.clip(j,0,None)
L['t_bid']=np.where(ok,BID[jj],np.nan); L['t_ask']=np.where(ok,ASK[jj],np.nan); L['t_sp']=np.where(ok,SPD[jj],np.nan); L['t_age_ms']=np.where(ok,L.ms-TM[jj],np.nan)
L['fill_minus_tq']=np.where(L.side=='BUY',L.live_price-L.t_ask,L.live_price-L.t_bid)
for pop in ['crash','news','open','evt_add']:
    m=L.population.str.contains(pop); out.append(dict(pop='live_'+pop,quote='tester_asof',**dist(L.loc[m,'t_sp'])))
O=pd.DataFrame(out); print(O.to_string())
print('clock check: live fill - tester quote (same side): med',L.fill_minus_tq.median(),'MAD',(L.fill_minus_tq-L.fill_minus_tq.median()).abs().median(),'|x|<=0.02 frac',(L.fill_minus_tq.abs()<=0.02).mean(),'n',L.fill_minus_tq.notna().sum())
for sh in (-3600000,3600000):
    j2=asof(L.ms.values+sh); ok2=j2>=0; v=np.where(L.side=='BUY',L.live_price-ASK[np.clip(j2,0,None)],L.live_price-BID[np.clip(j2,0,None)])[ok2]
    print('shift',sh/3.6e6,'h n',ok2.sum(),'med|x|',np.median(np.abs(v)) if len(v) else None)
B.to_csv('out/t391b_b20_entries_spread.csv',index=False); L.to_csv('out/t391b_live_tester_quotes.csv',index=False); O.to_csv('out/t391b_dist.csv',index=False)
