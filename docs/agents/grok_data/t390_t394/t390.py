import pandas as pd, numpy as np, glob, json, sys
ZONE='Europe/Athens'; K=0.1
import os
MODE=os.environ.get('MODE','primary'); VARS=os.environ.get('VARS','b,b50').split(',')
DS=pd.read_csv('duk_spread_m1.csv',parse_dates=['ts'] if False else [0],index_col=0).spread
MB=json.load(open('/workspace/t385/t385_validation.json'))['mult_basis']
CT=pd.read_csv('in/t384_tester/t384_segments_tester.csv').set_index('seg_id')
G=pd.read_csv('segs_t389.csv',parse_dates=['start_live','end_live','cut_live']).set_index('seg_id')
m1=pd.concat([pd.read_csv(f,parse_dates=['ts']) for f in sorted(glob.glob('/workspace/t383/m1data/m1_*.csv'))]).sort_values('ts').drop_duplicates('ts').set_index('ts')
H='/workspace/algotrade/history/'; FILES={'A3':'Black_Dragon_3','A4':'BTC_Bot_4','A5':'Black_Dragon_5','A6':'Black_Dragon_6'}
def toU(t): return pd.DatetimeIndex(pd.to_datetime(t)).tz_localize(ZONE,ambiguous='NaT',nonexistent='shift_forward').tz_convert('UTC').tz_localize(None)
def toS(t): return pd.Timestamp(t).tz_localize('UTC').tz_convert(ZONE).tz_localize(None)
def load(seg,v):
    d=pd.read_csv(f'in/t384_tester/{seg}_{v}.csv.gz',parse_dates=['ts']).reset_index(drop=True)
    d['side']=np.where(((d.dir=='in')&(d.type=='buy'))|((d.dir!='in')&(d.type=='sell')),'buy','sell')
    d['q']=np.where(d.side=='buy',1,-1)*np.where(d.dir=='in',1,-1)*d.vol_per_100k
    return d
def episodes(d):
    d=d.copy(); d['ep']=''
    for side in ['buy','sell']:
        vol=0.0; ep=0; cur=None
        for i in d.index[d.side==side]:
            q=d.at[i,'vol_per_100k']
            if d.at[i,'dir']=='in':
                if vol<1e-9: ep+=1; cur=f'{side}{ep}'
                vol+=q
            else: vol-=q
            d.at[i,'ep']=cur
            if vol<1e-9: vol=0.0
    return d
def curve(w,basis,t0,t1):
    """per-bar low equity (pct of deposit) of deals w (all deals since run start contribute via cumulative state), bars covering [t0,t1) server"""
    bars=m1.loc[toU([t0])[0].floor('min'):toU([t1])[0]-pd.Timedelta(seconds=1)]
    n=len(bars); bt=bars.index.values
    tu=toU(w.ts).values.astype('datetime64[ns]')
    bi=np.searchsorted(bt,tu,side='right')-1      # bar of deal; -1 => before window
    pos=np.clip(bi+1,0,n)                          # effective from next bar
    cost=(w.swap_pct+w.commission_pct).values
    Qc=np.zeros(n+1); QPc=np.zeros(n+1); Cc=np.zeros(n+1)
    np.add.at(Qc,pos,w.q.values); np.add.at(QPc,pos,(w.q*w.price).values); np.add.at(Cc,pos,cost)
    Qc=np.cumsum(Qc)[:n]; QPc=np.cumsum(QPc)[:n]; Cc=np.cumsum(Cc)[:n]
    sp=DS.reindex(bars.index).ffill().fillna(DS.median()).values
    if MODE=='t389': sa=0*sp
    elif MODE=='rfask': sa=np.maximum(sp-0.39,0)
    else: sa=sp
    isb=(w.side=='buy').values
    Qb=np.zeros(n+1); QPb=np.zeros(n+1); np.add.at(Qb,pos[isb],w.q.values[isb]); np.add.at(QPb,pos[isb],(w.q*w.price).values[isb])
    Qb=np.cumsum(Qb)[:n]; QPb=np.cumsum(QPb)[:n]; Qs=Qc-Qb; QPs=QPc-QPb
    lo=bars.low.values+basis; hi=bars.high.values+basis
    e_lo=K*(Qb*lo-QPb)+K*(Qs*(lo+sa)-QPs); e_hi=K*(Qb*hi-QPb)+K*(Qs*(hi+sa)-QPs)
    eql=np.minimum(e_lo,e_hi)+Cc
    return pd.Series(eql,index=bars.index)
