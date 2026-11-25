# t387 - descriptive shared-event analysis. Follows PREREG_t387.md (sha in PREREG_t387.sha256).
import pandas as pd, numpy as np, re, json
B='/workspace/bridge_pending/'
ev=pd.read_csv(B+'delivered_t376/t376_events.csv')
bk=pd.read_csv(B+'delivered_t379/t379_events_basket.csv')
st=pd.read_csv(B+'delivered_t377/t377_bd_sets.csv')
assert len(ev)==59 and len(bk)==59
e=ev.merge(bk[['acc','start','lead_side','buy_magic','sell_magic','buy_lot_init','sell_lot_init','lead_bal_start','prot_loss']],on=['acc','start'],how='left',validate='1:1')
assert e.prot_loss.notna().all()
alias={'BD1':'A1','BD2':'A2','BD3':'A3','BTC_Bot_4':'A4','BD5':'A5','BD6':'A6','BD7':'A7','BD8':'A8'}
e['aid']=e.acc.map(alias)
e['t_srv']=pd.to_datetime(e.start)
e['t']=e.t_srv+pd.to_timedelta(np.where(e.aid.isin(['A1','A8']),1,0),unit='h')  # CET->EET
e['date']=e.t.dt.normalize(); e['hour']=e.t.dt.floor('h')
e['lead_magic']=np.where(e.lead_side=='buy',e.buy_magic,e.sell_magic)
e['lot_init']=np.where(e.lead_side=='buy',e.buy_lot_init,e.sell_lot_init)
e['lot_per_eq']=e.lot_init/e.lead_bal_start*1e5   # lots per 100k account units (cents)
def fam(s):
    s=str(s)
    if s.startswith('Lars 1M per Excel but no trades'): return 'NOTRADES'
    if s.startswith('Lars'): return 'Lars'
    if s.startswith('casperit black dragon set m1'): return 'casper_m1'
    if 'Hybrid' in s: return 'CasperIT_Hybrid'
    if 'Agressive' in s or 'Aggressive' in s: return 'CasperIT_Aggressive'
    if s.startswith('1H_R'): return 'Ramil_1H'
    if s.startswith('EA_Black_Dragon_mt5_xauusd_m5_2_digits_stoch_true'): return 'stoch_true'
    if 'stochastic_asian' in s: return 'stoch_asian'
    if 'jpb' in s.lower(): return 'JPB'
    if s.startswith('BTC Bot'): return 'BTC_Bot'
    if 'Trend AI' in s: return 'TrendAI'
    if 'Hamster' in s: return 'Hamster'
    if 'manual' in s: return 'manual'
    return 'UNKNOWN'
st['aid']=st.acct.map(lambda a:{'BD4':'A4'}.get(a,'A'+a[2:]))
st['fam']=st.set_name.map(fam)
st['tf']=st.tf_observed.astype(str).str.split().str[0]
st['f']=pd.to_datetime(st.from_date); st['to']=pd.to_datetime(st.to_date)
st['magics']=st.magic.astype(str).str.split('/')
def cfg(r):
    d=r.t_srv.normalize()
    if r.lead_magic==0: return ('manual(magic0)','-')
    m=str(int(r.lead_magic))
    c=st[(st.aid==r.aid)&(st.f<=d)&(st.to>=d)&st.magics.map(lambda L:m in L)]
    if len(c)==0: return ('UNKNOWN','?')
    if len(c)>1: print('multi-match',r.aid,r.start,list(c.fam))
    return (c.iloc[0].fam,c.iloc[0].tf)
e[['set_fam','tf']]=e.apply(lambda r:pd.Series(cfg(r)),axis=1)
e=e.sort_values('t').reset_index(drop=True)
# groups
def groups(key):
    out=[]
    for k,g in e.groupby(key):
        if g.aid.nunique()>=2: out.append((k,g))
    return out
