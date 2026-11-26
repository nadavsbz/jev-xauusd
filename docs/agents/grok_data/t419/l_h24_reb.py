
import pandas as pd, numpy as np, json, hashlib
KL='/workspace/t417_kL/'; W='/workspace/t419/'
SYM={'BTCUSD':'BTCUSDT','ETHUSD':'ETHUSDT'}
px={}
for s,f in SYM.items():
    b=pd.read_csv(KL+f+'_6h.csv',parse_dates=['time']); b['ct']=b.time.dt.tz_localize(None)+pd.Timedelta(hours=6)
    b=b[(b.time>='2018-01-01')&(b.time<'2026-11-01')]; px[s]=b.set_index('ct').close
P=pd.DataFrame(px).dropna(); RET=P.pct_change()
Psc=P[P.index>=pd.Timestamp('2018-06-01 06:00')]
r1=Psc.pct_change().dropna()
# scenario paths: 4 consecutive bar returns, all overlapping windows
rb=r1.BTCUSD.values; re_=r1.ETHUSD.values; ns=len(rb)-3
SB=np.stack([rb[j:j+ns] for j in range(4)],1); SE=np.stack([re_[j:j+ns] for j in range(4)],1)
starts=r1.index[:ns]
ARMS={'A1_MG0.6':(60,0.6),'A2_VB20':(20,None)}
out={}
for arm,(n,cap) in ARMS.items():
    R=pd.read_csv(W+f'bars_t419_{arm}.csv.gz',parse_dates=['T']).set_index('T')
    res=np.empty(len(R)); arg=np.empty(len(R),int)
    for a in range(0,len(R),150):
        Rc=R.iloc[a:a+150]; m=len(Rc)
        E0=Rc.E.values[:,None]; NB=Rc.NB.values[:,None]*np.ones((1,ns)); NE=Rc.NE.values[:,None]*np.ones((1,ns))
        wB=NB/E0; wE=NE/E0
        # history sums per T for windows of n-j returns
        vols0={}; hs={}
        for s in SYM:
            hr=np.stack([RET[s].loc[:T].iloc[-n:].values for T in Rc.index])  # m x n (oldest..newest)
            hs[s]=hr
        def vol(s,j,scen):  # scen: ns x j returns
            h=hs[s][:,j:]  # drop oldest j
            S1=h.sum(1)[:,None]+(scen.sum(1)[None,:] if j else 0); S2=(h**2).sum(1)[:,None]+((scen**2).sum(1)[None,:] if j else 0)
            return np.sqrt(np.maximum((S2-S1**2/n)/(n-1),1e-18))
        v0={s:vol(s,0,None) for s in SYM}
        E=E0*np.ones((1,ns)); pnl_tot=np.zeros((m,ns))
        for j in range(4):
            p=NB*SB[None,:,j]+NE*SE[None,:,j]; pnl_tot+=p; E=E0+pnl_tot
            if j<3:
                vB=vol('BTCUSD',j+1,SB[:,:j+1]); vE=vol('ETHUSD',j+1,SE[:,:j+1])
                NB=E*wB*v0['BTCUSD']/vB; NE=E*wE*v0['ETHUSD']/vE
                if cap is not None:
                    g=(np.abs(NB)+np.abs(NE))/E; sc=np.where(g>cap,cap/g,1.0); NB*=sc; NE*=sc
        L=-pnl_tot/E0; jj=L.argmax(1); res[a:a+m]=L[np.arange(m),jj]; arg[a:a+m]=jj
    R['L_H24_reb']=res; i=R.L_H24_reb.idxmax()
    yr=R.groupby(R.index.year).agg(L_H24=('L_H24','max'),L_H24_reb=('L_H24_reb','max'))
    out[arm]=dict(max_reb=float(res.max()),T=str(i),win=str(starts[arg[R.index.get_loc(i)]]),max_noreb=float(R.L_H24.max()),
       pct_reb_gt25=float((res>0.25).mean()*100),years={int(y):[round(a*100,2),round(b*100,2)] for y,(a,b) in yr.iterrows()})
print(json.dumps(out,indent=1))
json.dump(out,open(W+'L_H24_reb.json','w'),indent=1)

