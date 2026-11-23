# t362 backtest: RoboQuant Daily Anchored VWAP Signal Strategy on SPY 3m (Alpaca SIP). Implements PREREG_t362.md.
import sys, json, glob, numpy as np, pandas as pd
D='/workspace/t362/data'
def load_bars():
    fs=sorted(glob.glob(f'{D}/SPY_1m_*.parquet'))
    df=pd.concat([pd.read_parquet(f) for f in fs],ignore_index=True)
    df['ts']=pd.to_datetime(df['t'],utc=True).dt.tz_convert('America/New_York')
    df=df.drop_duplicates('ts').sort_values('ts')
    df['b']=df['ts'].dt.floor('3min')
    g=df.groupby('b',sort=True)
    b=pd.DataFrame({'o':g['o'].first(),'h':g['h'].max(),'l':g['l'].min(),'c':g['c'].last(),'v':g['v'].sum()})
    cal=pd.DataFrame(json.load(open(f'{D}/calendar.json')))
    cal=cal.set_index('date')
    b['date']=b.index.strftime('%Y-%m-%d')
    b=b[b['date'].isin(cal.index)]
    mins=b.index.hour*60+b.index.minute
    om=cal['open'].map(lambda s:int(s[:2])*60+int(s[3:])); cm=cal['close'].map(lambda s:int(s[:2])*60+int(s[3:]))
    b['om']=b['date'].map(om).values; b['cm']=b['date'].map(cm).values
    b['rth']=(mins>=b['om'])&(mins+3<=b['cm'])
    return b
def indicators(b):
    c=b['c'].values; h=b['h'].values; l=b['l'].values
    ema=pd.Series(c).ewm(span=11,adjust=False).mean().values
    pc=np.r_[c[0],c[:-1]]
    tr=np.maximum(h-l,np.maximum(abs(h-pc),abs(l-pc)))
    def wilder(x,n):
        out=np.empty_like(x); out[0]=x[0]; a=1.0/n
        for i in range(1,len(x)): out[i]=out[i-1]+a*(x[i]-out[i-1])
        return out
    b['ema']=ema; b['atr14']=wilder(tr,14); b['atr50']=wilder(tr,50)
    tp=(b['h']+b['l']+b['c'])/3
    r=b[b['rth']].copy(); r['pv']=tp[b['rth']]*r['v']
    cpv=r.groupby('date')['pv'].cumsum(); cv=r.groupby('date')['v'].cumsum()
    b['vwap']=np.nan; b.loc[r.index,'vwap']=(cpv/cv).values
    rthi=np.where(b['rth'].values)[0]
    last=np.zeros(len(b),bool); first=np.zeros(len(b),bool)
    dts=b['date'].values
    for k,i in enumerate(rthi):
        if k==len(rthi)-1 or dts[rthi[k+1]]!=dts[i]: last[i]=True
        if k==0 or dts[rthi[k-1]]!=dts[i]: first[i]=True
    b['last']=last; b['first']=first
    return b
COSTPT=(0.25*5+0.62)  # $ per side per MES contract
def run(b,start,end,costmult=1.0):
    m=(b['date']>=start)&(b['date']<=end)
    idx=np.where(m.values)[0]
    o=b['o'].values;c=b['c'].values;ema=b['ema'].values;vw=b['vwap'].values
    a14=b['atr14'].values;a50=b['atr50'].values;rth=b['rth'].values;last=b['last'].values;first=b['first'].values
    dts=b['date'].values; ts=b.index
    cfrac=lambda P: costmult*COSTPT/(50.0*P)   # fraction of notional per side
    pos=0; trades=[]; cur=None; pend=None
    entries=0; win_today=False; last_exit_dir=0; armed=0; prev_rth=None
    for i in idx:
        # fill pending order at this bar open
        if pend is not None:
            kind,d=pend; P=o[i]; pend=None
            if kind=='exit': close_trade(cur,i,P,dts[i],cfrac); trades.append(cur); win_today=win_today or cur['net']>0; last_exit_dir=cur['dir']; cur=None; pos=0
            else: cur=dict(dir=d,ei=i,ep=P,edate=dts[i],ets=str(ts[i]),entry_cost=cfrac(P)); pos=d
        if not rth[i]: continue
        if first[i]: entries=0; win_today=False; armed=0; last_exit_dir=0; prev_rth=None
        exit_sig=False
        if pos==1 and c[i]<ema[i]: exit_sig=True
        if pos==-1 and c[i]>ema[i]: exit_sig=True
        if exit_sig:
            if last[i]: close_trade(cur,i,c[i],dts[i],cfrac); trades.append(cur); win_today=win_today or cur['net']>0; last_exit_dir=cur['dir']; cur=None; pos=0
            else: pend=('exit',0)
        elif pos==0 and pend is None:
            # arming for pullback
            if last_exit_dir!=0 and prev_rth is not None and armed==0:
                sp=np.sign(ema[prev_rth]-vw[prev_rth]); sn=np.sign(ema[i]-vw[i])
                if sp==last_exit_dir and sn==-last_exit_dir: armed=-last_exit_dir
            ok=(not win_today) and entries<3 and a14[i]<=1.1*a50[i]
            d=0
            if ema[i]>vw[i] and c[i]>ema[i]: d=1
            elif ema[i]<vw[i] and c[i]<ema[i]: d=-1
            if d==0 and armed!=0 and prev_rth is not None:
                if armed==-1 and c[prev_rth]>=vw[prev_rth] and c[i]<vw[i] and ema[i]<vw[i]: d=-1
                if armed==1 and c[prev_rth]<=vw[prev_rth] and c[i]>vw[i] and ema[i]>vw[i]: d=1
            if d!=0 and ok:
                entries+=1; armed=0; last_exit_dir=0
                if last[i]: cur=dict(dir=d,ei=i,ep=c[i],edate=dts[i],ets=str(ts[i]),entry_cost=cfrac(c[i])); pos=d
                else: pend=('entry',d)
        elif pos!=0 and last_exit_dir!=0:
            pass
        prev_rth=i
    if cur is not None:  # mark open trade at period end close
        i=idx[-1]; close_trade(cur,i,c[i],dts[i],cfrac); cur['open_at_end']=True; trades.append(cur)
    return trades
