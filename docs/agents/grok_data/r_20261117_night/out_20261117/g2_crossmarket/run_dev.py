"""Dev-only runs for PREREG G2-A (sha 50ac5ba9…) and G2-B (sha 1ab7019c…). Holdout data is never touched here:
all series are truncated at the dev end date BEFORE any signal/return computation."""
import json,csv,math,sys
import numpy as np, pandas as pd
which=sys.argv[1]
def tstat(x):
    x=np.asarray(x,float); return x.mean()/(x.std(ddof=1)/math.sqrt(len(x))) if len(x)>2 else float('nan')
def mdd_from_R(rs,risk=0.005):
    eq=1.0;peak=1.0;m=0.0
    for r in rs:
        eq*=1+risk*r; peak=max(peak,eq); m=min(m,eq/peak-1)
    return m,eq
def h1(path):
    d=pd.read_csv(path); d['t']=pd.to_datetime(d['open_time_ms'],unit='ms',utc=True); return d.set_index('t')[['open','high','low','close']]
def daily_atr(h,n):
    dd=h.resample('1D').agg({'open':'first','high':'max','low':'min','close':'last'}).dropna()
    pc=dd['close'].shift(1); tr=pd.concat([dd.high-dd.low,(dd.high-pc).abs(),(dd.low-pc).abs()],axis=1).max(axis=1)
    return tr.rolling(n).mean()   # ATR known at end of that UTC day
def simulate(h,entry_t,exit_t,side,sl_dist):
    seg=h.loc[entry_t:exit_t]
    e=seg['open'].iloc[0]; sl=e-side*sl_dist
    for ts,row in seg.iloc[:-1].iterrows() if len(seg)>1 else []:
        if side==1 and row.low<=sl: return min(row.open,sl) if ts!=seg.index[0] else sl, ts, True
        if side==-1 and row.high>=sl: return max(row.open,sl) if ts!=seg.index[0] else sl, ts, True
    return seg['open'].iloc[-1], seg.index[-1], False
if which=='A':
    DEV_END=pd.Timestamp('2021-12-31 23:59',tz='UTC')
    x=h1('data/XAUUSD_1h.csv'); x=x[x.index<=DEV_END+pd.Timedelta(days=20)]  # small tail only to close last dev trades
    sge=json.load(open('data/sge_au9999.json'))['time']
    s=pd.DataFrame(sge,columns=['date','open','close','low','high']); s['date']=pd.to_datetime(s['date']); s=s.set_index('date')
    s=s[s.index<=DEV_END.tz_localize(None)]
    cj=json.load(open('data/yahoo_CNYX.json'))['chart']['result'][0]
    cny=pd.Series(cj['indicators']['quote'][0]['close'],index=pd.to_datetime(cj['timestamp'],unit='s').normalize()).dropna()
    cny=cny[~cny.index.duplicated(keep='last')]
    atr=daily_atr(x,20)
    rows=[]
    for d,r in s.iterrows():
        t07=pd.Timestamp(d,tz='UTC')+pd.Timedelta(hours=7)
        if t07 not in x.index: continue
        c=cny[cny.index<=d]
        if not len(c) or (d-c.index[-1]).days>5: continue
        p_sge=r['close']*31.1034768/c.iloc[-1]
        rows.append((d,p_sge/x.loc[t07,'open']-1))
    P=pd.Series(dict(rows)).sort_index()
    med=P.shift(1).rolling(250,min_periods=200).median(); sd=P.shift(1).rolling(250,min_periods=200).std()
    Z=(P-med)/sd
    tdays=[t for t in x.index if t.hour==8]   # trading days = days with a 08:00 bar
    tdi={t.normalize():i for i,t in enumerate(tdays)}
    def trade(d,side):
        t8=pd.Timestamp(d,tz='UTC')+pd.Timedelta(hours=8)
        if t8.normalize() not in tdi: return None
        i=tdi[t8.normalize()]
        if i+10>=len(tdays): return None
        ex=tdays[i+10]
        a=atr[atr.index<t8.normalize()]
        if not len(a) or np.isnan(a.iloc[-1]): return None
        sl=2*a.iloc[-1]
        e=x.loc[t8,'open']; px,ets,hit=simulate(x,t8,ex,side,sl)
        nights=0
        for dd in pd.date_range(t8.normalize(),ets.normalize()-pd.Timedelta(days=1)):
            if dd.weekday()<5: nights+=3 if dd.weekday()==2 else 1
        sw=(-0.60 if side==1 else 0.19)*nights
        gross=side*(px-e); net=gross-0.24+sw
        return dict(entry=t8,exit=ets,side=side,e=e,x=px,sl=sl,hit=hit,nights=nights,gross_bp=gross/e*1e4,net_bp=net/e*1e4,R=net/sl,
                    stress_bp=(gross-0.48+(-0.60*nights if side==1 else 0))/e*1e4)
    T=[];busy_until=None
    for d,z in Z.dropna().items():
        if d<pd.Timestamp('2017-01-01'): continue
        if busy_until is not None and pd.Timestamp(d,tz='UTC')+pd.Timedelta(hours=8)<=busy_until: continue
        if z>=1: tr=trade(d,1)
        elif z<=-1: tr=trade(d,-1)
        else: continue
        if tr and tr['entry']<=DEV_END: T.append(tr); busy_until=tr['exit']
    U=[trade(d,1) for d in Z.dropna().index if d>=pd.Timestamp('2017-01-01')]
    U=[u for u in U if u and u['entry']<=DEV_END]
    tag='G2A'
