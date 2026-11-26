
import pandas as pd, numpy as np, json, math
d=pd.read_csv('/workspace/t402/in/i2_deals_2020_2026.csv',parse_dates=['ts'])
b=pd.read_csv('/workspace/t295/in/USTECHCash.csv'); b['t']=pd.to_datetime(b.time,unit='s'); b=b.set_index('t')
B=b[(b.index>='2018-01-01')&(b.index<'2026-11-01')]
o=B.open.values; hi=B.high.values; lo=B.low.values; tt=B.index.values.astype('datetime64[h]').astype(np.int64)
W={'long':{},'short':{}}; WT={'long':{},'short':{}}
n=len(o)
for h in range(1,7):
    mn=np.full(n-h+1,np.inf); mx=np.full(n-h+1,-np.inf)
    for j in range(h):
        mn=np.minimum(mn,lo[j:n-h+1+j]); mx=np.maximum(mx,hi[j:n-h+1+j])
    span=tt[h-1:]-tt[:n-h+1]
    ok=span<=h  # span between first and last bar start <= h hours (h-1 normally; +1 tolerance)
    al=np.where(ok,1-mn/o[:n-h+1],-1); as_=np.where(ok,mx/o[:n-h+1]-1,-1)
    W['long'][h]=float(al.max()); WT['long'][h]=str(B.index[al.argmax()])
    W['short'][h]=float(as_.max()); WT['short'][h]=str(B.index[as_.argmax()])
# pair trades
ins=d[d.dir=='in'].reset_index(drop=True); outs=d[d.dir=='out'].reset_index(drop=True)
assert len(ins)==len(outs)
T=pd.DataFrame({'year':ins.year,'tin':ins.ts,'tout':outs.ts,'side':np.where(ins.type=='buy','long','short'),'pin':ins.price,'pout':outs.price,'v':ins.vol_per_100k,'prof':outs.profit_pct})
sg=np.where(T.side=='long',1,-1)
cs=(T.prof/(T.v*(T.pout-T.pin)*sg/1000)).replace([np.inf,-np.inf],np.nan).median()
T['lev']=T.v*cs*T.pin/100000
T['hold_h']=(T.tout-T.tin).dt.total_seconds()/3600
T['h']=np.minimum(6,np.maximum(1,np.ceil(T.hold_h))).astype(int)
T['W']=[W[s][h] for s,h in zip(T.side,T.h)]
# realised MAE from H1 bars between tin and tout (bars starting >= tin and < tout)
mae=[]
for r in T.itertuples():
    x=b[(b.index>=r.tin)&(b.index<r.tout)]
    if len(x)==0: mae.append(np.nan); continue
    mae.append(1-x.low.min()/r.pin if r.side=='long' else x.high.max()/r.pin-1)
T['mae']=mae
out={'cs':float(cs),'n_trades':len(T),'hold_gt6':int((T.hold_h>6).sum()),'hold_median_h':float(T.hold_h.median()),
     'W_long':W['long'],'W_short':W['short'],'W_long_at':WT['long'],'W_short_at':WT['short'],'arms':{}}
for k in (0.5,1.0,1.25):
    lk=np.minimum(5,k*T.lev); L=lk*T.W; i=L.idxmax()
    yr={}
    for y,g in T.assign(L=L,lk=lk,M=lk*T.mae).groupby('year'):
        yr[int(y)]=dict(max_lev=round(float(g.lk.max()),3),maxL=round(float(g.L.max())*100,2),claude_form=round(float(g.lk.max())*max(W['long'][6],W['short'][6])*100,2),realMAE_x_lev=round(float(g.M.max())*100,2))
    out['arms'][k]=dict(maxL=round(float(L.max())*100,2),at=str(T.tin[i]),side=T.side[i],h=int(T.h[i]),lev=round(float(lk[i]),3),n_gt25=int((L>0.25).sum()),
        claude_form_max=round(float(lk.max())*max(W['long'][6],W['short'][6])*100,2),PASS=bool(L.max()<=0.25),years=yr)
print(json.dumps(out,indent=1))
json.dump(out,open('/workspace/t421/RESULTS_t421.json','w'),indent=1)

