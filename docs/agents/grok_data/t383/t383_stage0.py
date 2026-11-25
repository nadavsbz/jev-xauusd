# t383 stage 0 (v2 per PREREG_t383b_amendment): B1 equity-floor policy counterfactual on live BD data, M1 bars.
# Read-only on /workspace/algotrade; outputs only in /workspace/t383. Aliases A1..A8 only.
import pandas as pd, numpy as np, re, json, math, glob
H='/workspace/algotrade/history/'
XL='/workspace/algotrade/reports/adv2_reset_floors_from_excel.csv'
EV376='/workspace/bridge_pending/delivered_t376/t376_events.csv'
ACC=[('A1','Black_Dragon_1','BD1','#1'),('A2','Black_Dragon_2','BD2','#2'),('A3','Black_Dragon_3','BD3','#3'),
     ('A4','BTC_Bot_4','BTC_Bot_4','#4'),('A5','Black_Dragon_5','BD5','#5'),('A6','Black_Dragon_6','BD6','#6'),
     ('A7','Black_Dragon_7','BD7','#7'),('A8','Black_Dragon_8','BD8','#8')]
TZ={'A1':'Europe/Berlin','A8':'Europe/Berlin'}
P=0.15; NRE=r'^n_[\d.]+_v$'; FAR=np.int64(4102444800*10**9)  # 2100-01-01
CELLS=[(R,ref) for R in (1,7,14) for ref in ('ERESET','HWM')]
m1=pd.concat([pd.read_csv(f,parse_dates=['ts']) for f in sorted(glob.glob('m1data/m1_*.csv'))]).sort_values('ts').reset_index(drop=True)
BT=m1.ts.values.astype('datetime64[ns]').astype(np.int64); MIN=np.int64(60*10**9)
O0,H0,L0_,C0=m1.open.values,m1.high.values,m1.low.values,m1.close.values
PX_END=int(BT[-1]+MIN)
xl=pd.read_csv(XL); xl['date']=pd.to_datetime(xl.date)
ev376=pd.read_csv(EV376); ev376['start']=pd.to_datetime(ev376.start)
def ns(t): return np.int64(pd.Timestamp(t).value)
def s2u(ts,zone): return pd.Timestamp(ts).tz_localize(zone,ambiguous=False,nonexistent='shift_forward').tz_convert('UTC').tz_localize(None)
def u2s(ts,zone): return pd.Timestamp(ts).tz_localize('UTC').tz_convert(zone).tz_localize(None)

def prep(f,zone):
    d=pd.read_csv(H+f+'_deals.csv',dtype={'comment':str}); d['comment']=d.comment.fillna('')
    d['t']=pd.to_datetime(d.time,format='%Y.%m.%d %H:%M:%S'); d=d.sort_values(['time_msc','ticket']).reset_index(drop=True)
    d['net']=d.profit+d.commission+d.swap+d.fee; d.loc[d.type==3,'net']=0.0; d['bal']=d.net.cumsum()
    tu=pd.DatetimeIndex(d.t).tz_localize(zone,ambiguous='NaT',nonexistent='shift_forward').tz_convert('UTC').tz_localize(None)
    d['tu']=tu; d['tu']=d.tu.fillna(d.t-pd.Timedelta(hours=2))
    tr=d[d.type.isin([0,1])]; ent=tr[tr.entry==0]; ex=tr[tr.entry.isin([1,3])]
    pi=ent.groupby('position_id').agg(tin=('tu','first'),price=('price','first'),vol=('volume','sum'),type=('type','first'),sym=('symbol','first'),cost=('net','sum'))
    pi['tout']=ex.groupby('position_id').tu.max(); pi['realized']=tr.groupby('position_id').net.sum()
    n=tr[tr.comment.str.match(NRE)]; mm=[]
    for x in n.itertuples():
        if x.position_id in pi.index:
            e=pi.loc[x.position_id]; s=1 if e.type==0 else -1; dp=(x.price-e.price)*s*x.volume
            if abs(dp)>1e-6: mm.append(x.profit/dp)
    mult=float(np.median(mm)) if mm else 100.0
    nd=d[d.comment.str.match(NRE)&d.type.isin([0,1])]; cid=(nd.t.diff()>pd.Timedelta(minutes=30)).cumsum()
    events=[]; pos2ev={}
    for k,g in nd.groupby(cid):
        i0=g.index.min()
        events.append(dict(eid=len(events),start_srv=g.t.min(),start_u=g.tu.min(),bal_before=float(d.bal[i0-1]),loss=-float(g.net.sum())))
        for pid in g.position_id.unique(): pos2ev[pid]=len(events)-1
    pi['grp']=[pos2ev.get(p,-1) for p in pi.index]
    j=ent[ent.symbol.str.startswith('XAU')].copy(); j['ts']=j.tu.dt.floor('min')
    j=j.merge(m1,on='ts',how='inner'); basis=float((j.price-(j.high+j.low)/2).median())
    inbar=float(((j.price-basis>=j.low-0.5)&(j.price-basis<=j.high+0.5)).mean())
    cf=d[d.type==2][['tu','net']].reset_index(drop=True)
    return d,pi,mult,events,basis,cf,inbar

