# cusum_v1_sim.py  (t320) - adapted from t319/cusum_sim.py, seed 20261120
# Units: daily return standardized by sigma0. Page lower-side CUSUM: S=max(0,S+(mu0-r)/sigma0-k), alarm S>=h
# Inputs (VERIFIED from Claude tester, 2020-24.10.2025): I2 mu0=17.7bp sigma0=155bp (position days);
# C1 mu0=6.9bp sigma0=117bp (calendar days, 365/yr).
# Per side (VERIFIED, Claude tester, 20.11.2026 21:45; side defined by exit deal): Long n=420 mu0=25.2bp sigma0=144bp; Short n=388 mu0=9.7bp sigma0=172bp.
# Per-side runs use the SAME method (k=0.5*mu0/sigma0, ARL0=750 calibration, same scenarios); nothing else changed. Combined I2/C1 code and order unchanged.
import numpy as np
rng=np.random.default_rng(20261120)
def noise(n,T,df):
    return rng.standard_t(df,(n,T))/np.sqrt(df/(df-2)) if df else rng.standard_normal((n,T))
def alarm_times(x,m0,m1,k,h):
    # x standardized noise; true mean m1 (sigma units), reference m0
    S=np.zeros(x.shape[0]); al=np.full(x.shape[0],-1)
    for t in range(x.shape[1]):
        S=np.maximum(0,S+(m0-(m1+x[:,t]))-k)
        al[(S>=h)&(al<0)]=t+1
    return al
def calibrate(m0,k,df,target=750,n=4000,T=6000):
    x=noise(n,T,df); lo,hi=0.5,80
    for _ in range(18):
        h=(lo+hi)/2; al=alarm_times(x,m0,m0,k,h)
        arl=np.where(al<0,T,al).mean()
        if arl<target: lo=h
        else: hi=h
    h=hi; al=alarm_times(x,m0,m0,k,h)
    return h,np.where(al<0,T,al).mean(),(al<0).mean()
def report(label,mu_bp,sig_bp,ann,df,scen):
    m0=mu_bp/sig_bp; k=0.5*m0
    h,arl,cens=calibrate(m0,k,df)
    print(f"{label} df={df} mu0/sigma0={m0:.4f}/day (ann SR@{ann}d={m0*np.sqrt(ann):.3f}) k={k:.4f} h={h:.2f}  ARL0={arl:.0f} days (censored@6000: {cens:.1%} paths no alarm => ARL0 lower bound)")
    T1=3000;n=4000
    x=noise(n,T1,df)
    for name,ratio in scen:
        al=alarm_times(x,m0,m0*ratio,k,h)
        d=np.where(al<0,np.nan,al); a=al>0
        f=lambda L: np.mean(a&(al<=L))
        print(f"   {name}: true SR={ratio*m0*np.sqrt(ann):.3f}  alarm<=250d {f(250):.2f} <=500d {f(500):.2f} <=750d {f(750):.2f} <=3000d {f(3000):.2f}  median delay {np.nanmedian(d):.0f} p25 {np.nanpercentile(d,25):.0f} p75 {np.nanpercentile(d,75):.0f} (days; among alarmed)")
base=[("SR->0",0.0),("half SR",0.5)]
for df in (4,None):
    print("=== df",df)
    report("I2 combined (position days, 252)",17.7,155,252,df,base)
    report("C1 (calendar days, 365)",6.9,117,365,df,base)
    report("I2 Long side (side-days, n=420, 252)",25.2,144,252,df,base)
    report("I2 Short side (side-days, n=388, 252)",9.7,172,252,df,base)
