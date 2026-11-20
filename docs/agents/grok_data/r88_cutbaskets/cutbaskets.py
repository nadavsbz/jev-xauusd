import sys; sys.path.insert(0,'/workspace/algotrade/jev-xauusd/research/grok_crash')
import pandas as pd, numpy as np
from run_analysis import ACCOUNTS, load_deals, gold_positions, cluster_positions
rows=[]
for a in ACCOUNTS:
    d=load_deals(a); p,_=gold_positions(d); p=cluster_positions(p)
    for cid,g in p.groupby('cid'):
        t0=g.t0.min(); cut=bool(g.guard.fillna(False).any())
        srv=t0.tz_convert(ACCOUNTS[a]['tz'])
        il=t0.tz_convert('Asia/Jerusalem')
        tcut=g.t1.max() if cut else pd.NaT
        rows.append(dict(acc=a,cid=cid,t0_utc=t0,dow_il=il.day_name()[:3],hour_il=il.hour,dow_srv=srv.day_name()[:3],hour_srv=srv.hour,
            n=len(g),lots=g.volume.sum(),cut=cut,pnl=g.pnl.sum(),age_h=((tcut-t0).total_seconds()/3600 if cut else np.nan)))
B=pd.DataFrame(rows); B=B[B.t0_utc>=pd.Timestamp('2026-04-15',tz='UTC')]
B.to_csv('baskets.csv',index=False)
C=B[B.cut]
print('baskets',len(B),'cut baskets',len(C),'cut days(acc-day)',C.assign(day=C.t0_utc.dt.date).groupby(['acc','day']).ngroups)
order=['Mon','Tue','Wed','Thu','Fri','Sun','Sat']
for k in ['dow_il','dow_srv']:
    t=pd.DataFrame({'all':B[k].value_counts(),'cut':C[k].value_counts()}).reindex(order).dropna(how='all').fillna(0)
    t['cut_rate%']=(100*t.cut/t['all']).round(2); t['cut_pnl']=C.groupby(k).pnl.sum().reindex(t.index).round(0); print('\n',k); print(t)
for k in ['hour_il','hour_srv']:
    t=pd.DataFrame({'all':B[k].value_counts(),'cut':C[k].value_counts()}).sort_index().fillna(0)
    t['rate%']=(100*t.cut/t['all']).round(2); print('\n',k); print(t.T.to_string())
def grp(df,k):
    h=df[k]; return np.where(h.between(11,18),'11-19','out')
for k in ['hour_il','hour_srv']:
    B['h']=grp(B,k); C2=B[B.cut]
    t=pd.DataFrame({'all':B.h.value_counts(),'cut':C2.h.value_counts(),'cut_pnl':C2.groupby('h').pnl.sum(),'all_pnl':B.groupby('h').pnl.sum()}).fillna(0)
    t['rate%']=(100*t.cut/t['all']).round(2); print('\n',k,'bucket'); print(t.round(0))
B['thfr']=B.dow_srv.isin(['Thu','Fri'])
t=B.groupby('thfr').agg(all=('cut','size'),cut=('cut','sum'),pnl=('pnl','sum'),cut_pnl=('pnl',lambda s: s[B.loc[s.index,'cut']].sum()))
t['rate%']=(100*t.cut/t['all']).round(2); print('\nThu/Fri (server)'); print(t.round(0))
B['keep']=(~B.thfr)&B.hour_srv.between(11,18)
t=B.groupby('keep').agg(all=('cut','size'),cut=('cut','sum'),pnl=('pnl','sum')); t['rate%']=(100*t.cut/t['all']).round(2)
print('\nms20_h1119-like filter (non Thu/Fri & srv 11-19 start)'); print(t.round(0))
for per,(s,e) in {'tune':('2026-04-15','2026-09-01'),'holdout':('2026-09-01','2026-12-01')}.items():
    X=B[(B.t0_utc>=pd.Timestamp(s,tz='UTC'))&(B.t0_utc<pd.Timestamp(e,tz='UTC'))]
    print(per,'thfr cut rate',X.groupby('thfr').cut.mean().round(4).to_dict(),'keep cut rate',X.groupby('keep').cut.mean().round(4).to_dict(),'n cut',int(X.cut.sum()))
print('\nmedian age h of cut baskets',C.age_h.median().round(1))