def boundaries(R,start_u,zone):
    s0=u2s(start_u,zone).normalize(); e0=u2s(pd.Timestamp(PX_END),zone)+pd.Timedelta(days=1)
    days=pd.date_range(s0,e0,freq='D')
    b=days if R==1 else (days[days.weekday==0] if R==7 else days[days.weekday==0][::2])
    return [ns(s2u(x,zone)) for x in b]

def simulate(pi,mult,events,basis,cf,zone,mode,R=None,xl_b=None,floor_on=True,probe=None):
    pi=pi[pi.tin<pd.Timestamp(PX_END)]
    N=len(pi)
    tin=pi.tin.values.astype('datetime64[ns]').astype(np.int64)
    tout=pi.tout.fillna(pd.Timestamp('2100-01-01')).values.astype('datetime64[ns]').astype(np.int64)
    pr=pi.price.values; vol=pi.vol.values; s=np.where(pi.type.values==0,1.0,-1.0); real=pi.realized.values; cost=pi.cost.values
    isx=pi.sym.str.startswith('XAU').values; grp=pi.grp.values
    start=ns(cf.tu.min()) if len(cf) else int(tin.min())
    i0=int(np.searchsorted(BT,start-MIN+1)); BE=BT+MIN
    ib=np.searchsorted(BE,tin,side='right')          # first bar with be>tin
    ob=np.searchsorted(BT,tout,side='left')          # first bar with b0>=tout
    nb=len(BT)
    # per-bar add/remove lists
    order_in=np.argsort(ib,kind='stable'); order_out=np.argsort(ob,kind='stable')
    pin=0; pout=0
    cft=cf.tu.values.astype('datetime64[ns]').astype(np.int64); cfa=cf.net.values; pcf=0
    o_,h_,l_,c_=O0+basis,H0+basis,L0_+basis,C0+basis
    evb={}  # bar index -> list of eids
    for e in events:
        k=int(np.searchsorted(BE,ns(e['start_u']),side='right'))
        evb.setdefault(k,[]).append(e['eid'])
    if mode=='L0': bset=sorted(set(xl_b))
    else: bset=boundaries(R,pd.Timestamp(start),zone)
    bset=[b for b in bset]; bi=0
    state=np.zeros(N,np.int8)   # 0 pending/alive-included,1 excluded,2 altclosed,3 live-closed
    alive=set(); A=0.0; B=0.0; Cc=0.0; bal=0.0
    altval=np.zeros(N); epis=np.full(N,-1); episodes=[]; cuts=[]; ext_info={}
    ext_active=set(); gagg={}
    floor=None; ref=None; flat_until=None; flat_from=None; cut_since=False
    probe_out={}
    # positions entering before i0 (none expected) handled by loop from 0 on pointers
    for i in range(i0,nb):
        b0=BT[i]; be=b0+MIN
        # cashflows
        while pcf<len(cft) and cft[pcf]<be:
            bal+=cfa[pcf]
            if floor is not None: floor+=cfa[pcf]; ref+=cfa[pcf]
            pcf+=1
        # removals (live close) at bar ob
        while pout<N and ob[order_out[pout]]<=i:
            k=order_out[pout]; pout+=1
            if state[k]!=0: continue
            if grp[k]>=0 and grp[k] in ext_active: continue
            if ib[k]>ob[k]:   # never alive in a bar
                if flat_until is not None and tin[k]>=flat_from: state[k]=1; epis[k]=cuts[-1]['ep']; continue
                bal+=real[k]; state[k]=3; continue
            bal+=real[k]; state[k]=3
            if k in alive:
                alive.discard(k)
                if isx[k]: A-=s[k]*vol[k]; B-=s[k]*vol[k]*pr[k]; Cc-=cost[k]
        # boundary
        pend=False
        while bi<len(bset) and bset[bi]<=b0: bi+=1; pend=True
        if pend and flat_until is not None and b0>=flat_until: flat_until=None
        # additions
        while pin<N and ib[order_in[pin]]<=i:
            k=order_in[pin]; pin+=1
            if state[k]!=0 or ib[k]>ob[k]: continue
            if flat_until is not None and tin[k]>=flat_from:
                state[k]=1; epis[k]=cuts[-1]['ep']; continue
            alive.add(k)
            if isx[k]: A+=s[k]*vol[k]; B+=s[k]*vol[k]*pr[k]; Cc+=cost[k]
        if flat_until is not None:   # still flat: exclude anything alive opened after cut
            continue
        o,h,l,c=o_[i],h_[i],l_[i],c_[i]
        eq_o=bal+mult*(A*o-B)+Cc; eq_low=bal+min(mult*(A*l-B),mult*(A*h-B))+Cc
        if probe is not None and i in probe: probe_out[i]=eq_low
        if (pend or ref is None) and floor_on:
            if mode in ('ERESET','L0') or ref is None or cut_since: ref=eq_o
            else: ref=max(ref,eq_o)
            floor=(1-P)*ref; cut_since=False
        if floor_on and floor is not None and alive and eq_low<=floor:
            if eq_o<=floor: ps=o
            elif abs(A)>1e-12: ps=min(max((floor-bal-Cc+mult*B)/(mult*A),l),h)
            else: ps=o
            idx=np.fromiter(alive,int)
            vals=np.where(isx[idx],s[idx]*(ps-pr[idx])*vol[idx]*mult+cost[idx],real[idx])
            pre=bal; eqcut=bal+vals.sum()
            ep=len(episodes); episodes.append(dict(kind='cut',bar=i))
            altval[idx]=vals; state[idx]=2; epis[idx]=ep; bal=eqcut
            for g_ in list(ext_active):
                if g_ in set(grp[idx]): ext_active.discard(g_)
            alive=set(); A=B=Cc=0.0
            cuts.append(dict(t=pd.Timestamp(b0),eq=eqcut,bal=pre,loss_pct=(pre-eqcut)/pre*100 if pre>0 else np.nan,ep=ep,floor=floor))
            cut_since=True; flat_from=b0
            if mode=='L0':
                nxt=ns(s2u(u2s(pd.Timestamp(b0),zone).normalize()+pd.Timedelta(days=1),zone))
                bset=sorted(set(bset+[nxt])); bi=int(np.searchsorted(np.array(bset),b0,side='right')); flat_until=nxt
            else:
                flat_until=bset[bi] if bi<len(bset) else FAR
            floor=None
            continue
        # extended groups: resolve at close
        for g_ in list(ext_active):
            ks=[k for k in alive if grp[k]==g_]
            if not ks: ext_active.discard(g_); continue
            ka=np.array(ks); v=float((s[ka]*(c-pr[ka])*vol[ka]*mult+cost[ka]).sum())
            if v>=0:
                vals=s[ka]*(c-pr[ka])*vol[ka]*mult+cost[ka]
                altval[ka]=vals; state[ka]=2; bal+=vals.sum()
                for k in ks:
                    alive.discard(k); A-=s[k]*vol[k]; B-=s[k]*vol[k]*pr[k]; Cc-=cost[k]
                ext_active.discard(g_)
        # live events in this bar -> extended
        if floor_on and i in evb:
            for eid in evb[i]:
                m=[k for k in alive if grp[k]==eid]
                if m:
                    ext_active.add(eid); ep=len(episodes); episodes.append(dict(kind='ext',bar=i,eid=eid))
                    epis[np.array(m)]=ep; ext_info[eid]=dict(ep=ep,eq_low=eq_low,floor=floor)
    # end: extended MTM
    lc=c_[-1]
    for g_ in list(ext_active):
        ka=np.array([k for k in alive if grp[k]==g_])
        if len(ka): altval[ka]=s[ka]*(lc-pr[ka])*vol[ka]*mult+cost[ka]; state[ka]=2
    delta=np.where(state==1,-real,np.where(state==2,altval-real,0.0))
    eps=[dict(ep=k,kind=e['kind'],delta=float(delta[epis==k].sum())) for k,e in enumerate(episodes)]
    return dict(delta=delta,episodes=eps,cuts=cuts,unassigned=float(delta[epis<0].sum()),ext_info=ext_info,real=real,grp=grp,probe=probe_out,evb=evb)