def live_deals(al):
    d=pd.read_csv(H+FILES[al]+'_deals.csv',dtype={'comment':str}); d['comment']=d.comment.fillna('')
    d['t']=pd.to_datetime(d.time,format='%Y.%m.%d %H:%M:%S'); d=d.sort_values(['time_msc','ticket']).reset_index(drop=True)
    return d[d.type.isin([0,1])]
def bdesc(p,v,ts,side):
    if len(p)==0: return dict(side='',t_first='',p_first=np.nan,levels=0,spacing=np.nan,maxlot_first=np.nan,lot1=np.nan)
    return dict(side=side,t_first=pd.Timestamp(ts[0]),p_first=round(float(p[0]),2),levels=len(p),
                spacing=round(float(np.median(np.abs(np.diff(p)))),2) if len(p)>1 else np.nan,maxlot_first=round(float(v.max()/v[0]),2),lot1=round(float(v[0]),3),
                lotseq='/'.join(f'{x/v[0]:.2g}' for x in v[:20]))
def live_basket(seg,al,tc,start,lot_seg,LD):
    d=LD[al]
    ent=d[(d.entry==0)&(d.magic==5555)&(d.t>=start)&(d.t<=tc)]
    ex=d[(d.entry!=0)&(d.position_id.isin(ent.position_id))]
    tout=ex.groupby('position_id').t.max(); ent=ent.assign(tout=ent.position_id.map(tout))
    oc=ent[(ent.tout.isna())|(ent.tout>=tc)]
    vs=oc.groupby(np.where(oc.type==0,'buy','sell')).volume.sum(); lead=vs.idxmax()
    allent=d[(d.entry==0)&(d.magic==5555)&(d.t<=tc)&(np.where(d.type==0,'buy','sell')==lead)]
    allout=d[(d.entry!=0)&(d.position_id.isin(allent.position_id))].groupby('position_id').t.max()
    pos=pd.DataFrame(dict(tin=allent.t.values,tout=allent.position_id.map(allout).fillna(pd.Timestamp('2100-01-01')).values)).sort_values('tin')
    cur_end=pd.Timestamp('1900-01-01'); eps=None
    for x in pos.itertuples():
        if x.tin>cur_end: eps=x.tin
        cur_end=max(cur_end,x.tout)
    le=allent[allent.t>=eps]
    r=bdesc(le.price.values,le.volume.values/lot_seg,le.t.values,lead)
    r['open_lots_init']=round(float(vs.get(lead,0)/lot_seg),2); r['opp_open_lots_init']=round(float(vs.drop(lead).sum()/lot_seg),2) if len(vs)>1 else 0.0
    return r
def tester_basket(d,tref,vinit):
    up=d[d.ts<=tref]
    ov=up.groupby('side').apply(lambda x:(x[x.dir=='in'].vol_per_100k.sum()-x[x.dir!='in'].vol_per_100k.sum())) if len(up) else pd.Series(dtype=float)
    ov=ov[ov>1e-9]
    if len(ov)==0: r=bdesc([],[],[],''); r['open_lots_init']=0.0; r['opp_open_lots_init']=0.0; return r
    lead=ov.idxmax(); lv=up[up.side==lead]; ep=lv.ep.iloc[-1]
    e=d[(d.ep==ep)&(d.dir=='in')&(d.ts<=tref)]
    r=bdesc(e.price.values,e.vol_per_100k.values/vinit,e.ts.values,lead)
    r['open_lots_init']=round(float(ov[lead]/vinit),2); r['opp_open_lots_init']=round(float(ov.drop(lead).sum()/vinit),2)
    return r
def classify(L,T):
    if not T['side'] or T['side']!=L['side']: return 'DIFFERENT'
    dt=abs((T['t_first']-L['t_first']).total_seconds())/60; dl=abs(T['levels']-L['levels'])
    if dt<=15 and abs(T['p_first']-L['p_first'])<=3 and dl<=2 and abs(T['maxlot_first']/L['maxlot_first']-1)<=0.25: return 'SAME'
    if dt<=120 and dl<=4: return 'SIMILAR'
    return 'DIFFERENT'
