
import pandas as pd, numpy as np, json, glob
W=json.load(open('/workspace/t421/RESULTS_t421.json'))
Wl={int(k):v for k,v in W['W_long'].items()}; Ws={int(k):v for k,v in W['W_short'].items()}
b=pd.read_csv('/workspace/t295/in/USTECHCash.csv'); b['t']=pd.to_datetime(b.time,unit='s'); b=b.set_index('t')
out={}; allT=[]
for f in sorted(glob.glob('/workspace/t423/tt/t423_lev195_*.csv')):
    y=int(f[-8:-4]); d=pd.read_csv(f,parse_dates=['ts'])
    ins=d[d.dir=='in'].reset_index(drop=True); outs=d[d.dir=='out'].reset_index(drop=True)
    # stacking check: open count per side over time
    open_={'buy':0,'sell':0}; mx=0
    for r in d.itertuples():
        if r.dir=='in': open_[r.type]+=1; mx=max(mx,open_[r.type])
        else: k='sell' if r.type=='buy' else 'buy'; open_[k]-=1
    assert len(ins)==len(outs)
    eq_in=ins.balance-ins.commission  # balance before entry commission
    T=pd.DataFrame({'year':y,'tin':ins.ts,'tout':outs.ts,'side':np.where(ins.type=='buy','long','short'),'lev':ins.volume*ins.price/eq_in})
    T['hold_h']=(T.tout-T.tin).dt.total_seconds()/3600
    T['h']=np.minimum(6,np.maximum(1,np.ceil(T.hold_h))).astype(int)
    T['W']=[ (Wl if s=='long' else Ws)[h] for s,h in zip(T.side,T.h)]
    T['L']=T.lev*T.W
    T['L_cap']=np.minimum(T.lev,1.95)*T.W
    net=(d.profit+d.swap+d.commission).sum()
    bal=pd.concat([pd.Series([120000.0]),d.balance]); cdd=float((1-bal/bal.cummax()).max()*100)
    out[y]=dict(net_pct=round(net/1200,2),closed_dd=round(cdd,2),max_lev=round(float(T.lev.max()),3),n_lev_gt_tol=int((T.lev>1.95*1.02).sum()),n=len(T),
        maxL=round(float(T.L.max())*100,2),maxL_side=T.side[T.L.idxmax()],n_L_gt25=int((T.L>0.25).sum()),maxL_capped=round(float(T.L_cap.max())*100,2),
        med_hold_min=round(float(T.hold_h.median()*60),1),max_open_side=mx)
    allT.append(T)
A=pd.concat(allT)
tot=dict(net_sum=round(sum(v['net_pct'] for v in out.values()),2),pos_years=int(sum(v['net_pct']>0 for v in out.values())),
  maxL=round(float(A.L.max())*100,2),n_L_gt25=int((A.L>0.25).sum()),n_lev_gt_tol=int((A.lev>1.989).sum()),max_lev=round(float(A.lev.max()),3),
  worst=A.loc[A.L.idxmax(),['year','tin','side','h','lev']].astype(str).to_dict(), max_closed_dd=max(v['closed_dd'] for v in out.values()))
print(json.dumps(out,indent=0,default=str)); print(json.dumps(tot,indent=0,default=str))
json.dump(dict(years=out,total=tot),open('/workspace/t423/RESULTS_t423.json','w'),indent=1,default=str)

