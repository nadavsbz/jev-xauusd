"""Crash days: what a basket stop at level k would have changed, from the clone deals (docs/CRASH_LINK_PLAN.md, static, no compounding).
Usage: python research/growth/crash_stopk.py DIR_WITH_oos_b.csv"""
import sys, pandas as pd, numpy as np
sys.path[:0]=["research/btc","research/bd1"]
import guardian_sim as g
S=sys.argv[1]
B=pd.concat([pd.read_csv('data/derived/crash_signs/baskets.csv'),pd.read_csv(S+'/oos_b.csv')])
D=B[(B.levels>=8)].drop_duplicates(['report','side','t0'])
out=[]
for rep,dd in D.groupby('report'):
    p=g.pair(g.deals(f"C:/MT5_JEV_TEST/{rep}.htm"))[0]
    for _,b in dd.iterrows():
        x=p[(p.side==b.side)&(p.t0>=b.t0)&(p.t0<=b.t1)].sort_values('t0')
        sg=1 if b.side=='buy' else -1
        r={'rep':rep,'cut':b.kind=='cut','net':x.net.sum(),'n':len(x)}
        for k in range(8,15):
            if len(x)>=k: r[f's{k}']=(sg*(x.p0.iloc[k-1]-x.p0.iloc[:k-1])*x.vol.iloc[:k-1]*100).sum()
        out.append(r)
R=pd.DataFrame(out)
print('baskets',len(R))
for k in range(8,15):
    m=R[f's{k}'].notna(); 
    act=R[m].groupby('rep').net.sum()/1000; stop=R[m].groupby('rep')[f's{k}'].sum()/1000
    print(f'stop at L{k}: baskets {m.sum()}, cut among them {R[m].cut.sum()}; gain vs actual by report (k$):', (stop-act).round(0).to_dict(), 'total', round((stop-act).sum()))