LD={}; rows=[]
for seg,s in G.iterrows():
    al=seg[:2]; basis=MB[al]['basis']; Gp=s.G_FloorPct; cutL=s.cut_live if pd.notna(s.cut_live) else None
    T_end=s.end_live
    if cutL is not None and al not in LD: LD[al]=live_deals(al)
    r=dict(seg_id=seg,G_FloorPct=Gp,start_live=s.start_live,end_live=T_end,live_cut=cutL)
    L=live_basket(seg,al,cutL,s.start_live,s.lot_seg,LD) if cutL is not None else None
    if L:
        for k,vv in L.items(): r[f'live_{k}']=vv
    if al not in LD: LD[al]=live_deals(al)
    dl=LD[al]; en=dl[(dl.entry==0)&(dl.magic==5555)]; xo=dl[dl.entry!=0].groupby('position_id').t.max()
    en=en.assign(tout=en.position_id.map(xo).fillna(pd.Timestamp('2100-01-01')))
    for nmT,tT in (('Tstart',s.start_live),('Tend',T_end)):
        o=en[(en.t<=tT)&(en.tout>tT)]; vs=o.groupby(np.where(o.type==0,'buy','sell')).volume.sum()
        r[f'live_open_{nmT}']='/'.join(f'{k}:{x/s.lot_seg:.2f}' for k,x in vs.items()) or 'flat'
    for v in VARS:
        d=episodes(load(seg,v)); vinit=d[d.dir=='in'].vol_per_100k.min()
        last=d.ts.max(); cov_deal=bool(last>=T_end); cov_rep=bool(CT.loc[seg].get(f'{v}_covered',False))
        r[f'{v}_last_deal']=last; r[f'{v}_coverage']='deal' if cov_deal else ('report' if cov_rep else 'UNKNOWN(coverage)')
        if r[f'{v}_coverage'].startswith('UNKNOWN'): continue
        for nmT,tT in (('Tstart',s.start_live),('Tend',T_end)):
            up=d[d.ts<=tT]; ov=up.groupby('side').apply(lambda x:(x[x.dir=='in'].vol_per_100k.sum()-x[x.dir!='in'].vol_per_100k.sum())) if len(up) else pd.Series(dtype=float)
            r[f'{v}_open_{nmT}']='/'.join(f'{k}:{x/vinit:.2f}' for k,x in ov.items() if x>1e-9) or 'flat'
        # primary account curve: all deals since run start
        ca=curve(d,basis,s.start_live,T_end)
        # sensitivity segment curve: exclude episodes started before start_live, deals from start_live
        first=d[d.dir=='in'].groupby('ep').ts.min(); pre=set(first[first<s.start_live].index)
        ws=d[(d.ts>=s.start_live)&(~d.ep.isin(pre))]
        cs=curve(ws,basis,s.start_live,T_end)
        r[f'{v}_n_pre_eps']=len(pre)
        for nm,c in (('acct',ca),('seg',cs)):
            r[f'{v}_{nm}_min']=round(float(c.min()),2); r[f'{v}_{nm}_min_t']=toS(c.idxmin())
            if pd.notna(Gp):
                hit=c[c<=-Gp]; tx=toS(hit.index[0]) if len(hit) else None
                r[f'{v}_{nm}_cross']=tx
                r[f'{v}_{nm}_cross_dmin']=round((tx-cutL).total_seconds()/60,1) if (tx is not None and cutL is not None) else np.nan
                if cutL is not None: r[f'{v}_{nm}_match']=bool(tx is not None and abs((tx-cutL).total_seconds())<=86400)
                else: r[f'{v}_{nm}_match']=bool(tx is None)
                # late crossing descriptive
                if tx is None:
                    t2=min(T_end+pd.Timedelta(hours=24),last)
                    if t2>T_end+pd.Timedelta(minutes=1):
                        cl=curve(d if nm=='acct' else ws,basis,s.start_live,t2); cl=cl[cl.index>=toU([T_end])[0]]
                        h2=cl[cl<=-Gp]; r[f'{v}_{nm}_late_cross']=toS(h2.index[0]) if len(h2) else None
                        r[f'{v}_{nm}_late_min']=round(float(cl.min()),2) if len(cl) else np.nan
        if cutL is not None:
            tref=r.get(f'{v}_acct_cross') or cutL
            T=tester_basket(d,tref,vinit); r[f'{v}_tref']=tref
            for k,vv in T.items(): r[f'{v}_{k}']=vv
            r[f'{v}_basket']=classify(L,T)
            near=d[(d.dir=='in')&(d.side==L['side'])]; dt=(near.ts-L['t_first']).abs()
            if len(near):
                j=dt.idxmin(); r[f'{v}_nearest_dt_min']=round((near.ts[j]-L['t_first']).total_seconds()/60,1); r[f'{v}_nearest_dp']=round(near.price[j]-L['p_first'],2)
                r[f'{v}_anchored']=bool(dt[j]<=pd.Timedelta(minutes=5) and abs(near.price[j]-L['p_first'])<=1)
    rows.append(r)
X=pd.DataFrame(rows); X.to_csv(f'out/t390_windows_{MODE}.csv',index=False)
pd.set_option('display.width',250); pd.set_option('display.max_rows',500)
print(X.T.to_string())
