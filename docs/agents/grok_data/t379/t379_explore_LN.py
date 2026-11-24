# EXPLORATORY (not in PREREG): L7/L8/L10/L12, 5555 only, spread 0.30. Same code as t379_map.py.
# t379: map 59 protection events to BD baskets + counterfactual rules. Read-only, box only, aliases only.
import pandas as pd, numpy as np, re, json, sys
H='/workspace/algotrade/history/'
EV='/workspace/bridge_pending/delivered_t376/t376_events.csv'
PX='/workspace/claude_bridge/out_20261117/g2_crossmarket/data/XAUUSD_1h.csv'
ACC={'BD1':'Black_Dragon_1','BD2':'Black_Dragon_2','BD3':'Black_Dragon_3','BD5':'Black_Dragon_5',
     'BD6':'Black_Dragon_6','BD7':'Black_Dragon_7','BD8':'Black_Dragon_8','BTC_Bot_4':'BTC_Bot_4'}
K=100.0; SPREAD=0.30; NRE=r'^n_[\d.]+_v$'; BDRE=re.compile(r'black.?dragon|eabd',re.I)
DST=sys.argv[1] if len(sys.argv)>1 else 'EU'
px=pd.read_csv(PX); px['t']=pd.to_datetime(px.utc); px=px.set_index('t')[['open','high','low','close']]
pc=px.close.shift(); tr=np.maximum(px.high-px.low,np.maximum((px.high-pc).abs(),(px.low-pc).abs()))
px['atr']=tr.rolling(14).mean().shift(1)   # ATR of 14 closed bars before this bar
# server TZ per account, chosen by in-bar validation (deviation from PREREG: EGlobal accounts BD1/BD8 fit CET/CEST, not EET/EEST)
TZ={'BD1':'Europe/Berlin','BD8':'Europe/Berlin'}
ZONE=['Europe/Athens']
def srv2utc(ts):
    ts=pd.DatetimeIndex(ts)
    return ts.tz_localize(ZONE[0],ambiguous='NaT',nonexistent='shift_forward').tz_convert('UTC').tz_localize(None)
def utc2srv(ts):
    return pd.DatetimeIndex(ts).tz_localize('UTC').tz_convert(ZONE[0]).tz_localize(None)
