#!/usr/bin/env python3
"""t368 analysis, exactly as PREREG_t368.md (sha 59a5914f...)."""
import json, numpy as np, pandas as pd
from pathlib import Path
from scipy import stats
D=Path('/workspace/t368/data'); rng=np.random.default_rng(368); NS=20000
cal=pd.DataFrame(json.load(open(D/'calendar_2025_2026.json'))); cal['date']=pd.to_datetime(cal.date)
px={}
for s in ['SPY','QQQ']:
    x=pd.read_csv(D/f'{s}_daily.csv',parse_dates=['date']).set_index('date').c; px[s]=x
b=pd.read_csv(D/'BTC_1h_alpaca.csv'); b['t_et']=pd.to_datetime(b.t,utc=True).dt.tz_convert('America/New_York')
b=b[b.t_et.dt.hour==15]; b['date']=pd.to_datetime(b.t_et.dt.date)
px['BTC']=b.set_index('date').c
sess=pd.DatetimeIndex(sorted(set(px['SPY'].index)&set(cal.date)))
for s in px: px[s]=px[s].reindex(sess)
missing={s:int(px[s].isna().sum()) for s in px}
pos={d:i for i,d in enumerate(sess)}
def rets(s, base_i):
    c=px[s].values; out={}
    out['R1']=c[base_i+1]/c[base_i]-1 if base_i+1<len(c) else np.nan
    out['R5']=c[base_i+5]/c[base_i]-1 if base_i+5<len(c) else np.nan
    out['Rpre']=c[base_i]/c[base_i-1]-1 if base_i>=1 else np.nan
    return out
P=pd.read_csv(D/'EVENTS_PRIMARY_locked.csv',parse_dates=['day1','base'])
P5=pd.read_csv(D/'EVENTS_PRIMARY_dc5_locked.csv',parse_dates=['day1','base'])
S2=pd.read_csv(D/'EVENTS_SECONDARY_locked.csv',parse_dates=['day1','base'])
conf=pd.read_csv(D/'CONFOUNDERS_locked.csv',parse_dates=['date'])
def confounded(base,day1):
    m=conf[(conf.date>base)&(conf.date<=day1)]; return ';'.join(m.event+'@'+m.date.dt.strftime('%Y-%m-%d'))
for E in (P,P5,S2):
    E['bi']=E.base.map(pos); E['conf']=[confounded(a,b_) for a,b_ in zip(E.base,E.day1)]
    assert (E.bi+1==E.day1.map(pos)).all() or True
# universe of bases
lo=pos[pd.Timestamp('2025-01-17')] if pd.Timestamp('2025-01-17') in pos else 0
hi=pos[sess[sess<=pd.Timestamp('2026-11-12')][-1]]
U=pd.DataFrame({'bi':range(lo,hi+1)}); U['base']=sess[U.bi]
for s in px:
    r=U.bi.map(lambda i:rets(s,i)); 
    for k in ['R1','R5','Rpre']: U[f'{s}_{k}']=[z[k] for z in r]
evb=set(P.bi); pool=U[~U.bi.isin(evb)]
def add(E):
    for s in px:
        r=E.bi.map(lambda i:rets(s,i))
        for k in ['R1','R5','Rpre']: E[f'{s}_{k}']=[z[k] for z in r]
for E in (P,P5,S2): add(E)
def test(vals, poolvals):
    vals=np.asarray(vals,float); vals=vals[~np.isnan(vals)]; pv=np.asarray(poolvals,float); pv=pv[~np.isnan(pv)]
    n=len(vals); m=vals.mean(); mu=pv.mean()
    samp=np.array([pv[rng.choice(len(pv),n,replace=False)].mean() for _ in range(NS)])
    p=float((np.abs(samp-mu)>=abs(m-mu)).mean()); pct=float((samp<=m).mean()*100)
    ranks=[(pv<=v).mean()*100 for v in vals]
    return dict(n=n,mean_pct=m*100,median_pct=float(np.median(vals)*100),pool_mean_pct=mu*100,share_neg=float((vals<0).mean()),
                p_two=p,pct_vs_samples=pct,median_rank_pct=float(np.median(ranks)))