rows=[]; cutrows=[]; evrows=[]; val={}
for Aa,f,old,xlname in ACC:
    zone=TZ.get(Aa,'Europe/Athens')
    d,pi,mult,events,basis,cf,inbar=prep(f,zone)
    # C2: live path, floor off
    rl=simulate(pi,mult,events,basis,cf,zone,'ERESET',R=1,floor_on=False,probe=None)
    evbar={eid:k for k,l in rl['evb'].items() for eid in l}
    rl=simulate(pi,mult,events,basis,cf,zone,'ERESET',R=1,floor_on=False,probe=set(evbar.values()))
    e376=ev376[ev376.acc==old].sort_values('start').reset_index(drop=True)
    for e in events:
        i=e['eid']; eq=rl['probe'].get(evbar[i],np.nan); et=e376.eq_trig.iloc[i] if i<len(e376) else np.nan
        evrows.append(dict(acc=Aa,eid=i,start_srv=e['start_srv'],bal_before=round(e['bal_before']),live_loss=round(e['loss']),
            live_loss_pct=round(e['loss']/e['bal_before']*100,2),eq_low_recon_m1=round(eq) if eq==eq else np.nan,eq_trig_t376=et,
            recon_err_pct=round(abs(eq-et)/e['bal_before']*100,3) if eq==eq and et==et else np.nan))
    val[Aa]=dict(mult=round(mult,3),basis_m1=round(basis,3),deal_in_m1bar=round(inbar,4),n_events=len(events),n_pos=len(pi),
                 n_nonXAU=int((~pi.sym.str.startswith('XAU')).sum()),start_utc=str(cf.tu.min()),end_deals_utc=str(d.tu.max()))
    start=cf.tu.min(); xd=xl[xl.acct==xlname].date.tolist()
    xb=[ns(start)]+[ns(s2u(x,zone)) for x in xd]
    allc=[('L0',simulate(pi,mult,events,basis,cf,zone,'L0',xl_b=xb))]
    for R,ref in CELLS: allc.append((f'R{R}_{ref}',simulate(pi,mult,events,basis,cf,zone,ref,R=R)))
    for name,r in allc:
        ep=pd.DataFrame(r['episodes'])
        saved=float(ep.delta.clip(lower=0).sum()) if len(ep) else 0.0
        forg=float((-ep.delta.clip(upper=0)).sum()) if len(ep) else 0.0
        net=float(r['delta'].sum())
        extd=float(ep[ep.kind=='ext'].delta.sum()) if len(ep) else 0.0
        padj=sum(-max(0.0,ei['eq_low']-ei['floor']) for ei in r['ext_info'].values() if ei['floor'] is not None)
        cl=[c['loss_pct'] for c in r['cuts']]
        rows.append(dict(cell=name,acc=Aa,n_live_events=len(events),n_cuts=len(r['cuts']),n_ext=len(r['ext_info']),
            med_loss_pct_cut=round(float(np.median(cl)),2) if cl else np.nan,saved_usd=round(saved/100,2),forgone_usd=round(forg/100,2),
            net_usd=round(net/100,2),unassigned_usd=round(r['unassigned']/100,2),net_opt_usd=round((net-extd)/100,2),net_pess_usd=round((net-extd+padj)/100,2)))
        for c in r['cuts']:
            near=min(abs((pd.Timestamp(e['start_u'])-c['t']).total_seconds())/3600 for e in events) if events else np.nan
            cutrows.append(dict(cell=name,acc=Aa,t_utc=c['t'],bal_before_usd=round(c['bal']/100,2),eq_cut_usd=round(c['eq']/100,2),
                loss_pct=round(c['loss_pct'],2),hours_to_nearest_live_event=round(near,1)))
    print(Aa,'done',val[Aa],flush=True)

