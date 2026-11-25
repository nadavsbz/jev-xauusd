# t394 stage0 per PREREG_t394.md (sha 30b39777...). read-only.
import pandas as pd, numpy as np, glob
H='/workspace/algotrade/history/'
ACC={'A1':'Black_Dragon_1','A2':'Black_Dragon_2','A3':'Black_Dragon_3','A4':'BTC_Bot_4','A5':'Black_Dragon_5','A6':'Black_Dragon_6','A7':'Black_Dragon_7','A8':'Black_Dragon_8'}
T76={'BD1':'A1','BD2':'A2','BD3':'A3','BTC_Bot_4':'A4','BD5':'A5','BD6':'A6','BD7':'A7','BD8':'A8'}
EG={'A1','A8'}
def athens(a,ms):
    t=pd.to_datetime(ms,unit='ms'); return t+pd.Timedelta(hours=1) if a in EG else t
def toutc(t): return pd.DatetimeIndex(t).tz_localize('Europe/Athens',ambiguous='NaT',nonexistent='shift_forward').tz_convert('UTC').tz_localize(None)
m1=pd.concat([pd.read_csv(f,parse_dates=['ts']) for f in sorted(glob.glob('/workspace/t383/m1data/m1_*.csv'))]).sort_values('ts').drop_duplicates('ts').set_index('ts').close
POS=[]; BAL=[]
for a,f in ACC.items():
    d=pd.read_csv(H+f+'_deals.csv',dtype={'comment':str,'symbol':str}); d['ta']=athens(a,d.time_msc)
    d['cash']=d.profit+d.swap+d.commission+d.fee
    BAL.append(pd.DataFrame({'acc':a,'ta':d.ta,'cash':d.cash}))
    g=d[(d.type<=1)&(d.symbol.fillna('').str.startswith('XAUUSD'))]
    en=g[g.entry==0]; ex=g[g.entry!=0]
    agg=g.groupby('position_id').agg(pnl=('cash','sum'),mtm=('profit','sum'),cost=('commission','sum'),swap=('swap','sum'))
    agg['cost']=agg.cost+agg.swap
    tc=ex.groupby('position_id').ta.max()
    p=en.drop_duplicates('position_id').set_index('position_id')[['ta','type','volume','price','magic']].rename(columns={'ta':'t_open'})
    p=p.join(agg[['pnl','mtm','cost']]).join(tc.rename('t_close')); p['acc']=a
    POS.append(p.reset_index())
P=pd.concat(POS,ignore_index=True); P['sgn']=np.where(P.type==0,1,-1); P['t_close']=P.t_close.fillna(pd.Timestamp('2100-01-01'))
P['side']=np.where(P.sgn>0,'B','S')
# baskets per (acc,magic,side)
P=P.sort_values(['t_open','position_id']).reset_index(drop=True); P['basket']=''; P['level']=0
for (a,mg,s),g in P.groupby(['acc','magic','side']):
    bid=0; lvl=0; end=pd.Timestamp('1970-01-01')
    for i in g.index:
        if P.at[i,'t_open']>end: bid+=1; lvl=0
        lvl+=1; end=max(end,P.at[i,'t_close']); P.at[i,'basket']=f'{a}_{mg}_{s}_{bid}'; P.at[i,'level']=lvl
P['tu_open']=toutc(P.t_open); P['tu_close']=toutc(P.t_close.where(P.t_close<pd.Timestamp('2099-01-01'),pd.Timestamp('2099-01-01')))
# E0 per Athens day
B=pd.concat(BAL).sort_values('ta')
days=pd.date_range(P.t_open.min().floor('D'),P.t_open.max().floor('D'),freq='D')
E0={}
for d0 in days:
    tot=0.0
    for a in ACC:
        b=B[(B.acc==a)&(B.ta<d0)]
        if len(b)==0: continue
        bal=b.cash.sum()
        op=P[(P.acc==a)&(P.t_open<d0)&(P.t_close>=d0)]
        if len(op):
            u=toutc([d0])[0]; j=m1.index.searchsorted(u,side='right')-1; px=m1.iloc[j]+0.30
            bal+=((px-op.price)*op.sgn*op.volume*100).sum()
        tot+=bal
    E0[d0]=tot
P['day']=P.t_open.dt.floor('D'); P['E0']=P.day.map(E0)
# chronological replay (UTC): events = opens and closes
ev=[]
for i,r in P.iterrows():
    ev.append((r.tu_open,1,i)); ev.append((r.tu_close,0,i))
ev.sort(key=lambda x:(x[0],x[1]))
L=0.0; blocked=np.zeros(len(P),bool); bblk=set(); P['L_act']=np.nan; P['L_cf']=np.nan; P['blk_first']=False; P['PS']=np.nan
Lact=0.0; trace=[]
for t,kind,i in ev:
    q=P.at[i,'sgn']*P.at[i,'volume']
    if kind==0:
        Lact-=q
        if not blocked[i]: L-=q
        trace.append((t,Lact,L)); continue
    b=P.at[i,'basket']; lvl=P.at[i,'level']; mg=P.at[i,'magic']
    if b in bblk: blocked[i]=True
    elif lvl>=2 and mg!=0:
        ps=abs(L+q)*100*12+abs(q)*100*0.5; P.at[i,'PS']=ps
        if ps>0.08*P.at[i,'E0']: blocked[i]=True; bblk.add(b); P.at[i,'blk_first']=True
    Lact+=q
    if not blocked[i]: L+=q
    trace.append((t,Lact,L))
P['blocked']=blocked
TR=pd.DataFrame(trace,columns=['tu','L_act','L_cf'])
P.to_pickle('P394.pkl'); TR.to_pickle('TR394.pkl'); pd.Series(E0).to_csv('E0.csv')
print('positions',len(P),'blocked',blocked.sum(),'baskets blocked',len(bblk),'of',P.basket.nunique())
