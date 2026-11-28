import numpy as np
rng=np.random.default_rng(20261120)
def sim(sr_ann, n, T, df=None):
    mu=sr_ann/np.sqrt(252)
    if df: x=rng.standard_t(df,(n,T))/np.sqrt(df/(df-2))
    else: x=rng.standard_normal((n,T))
    return mu+x   # units of sigma0
def cusum_alarm(r, mu0, k, h):
    # lower-side Page CUSUM on standardized shortfall
    S=np.zeros(r.shape[0]); al=np.full(r.shape[0],-1)
    for t in range(r.shape[1]):
        S=np.maximum(0,S+(mu0-r[:,t])-k)
        hit=(S>=h)&(al<0); al[hit]=t+1
    return al
def run(sr0,df,label):
    mu0=sr0/np.sqrt(252)
    for frac in (0.5,):
        # k = half the shift from mu0 to 0  (detect edge->0)
        k=frac*mu0
        # calibrate h for ARL0 target 750 days
        T=3000;n=4000
        r=sim(sr0,n,T,df)
        lo,hi=0.5,60
        for _ in range(14):
            h=(lo+hi)/2; al=cusum_alarm(r,mu0,k,h)
            arl=np.where(al<0,T,al).mean()   # censored at T -> lower bound
            if arl<750: lo=h
            else: hi=h
        h=hi
        print(label,"sr0",sr0,"df",df,"k=%.4f"%k,"h=%.2f"%h,"ARL0~%.0f(cens@%d)"%(arl,T))
        for sr1 in (0.0,-0.46):
            r1=sim(sr1,n,1500,df); al=cusum_alarm(r1,mu0,k,h)
            d=np.where(al<0,np.nan,al)
            print("   true SR",sr1,"alarm<=250d: %.2f"%np.mean((al>0)&(al<=250)),"<=500d: %.2f"%np.mean((al>0)&(al<=500)),"median delay %.0f"%np.nanmedian(d),"p25 %.0f"%np.nanpercentile(d,25))
run(1.33,4,"I2")
run(1.33,None,"I2n")
run(1.5,4,"C1")