T=pd.DataFrame(rows); C=pd.DataFrame(cutrows); EV=pd.DataFrame(evrows)
T.to_csv('t383_cell_account.csv',index=False); C.to_csv('t383_cuts.csv',index=False); EV.to_csv('t383_live_events_recon.csv',index=False)
n_elig=int((T[T.cell=='L0'].n_live_events>0).sum()); need=math.ceil(5/8*n_elig)
summ=[]
for name in ['L0']+[f'R{R}_{ref}' for R,ref in CELLS]:
    t=T[T.cell==name]; te=t[t.n_live_events>0]; pos=int((te.net_usd>0).sum()); tot=float(t.net_usd.sum())
    summ.append(dict(cell=name,in_K=name!='L0',n_elig=n_elig,need=need,acc_net_pos=pos,total_net_usd=round(tot,2),
        total_saved_usd=round(float(t.saved_usd.sum()),2),total_forgone_usd=round(float(t.forgone_usd.sum()),2),
        total_net_opt_usd=round(float(t.net_opt_usd.sum()),2),total_net_pess_usd=round(float(t.net_pess_usd.sum()),2),
        n_cuts=int(t.n_cuts.sum()),med_loss_pct_cut=round(float(C[C.cell==name].loss_pct.median()),2) if (C.cell==name).any() else np.nan,
        passes=bool((name!='L0') and pos>=need and tot>0)))