evt=pd.read_csv(EV); evt['start']=pd.to_datetime(evt.start)
B_rows=[];E_rows=[];CF=[];VAL={}
for a,f in ACC.items():
    ZONE[0]=TZ.get(a,'Europe/Athens')
    d=pd.read_csv(H+f+'_deals.csv',dtype={'comment':str}); d['comment']=d.comment.fillna('')
    d['t']=pd.to_datetime(d.time,format='%Y.%m.%d %H:%M:%S'); d=d.sort_values(['time_msc','ticket']).reset_index(drop=True)
    d['net']=d.profit+d.commission+d.swap+d.fee; d.loc[d.type==3,'net']=0.0
    d['bal']=d.net.cumsum()
    d['tu']=srv2utc(d.t); d['tu']=d.tu.fillna(d.t-pd.Timedelta(hours=2)); print(a,ZONE[0],'NaT',int(srv2utc(d.t).isna().sum()))
    tr_=d[d.type.isin([0,1])].copy()
    ent=tr_[tr_.entry==0]; pinfo=ent.groupby('position_id').first()
    # mult calibration (t376 method)
    n=tr_[tr_.comment.str.match(NRE)]; mm=[]
    for x in n.itertuples():
        if x.position_id in pinfo.index:
            e=pinfo.loc[x.position_id]; s=1 if e.type==0 else -1; dp=(x.price-e.price)*s*x.volume
            if abs(dp)>1e-6: mm.append(x.profit/dp)
    mult=float(np.median(mm)) if mm else 100.0
    # baskets: key = symbol, magic(of entry), side
    open_v={}; gopen={}; pos2b={}; bk={}; bid=0
    for r in tr_.itertuples():
        if r.entry==0:
            key=(r.symbol,r.magic,r.type)
            if gopen.get(key,0)<1e-9:
                bid+=1; bk[bid]=dict(acc=a,bid=bid,symbol=r.symbol,magic=r.magic,side='buy' if r.type==0 else 'sell',
                    is_bd=bool(BDRE.search(r.comment)),t0=r.t,entries=[],closed=None); gk=key; bk[bid]['key']=key; cur={}
                gopen[key+('bid',)]=bid
            b=gopen[key+('bid',)]; pos2b[r.position_id]=b; bk[b]['entries'].append((r.t,r.price,r.volume,r.commission,r.position_id,r.Index))
            open_v[r.position_id]=open_v.get(r.position_id,0)+r.volume; gopen[key]=gopen.get(key,0)+r.volume
        elif r.entry in (1,3) and r.position_id in pos2b:
            b=pos2b[r.position_id]; key=bk[b]['key']; open_v[r.position_id]-=r.volume; gopen[key]-=r.volume
            if gopen[key]<1e-9: bk[b]['closed']=r.t; gopen[key]=0
    tr_['bid']=tr_.position_id.map(pos2b)
    bnet=tr_.groupby('bid').net.sum()
    # exit commission per lot (median of actual exits)
    ex=tr_[tr_.entry.isin([1,3])&(tr_.volume>0)]; exc=float((ex.commission/ex.volume).median()) if len(ex) else 0.0
    # position intervals
    P=ent.groupby('position_id').agg(tin=('tu','first'),price=('price','first'),vol=('volume','sum'),type=('type','first'),sym=('symbol','first'),magic=('magic','first'))
    P['tout']=tr_[tr_.entry.isin([1,3])].groupby('position_id').tu.max(); P['tout']=P.tout.fillna(pd.Timestamp('2100-01-01'))
    P['realized']=tr_.groupby('position_id').net.sum(); P['s']=np.where(P.type==0,1,-1); P['bid']=P.index.map(pos2b)
    P=P[P.sym.str.startswith('XAU')]
    # basis & time validation
    j=ent[ent.symbol.str.startswith('XAU')].copy(); j['bar']=j.tu.dt.floor('h'); j=j.join(px,on='bar',how='inner')
    basis=float((j.price-(j.high+j.low)/2).median()); ok=((j.price-basis>=j.low-1)&(j.price-basis<=j.high+1)).mean()
    VAL[a]=dict(mult=mult,basis=round(basis,3),in_bar=round(float(ok),4),exit_comm_per_lot=exc,n=len(j))
    hp=px.copy(); hp[['open','high','low','close']]+=basis
    for b,v in bk.items():
        v['net']=float(bnet.get(b,0.0)); v['levels']=len(v['entries'])
    # ---------- floating helpers (positions alive during bar, balance at bar start)
    def float_series(pp,bars,with_real=True):
        # returns for each bar: F at low, F at high (+ realized of positions closed before bar start)
        out=[]
        tin=pp.tin.values; tout=pp.tout.values; pr=pp.price.values; vo=pp.vol.values; s=pp.s.values; re_=pp.realized.values
        for bt in bars:
            be=bt+pd.Timedelta(hours=1)
            alive=(tin<np.datetime64(be))&(tout>np.datetime64(bt)); done=tout<=np.datetime64(bt)
            lo=hp.at[bt,'low']; hi=hp.at[bt,'high']
            fl=(s[alive]*(lo-pr[alive])*vo[alive]).sum()*mult; fh=(s[alive]*(hi-pr[alive])*vo[alive]).sum()*mult
            r=re_[done].sum() if with_real else 0.0
            out.append((min(fl,fh)+r, alive, done))
        return out
    # ---------- events
    nd=d[d.comment.str.match(NRE)&d.type.isin([0,1])]
    cid=(nd.t.diff()>pd.Timedelta(minutes=30)).cumsum()
    crash_b=set()
    for k,g in nd.groupby(cid):
        st=g.t.min(); trig=float(re.match(r'^n_([\d.]+)_v$',g.comment.iloc[0]).group(1))
        bs=sorted(set(g.position_id.map(pos2b).dropna().astype(int))); crash_b|=set(bs)
        i0=g.index.min(); bb=float(d.bal[i0-1])
        tu0=g.tu.min(); bar=tu0.floor('h'); atr=float(px.atr.get(bar,np.nan))
        row=dict(acc=a,start=st,trigger_price=trig,bal_before=round(bb),prot_loss=round(-g.net.sum()),atr14_h1=round(atr,2) if atr==atr else np.nan)
        # per side summary of baskets open at trigger (all XAU magics, BD flag)
        lead=None
        for side in ['buy','sell']:
            sb=[b for b in bs if bk[b]['side']==side]
            if not sb: row.update({f'{side}_levels':0}); continue
            vol_open={b:P[(P.bid==b)&(P.tout>=tu0)].vol.sum() for b in sb}
            b=max(sb,key=lambda x:vol_open[x]); v=bk[b]
            ents=[e for e in v['entries'] if e[0]<=st]
            lv=len(ents); vols=[e[2] for e in ents]; p1=ents[0][1]
            dist=(trig-p1)*(1 if side=='buy' else -1)
            row.update({f'{side}_baskets':len(sb),f'{side}_magic':v['magic'],f'{side}_levels':lv,f'{side}_lot_init':vols[0],
                f'{side}_maxlot_over_first':round(max(vols)/vols[0],2),f'{side}_first_price':p1,f'{side}_adverse_dist_usd':round(dist,2),
                f'{side}_adverse_dist_atr':round(dist/atr,2) if atr==atr and atr>0 else np.nan,
                f'{side}_hours_first_to_trig':round((st-v['t0']).total_seconds()/3600,1),
                f'{side}_ratio_med':round(float(np.median(np.array(vols[1:])/np.array(vols[:-1]))),3) if lv>1 else np.nan})
            if lead is None or vol_open[b]>lead[1]: lead=(b,vol_open[b])
        # thresholds for lead basket
        if lead:
            b=lead[0]; v=bk[b]; pp=P[P.bid==b]; b0=float(d[d.t<v['t0']].bal.iloc[-1]) if (d.t<v['t0']).any() else bb
            bars=px.index[(px.index>=pp.tin.min().floor('h'))&(px.index<=tu0.floor('h'))]
            fs=float_series(pp,bars); lv5=lv10=np.nan; h5=h10=np.nan
            for bt,(fv,al,dn) in zip(bars,fs):
                be=bt+pd.Timedelta(hours=1); nlev=int((pp.tin<be).sum())
                if lv5!=lv5 and fv<=-0.05*b0: lv5=nlev; h5=round((tu0-bt).total_seconds()/3600,1)
                if lv10!=lv10 and fv<=-0.10*b0: lv10=nlev; h10=round((tu0-bt).total_seconds()/3600,1)
            row.update(lead_side=v['side'],lead_is_bd=v['is_bd'],lead_bal_start=round(b0),level_at_m5pct=lv5,hours_m5_to_trig=h5,level_at_m10pct=lv10,hours_m10_to_trig=h10)
        E_rows.append(row)
    for b,v in bk.items():
        v['crash']=b in crash_b
    # ---------- L_N rules
    for N in (7,8,10,12):
        for scope in ('5555',):
            for spread in (SPREAD,):
                for b,v in bk.items():
                    if not v['symbol'].startswith('XAU'): continue
                    if scope=='5555' and v['magic']!=5555: continue
                    if scope=='BD_all' and not v['is_bd']: continue
                    if v['levels']<N: continue
                    eN=v['entries'][N-1]; tN=eN[0]; pN=eN[1]; idxN=eN[5]
                    pids=[e[4] for e in v['entries'][:N]]
                    sub=tr_[tr_.position_id.isin(pids)&(tr_.index<=idxN)]
                    realized=sub.net.sum()
                    ov=sub.assign(sv=np.where(sub.entry==0,sub.volume,-sub.volume)).groupby('position_id').sv.sum()
                    fl=0.0; vol=0.0
                    for pid,vv in ov.items():
                        if vv>1e-9:
                            e=pinfo.loc[pid]; s=1 if e.type==0 else -1; fl+=s*(pN-e.price)*vv*mult; vol+=vv
                    res=realized+fl+exc*vol-spread*vol*mult
                    CF.append(dict(acc=a,rule=f'L{N}',scope=scope,spread=spread,bid=b,crash=v['crash'],actual=v['net'],rule_res=res,delta=res-v['net']))
    # ---------- daily equity stop D5/D8 (account level, all XAU positions; non-XAU ignored)
    Pa=P.copy(); bal_ser=d.set_index('tu').bal
    flows=d[d.type==2].set_index('tu').net
    fday=pd.DatetimeIndex(utc2srv(flows.index)).normalize() if len(flows) else None
    tin=Pa.tin.values; tout=Pa.tout.values; pr=Pa.price.values; vo=Pa.vol.values; s=Pa.s.values
    bars=px.index[(px.index>=d.tu.min().floor('h'))&(px.index<=d.tu.max().floor('h'))]
    srv=utc2srv
    # balance at bar start
    balv=np.interp(bars.values.astype('int64'),d.tu.values.astype('int64'),d.bal.values,left=0)
    bidx=np.searchsorted(d.tu.values,bars.values,side='left')-1
    bal_bs=np.where(bidx>=0,d.bal.values[np.clip(bidx,0,None)],0.0)
    EQ=[]
    for i,bt in enumerate(bars):
        be=bt+pd.Timedelta(hours=1); al=(tin<np.datetime64(be))&(tout>np.datetime64(bt))
        lo=hp.at[bt,'low']; hi=hp.at[bt,'high']
        el=bal_bs[i]+(s[al]*(lo-pr[al])*vo[al]).sum()*mult; eh=bal_bs[i]+(s[al]*(hi-pr[al])*vo[al]).sum()*mult
        ex_=(s[al]*vo[al]).sum()
        EQ.append((el,eh,ex_,al))
    day=pd.DatetimeIndex(srv(bars)).normalize()
    for X in ():
        cur=None; ref=None; stopped=False; fired=[]
        for i,bt in enumerate(bars):
            if day[i]!=cur:
                cur=day[i]; stopped=False; el,eh,_,_=EQ[i]; ref=(el+eh)/2 if True else None; fl_day=0.0; refbal=bal_bs[i]
            if stopped: continue
            # adjust ref for flows inside the day
            fd=flows[(flows.index<bt) & (fday==cur)].sum() if len(flows) else 0.0
            el,eh,ex_,al=EQ[i]; thr=(ref+fd)*(1-X/100.0); worst=min(el,eh)
            if worst<=thr and al.any():
                stopped=True
                pw=hp.at[bt,'low'] if el<=eh else hp.at[bt,'high']
                # optimistic price where equity==thr (linear in P with net exposure)
                pop=pw
                if abs(ex_)>1e-9:
                    base=bal_bs[i]+(-(s[al]*pr[al]*vo[al]).sum())*mult
                    pop=(thr-base)/(ex_*mult)
                    pop=min(max(pop,hp.at[bt,'low']),hp.at[bt,'high'])
                fired.append(dict(bar=bt,al=np.where(al)[0],pw=pw,pop=pop,daykey=cur))
        for fz in fired:
            ids=Pa.index[fz['al']]; endday=srv2utc([fz['daykey']+pd.Timedelta(days=1)-pd.Timedelta(minutes=1)])[0]
            res_by_b={}
            for mode,pc_ in (('pess',fz['pw']),('opt',fz['pop'])):
                rb={}
                for pid in ids:
                    q=Pa.loc[pid]; b=q.bid
                    # realized part of this position before the bar (partial exits) ~ entry commission only
                    rows=tr_[(tr_.position_id==pid)&(tr_.tu<fz['bar'])]
                    rem=q.vol-rows[rows.entry.isin([1,3])].volume.sum()
                    val=rows.net.sum()+q.s*(pc_-q.price)*rem*mult+exc*rem-SPREAD*rem*mult
                    if rows.empty: val+=ent[ent.position_id==pid].commission.sum()
                    rb[b]=rb.get(b,0.0)+val-Pa.at[pid,'realized']
                res_by_b[mode]=rb
            # baskets opened after the stop the same server day: removed
            later=[b for b,v in bk.items() if v['symbol'].startswith('XAU') and srv2utc([v['t0']])[0]>fz['bar']+pd.Timedelta(hours=1) and srv2utc([v['t0']])[0]<endday]
            for mode in ('pess','opt'):
                for b,dl in res_by_b[mode].items():
                    CF.append(dict(acc=a,rule=f'D{X}',scope=mode,spread=SPREAD,bid=b,crash=bk[b]['crash'],actual=bk[b]['net'],rule_res=bk[b]['net']+dl,delta=dl,stop_bar=fz['bar']))
                for b in later:
                    CF.append(dict(acc=a,rule=f'D{X}',scope=mode,spread=SPREAD,bid=b,crash=bk[b]['crash'],actual=bk[b]['net'],rule_res=0.0,delta=-bk[b]['net'],stop_bar=fz['bar'],removed=True))
    for b,v in bk.items():
        B_rows.append(dict(acc=a,bid=b,symbol=v['symbol'],magic=v['magic'],side=v['side'],is_bd=v['is_bd'],t0=v['t0'],closed=v['closed'],levels=v['levels'],
            lot_init=v['entries'][0][2],max_over_first=round(max(e[2] for e in v['entries'])/v['entries'][0][2],2),net=round(v['net'],2),crash=v['crash']))
    print(a,VAL[a],len(bk),'crash baskets',len(crash_b),flush=True)
pd.DataFrame(B_rows).to_csv(f'/tmp/t379x_baskets.csv',index=False)
pd.DataFrame(E_rows).to_csv(f'/tmp/t379x_events.csv',index=False)
pd.DataFrame(CF).to_csv(f'/tmp/t379x_cf_raw.csv',index=False)
json.dump(VAL,open(f'/tmp/t379x_val.json','w'),indent=1)
