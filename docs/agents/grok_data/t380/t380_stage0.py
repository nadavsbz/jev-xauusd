# t380 stage 0: speed-conditioned L_N cut, live counterfactual. Read-only, box only, aliases only.
# Basket/loader/basis/ATR code reused verbatim from t379_map.py. PREREG_t380.md sha256 f13144287fdd6d77ef54d20ccb399f24d46230ae2083169a3c0fce752cabf24a
import pandas as pd, numpy as np, re, json, itertools
H='/workspace/algotrade/history/'
PX='/workspace/claude_bridge/out_20261117/g2_crossmarket/data/XAUUSD_1h.csv'
ACC={'BD1':'Black_Dragon_1','BD2':'Black_Dragon_2','BD3':'Black_Dragon_3','BD5':'Black_Dragon_5',
     'BD6':'Black_Dragon_6','BD7':'Black_Dragon_7','BD8':'Black_Dragon_8','BTC_Bot_4':'BTC_Bot_4'}
NRE=r'^n_[\d.]+_v$'; BDRE=re.compile(r'black.?dragon|eabd',re.I)
px=pd.read_csv(PX); px['t']=pd.to_datetime(px.utc); px=px.set_index('t')[['open','high','low','close']]
pc=px.close.shift(); tr=np.maximum(px.high-px.low,np.maximum((px.high-pc).abs(),(px.low-pc).abs()))
px['atr']=tr.rolling(14).mean().shift(1)
PXEND=px.index.max()
TZ={'BD1':'Europe/Berlin','BD8':'Europe/Berlin'}
def srv2utc(ts,z):
    return pd.DatetimeIndex(ts).tz_localize(z,ambiguous='NaT',nonexistent='shift_forward').tz_convert('UTC').tz_localize(None)
def is_data_et(c):
    t=pd.Timestamp(c).tz_localize('UTC').tz_convert('America/New_York')
    if t.weekday()>4: return False
    for hh,mm in ((8,30),(10,0)):
        r=t.normalize()+pd.Timedelta(hours=hh,minutes=mm)
        if r<=t<=r+pd.Timedelta(minutes=90): return True
    return False
def is_data_srv(c,z):
    t=pd.Timestamp(c).tz_localize('UTC').tz_convert(z)
    if t.weekday()>4: return False
    for hh,mm in ((14,30),(16,0)):
        r=t.normalize()+pd.Timedelta(hours=hh,minutes=mm)
        if r<=t<=r+pd.Timedelta(minutes=90): return True
    return False
