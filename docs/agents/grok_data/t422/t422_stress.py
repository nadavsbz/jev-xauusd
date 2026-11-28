#!/usr/bin/env python3
"""t422_stress.py - brake-aware stress per PREREG_t422.md (sha256 1ca156d4bdb43eaa1533841bc5c2b065ef01fa7cdf0737f958776a8a4d76abf3).
Input: bars CSV produced by t418.py core (unchanged, sha de171394...f28a) for the arm deals: columns T,E,NB,NE (USD notionals at H6 close T).
For every grid bar T and every historical joint 4-bar scenario window (Binance H6 2018-06..2026-10, same set as t418 H24):
  cumulative loss after bar m (m=1..4): L_m = -(NB*(P_m/P_0-1)+NE*(...))/E   (no rebalance inside window, as t418)
  trigger at bar m if for BTC or ETH: |ln(P_m/P_{m-1})| / sd >= 3.0 and the move is against the held sign (sign of NB/NE at T),
  sd = sample std (ddof=1, as EA C1b) of the 60 H6 log returns preceding bar m = last (60-(m-1)) historical log returns up to T + scenario bars 1..m-1.
  k = first trigger bar; L_brake = L_k + 0.5*(L_4 - L_k) if k exists else L_4.
Gate G2: max over T,scenarios of L_brake <= 25%.
Usage: python3 t422_stress.py <bars.csv.gz> <out_prefix>
"""
import pandas as pd, numpy as np, json, sys
KL='/workspace/t417_kL/'; SYM={'BTCUSD':'BTCUSDT','ETHUSD':'ETHUSDT'}; CAP=0.25; Z=3.0; NW=60
bars_path, outp = sys.argv[1], sys.argv[2]
px={}
for s,f in SYM.items():
    b=pd.read_csv(KL+f+'_6h.csv',parse_dates=['time']); b['ct']=b.time.dt.tz_localize(None)+pd.Timedelta(hours=6)
    b=b[(b.time<'2026-11-01')]; px[s]=b.set_index('ct').close
Pall=pd.DataFrame(px).dropna()
P=Pall[Pall.index>=pd.Timestamp('2018-06-01 06:00')]   # same scenario set as t418 (time>='2018-06-01' -> first close 06:00)
LR=np.log(Pall).diff()
# scenario windows of 4 bars: start close index j, bars j+1..j+4
pb=P.BTCUSD.values; pe=P.ETHUSD.values; ns=len(P)-4
CB=np.stack([pb[j+1:j+1+ns]/pb[:ns]-1 for j in range(4)],1)  # cumulative simple return after bar m (ns x 4)
CE=np.stack([pe[j+1:j+1+ns]/pe[:ns]-1 for j in range(4)],1)
LB=np.stack([np.log(pb[j+1:j+1+ns]/pb[j:j+ns]) for j in range(4)],1)  # bar log returns
LE=np.stack([np.log(pe[j+1:j+1+ns]/pe[j:j+ns]) for j in range(4)],1)
starts=P.index[:ns]
R=pd.read_csv(bars_path,parse_dates=['T']).set_index('T')
def histsums(sym):
    S1=np.zeros((len(R),4)); S2=np.zeros((len(R),4))
    lr=LR[sym]
    for i,T in enumerate(R.index):
        h=lr.loc[:T].values[-NW:]
        for q in range(4):
            x=h[q:]; S1[i,q]=x.sum(); S2[i,q]=(x*x).sum()   # last 60-q returns
    return S1,S2
H={'BTCUSD':histsums('BTCUSD'),'ETHUSD':histsums('ETHUSD')}
SCN={'BTCUSD':LB,'ETHUSD':LE}
out_L4=np.empty(len(R)); out_Lb=np.empty(len(R)); arg=np.empty(len(R),int); ktrig=np.zeros(len(R),int)
E=R.E.values; NB=R.NB.values; NE=R.NE.values; CH=60
for a in range(0,len(R),CH):
    sl=slice(a,a+CH); m_=len(E[sl])
    pnl=NB[sl,None,None]*CB[None]+NE[sl,None,None]*CE[None]        # m x ns x 4
    L=-pnl/E[sl,None,None]
    trig=np.zeros_like(L,dtype=bool)
    for s,N in (('BTCUSD',NB),('ETHUSD',NE)):
        S1h,S2h=H[s]; X=SCN[s]
        cs1=np.concatenate([np.zeros((ns,1)),np.cumsum(X,1)[:,:3]],1); cs2=np.concatenate([np.zeros((ns,1)),np.cumsum(X*X,1)[:,:3]],1)
        s1=S1h[sl][:,None,:]+cs1[None]; s2=S2h[sl][:,None,:]+cs2[None]
        var=(s2-s1*s1/NW)/(NW-1); sd=np.sqrt(np.maximum(var,0))
        sg=np.sign(N[sl])[:,None,None]
        adverse=(sg!=0)&(np.sign(X)[None]!=sg)&(X[None]!=0)
        trig|=(sd>0)&(np.abs(X)[None]/np.where(sd>0,sd,1)>=Z)&adverse
    any_=trig.any(2); k=np.where(any_,trig.argmax(2),3)
    Lk=np.take_along_axis(L,k[...,None],2)[...,0]; L4=L[...,3]
    Lb=np.where(any_,Lk+0.5*(L4-Lk),L4)
    j=Lb.argmax(1); out_Lb[sl]=Lb[np.arange(m_),j]; arg[sl]=j; out_L4[sl]=L4.max(1)
    ktrig[sl]=np.where(any_[np.arange(m_),j],k[np.arange(m_),j]+1,0)
R['L_H24_plain']=out_L4; R['L_H24_brake']=out_Lb; R['W_brake']=starts[arg]; R['k_brake']=ktrig
i=R.L_H24_brake.idxmax()
res=dict(max_L_H24_brake=float(R.L_H24_brake.max()),at=str(i),window_start=str(R.loc[i,'W_brake']),k=int(R.loc[i,'k_brake']),
         max_L_H24_plain=float(R.L_H24_plain.max()),n_bars_brake_gt25=int((R.L_H24_brake>CAP).sum()),n=len(R),
         G2=bool(R.L_H24_brake.max()<=CAP),
         per_year={int(y):round(float(x.L_H24_brake.max())*100,2) for y,x in R.groupby(R.index.year)})
R[['E','NB','NE','L_H24_plain','L_H24_brake','W_brake','k_brake']].to_csv(outp+'_bars.csv.gz')
json.dump(res,open(outp+'.json','w'),indent=1); print(json.dumps(res,indent=1))