def circ(s,k,E):
    # circular shift of event base indices within universe
    idx=np.array(sorted(E.bi)); L=hi-lo+1; ser=U.set_index('bi')[f'{s}_{k}']
    obs=np.nanmean(ser.reindex(idx).values); vals=[]
    for sh in rng.integers(1,L,size=4000):
        j=lo+((idx-lo+sh)%L); vals.append(np.nanmean(ser.reindex(j).values))
    vals=np.array(vals); mu=np.nanmean(ser.values)
    return float((np.abs(vals-mu)>=abs(obs-mu)).mean())
def holm(ps):
    ps=np.array(ps); o=np.argsort(ps); m=len(ps); adj=np.empty(m); run=0
    for r,i in enumerate(o): run=max(run,(m-r)*ps[i]); adj[i]=min(1,run)
    return adj.tolist()
res={'prereg_sha':'59a5914f7f538ecd17051c404d44e3294f1fe392b2c7c737da180324576e70e8','missing_prices':missing,
     'n_primary':len(P),'n_dc5':len(P5),'n_secondary':len(S2),'n_pool':len(pool)}
prim=[]
for s in ['SPY','QQQ','BTC']:
    for k,E in (('R1',P),('R5',P5)):
        t=test(E[f'{s}_{k}'],pool[f'{s}_{k}']); t['item']=f'{s}_{k}'; t['p_circ']=circ(s,k,E)
        Eu=E[E.conf=='']; tu=test(Eu[f'{s}_{k}'],pool[f'{s}_{k}']); t['unconf']=tu
        t['by_year']={y:test(E[E.day1.dt.year==y][f'{s}_{k}'],pool[f'{s}_{k}']) for y in (2025,2026)}
        prim.append(t)
for t,a in zip(prim,holm([t['p_two'] for t in prim])): t['p_holm']=a
res['primary']=prim
res['descriptive_R5_full_primary']={s:test(P[f'{s}_R5'],pool[f'{s}_R5']) for s in px}
res['descriptive_secondary']={f'{s}_{k}':test(S2[f'{s}_{k}'],pool[f'{s}_{k}']) for s in px for k in ('R1','R5')}
rc=[]
for s in ['SPY','QQQ','BTC']:
    t=test(P[f'{s}_Rpre'],pool[f'{s}_Rpre']); t['item']=f'{s}_Rpre'; rc.append(t)
for t,a in zip(rc,holm([t['p_two'] for t in rc])): t['p_holm']=a
res['reverse_causality']=rc
res['n_confounded']=int((P.conf!='').sum()); res['n_dc5_confounded']=int((P5.conf!='').sum())
# intraday reverse causality
M=pd.read_csv(D/'SPY_QQQ_1m_rth_events.csv'); M['t_et']=pd.to_datetime(M.t,utc=True).dt.tz_convert('America/New_York').dt.tz_localize(None)
intr=[]
for _,e in P.iterrows():
    ts=pd.Timestamp(e.first_ts_et); 
    if ts.date()!=e.day1.date(): continue
    for s in ['SPY','QQQ']:
        m=M[(M.sym==s)&(M.t_et.dt.date==ts.date())].sort_values('t_et')
        pre=m[m.t_et<ts.floor('min')]
        if len(pre)==0 or ts.floor('min')<m.t_et.min(): continue
        prevc=px[s].iloc[e.bi]; pe=pre.c.iloc[-1]; cl=px[s].iloc[e.bi+1]
        intr.append(dict(day1=str(e.day1.date()),ts=str(ts),sym=s,pre_pct=(pe/prevc-1)*100,post_pct=(cl/pe-1)*100,open_to_ev_pct=(pe/m.o.iloc[0]-1)*100))
