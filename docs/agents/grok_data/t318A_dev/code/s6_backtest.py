import pandas as pd, numpy as np, json, math
from zoneinfo import ZoneInfo
from statistics import NormalDist
ND=NormalDist()
from cfg import D, P, FIRST, LAST, EVAL_START
ET=ZoneInfo('America/New_York')
calj={c['date']:c for c in json.load(open(D+'calendar.json'))}
S=pd.read_parquet(D+'selected.parquet')
rng=np.random.default_rng(318)
# ---------- load full-day bars + data quality ----------
dq=[]; bars={}
for d,g in S.groupby('date'):
    b=pd.read_parquet(D+f'full/{d}.parquet')
    b['et']=pd.to_datetime(b.t).dt.tz_convert(ET); b['m']=b.et.dt.hour*60+b.et.dt.minute-570
    cl=calj[d]['close']; close_m=int(cl[:2])*60+int(cl[3:])-570
    for s,x in b.groupby('symbol'):
        x=x[(x.m>=0)].sort_values('m')
        n_after=int((x.m>=close_m).sum()); x=x[x.m<close_m]
        o,h,l,c=(x[k].to_numpy(float) for k in 'ohlc'); m=x.m.to_numpy()
        r=np.diff(np.log(c)) if len(c)>2 else np.array([0.0])
        sig=max(1.4826*np.median(np.abs(r-np.median(r))),0.0005)
        hp=np.r_[h[1:],h[-1]]; hm=np.r_[h[0],h[:-1]]; lp=np.r_[l[1:],l[-1]]; lm=np.r_[l[0],l[:-1]]
        ph=((h-np.maximum(o,c))>5*sig*c)&((h-np.maximum(hm,hp))>5*sig*c)
        pl=((np.minimum(o,c)-l)>5*sig*c)&((np.minimum(lm,lp)-l)>5*sig*c)
        flat=(o==h)&(h==l)&(l==c); same=np.r_[False,(c[1:]==c[:-1])&flat[1:]&flat[:-1]]
        run=0; mx=0
        for v in same:
            run=run+1 if v else 0; mx=max(mx,run)
        stale=(mx+1)>=30
        gaps=np.diff(np.r_[m,close_m]) - 1; halt=int((gaps>=10).sum())
        dq.append(dict(date=d,symbol=s,nbars=len(m),expected=close_m,phantom_bars=int(ph.sum()+pl.sum()),stale=bool(stale),
                       early_close_bars_dropped=n_after,halt_gaps=halt))
        bars[(d,s)]=(m,o,h,l,c,close_m)
DQ=pd.DataFrame(dq); DQ['excluded']=(DQ.phantom_bars>0)|DQ.stale
DQ.to_csv(P+'data_quality_symbol_days.csv',index=False)
excl=set(zip(DQ[DQ.excluded].date,DQ[DQ.excluded].symbol))
# ---------- trade sim ----------
def sim(key,ortype,side,orh,orl,atr,stopmode,s,conservative=True,extra=0.01):
    if key not in bars: return None
    m,o,h,l,c,close_m=bars[key]
    start=ortype
    i0=np.searchsorted(m,start)
    if i0>=len(m): return None
    if side>0: hit=np.nonzero(h[i0:]>=orh)[0]
    else: hit=np.nonzero(l[i0:]<=orl)[0]
    if len(hit)==0: return None
    i=i0+hit[0]
    ex=extra if s>0 else 0.0
    if side>0:
        fill=max(orh,o[i])+s
        stop=fill-0.10*atr if stopmode=='a10' else fill-0.25*atr if stopmode=='a25' else orl
    else:
        fill=min(orl,o[i])-s
        stop=fill+0.10*atr if stopmode=='a10' else fill+0.25*atr if stopmode=='a25' else orh
    dist=abs(fill-stop)
    if dist<=0: return None
    j=None; px=None
    if conservative and ((side>0 and l[i]<=stop) or (side<0 and h[i]>=stop)):
        j=i; px=stop-side*(s+ex)
    else:
        if side>0:
            k=np.nonzero(l[i+1:]<=stop)[0]
        else:
            k=np.nonzero(h[i+1:]>=stop)[0]
        if len(k):
            j=i+1+k[0]
            g=o[j]<=stop if side>0 else o[j]>=stop
            px=(o[j] if g else stop)-side*(s+ex)
    if j is None:
        j=len(m)-1; px=c[-1]-side*s; kind='moc'
    else: kind='stop'
    pnl=side*(px-fill)
    return dict(fill=fill,exit=px,dist=dist,pnl_sh=pnl,R=pnl/dist,kind=kind,hold=int(m[j]-m[i]+1),entry_m=int(m[i]))
