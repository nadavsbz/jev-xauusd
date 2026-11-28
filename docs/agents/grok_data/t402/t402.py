
import pandas as pd, numpy as np, json
d=pd.read_csv('in/i2_deals_2020_2026.csv',parse_dates=['ts'])
d['net']=d.profit_pct+d.swap_pct+d.commission_pct
ins=d[d.dir=='in'].reset_index(drop=True); outs=d[d.dir=='out'].reset_index(drop=True)
assert len(ins)==len(outs)
T=pd.DataFrame({'year':ins.year,'t_in':ins.ts,'t_out':outs.ts,'side':ins.type,'p_in':ins.price,'p_out':outs.price,'vol':ins.vol_per_100k,'net':ins.net.values+outs.net.values})
T['sgn']=np.where(T.side=='buy',1,-1); T['pts']=(T.p_out-T.p_in)*T.sgn
T['hold']=(T.t_out-T.t_in).dt.total_seconds()/60
# pct per point per vol: from gross
g=outs.profit_pct.values; k=np.median(g[T.pts!=0]/(T.pts[T.pts!=0]*T.vol[T.pts!=0]))
T['stress']=T.net-1.0*T.vol*k
ok=(T.t_out>=T.t_in).all()
# concurrency
ev=pd.concat([pd.DataFrame({'t':T.t_in,'c':1}),pd.DataFrame({'t':T.t_out,'c':-1})]).sort_values(['t','c']); maxconc=int(ev.c.cumsum().max())
out={'n_trades':len(T),'order_ok':bool(ok),'maxconc':maxconc,'hold_med_min':float(T.hold.median()),'hold_p10':float(T.hold.quantile(.1)),'k_pct_per_pt_vol':float(k),'pts_mean':round(T.pts.mean(),2),'pts_med':round(T.pts.median(),2),'win%':round((T.net>0).mean()*100,1),'long%':round((T.side=='buy').mean()*100,1)}
yr={}; mon=[]
for y,g2 in T.groupby('year'):
  g2=g2.sort_values('t_out'); eq=100+g2.net.cumsum(); dd=float(((np.maximum.accumulate(np.r_[100,eq.values])[1:]-eq.values)/np.maximum.accumulate(np.r_[100,eq.values])[1:]).max()*100)
  m=g2.set_index('t_out').net.resample('ME').sum(); e=100+m.cumsum(); prev=np.r_[100,e.values[:-1]]; r=m.values/prev
  mon+=list(zip(m.index.strftime('%Y-%m'),r))
  yr[int(y)]={'net%':round(g2.net.sum(),1),'stress_net%':round(g2.stress.sum(),1),'ddc%':round(dd,1),'n':len(g2)}
M=pd.Series(dict(mon)); w=M[M.index>='2022-01']
geo=lambda s:((1+s).prod()**(1/len(s))-1)*100
out['geo_all']=round(geo(M),2); out['geo_2022']=round(geo(w),2); out['geo_2022_live_x0.5']=round(geo(w*0.5),2)
day=T.groupby(T.t_out.dt.date).net.sum(); out['top10_share%']=round(day.nlargest(10).sum()/T.net.sum()*100,1)
w2=T[T.year>=2022]; dd2=w2.groupby(w2.t_out.dt.date).net.sum(); out['top10_share_2022%']=round(dd2.nlargest(10).sum()/w2.net.sum()*100,1)
out['years']=yr
Y=[yr[y] for y in yr if y>=2022]
gate={'1_geo>=3.5':out['geo_2022']>=3.5,'2_dd<=25':all(v['ddc%']<=25 for v in Y),'3_top10<=50':out['top10_share%']<=50,'4_noStack':maxconc<=1,'5_hold>=15':out['hold_med_min']>=15,'6_stress+':all(v['stress_net%']>0 for v in Y),'7_years>=4/5':sum(v['net%']>0 for v in Y)>=4}
out['gate']=gate; out['PASS']=all(gate.values())
print(json.dumps(out,indent=1,default=str)); json.dump(out,open('RESULTS_t402.json','w'),indent=1,default=str)
