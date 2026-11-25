import sys; sys.path.insert(0,'/workspace/t384_m2')
from common import *
from scipy.stats import spearmanr
K=0.1
def tester_eq(seg,v,T_end,s,basis):
    d=episodes(load(seg,v))
    first=d[d.dir=='in'].groupby('ep').ts.min(); pre=set(first[first<s.start_srv].index)
    w=d[(d.ts>=s.start_srv)&(d.ts<T_end)&(~d.ep.isin(pre))].copy()
    real=w[w.dir!='in'].net_pct.sum()
    w['q']=np.where(w.side=='buy',1,-1)*np.where(w.dir=='in',1,-1)*w.vol_per_100k
    Q=w.q.sum(); P=price_at(toU([T_end])[0],basis)
    tot_mtm=K*(Q*P-(w.q*w.price).sum()); gross_real=w[w.dir!='in'].profit_pct.sum(); flo=tot_mtm-gross_real
    costs=w.swap_pct.sum()+w.commission_pct.sum()
    return dict(real=real,flo=flo,eq=gross_real+flo+costs,openQ=w.groupby('side').q.sum().abs().round(4).to_dict(),n_pre=len(pre),last=d.ts.max())
EX=['A3_20260227','A3_20260311']
rows=[]
for _,s in S.iterrows():
    seg=s.seg_id
    if s.cut or seg in EX: continue
    basis=MB[seg[:2]]['basis']; r=dict(seg_id=seg,live_m2=s.eq_seg_end_pct,end=s.end_upper_srv,week=s.start_srv.isocalendar().week)
    for v in ['b','b50']:
        o=tester_eq(seg,v,s.end_upper_srv,s,basis); r[f'{v}_m2']=round(o['eq'],4); r[f'{v}_float']=round(o['flo'],4); r[f'{v}_open']=str(o['openQ']); r[f'{v}_cov']=bool(o['last']>=s.end_upper_srv)
    rows.append(r)
R=pd.DataFrame(rows); print(R.to_string())
out={}
for v in ['b','b50']:
    d=R[f'{v}_m2']-R.live_m2
    out[v]=dict(n=len(R),spearman=round(spearmanr(R.live_m2,R[f'{v}_m2']).statistic,3),dev_ratio=round(abs(d.sum())/R.live_m2.abs().sum(),3),
        sumabs_ratio=round(d.abs().sum()/R.live_m2.abs().sum(),3),med_abs_d=round(d.abs().median(),3),sum_live=round(R.live_m2.sum(),2),sum_t=round(R[f'{v}_m2'].sum(),2))
    out[v]['B_pass']=bool(out[v]['spearman']>=0.7 and out[v]['dev_ratio']<=0.3 and out[v]['med_abs_d']<=5)
    print(v,out[v])
R.to_csv('out/t390_M2_normal.csv',index=False); pd.Series(out).to_json('out/t390_M2_stats.json')