VARS=[(5,'a10'),(5,'a25'),(5,'opp'),(1,'a10'),(1,'a25'),(1,'opp')]
def vname(v): return f"OR{v[0]}m_{v[1]}"
def run(v,s,reverse=False,conservative=True,longonly=False,use_excl=True,gross=False):
    ortype,stopmode=v; T=[]
    for r in S[S.ortype==ortype].itertuples():
        key=(r.date,r.symbol)
        if use_excl and key in excl: continue
        side=-r.dir if reverse else r.dir
        if longonly and side<0: continue
        t=sim(key,ortype,side,r.orh,r.orl,r.atr,stopmode,s,conservative)
        if t: t.update(date=r.date,symbol=r.symbol,side=side,N=r.N); T.append(t)
    return pd.DataFrame(T)
def equity(T,gross=False,E0=25000.0):
    days=sorted(calj_d)
    E=E0; eq=[]; T=T.copy(); T['qty']=0; T['netpnl']=0.0; T['fees']=0.0
    byd={d:g for d,g in T.groupby('date')} if len(T) else {}
    for d in days:
        pnl=0.0
        if d in byd:
            g=byd[d]
            qty=np.floor(np.minimum(E*0.01/g.dist, 4*E/(g.N*g.fill))).clip(lower=0)
            sec=sec_rate(d)/1e6
            sell_px=np.where(g.side>0,g.exit,g.fill)
            fees=0 if gross else qty*0.0035*2 + qty*sell_px*sec + qty*0.000166
            net=qty*g.pnl_sh-fees
            T.loc[g.index,'qty']=qty; T.loc[g.index,'netpnl']=net; T.loc[g.index,'fees']=fees
            pnl=float(np.sum(net))
        eq.append((d,E,pnl/E)); E+=pnl
    Q=pd.DataFrame(eq,columns=['date','E_start','ret'])
    T['Rnet']=np.where(T.qty>0,T.netpnl/(T.qty*T.dist).replace(0,np.nan),np.nan)
    T['bp_net']=np.where(T.qty>0,1e4*T.netpnl/(T.qty*T.fill),np.nan)
    return T,Q
calj_d=[d for d in calj if EVAL_START<=d<=LAST]
MONTHS=(pd.Timestamp(LAST)-pd.Timestamp(EVAL_START)).days/30.4375
# SEC Section 31 rate per $1M by charge date (sec.gov advisories 2016-2, 2017-111, 2018-67; 2019-2021 per SEC advisories)
SEC=[('2016-02-16',21.80),('2017-07-04',23.10),('2018-05-22',13.00),('2019-04-16',20.70),('2020-02-18',22.10),('2021-02-25',5.10)]
def sec_rate(d):
    r=18.40
    for s,v in SEC:
        if d>=s: r=v
    return r
MID='2019-01-01'   # DEV halves: 2016-2018 | 2019-2021
def stats(T,Q):
    T=T[T.qty>0] if 'qty' in T else T
    E=(1+Q.ret).cumprod(); dd=1-E/E.cummax()
    mret=(E.iloc[-1])**(1/MONTHS)-1
    sh=Q.ret.mean()/Q.ret.std()*math.sqrt(252) if Q.ret.std()>0 else 0
    return dict(trades=int(len(T)),R_net=float(T.Rnet.mean()),bp_net=float(T.bp_net.mean()),
        hit=float((T.netpnl>0).mean()),stop_share=float((T.kind=='stop').mean()),median_hold=float(T.hold.median()),
        monthly_geo=float(mret),total=float(E.iloc[-1]-1),MDD=float(dd.max()),worst_day=float(Q.ret.min()),sharpe=float(sh),
        H1_total=float((1+Q.ret[Q.date<MID]).prod()-1),H2_total=float((1+Q.ret[Q.date>=MID]).prod()-1),
        es975=float(-np.sort(Q.ret.to_numpy())[:max(1,int(len(Q)*0.025))].mean()),
        years={y:float((1+g.ret).prod()-1) for y,g in Q.groupby(Q.date.str[:4])},
        R_net_by_year={y:float(g.Rnet.mean()) for y,g in T.groupby(T.date.str[:4])} if len(T) else {})
