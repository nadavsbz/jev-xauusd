# EXPLORATORY: R1 vol-floor step and R2 depth-dependent time spacing on the simplified BD-like ladder (see bdlike_sim.py).
import numpy as np, pandas as pd, numba
from bdlike_rules import prep
SP=0.30
@numba.njit
def run(tmin,o,h,l,sig,volref,c,r2,F,res,days):
    nb=0
    nlev=np.zeros(2,np.int64); fills=np.zeros((2,12)); lots=np.zeros((2,12))
    lastaddbar=np.zeros(2,np.int64); rec=np.zeros(2,np.int64)
    for i in range(len(tmin)):
        bar=tmin[i]//15
        if tmin[i]%15==0 and sig[i]!=0:
            s=0 if sig[i]>0 else 1
            if nlev[s]==0:
                nlev[s]=1; fills[s,0]=o[i]+SP if s==0 else o[i]; lots[s,0]=1.0; lastaddbar[s]=bar
                rec[s]=nb; res[nb,0]=i; res[nb,1]=-1; res[nb,2]=1; res[nb,3]=0; res[nb,4]=0; nb+=1
        for s in range(2):
            k=nlev[s]
            if k==0: continue
            r=rec[s]; fl=0.0; vol=0.0; wsum=0.0
            for j in range(k):
                if s==0: fl+=lots[s,j]*(fills[s,j]-l[i])
                else: fl+=lots[s,j]*((h[i]+SP)-fills[s,j])
                vol+=lots[s,j]; wsum+=lots[s,j]*fills[s,j]
            if fl>res[r,4]: res[r,4]=fl
            if F>0 and fl>=F:
                res[r,1]=i; res[r,3]=-F; nlev[s]=0; days[i]-=F; continue
            gap=1
            if r2 and k>=5: gap=k-3      # level 6 needs 2 bars since last add, level 7 needs 3, ...
            added=False
            if k<10 and bar-lastaddbar[s]>=gap:
                dist=3.0 if k<5 else 2.0*1.2**(k-5)
                if c>0 and c*volref[i]>dist: dist=c*volref[i]
                last=fills[s,k-1]
                if s==0:
                    trig=(last-SP)-dist
                    if l[i]<=trig: fills[s,k]=min(trig,o[i])+SP; lots[s,k]=lots[s,k-1]*1.5; added=True
                else:
                    trig=last+dist
                    if h[i]+SP>=trig: fills[s,k]=max(trig,o[i]+SP); lots[s,k]=lots[s,k-1]*1.5; added=True
                if added: nlev[s]=k+1; lastaddbar[s]=bar; res[r,2]=k+1
            if not added:
                avg=wsum/vol
                if (s==0 and h[i]>=avg+0.6) or (s==1 and (l[i]+SP)<=avg-0.6):
                    res[r,1]=i; res[r,3]=0.5*vol; days[i]+=0.5*vol; nlev[s]=0
    return nb
df,tmin,sig=prep()
m15=df.resample('15min').agg({'h':'max','l':'min'}).dropna(); rng=(m15.h-m15.l); rng=rng[rng>0]
d=rng.groupby(rng.index.normalize()).median()
ref=d.rolling(5).median().shift(1)        # median M15 range of the previous 5 trading days (known at day start)
volref=ref.reindex(df.index.normalize()).values; volref=np.nan_to_num(volref,nan=0.0)
rows=[]
for F in (150.0,300.0):
  for name,c,r2 in [('baseline',0,False),('R1 c=1.0',1.0,False),('R1 c=1.5',1.5,False),('R2 time-spacing',0,True),('R1c1.5+R2',1.5,True)]:
    res=np.zeros((len(df)//2,5)); days=np.zeros(len(df))
    nb=run(tmin,df.o.values,df.h.values,df.l.values,sig,volref,c,r2,F,res,days)
    r=pd.DataFrame(res[:nb],columns=['i_open','i_close','maxlev','pnl','peak']); r['t']=df.index[r.i_open.astype(int)]
    ds=pd.Series(days,index=df.index).resample('1D').sum(); ds=ds[ds!=0]
    for per,(a,b) in {'dev18-22':('2018','2022'),'hold23-26':('2023','2026')}.items():
        rr=r[(r.t>=a)&(r.t<str(int(b)+1))]; dd=ds[a:b]; eq=dd.cumsum()
        rows.append(dict(F=F,variant=name,period=per,baskets=len(rr),L8plus=int((rr.maxlev>=8).sum()),cuts=int((rr.pnl<0).sum()),
             gross_win=round(rr.pnl[rr.pnl>0].sum(),0),pnl=round(rr.pnl.sum(),0),worst_day=round(dd.min(),0),mdd=round((eq.cummax()-eq).max(),0)))
out=pd.DataFrame(rows); out.to_csv('data/r1r2_screen.csv',index=False); pd.set_option('display.width',250); print(out.to_string())