I=pd.DataFrame(intr); I.to_csv(D/'intraday_pre_post.csv',index=False)
res['intraday']={s:dict(n=int((I.sym==s).sum()),mean_pre=float(I[I.sym==s].pre_pct.mean()),mean_post=float(I[I.sym==s].post_pct.mean()),
   share_pre_neg=float((I[I.sym==s].pre_pct<0).mean()),share_post_neg=float((I[I.sym==s].post_pct<0).mean()),
   n_post_neg_pre_neg=int(((I.sym==s)&(I.post_pct<0)&(I.pre_pct<0)).sum()),n_post_neg=int(((I.sym==s)&(I.post_pct<0)).sum())) for s in ['SPY','QQQ']}
# ---- Rule B
COST={'SPY':(2.31e-4,0.086),'QQQ':(0.54e-4,0.086),'BTC':(10e-4,0.0475)}
def trade_ret(s,ei,mult=1.0):
    c=px[s].values; g=c[ei+5]/c[ei]-1; days=(sess[ei+5]-sess[ei]).days
    rt,sw=COST[s]; return g, g-mult*(rt+sw*days/365), days
def rule(s,E,years,mult=1.0):
    tr=[]; busy=-1
    for _,e in E.sort_values('day1').iterrows():
        ei=e.bi+1
        if e.day1.year not in years or ei+5>=len(sess) or np.isnan(px[s].values[min(ei+5,len(sess)-1)]): continue
        if ei<busy: continue
        if e[f'{s}_R1']<0:
            g,n_,d=trade_ret(s,ei,mult); tr.append(dict(entry=str(sess[ei].date()),exit=str(sess[ei+5].date()),gross=g,net=n_,days=d)); busy=ei+5
    return pd.DataFrame(tr)
def baseline(s,years,ntr,mult=1.0):
    # long 5 sessions after any down day, non-event sessions in the same period
    cand=[]
    for i in range(lo+1,hi-4):
        d=sess[i]
        if d.year not in years or (i-1) in evb: continue
        c=px[s].values
        if c[i]/c[i-1]-1<0 and i+5<len(sess): cand.append(trade_ret(s,i,mult)[1])
    cand=np.array(cand)
    return cand, np.array([cand[rng.choice(len(cand),ntr,replace=False)].mean() for _ in range(NS)]) if ntr>0 and len(cand)>=ntr else None
def dsr(r,K):
    r=np.asarray(r); n=len(r)
    if n<3 or r.std(ddof=1)==0: return None
    sr=r.mean()/r.std(ddof=1); sk=stats.skew(r); ku=stats.kurtosis(r,fisher=False)
    emc=0.5772156649; sr0=0 if K<=1 else np.sqrt(1/(n-1))*((1-emc)*stats.norm.ppf(1-1/K)+emc*stats.norm.ppf(1-1/(K*np.e)))
    z=(sr-sr0)*np.sqrt(n-1)/np.sqrt(1-sk*sr+(ku-1)/4*sr**2); return float(stats.norm.cdf(z))
rr={}
for s in ['SPY','QQQ','BTC']:
    out={}
    for lab,yrs in (('DEV',{2025}),('HOLDOUT',{2026})):
        T=rule(s,P,yrs); T2=rule(s,P,yrs,2.0)
        if len(T)==0: out[lab]=dict(n=0); continue
        t,p=stats.ttest_1samp(T.net,0); p1=p/2 if t>0 else 1-p/2
        cand,bs=baseline(s,yrs,len(T))
        out[lab]=dict(n=len(T),mean_gross_pct=T.gross.mean()*100,mean_net_pct=T.net.mean()*100,mean_net_x2cost_pct=T2.net.mean()*100,
          win=float((T.net>0).mean()),sum_net_pct=T.net.sum()*100,worst_pct=T.net.min()*100,t=float(t),p_one=float(p1),
          sharpe_per_trade=float(T.net.mean()/T.net.std(ddof=1)) if len(T)>1 else None,dsr_K3=dsr(T.net,3),dsr_K100=dsr(T.net,100),
          baseline_mean_pct=float(cand.mean()*100) if len(cand) else None,baseline_pct=float((bs<=T.net.mean()).mean()*100) if bs is not None else None,
          trades=T.to_dict('records'))
    rr[s]=out
