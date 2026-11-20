# EXPLORATORY rule screen on the simplified BD-like ladder (see bdlike_sim.py header for all simplifications).
# Variants: baseline; FREEZE(N,T): if a basket reaches level N within T minutes of its L1, no further levels for that basket;
# WIDEN(N,T,X): same trigger, but all further steps are multiplied by X. Floor proxy: a basket is cut when its floating loss
# (L1-lot units x $) reaches F; realized -F. Profit per closed basket = +0.5 x total units (exit at avg+0.5).
import numpy as np, pandas as pd, numba, sys
SP=0.30
@numba.njit
def run(tmin,o,h,l,sig,maxlev,N,T,X,mode,F,res,days):
    # res: per-basket [open_i, close_i, maxlev, pnl, peakfloat, fired_i]
    nb=0
    nlev=np.zeros(2,np.int64); fills=np.zeros((2,12)); lots=np.zeros((2,12))
    lastaddbar=np.zeros(2,np.int64); topen=np.zeros(2,np.int64); fired=np.zeros(2,np.int64); rec=np.zeros(2,np.int64)
    for i in range(len(tmin)):
        bar=tmin[i]//15
        if tmin[i]%15==0 and sig[i]!=0:
            s=0 if sig[i]>0 else 1
            if nlev[s]==0:
                nlev[s]=1; fills[s,0]=o[i]+SP if s==0 else o[i]; lots[s,0]=1.0
                lastaddbar[s]=bar; topen[s]=tmin[i]; fired[s]=0
                rec[s]=nb; res[nb,0]=i; res[nb,1]=-1; res[nb,2]=1; res[nb,3]=0; res[nb,4]=0; res[nb,5]=-1; nb+=1
        for s in range(2):
            k=nlev[s]
            if k==0: continue
            r=rec[s]
            fl=0.0; vol=0.0; wsum=0.0
            for j in range(k):
                if s==0: fl+=lots[s,j]*(fills[s,j]-l[i])
                else: fl+=lots[s,j]*((h[i]+SP)-fills[s,j])
                vol+=lots[s,j]; wsum+=lots[s,j]*fills[s,j]
            if fl>res[r,4]: res[r,4]=fl
            if F>0 and fl>=F:
                res[r,1]=i; res[r,3]=-F; nlev[s]=0; days[i]+= -F; continue
            added=False
            allow = k<maxlev and bar!=lastaddbar[s]
            if fired[s]==1 and mode==1: allow=False
            if allow:
                dist=3.0 if k<5 else 2.0*1.2**(k-5)
                if fired[s]==1 and mode==2: dist*=X
                last=fills[s,k-1]
                if s==0:
                    trig=(last-SP)-dist
                    if l[i]<=trig:
                        fills[s,k]=min(trig,o[i])+SP; lots[s,k]=lots[s,k-1]*1.5; added=True
                else:
                    trig=last+dist
                    if h[i]+SP>=trig:
                        fills[s,k]=max(trig,o[i]+SP); lots[s,k]=lots[s,k-1]*1.5; added=True
                if added:
                    nlev[s]=k+1; lastaddbar[s]=bar; res[r,2]=k+1
                    if mode>0 and fired[s]==0 and k+1>=N and (tmin[i]-topen[s])<=T:
                        fired[s]=1; res[r,5]=i
            if not added:
                avg=wsum/vol
                if (s==0 and h[i]>=avg+0.6) or (s==1 and (l[i]+SP)<=avg-0.6):
                    res[r,1]=i; res[r,3]=0.5*vol; days[i]+=0.5*vol; nlev[s]=0
    return nb
def prep():
    df=pd.read_pickle('data/m1_all.pkl')
    m15=df.c.resample('15min').last().dropna(); ema=m15.ewm(span=99,adjust=False).mean()
    sig=np.sign(m15-ema).shift(1).reindex(df.index,method='ffill').fillna(0).values.astype(np.int64)
    tmin=(df.index.as_unit('s').asi8//60).astype(np.int64)
    return df,tmin,sig
if __name__=='__main__':
    df,tmin,sig=prep()
    rows=[]
    variants=[('baseline',0,0,1,0)]
    for N in (4,5):
        for T in (45,60,90,120):
            variants.append((f'FREEZE N{N} T{T}',N,T,1,1))
            variants.append((f'WIDEN x2 N{N} T{T}',N,T,2.0,2))
    for F in (150.0,300.0):
        for name,N,T,X,mode in variants:
            res=np.zeros((len(df)//2,6)); days=np.zeros(len(df))
            nb=run(tmin,df.o.values,df.h.values,df.l.values,sig,10,N,T,X,mode,F,res,days)
            r=pd.DataFrame(res[:nb],columns=['i_open','i_close','maxlev','pnl','peak','i_fired'])
            r['t']=df.index[r.i_open.astype(int)]
            dser=pd.Series(days,index=df.index).resample('1D').sum(); dser=dser[dser!=0]
            for per,(a,b) in {'dev18-22':('2018','2022'),'hold23-26':('2023','2026')}.items():
                rr=r[(r.t>=a)&(r.t<str(int(b)+1))]; dd=dser[a:b]
                eq=dd.cumsum(); mdd=(eq.cummax()-eq).max()
                rows.append(dict(F=F,variant=name,period=per,baskets=len(rr),cuts=int((rr.pnl<0).sum()),
                  fired=int((rr.i_fired>=0).sum()), pnl=round(rr.pnl.sum(),1), worst_day=round(dd.min(),1), mdd=round(mdd,1),
                  open_at_end=int((rr.i_close<0).sum())))
    out=pd.DataFrame(rows); out.to_csv('data/rule_screen.csv',index=False)
    pd.set_option('display.width',250); print(out.to_string())