def close_trade(t,i,P,d,cfrac):
    t['xi']=i; t['xp']=P; t['xdate']=d; t['exit_cost']=cfrac(P)
    t['gross']=t['dir']*(P/t['ep']-1); t['net']=t['gross']-t['entry_cost']-t['exit_cost']
def finalize(trades,costmult):
    for t in trades:
        t['usd']=150*t['dir']*(t['xp']-t['ep'])-3*2*COSTPT*costmult
        t['overnight']=t['edate']!=t['xdate']
    return trades
def daily_series(b,trades,start,end,costmult):
    rthb=b[b['rth']]
    days=sorted(rthb.loc[(rthb['date']>=start)&(rthb['date']<=end),'date'].unique())
    lastc=rthb[rthb['last']].set_index('date')['c']; firsto=rthb[rthb['first']].set_index('date')['o']
    r=pd.Series(0.0,index=days); usd=pd.Series(0.0,index=days); on=pd.Series(0.0,index=days); onusd=pd.Series(0.0,index=days)
    pos=pd.Series(0,index=days)
    di={d:k for k,d in enumerate(days)}
    for t in trades:
        k0=di[t['edate']]; k1=di[t['xdate']]; d=t['dir']
        for k in range(k0,k1+1):
            day=days[k]
            ps=t['ep'] if k==k0 else lastc[days[k-1]]
            pe=t['xp'] if k==k1 else lastc[day]
            seg=d*(pe/ps-1); su=150*d*(pe-ps)
            if k==k0: seg-=t['entry_cost']; su-=3*COSTPT*costmult
            if k==k1: seg-=t['exit_cost']; su-=3*COSTPT*costmult
            r[day]+=seg; usd[day]+=su
            if k>k0:
                g=d*(firsto[day]/lastc[days[k-1]]-1); on[day]+=g; onusd[day]+=150*d*(firsto[day]-lastc[days[k-1]])
            if k<k1: pos[day]=d
    return pd.DataFrame({'r':r,'usd':usd,'on':on,'onusd':onusd,'pos_eod':pos})
def stats(trades,ds,label):
    n=len(trades); net=np.array([t['net'] for t in trades]) if n else np.array([])
    gp=net[net>0].sum(); gl=-net[net<0].sum()
    usd=np.array([t['usd'] for t in trades]) if n else np.array([])
    eq=(1+ds['r']).cumprod(); dd=(eq/eq.cummax()-1).min()
    sh=ds['r'].mean()/ds['r'].std()*np.sqrt(252) if ds['r'].std()>0 else np.nan
    E=10000+ds['usd'].cumsum(); Eprev=E.shift(1).fillna(10000); ur=ds['usd']/Eprev
    udd=((E-E.cummax())/E.cummax()).min()
    ush=ur.mean()/ur.std()*np.sqrt(252) if ur.std()>0 else np.nan
    ugp=usd[usd>0].sum(); ugl=-usd[usd<0].sum()
    return dict(label=label,trades=n,win=float((net>0).mean()) if n else None,pf_1x=float(gp/gl) if gl>0 else None,
        ret_1x=float(eq.iloc[-1]-1),cagr_1x=float(eq.iloc[-1]**(252/len(ds))-1),sharpe_1x=float(sh),maxdd_1x=float(dd),
        usd_net=float(usd.sum()),usd_ret_on_10k=float(usd.sum()/10000),pf_usd=float(ugp/ugl) if ugl>0 else None,
        win_usd=float((usd>0).mean()) if n else None,maxdd_usd_10k=float(udd),sharpe_usd=float(ush),days=len(ds),
        exposure_days_frac=float((ds['r']!=0).mean()))