COMBOS=[(N,T,k) for N in (6,8) for T in (2,4) for k in (2,3)]
CUT=[];VAL={}
for a,f in ACC.items():
    z=TZ.get(a,'Europe/Athens')
    d=pd.read_csv(H+f+'_deals.csv',dtype={'comment':str}); d['comment']=d.comment.fillna('')
    d['t']=pd.to_datetime(d.time,format='%Y.%m.%d %H:%M:%S'); d=d.sort_values(['time_msc','ticket']).reset_index(drop=True)
    d['net']=d.profit+d.commission+d.swap+d.fee; d.loc[d.type==3,'net']=0.0
    d['tu']=srv2utc(d.t,z); d['tu']=d.tu.fillna(d.t-pd.Timedelta(hours=2))
    tr_=d[d.type.isin([0,1])].copy()
    ent=tr_[tr_.entry==0]; pinfo=ent.groupby('position_id').first()
    n=tr_[tr_.comment.str.match(NRE)]; mm=[]
    for x in n.itertuples():
        if x.position_id in pinfo.index:
            e=pinfo.loc[x.position_id]; s=1 if e.type==0 else -1; dp=(x.price-e.price)*s*x.volume
            if abs(dp)>1e-6: mm.append(x.profit/dp)
    mult=float(np.median(mm)) if mm else 100.0
    gopen={}; pos2b={}; bk={}; bid=0
    for r in tr_.itertuples():
        if r.entry==0:
            key=(r.symbol,r.magic,r.type)
            if gopen.get(key,0)<1e-9:
                bid+=1; bk[bid]=dict(symbol=r.symbol,magic=r.magic,s=1 if r.type==0 else -1,is_bd=bool(BDRE.search(r.comment)),entries=[],key=key)
                gopen[key+('bid',)]=bid
            b=gopen[key+('bid',)]; pos2b[r.position_id]=b; bk[b]['entries'].append((r.tu,r.price,r.volume,r.position_id))
            gopen[key]=gopen.get(key,0)+r.volume
        elif r.entry in (1,3) and r.position_id in pos2b:
            b=pos2b[r.position_id]; key=bk[b]['key']; gopen[key]-=r.volume
            if gopen[key]<1e-9: gopen[key]=0
    tr_['bid']=tr_.position_id.map(pos2b)
    bnet=tr_.groupby('bid').net.sum(); bclose=tr_[tr_.entry.isin([1,3])].groupby('bid').tu.max()
    ex=tr_[tr_.entry.isin([1,3])&(tr_.volume>0)]; exc=float((ex.commission/ex.volume).median()) if len(ex) else 0.0
    j=ent[ent.symbol.str.startswith('XAU')].copy(); j['bar']=j.tu.dt.floor('h'); j=j.join(px,on='bar',how='inner')
    basis=float((j.price-(j.high+j.low)/2).median())
    nd=d[d.comment.str.match(NRE)&d.type.isin([0,1])]
    crash_b=set(nd.position_id.map(pos2b).dropna().astype(int))
    VAL[a]=dict(tz=z,mult=round(mult,4),basis=round(basis,3),exc=exc,crash_baskets=len(crash_b))
    grp={b:g for b,g in tr_.groupby('bid')}
    for b,v in bk.items():
        if not v['symbol'].startswith('XAU'): continue
        scopes=[sc for sc,ok in (('5555',v['magic']==5555),('BD_all',v['is_bd'])) if ok]
        if not scopes or len(v['entries'])<6: continue
        t0=v['entries'][0][0]; p1=v['entries'][0][1]; s=v['s']
        tclose=bclose.get(b,pd.Timestamp('2100-01-01')); actual=float(bnet.get(b,0.0)); g=grp[b]
        for (N,T,k) in COMBOS:
            if len(v['entries'])<N: continue
            tN=v['entries'][N-1][0]
            if not (tN-t0<pd.Timedelta(hours=T)): continue
            bt=tN.floor('h')
            while True:
                c=bt+pd.Timedelta(hours=1)
                if not (c-t0<pd.Timedelta(hours=T+1)) or not (c<tclose) or bt>PXEND: bt=None; break
                if bt in px.index:
                    C=px.at[bt,'close']+basis; atr=px.at[bt,'atr']
                    if atr==atr and s*(p1-C)>=k*atr: break
                bt=bt+pd.Timedelta(hours=1)
            if bt is None: continue
            sub=g[g.tu<=c]; realized=sub.net.sum()
            ov=sub.assign(sv=np.where(sub.entry==0,sub.volume,-sub.volume)).groupby('position_id').sv.sum()
            fl=0.0; vol=0.0
            for pid,vv in ov.items():
                if vv>1e-9: fl+=s*(C-pinfo.at[pid,'price'])*vv*mult; vol+=vv
            for spread in (0.30,0.0):
                res=realized+fl+exc*vol-spread*vol*mult
                for sc in scopes:
                    CUT.append(dict(combo=f'N{N}_T{T}_k{k}',N=N,T=T,k=k,acc=a,scope=sc,spread=spread,bid=b,crash=b in crash_b,
                        t0_utc=t0,tN_utc=tN,cut_utc=c,atr=round(atr,3),adverse_usd=round(s*(p1-C),2),vol_open=round(vol,2),
                        actual=actual,rule_res=res,delta=res-actual,data_et=is_data_et(c),data_srv=is_data_srv(c,z)))
    print(a,VAL[a],flush=True)
