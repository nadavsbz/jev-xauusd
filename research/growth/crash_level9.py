"""Crash days: at level 9, do cut baskets differ from deep baskets that recovered? (docs/CRASH_LINK_PLAN.md)
Usage: python research/growth/crash_level9.py DIR_WITH_oos_b.csv"""
import sys, pandas as pd, numpy as np
sys.path[:0]=["research/btc","research/bd1"]
import guardian_sim as g
from scipy.stats import mannwhitneyu
S=sys.argv[1]
B=pd.concat([pd.read_csv('data/derived/crash_signs/baskets.csv'),pd.read_csv(S+'/oos_b.csv')])
D=B[(B.levels>=9)].drop_duplicates(['report','side','t0'])
h=pd.read_csv('data/derived/intraday/XAUUSD_H1.csv'); h.index=pd.to_datetime(h.time,unit='s'); h=h[~h.index.duplicated()]
c=h.close; atr=(h.high-h.low).rolling(120).mean()
rows=[]
for rep,dd in D.groupby('report'):
    p=g.pair(g.deals(f"C:/MT5_JEV_TEST/{rep}.htm"))[0]
    for _,b in dd.iterrows():
        x=p[(p.side==b.side)&(p.t0>=b.t0)&(p.t0<=b.t1)].sort_values('t0')
        if len(x)<9: continue
        sg=1 if b.side=='buy' else -1; t9=pd.to_datetime(x.t0.iloc[8],unit='s'); t0=pd.to_datetime(x.t0.iloc[0],unit='s')
        i=c.index.searchsorted(t9)-1; j=c.index.searchsorted(t0)-1
        if i<240: continue
        a=atr.iloc[i]
        f=dict(rep=rep,cut=b.kind=='cut',
          against_5d=sg*(c.iloc[i]-c.iloc[i-120])/a,      # >0 basket with 5-day trend
          against_1d=sg*(c.iloc[i]-c.iloc[i-24])/a,
          pre_open_24h=sg*(c.iloc[j]-c.iloc[j-24])/a,     # move before the basket opened, in basket direction
          atr_ratio=atr.iloc[i]/atr.iloc[i-240],
          rng_last6=(h.high.iloc[i-5:i+1].max()-h.low.iloc[i-5:i+1].min())/a,
          spread_lv=(x.p0.iloc[8]-x.p0.iloc[0])*sg/a)
        rows.append(f)
R=pd.DataFrame(rows); print(R.cut.value_counts().to_dict())
for k in R.columns[2:]:
    a=R[R.cut][k].dropna(); b=R[~R.cut][k].dropna(); u,pv=mannwhitneyu(a,b)
    # stability: AUC per period group
    au=[]
    for grp,m in (('19-21',R.rep.str.startswith('d6t')),('22-25',R.rep.str.startswith('rf')),('EG',R.rep=='yearf_live')):
        Rg=R[m]; aa=Rg[Rg.cut][k].dropna(); bb=Rg[~Rg.cut][k].dropna()
        au.append(round(mannwhitneyu(aa,bb)[0]/len(aa)/len(bb),2) if len(aa)>3 else None)
    print(f'{k:14s} AUC {u/len(a)/len(b):.3f} p {pv:.4f} med cut {a.median():.2f} rec {b.median():.2f} by period {au}')