res={}; trades_main={}
for v in VARS:
    n=vname(v); res[n]={}
    G=run(v,0.0); G['Rg']=G.R; G['bp_g']=1e4*G.pnl_sh/G.fill
    res[n]['gross']=dict(trades=len(G),R_gross=float(G.R.mean()),bp_gross=float(G.bp_g.mean()),hit_gross=float((G.pnl_sh>0).mean()))
    for s in (0.0,0.01,0.02,0.03,0.05):
        T=run(v,s); T,Q=equity(T); res[n][f's{int(s*100)}']=stats(T,Q)
        if s==0.02: trades_main[n]=(T,Q)
    T=run(v,0.02,reverse=True); T,Q=equity(T); res[n]['reverse_s2']=stats(T,Q)
    T=run(v,0.02,longonly=True); T,Q=equity(T); res[n]['longonly_s2']=stats(T,Q)
    T=run(v,0.02,conservative=False); T,Q=equity(T); res[n]['optimistic_samebar_s2']=stats(T,Q)
    T=run(v,0.02,use_excl=False); T,Q=equity(T); res[n]['no_dq_exclusion_s2']=stats(T,Q)
    print('VARIANT_DONE',n,json.dumps(res[n]['gross']),json.dumps({k:(round(x,4) if isinstance(x,float) else x) for k,x in res[n]['s2'].items()}),flush=True)
# ---------- G0 permutation (net 2+1, R per symbol-day, sizing-free R incl. costs approx via R from sim) ----------
def r_per_symday(v,reverse):
    T=run(v,0.02,reverse=reverse); 
    return T.set_index(['date','symbol']).R
for v in VARS:
    n=vname(v); a=r_per_symday(v,False); b=r_per_symday(v,True)
    idx=a.index.union(b.index); A=a.reindex(idx).to_numpy(); B=b.reindex(idx).to_numpy()
    obs=np.nanmean(A)-np.nanmean(B); cnt=0
    for _ in range(2000):
        sw=rng.random(len(idx))<0.5
        X=np.where(sw,B,A); Y=np.where(sw,A,B)
        if np.nanmean(X)-np.nanmean(Y)>=obs: cnt+=1
    res[n]['G0']=dict(delta=float(obs),p=(cnt+1)/2001)
# ---------- G6 Holm on daily mean net R; G5 DSR ----------
ps={}; srs={}; rets={}
for n,(T,Q) in trades_main.items():
    dm=T[T.qty>0].groupby('date').Rnet.mean()
    t=dm.mean()/(dm.std()/math.sqrt(len(dm))); ps[n]=1-ND.cdf(t)
    r=Q.ret; srs[n]=r.mean()/r.std(); rets[n]=r
order=sorted(ps,key=ps.get); holm={}; stop=False
for k,n in enumerate(order):
    thr=0.05/(6-k); ok=(ps[n]<thr) and not stop; stop=stop or not ok; holm[n]=dict(p=float(ps[n]),holm_pass=bool(ok))
srv=np.var(list(srs.values()),ddof=1); g=0.5772156649; Nn=6
sr0=math.sqrt(srv)*((1-g)*ND.inv_cdf(1-1/Nn)+g*ND.inv_cdf(1-1/(Nn*math.e)))
for n in srs:
    r=rets[n]; sr=srs[n]; T_=len(r); sk=float(((r-r.mean())**3).mean()/r.std()**3); ku=float(((r-r.mean())**4).mean()/r.std()**4)
    z=(sr-sr0)*math.sqrt(T_-1)/math.sqrt(max(1e-12,1-sk*sr+(ku-1)/4*sr*sr))
    res[n]['G5_DSR_N6_upperbound']=float(ND.cdf(z)); res[n]['G6']=holm[n]
json.dump(res,open(P+'results_t318A_DEV.json','w'),indent=1)
for n,(T,Q) in trades_main.items(): T.to_csv(P+f'trades_{n}_s2.csv.gz',index=False)
DQs=dict(selected_symbol_days=int(len(DQ)),excluded=int(DQ.excluded.sum()),phantom_days=int((DQ.phantom_bars>0).sum()),
    stale_days=int(DQ.stale.sum()),early_close_bars_dropped=int(DQ.early_close_bars_dropped.sum()),
    symbol_days_with_halt_gap=int((DQ.halt_gaps>0).sum()),bars_total=int(DQ.nbars.sum()),bars_expected=int(DQ.expected.sum()))
json.dump(DQs,open(P+'dq_summary.json','w'),indent=1); print(DQs); print('S6_DONE',flush=True)
