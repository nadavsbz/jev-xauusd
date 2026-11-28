import pandas as pd, numpy as np, json
P=pd.read_pickle('P394.pkl'); TR=pd.read_pickle('TR394.pkl')
T76={'BD1':'A1','BD2':'A2','BD3':'A3','BTC_Bot_4':'A4','BD5':'A5','BD6':'A6','BD7':'A7','BD8':'A8'}; EG={'A1','A8'}
ev=pd.read_csv('/workspace/bridge_pending/delivered_t376/t376_events.csv'); ev['a']=ev.acc.map(T76)
ev['ta']=pd.to_datetime(ev.start)+np.where(ev.a.isin(EG),pd.Timedelta(hours=1),pd.Timedelta(0))
ev['ref']=-ev.real_loss_pct*ev.bal_before/100
rows=[]; evpos=set()
for r in ev.itertuples():
    m=(P.acc==r.a)&(P.t_open<=r.ta+pd.Timedelta(seconds=1))&(P.t_close>=r.ta-pd.Timedelta(seconds=5))&(P.t_close<=r.ta+pd.Timedelta(seconds=300))
    x=P[m]; evpos|=set(x.index)
    act=x.pnl.sum(); sav=-x[x.blocked].pnl.sum(); savm=-x[x.blocked].mtm.sum()
    # blocked before protection?
    bb=P[(P.acc==r.a)&P.basket.isin(x.basket)&P.blk_first&(P.t_open<=r.ta)]
    rows.append(dict(ev=f'{r.a}@{r.ta}',a=r.a,day=r.ta.floor('D'),hour=r.ta.floor('h'),ref=r.ref,act=act,repro=abs(act-r.ref)<=0.01*abs(r.ref),
        n_pos=len(x),n_blk=int(x.blocked.sum()),cf=act+sav,sav=sav,sav_mtm=savm,blk_before=len(bb)>0))
E=pd.DataFrame(rows)
print(E[['ev','ref','act','repro','n_pos','n_blk','cf','sav','blk_before']].round(0).to_string())
# all-baskets
evb=set(P.loc[list(evpos),'basket'])
nonev=P[~P.basket.isin(evb)]
forg_all=nonev[nonev.blocked].pnl.sum()
live_nonev=nonev.groupby('basket').pnl.sum(); live_nonev_profit=live_nonev.sum()
aff=nonev[nonev.basket.isin(nonev[nonev.blocked].basket)]; live_aff=aff.pnl.sum()
# fleet-level NetSaving
NS=-P[P.blocked].pnl.sum()
bl=P[P.blocked]; forg_pos=bl[bl.pnl>0].pnl.sum(); cost_sav=-bl.cost.sum()
surv_aff=P[(~P.blocked)&P.basket.isin(bl.basket)]
stress_extra=(0.11*100*surv_aff.volume).sum()
NS_stress=-(bl[bl.pnl<=0].pnl.sum()) - 2*forg_pos + 0  # losses avoided unchanged, forgone x2
# adjust cost: blocked pnl already includes costs; stress halves the cost saving: subtract half of cost_sav
NS_stress=NS_stress - 0.5*cost_sav - stress_extra
# groups
g=pd.read_csv('/workspace/t387/t387_groups.csv'); gh=g[g.level=='hour']; gd=g[(g.level=='day')&(g.n_acc>=3)]
def grp_rows(key):
    k=pd.Timestamp(key); return E[E.hour==k]
G=[]
for r in gh.itertuples():
    k=pd.Timestamp(r.key); accs=r.accounts.split('|'); x=E[(E.hour==k)&E.a.isin(accs)]
    d0=k.floor('D'); d1=d0+pd.Timedelta(days=1)
    # peak |L| in that Athens day (TR in UTC -> approx shift by 2-3h; use UTC day window of Athens day)
    u0=pd.Timestamp(d0).tz_localize('Europe/Athens').tz_convert('UTC').tz_localize(None); u1=pd.Timestamp(d1).tz_localize('Europe/Athens').tz_convert('UTC').tz_localize(None)
    tr=TR[(TR.tu>=u0)&(TR.tu<u1)]
    G.append(dict(key=r.key,accs=r.accounts,n_found=len(x),full_repro=bool(len(x)>=len(accs) and x.repro.all()),loss_act=x.act.sum(),loss_cf=x.cf.sum(),
        peakL_act=tr.L_act.abs().max(),peakL_cf=tr.L_cf.abs().max()))
