import pandas as pd,glob,numpy as np
out=[]
for f in sorted(glob.glob("*_deals.csv")):
    acc=f.replace("_deals.csv","").replace("Black_Dragon_","BD")
    d=pd.read_csv(f); d['t']=pd.to_datetime(d.time,format="%Y.%m.%d %H:%M:%S")
    d=d.sort_values(['time_msc','ticket']).reset_index(drop=True)
    d['net']=d.profit+d.commission+d.swap+d.fee; d['bal']=d.net.cumsum()
    d['isn']=d.comment.astype(str).str.match(r"^n_[\d.]+_v$")
    pass
    if not d.isn.any(): continue
    d['cp']=d.comment.astype(str).str.extract(r"^n_([\d.]+)_v$")[0].astype(float)
    n=d[d.isn]
    ent=d[(d.entry==0)&d.type.isin([0,1])].set_index('position_id')
    # multiplier calibration
    mm=[]
    for _,x in n.iterrows():
        if x.position_id in ent.index:
            e=ent.loc[[x.position_id]].iloc[0]; s=1 if e.type==0 else -1
            dp=(x.price-e.price)*s*x.volume
            if abs(dp)>1e-6: mm.append(x.profit/dp)
    mult=np.median(mm)
    ev=(n.t.diff()>pd.Timedelta(minutes=30)).cumsum()
    prev_after=None
    for k,g in n.groupby(ev):
        i0=g.index.min(); fp=g.cp.iloc[0]; sym=g.symbol.iloc[0]
        sub=d.loc[:i0-1]; tr=sub[sub.type.isin([0,1])]
        ins=tr[tr.entry==0]; outs=tr[tr.entry.isin([1,3])]
        vout=outs.groupby('position_id').volume.sum()
        fl=0; vol=0; npos=0
        for pid,e in ins.groupby('position_id'):
            v=e.volume.sum()-vout.get(pid,0)
            if v>1e-9:
                e0=e.iloc[0]; s=1 if e0.type==0 else -1
                # use comment price for the symbol (approx; bid/ask ignored)
                fl+=(fp-e0.price)*s*v*mult; vol+=v; npos+=1
        bb=d.bal[i0-1]; eq=bb+fl
        hist=d.loc[:i0-1]; peak=hist.bal.max()
        # last deposit time / balance at 7,14,21 days before
        def bal_at(dt):
            h=d[d.t<=dt]; return h.bal.iloc[-1] if len(h) else np.nan
        out.append(dict(acc=acc,start=g.t.min(),npos=npos,vol=round(vol,2),bal_before=round(bb),eq_trig=round(eq),
            dd_vs_bal=round((1-eq/bb)*100,2),dd_vs_peakbal=round((1-eq/peak)*100,2),
            dd_vs_prev_after=round((1-eq/prev_after)*100,2) if prev_after else np.nan,
            loss_money=round(bb-eq),real_loss_pct=round(-g.net.sum()/bb*100,2),
            slip_pct=round((-g.net.sum()-(bb-eq))/bb*100,2),mult=round(mult,1),
            dd_vs_bal7=round((1-eq/bal_at(g.t.min()-pd.Timedelta(days=7)))*100,1),
            dd_vs_bal14=round((1-eq/bal_at(g.t.min()-pd.Timedelta(days=14)))*100,1)))
        prev_after=d.bal[g.index.max()]
r=pd.DataFrame(out); r.to_csv("/tmp/t376_events2.csv",index=False)
pd.set_option('display.width',250)
print(r.to_string())
print(r.groupby(r.acc.str.startswith('BD'))[['dd_vs_bal','real_loss_pct','dd_vs_peakbal']].describe().T)