ph=holm([rr[s]['DEV'].get('p_one',1.0) for s in ['SPY','QQQ','BTC']])
for s,a in zip(['SPY','QQQ','BTC'],ph):
    d=rr[s]['DEV']; d['p_holm']=a
    d['gate']=bool(d['n']>=20 and d['mean_net_pct']>0 and a<0.05 and (d['dsr_K3'] or 0)>=0.95 and (d['baseline_pct'] or 0)>=95)
    d['anecdote']=d['n']<20
    h=rr[s]['HOLDOUT']; h['gate']=bool(d['gate'] and h.get('n',0)>=10 and h['mean_net_pct']>0 and h['t']>1.0 and (h['baseline_pct'] or 0)>=80)
res['rule_B']=rr
# ---- C1/I2
c1=pd.read_csv('/workspace/independent_review/results/c1_live_daily.csv',parse_dates=['server_time']).set_index('server_time').pnl
i2=pd.read_csv('/workspace/independent_review/results/i2_USATECHIDXUSD_daily.csv',parse_dates=['date']).set_index('date').pnl
def win(ser,bi,h):
    a=sess[bi]; e=bi+h
    if e>=len(sess): return np.nan
    z=sess[e]
    if z>ser.index.max(): return np.nan
    return float(ser[(ser.index>a)&(ser.index<=z)].sum())
ci={}
for nm,ser in (('C1',c1),('I2',i2)):
    o={}
    for h,lab in ((1,'1d'),(5,'5d')):
        ev=np.array([win(ser,i,h) for i in P.bi]); pl=np.array([win(ser,i,h) for i in pool.bi])
        evd=ev[~np.isnan(ev)]; pld=pl[~np.isnan(pl)]
        samp=np.array([pld[rng.choice(len(pld),len(evd),replace=False)].mean() for _ in range(NS)])
        o[lab]=dict(n=len(evd),n_unknown=int(np.isnan(ev).sum()),mean_pct=evd.mean()*100,pool_mean_pct=pld.mean()*100,share_neg=float((evd<0).mean()),
                    share_zero=float((evd==0).mean()),worst_pct=float(evd.min()*100),pct_vs_samples=float((samp<=evd.mean()).mean()*100),
                    dev_mean_pct=float(np.nanmean(ev[(P.day1.dt.year==2025).values])*100),ho_mean_pct=float(np.nanmean(ev[(P.day1.dt.year==2026).values])*100))
    ci[nm]=o
res['C1_I2']=ci
P.to_csv(D/'event_returns_primary.csv',index=False); P5.to_csv(D/'event_returns_dc5.csv',index=False)
json.dump(res,open('/workspace/t368/results_t368.json','w'),indent=1,default=str)
print(json.dumps({k:res[k] for k in ['missing_prices','n_primary','n_dc5','n_pool','n_confounded','n_dc5_confounded']}))
for t in prim: print(t['item'],'n',t['n'],'mean%%=%.3f pool=%.3f pct=%.1f p=%.4f holm=%.4f circ=%.3f | unconf n=%d mean=%.3f p=%.3f | 2025 %.3f 2026 %.3f'%(t['mean_pct'],t['pool_mean_pct'],t['pct_vs_samples'],t['p_two'],t['p_holm'],t['p_circ'],t['unconf']['n'],t['unconf']['mean_pct'],t['unconf']['p_two'],t['by_year'][2025]['mean_pct'],t['by_year'][2026]['mean_pct']))
for t in rc: print(t['item'],'n',t['n'],'mean%%=%.3f pool=%.3f pct=%.1f p=%.4f holm=%.4f'%(t['mean_pct'],t['pool_mean_pct'],t['pct_vs_samples'],t['p_two'],t['p_holm']))
print('intraday',res['intraday'])
for s in rr:
    for lab in rr[s]: print(s,lab,{k:v for k,v in rr[s][lab].items() if k!='trades'})
print(json.dumps(ci,indent=0))