G=pd.DataFrame(G); G['peak_red']=1-G.peakL_cf/G.peakL_act
D3=[]
for r in gd.itertuples():
    d=pd.Timestamp(r.key).floor('D'); x=E[E.day==d]; D3.append(dict(day=d,blk_before_any=bool(x.blk_before.any()),n=len(x)))
D3=pd.DataFrame(D3)
dayloss=E.groupby('day')[['act','cf']].sum()
best_day=E.groupby('day').sav.sum().idxmax()
Ex=E[E.day!=best_day]
# NetSaving per day (fleet, all blocked)
bl=bl.assign(d=bl.t_open.dt.floor('D')); nsd=(-bl.groupby('d').pnl.sum())
ns_wo_best=NS-(-bl[bl.d==nsd.idxmax()].pnl.sum())
rng=np.random.default_rng(394); alld=pd.Series(0.0,index=pd.date_range(P.t_open.min().floor('D'),P.t_open.max().floor('D'))); alld.loc[nsd.index]+=nsd.values
bs=[rng.choice(alld.values,len(alld)).sum() for _ in range(10000)]
C={}
C['1_repro']=(int(E.repro.sum()),len(E),bool(E.repro.sum()>=50))
C['2_groups_full']=(int(G.full_repro.sum()),len(G),bool(G.full_repro.sum()>=8))
C['3_blk_before_3acc_days']=(int(D3.blk_before_any.sum()),len(D3),bool(D3.blk_before_any.mean()>=0.7))
C['4_peakL_red_median']=(round(float(G.peak_red.median()),3),bool(G.peak_red.median()>=0.4))
C['5_ev_loss_red']=(round(1-E.cf.sum()/E.act.sum(),4),bool(1-E.cf.sum()/E.act.sum()>=0.3))
C['6_grp_loss_red']=(round(1-G.loss_cf.sum()/G.loss_act.sum(),4),bool(1-G.loss_cf.sum()/G.loss_act.sum()>=0.35))
C['7_worst_day']=(round(dayloss.act.min()),round(dayloss.cf.min()),bool(dayloss.cf.min()>=dayloss.act.min()))
C['8_n_events']='UNKNOWN (not measurable without new path)'
C['9_forgone_nonev_literal']=(round(forg_all),round(live_nonev_profit),round(forg_all/live_nonev_profit,4),bool(forg_all<=0.2*live_nonev_profit))
C['9_strict_affected']=(round(forg_all),round(live_aff),round(forg_all/live_aff,4) if live_aff>0 else 'live_aff<=0',bool(live_aff>0 and forg_all<=0.2*live_aff))
C['10_NS_stress']=(round(NS),round(NS_stress),bool(NS_stress>0))
sv=E.sav.sum(); C['11_mtm_share']=(round(E.sav_mtm.sum()/sv,3) if sv!=0 else None,bool(sv>0 and E.sav_mtm.sum()/sv>=0.6))
C['12_wo_best']=(str(best_day.date()),round(ns_wo_best),round(1-Ex.cf.sum()/Ex.act.sum(),4),bool(ns_wo_best>0 and 1-Ex.cf.sum()/Ex.act.sum()>=0.2))
C['13_boot_NS']=(round(float(np.percentile(bs,5))),round(float(np.median(bs))),round(float(np.percentile(bs,95))))
C['info']=dict(blocked_pos=int(P.blocked.sum()),blocked_baskets=int(P[P.blk_first].basket.nunique()),NS_total=round(NS),ev_sav=round(sv),ev_loss_act=round(E.act.sum()),nonev_forgone=round(forg_all),stress_extra=round(stress_extra))
print(G.round(2).to_string()); print(D3.to_string())
for k,v in C.items(): print(k,v)
E.to_csv('t394_events.csv',index=False); G.to_csv('t394_groups.csv',index=False); json.dump({k:str(v) for k,v in C.items()},open('t394_criteria.json','w'),indent=1,ensure_ascii=False)