def cfg_flags(g):
    f=g.sort_values('t').groupby('aid').first()
    known=~f.set_fam.isin(['UNKNOWN'])
    s_set=known.all() and f.set_fam.nunique()==1
    s_tf=s_set and f.tf.nunique()==1 and not (f.tf=='?').any()
    lr=f.lot_per_eq.max()/f.lot_per_eq.min()
    s_lot=s_tf and lr<=1.20
    return s_set,s_tf,s_lot,lr,f
# time clusters <=60 min across >=2 accounts
e['tc']=(e.t.diff()>pd.Timedelta(minutes=60)).cumsum()
gl={}
rows=[]
for name,key in [('day','date'),('hour','hour'),('cluster60','tc')]:
    gs=groups(key); gl[name]=gs
    e['shared_'+name]=e[key].isin([k for k,_ in gs])
    for k,g in gs:
        s_set,s_tf,s_lot,lr,f=cfg_flags(g)
        rows.append(dict(level=name,key=str(k) if name!='cluster60' else str(g.t.min()),n_acc=g.aid.nunique(),n_ev=len(g),
            accounts='|'.join(sorted(g.aid.unique())),configs='|'.join(f'{a}:{r.set_fam}/{r.tf}/{r.lot_per_eq:.3f}' for a,r in f.iterrows()),
            same_set=s_set,same_set_tf=s_tf,same_set_tf_lot=s_lot,lot_ratio_maxmin=round(lr,3),
            prot_loss_cents=int(g.prot_loss.sum())))
G=pd.DataFrame(rows)
e['n_acc_day']=e.groupby('date').aid.transform('nunique')
# Q3
tot=e.prot_loss.sum(); tot2=e.loss_money.sum()
q3={}
for lab,m in [('>=3',e.n_acc_day>=3),('==2',e.n_acc_day==2),('>=2',e.n_acc_day>=2),('==1',e.n_acc_day==1)]:
    q3[lab]=dict(n_days=int(e[m].date.nunique()),n_ev=int(m.sum()),prot_loss_usd=round(e[m].prot_loss.sum()/100,2),share=round(e[m].prot_loss.sum()/tot,4),
                 lossmoney_usd=round(e[m].loss_money.sum()/100,2),share_lossmoney=round(e[m].loss_money.sum()/tot2,4))
# Q2 day classes
days=pd.bdate_range('2026-04-13','2026-10-26')
act=st[st.fam!='NOTRADES']
cls=[]
for d in days:
    a=act[(act.f<=d)&(act.to>=d)]
    na=a.aid.nunique()
    c=None if na<2 else ('LARS_ALL' if (a.fam=='Lars').all() else 'MIXED')
    de=e[e.date==d]
    cls.append(dict(date=d,cls=c,n_active=na,n_ev=len(de),n_acc_ev=de.aid.nunique(),shared=int(de.aid.nunique()>=2),evday=int(len(de)>0)))
D=pd.DataFrame(cls)
ev_wk=e[(e.date<pd.Timestamp('2026-04-13'))|(e.date>pd.Timestamp('2026-10-26'))|(e.date.dt.dayofweek>=5)]
print('events outside window/weekend:',len(ev_wk))
D=D[D.cls.notna()].copy()
D['wk']=D.date.dt.isocalendar().week.astype(int)
def metrics(d):
    return dict(R1=d.shared.sum()/len(d), R2=(d.shared.sum()/d.evday.sum()) if d.evday.sum()>0 else np.nan,
                R3=d.n_ev.sum()/d.n_active.sum())
obs={c:metrics(D[D.cls==c]) for c in ['MIXED','LARS_ALL']}
desc={c:dict(days=int((D.cls==c).sum()),weeks=int(D[D.cls==c].wk.nunique()),shared_days=int(D[D.cls==c].shared.sum()),
             event_days=int(D[D.cls==c].evday.sum()),events=int(D[D.cls==c].n_ev.sum()),acc_days=int(D[D.cls==c].n_active.sum()),
             mean_active=round(D[D.cls==c].n_active.mean(),2)) for c in ['MIXED','LARS_ALL']}