cut=pd.DataFrame(CUT); cut.to_csv('t380_cuts_raw.csv.gz',index=False)
json.dump(VAL,open('t380_validation.json','w'),indent=1)
# ---------- aggregate
def agg(x):
    cr=x[x.crash]; nc=x[~x.crash]
    return pd.Series(dict(cuts=len(x),crash_cut=len(cr),saved_cents=cr.delta.sum(),noncrash_cut=len(nc),cut_profitable=int((nc.actual>0).sum()),
        forgone_cents=nc.delta.sum(),net_cents=x.delta.sum()))
rows=[]
for (combo,sc,sp),x in cut.groupby(['combo','scope','spread']):
    for a in ACC:
        xa=x[x.acc==a]; r=dict(combo=combo,scope=sc,spread=sp,acc=a); r.update(agg(xa))
        for lab,m in (('data',xa.data_et),('other',~xa.data_et)):
            q=agg(xa[m]); r.update({f'{lab}_cuts':q.cuts,f'{lab}_saved_cents':q.saved_cents,f'{lab}_forgone_cents':q.forgone_cents,f'{lab}_net_cents':q.net_cents})
        r['other_srvlit_net_cents']=xa[~xa.data_srv].delta.sum()
        rows.append(r)
# include combos with zero cuts
st=pd.DataFrame(rows)
full=[]
for (N,T,k) in COMBOS:
    for sc in ('5555','BD_all'):
        for sp in (0.3,0.0):
            for a in ACC:
                m=st[(st.combo==f'N{N}_T{T}_k{k}')&(st.scope==sc)&(st.spread==sp)&(st.acc==a)]
                full.append(m.iloc[0].to_dict() if len(m) else dict(combo=f'N{N}_T{T}_k{k}',scope=sc,spread=sp,acc=a))
st=pd.DataFrame(full).fillna(0)
for c in [c for c in st.columns if c.endswith('_cents')]: st[c.replace('_cents','_usd')]=(st[c]/100).round(2)
st.to_csv('t380_stage0.csv',index=False)
S=[]
for (combo,sc,sp),x in st.groupby(['combo','scope','spread'],sort=False):
    N,T,k=[int(v[1:]) for v in combo.split('_')]
    r=dict(combo=combo,N=N,T=T,k=k,scope=sc,spread=sp,cuts=int(x.cuts.sum()),crash_cut=int(x.crash_cut.sum()),noncrash_cut=int(x.noncrash_cut.sum()),
        cut_profitable=int(x.cut_profitable.sum()),saved_usd=round(x.saved_cents.sum()/100,2),forgone_usd=round(x.forgone_cents.sum()/100,2),
        net_usd=round(x.net_cents.sum()/100,2),net_data_usd=round(x.data_net_cents.sum()/100,2),net_other_usd=round(x.other_net_cents.sum()/100,2),
        net_other_srvlit_usd=round(x.other_srvlit_net_cents.sum()/100,2),
        acc_pos=int((x.net_cents>0).sum()),acc_pos_other=int((x.other_net_cents>0).sum()),acc_with_cuts=int((x.cuts>0).sum()))
    r['pass_a']=r['acc_pos']>=5; r['pass_b']=r['net_usd']>0; r['pass_c']=r['net_other_usd']>0; r['PASS']=r['pass_a'] and r['pass_b'] and r['pass_c']
    S.append(r)
S=pd.DataFrame(S); S.to_csv('t380_stage0_summary.csv',index=False)
main=S[(S.scope=='5555')&(S.spread==0.3)]
pd.set_option('display.width',250); print(S.to_string())
w=main[main.PASS].sort_values(['net_usd','N','T','k'],ascending=[False,True,False,False])
print('DECISION:', 'GO winner '+w.iloc[0].combo if len(w) else 'NO-GO')
