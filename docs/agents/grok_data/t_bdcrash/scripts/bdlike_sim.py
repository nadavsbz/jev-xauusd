# EXPLORATORY (not pre-registered). Simplified BD-like ladder on Dukascopy XAUUSD M1 bid (GitHub mirror kevingtlin/dukascopy_XAUUSD_1m_Data).
# Rules approximated from docs/BD_CLONE.md (read-only): entry at M15 open by sign(prev M15 close - EMA99 M15), x1.5 lots,
# $3 steps for levels 2-5, $2*1.2^(k-6) from level 6, max one add per basket per M15 bar, none in the opening bar,
# exit when bid reaches avg+0.6 (closed at avg+0.5 ~ trailing 0.6/0.1). Overlap, swaps, news pause, Thu/Fri off, floor: NOT modelled.
# Constant spread 0.30. Intrabar: adverse add is processed before exit; no exit in a bar that added.
import numpy as np, pandas as pd, glob, sys, numba
SP=0.30
def load(files):
    dfs=[pd.read_csv(f) for f in sorted(files)]
    d=pd.concat(dfs); d=d.drop_duplicates('timestamp').sort_values('timestamp')
    # drop flat filler minutes (Dukascopy fills closed market with constant price)
    return d
@numba.njit
def sim(tmin,o,h,l,c,ema_prev_sig,maxlev, out):
    # out rows: side, open_idx, close_idx, maxlev, t_lvl(1..10 idx), mae_float_units, fills
    nb=0
    open_=np.zeros(2,np.int64); nlev=np.zeros(2,np.int64)
    fills=np.zeros((2,12)); lots=np.zeros((2,12)); lastaddbar=np.zeros(2,np.int64); openbar=np.zeros(2,np.int64)
    rec=np.full(2,-1,np.int64)
    for i in range(len(tmin)):
        bar=tmin[i]//15
        if tmin[i]%15==0:
            sg=ema_prev_sig[i]
            if sg!=0:
                s=0 if sg>0 else 1
                if nlev[s]==0:
                    nlev[s]=1; fills[s,0]= o[i]+SP if s==0 else o[i]; lots[s,0]=1.0
                    openbar[s]=bar; lastaddbar[s]=bar
                    r=nb; nb+=1; rec[s]=r
                    out[r,0]=s; out[r,1]=i; out[r,2]=-1; out[r,3]=1; out[r,4]=i
                    for k in range(5,14): out[r,k]=-1
                    out[r,14]=0.0; out[r,15]=fills[s,0]
        for s in range(2):
            if nlev[s]==0: continue
            r=rec[s]; k=nlev[s]
            # floating loss at adverse extreme (units: L1 lot x $)
            fl=0.0; vol=0.0; wsum=0.0
            for j in range(k):
                if s==0: fl+=lots[s,j]*(fills[s,j]-l[i])
                else: fl+=lots[s,j]*((h[i]+SP)-fills[s,j])
                vol+=lots[s,j]; wsum+=lots[s,j]*fills[s,j]
            if fl>out[r,14]: out[r,14]=fl
            added=False
            if k<maxlev and bar!=lastaddbar[s]:
                if k<5: dist=3.0
                else: dist=2.0*1.2**(k-5)
                last=fills[s,k-1]
                if s==0:
                    trig=(last-SP)-dist  # bid level
                    if l[i]<=trig:
                        px=min(trig,o[i])+SP; fills[s,k]=px; lots[s,k]=lots[s,k-1]*1.5; added=True
                else:
                    trig=last+dist
                    if h[i]+SP>=trig:
                        px=max(trig,o[i]+SP)-SP+SP; px=max(trig,o[i]); fills[s,k]=px; lots[s,k]=lots[s,k-1]*1.5; added=True
                if added:
                    nlev[s]=k+1; lastaddbar[s]=bar; out[r,3]=k+1; out[r,4+k]=i
                    vol+=lots[s,k]; wsum+=lots[s,k]*fills[s,k]
            if not added:
                avg=wsum/vol
                if s==0 and h[i]>=avg+0.6:
                    out[r,2]=i; nlev[s]=0
                elif s==1 and (l[i]+SP)<=avg-0.6:
                    out[r,2]=i; nlev[s]=0
    return nb
if __name__=='__main__':
    files=glob.glob('data/m1_bid/xauusd_bid_m1_*.csv')
    d=load(files)
    t=pd.to_datetime(d.timestamp,unit='ms',utc=True)
    df=pd.DataFrame({'o':d.open.values,'h':d.high.values,'l':d.low.values,'c':d.close.values},index=t)
    # remove filler: minutes where o=h=l=c equal to previous close for weekends
    df=df[df.index.dayofweek<5]
    m15=df.c.resample('15min').last().dropna()
    ema=m15.ewm(span=99,adjust=False).mean()
    sig=np.sign(m15-ema)                 # computed at M15 close
    sig_next=sig.shift(1)                # known at next bar open
    s1=sig_next.reindex(df.index,method='ffill').fillna(0).values
    tmin=(df.index.as_unit('s').asi8//60).astype(np.int64)
    out=np.zeros((len(df)//2,16))
    nb=sim(tmin,df.o.values,df.h.values,df.l.values,df.c.values,s1.astype(np.int64),10,out)
    out=out[:nb]
    cols=['side','i_open','i_close','maxlev']+[f'i_L{k}' for k in range(1,11)]+['peak_float','fill1']
    b=pd.DataFrame(out,columns=cols)
    idx=df.index
    for ccol in ['i_open','i_close']+[f'i_L{k}' for k in range(1,11)]:
        b[ccol.replace('i_','t_')]=[idx[int(x)] if x>=0 else pd.NaT for x in b[ccol]]
    b.to_pickle('data/bdlike_baskets.pkl')
    df.to_pickle('data/m1_all.pkl')
    print(nb, b.maxlev.value_counts().sort_index().to_dict())