else:
    DEV_END=pd.Timestamp('2021-12-31 23:59',tz='UTC')
    bn=h1('/workspace/research_new_component/data/binance/BTCUSDT_1h.csv')
    cb=pd.read_csv('data/coinbase_BTCUSD_1h.csv'); cb['t']=pd.to_datetime(cb['time'],unit='s',utc=True); cb=cb.set_index('t')
    bn=bn[bn.index<=DEV_END+pd.Timedelta(days=3)]; cb=cb[cb.index<=DEV_END]
    j=bn[['close']].join(cb[['close']],rsuffix='_cb',how='inner')
    p=j['close_cb']/j['close']-1
    g=p.groupby(p.index.normalize()); s=g.mean()[g.count()>=20]
    s=s.reindex(pd.date_range(s.index.min(),s.index.max(),freq='D',tz='UTC'))
    mu=s.shift(1).rolling(30,min_periods=25).mean(); sd=s.shift(1).rolling(30,min_periods=25).std()
    Z=((s-mu)/sd).dropna()
    atr=daily_atr(bn,14)
    def trade(d,side):
        t0=d+pd.Timedelta(days=1); t1=d+pd.Timedelta(days=2)
        if t0 not in bn.index or t1 not in bn.index or d not in atr.index or np.isnan(atr.loc[d]): return None
        sl=2*atr.loc[d]; e=bn.loc[t0,'open']; px,ets,hit=simulate(bn,t0,t1,side,sl)
        wd=t0.weekday(); swbp=0 if wd>=5 else (1.30*3 if wd==4 else 1.30)
        gross_bp=side*(px-e)/e*1e4; net=gross_bp-2.84-swbp
        return dict(entry=t0,exit=ets,side=side,e=e,x=px,sl=sl,hit=hit,gross_bp=gross_bp,net_bp=net,R=net/1e4*e/sl,stress_bp=gross_bp-2*(2.84+swbp))
    T=[]
    for d,z in Z.items():
        if d<pd.Timestamp('2018-01-01',tz='UTC') or d+pd.Timedelta(days=1)>DEV_END: continue
        if z>=1: tr=trade(d,1)
        elif z<=-1: tr=trade(d,-1)
        else: continue
        if tr: T.append(tr)
    U=[trade(d,1) for d in Z.index if d>=pd.Timestamp('2018-01-01',tz='UTC') and d+pd.Timedelta(days=1)<=DEV_END]; U=[u for u in U if u]
    tag='G2B'
T=pd.DataFrame(T); U=pd.DataFrame(U)
T.to_csv(f'{tag}_dev_trades.csv',index=False)
res={}
res['n']=len(T); res['net_mean_bp']=T.net_bp.mean(); res['t']=tstat(T.net_bp); res['gross_mean_bp']=T.gross_bp.mean()
for sd_,nm in ((1,'long'),(-1,'short')):
    q=T[T.side==sd_]; res[f'n_{nm}']=len(q); res[f'net_{nm}_bp']=q.net_bp.mean() if len(q) else None; res[f't_{nm}']=tstat(q.net_bp) if len(q)>2 else None
res['uncond_long_net_bp']=U.net_bp.mean(); res['long_minus_uncond_bp']=(res['net_long_bp'] or 0)-U.net_bp.mean()
m,eq=mdd_from_R(T.sort_values('exit').R.values); res['mdd_0.5pct']=m; res['end_equity_x']=eq
res['stress_mean_bp']=T.stress_bp.mean(); res['sl_hits']=int(T.hit.sum())
T['yr']=pd.to_datetime(T.entry).dt.year; res['by_year_net_bp']=T.groupby('yr').net_bp.mean().round(1).to_dict(); res['by_year_n']=T.groupby('yr').size().to_dict()
json.dump(res,open(f'{tag}_dev_result.json','w'),indent=1,default=float); print(json.dumps(res,indent=1,default=float))