rng=np.random.default_rng(387)
blk={c:[g[['shared','evday','n_ev','n_active']].sum().values for _,g in D[D.cls==c].groupby('wk')] for c in ['MIXED','LARS_ALL']}
blk={c:np.array(v,dtype=float) for c,v in blk.items()}
nd={c:np.array([len(g) for _,g in D[D.cls==c].groupby('wk')],dtype=float) for c in blk}
B_=10000; res={k:[] for k in ['R1','R2','R3']}; dropped=0
for _ in range(B_):
    m={}
    for c in blk:
        i=rng.integers(0,len(blk[c]),len(blk[c])); s=blk[c][i].sum(0); n=nd[c][i].sum()
        m[c]=dict(R1=s[0]/n,R2=s[0]/s[1] if s[1]>0 else np.nan,R3=s[2]/s[3])
    for k in res: res[k].append(m['MIXED'][k]-m['LARS_ALL'][k])
boot={}
for k,v in res.items():
    v=np.array(v); ok=v[~np.isnan(v)]
    boot[k]=dict(diff=obs['MIXED'][k]-obs['LARS_ALL'][k],lo=np.percentile(ok,2.5),hi=np.percentile(ok,97.5),n_valid=len(ok),p_le0=float((ok<=0).mean()))
# outputs
outcols=['aid','t','date','set_fam','tf','lead_side','lot_per_eq','n_acc_day','shared_day','shared_hour','shared_cluster60','prot_loss','loss_money']
E=e[outcols].copy(); E['t']=E.t.dt.strftime('%Y-%m-%d %H:%M:%S'); E['date']=E.date.dt.strftime('%Y-%m-%d')
E['lot_per_eq']=E.lot_per_eq.round(4)
cl=D.set_index('date').cls; E['period_cls']=pd.to_datetime(E.date).map(cl)
E.rename(columns={'t':'t_athens','prot_loss':'prot_loss_cents','loss_money':'lossmoney_cents','lot_per_eq':'lot_per_100k_units'}).to_csv('t387_events_shared.csv',index=False)
G.to_csv('t387_groups.csv',index=False)
D.assign(date=D.date.dt.strftime('%Y-%m-%d')).to_csv('t387_days.csv',index=False)
S=[]
for lvl in ['day','hour','cluster60']:
    g=G[G.level==lvl]
    S.append(dict(question='Q1',metric=f'shared_{lvl}_groups',value=len(g),extra=f'events_in={int(g.n_ev.sum())}; same_set={int(g.same_set.sum())}; same_set_tf={int(g.same_set_tf.sum())}; same_set_tf_lot={int(g.same_set_tf_lot.sum())}; n_acc_dist={dict(g.n_acc.value_counts().sort_index())}'))
for c in desc: S.append(dict(question='Q2',metric=f'{c}_desc',value='',extra=json.dumps(desc[c])))
for k in boot:
    S.append(dict(question='Q2',metric=f'{k}_MIXED',value=round(obs['MIXED'][k],4),extra=''))
    S.append(dict(question='Q2',metric=f'{k}_LARS_ALL',value=round(obs['LARS_ALL'][k],4),extra=''))
    S.append(dict(question='Q2',metric=f'{k}_diff_MIXED_minus_LARS',value=round(boot[k]['diff'],4),extra=f"CI95=[{boot[k]['lo']:.4f},{boot[k]['hi']:.4f}]; n_valid={boot[k]['n_valid']}; frac_boot<=0={boot[k]['p_le0']:.3f}"))
for lab,v in q3.items(): S.append(dict(question='Q3',metric=f'days_{lab}_accounts',value=v['prot_loss_usd'],extra=json.dumps(v)))
S.append(dict(question='Q3',metric='total_prot_loss_usd',value=round(tot/100,2),extra=f'lossmoney_total_usd={tot2/100:.2f}; n_events=59'))
pd.DataFrame(S).to_csv('t387_summary.csv',index=False)
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',200)
print(E.to_string()); print(G.to_string()); print(pd.DataFrame(S).to_string())