S=pd.DataFrame(summ); S.to_csv('t383_summary.csv',index=False)
c1=float(C[C.cell=='L0'].loss_pct.median()); c2=float(EV.recon_err_pct.median())
C1=bool(16.5<=c1<=26.5); C2=bool(c2<=3.0)
l0c=C[C.cell=='L0']; w48=int((l0c.hours_to_nearest_live_event<=48).sum())
cand=S[S.passes].copy(); winner=None
if len(cand):
    cand['rn']=cand.total_net_usd.round(0); cand['R']=cand.cell.str.extract(r'R(\d+)_')[0].astype(int); cand['e']=cand.cell.str.endswith('ERESET').astype(int)
    winner=cand.sort_values(['rn','R','e'],ascending=False).iloc[0].cell
verdict='GO' if (winner and C1 and C2) else 'NO-GO'
out=dict(version='v2_M1',n_elig=n_elig,need=need,K_this_run=6,K_cumulative_t383=12,C1_L0_median_loss_pct=round(c1,2),C1_pass=C1,
    C2_median_recon_err_pct=round(c2,3),C2_pass=C2,L0_cuts=int(len(l0c)),L0_cuts_within48h_of_live=w48,live_events=int(len(EV)),
    live_median_loss_pct=round(float(EV.live_loss_pct.median()),2),L0_total_net_usd=float(S[S.cell=='L0'].total_net_usd.iloc[0]),
    winner=winner,verdict=verdict,m1_bars=int(len(BT)),m1_end_utc=str(pd.Timestamp(PX_END)),validation=val)
json.dump(out,open('t383_validation.json','w'),indent=1,default=str)
pd.set_option('display.width',250); pd.set_option('display.max_rows',200)
print(S.to_string()); print(json.dumps({k:v for k,v in out.items() if k!='validation'},indent=1,default=str))
