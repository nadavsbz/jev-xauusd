# t426: max scale factor k under one-day stress, C1-A4 + I2-ML1.90. Measurement only (K+0). See PREREG_t426.md
import pandas as pd, numpy as np, json, glob, hashlib
P=hashlib.sha256(open('/workspace/t426/PREREG_t426.md','rb').read()).hexdigest()
KS=[1,1.5,2,2.5,3]; CAP=25.0
# ---- C1-A4
B=pd.read_csv('/workspace/t420/bars_t420_A4_MG0.5_drift.csv.gz',parse_dates=['T'])
D=pd.read_csv('/workspace/t420/t420_A4_deals.csv.gz',parse_dates=['ts'])
c1_H24=float(B.L_H24.max()*100); c1_H6=float(B.L_H6.max()*100); c1_H48=float(B.L_H48.max()*100)
c1_tH24=str(B['T'][B.L_H24.idxmax()]); c1_maxgross=float(B.gross.max())
r=B.E.pct_change().fillna(B.E.iloc[0]/120000-1).values
def dd(x): x=np.asarray(x,float); return float((1-x/np.maximum.accumulate(x)).max()*100)
rb=pd.concat([pd.Series([120000.0]),D.balance]).pct_change().dropna().values
# ---- I2
W=json.load(open('/workspace/t421/RESULTS_t421.json'))
Wl={int(a):v for a,v in W['W_long'].items()}; Ws={int(a):v for a,v in W['W_short'].items()}
S=json.load(open('/workspace/t424/tt/summary.json'))
eqdd={int(k[-4:]):float(v['eq_dd'].split('(')[1].rstrip('%)')) for k,v in S.items() if 'lev190' in k}
I2={}; T_all=[]
for f in sorted(glob.glob('/workspace/t424/tt/t424_lev190_*.csv')):
    y=int(f[-8:-4]); d=pd.read_csv(f,parse_dates=['ts'])
    ins=d[d.dir=='in'].reset_index(drop=True); outs=d[d.dir=='out'].reset_index(drop=True)
    T=pd.DataFrame({'tin':ins.ts,'tout':outs.ts,'side':np.where(ins.type=='buy','long','short'),'lev':ins.volume*ins.price/(ins.balance-ins.commission)})
    T['h']=np.minimum(6,np.maximum(1,np.ceil((T.tout-T.tin).dt.total_seconds()/3600))).astype(int)
    T['L']=T.lev*[(Wl if s=='long' else Ws)[h] for s,h in zip(T.side,T.h)]
    T_all.append(T); I2[y]=d
TA=pd.concat(T_all,ignore_index=True)
i2_L=float(TA.L.max()*100); i2_lev=float(TA.lev.max())
i2_net={y:float((d.profit+d.swap+d.commission).sum()/1200) for y,d in I2.items()}
def i2_cdd(d,k): bal=np.r_[120000.0,d.balance.values]; return dd(120000+k*(bal-120000))
san=dict(c1_L_H24=round(c1_H24,2),c1_L_H6=round(c1_H6,2),i2_maxL=round(i2_L,2),i2_net=round(sum(round(v,2) for v in i2_net.values()),2),
  i2_closed_dd=round(max(i2_cdd(d,1) for d in I2.values()),2),i2_eqdd=max(eqdd.values()),i2_maxlev=round(i2_lev,3))
exp=dict(c1_L_H24=21.12,c1_L_H6=11.45,i2_maxL=24.08,i2_net=87.84,i2_closed_dd=9.83,i2_eqdd=10.05,i2_maxlev=1.916)
san_ok=all(abs(san[a]-exp[a])<0.006 for a in exp)
# time-aligned combo (info)
Bi=B.set_index('T').sort_index()
c1_at=Bi.L_H24.reindex(TA.tin.sort_values().values,method='ffill')
ta=(TA.sort_values('tin').L.values+c1_at.values)*100
ta_max=float(np.nanmax(ta)); ta_at=str(TA.sort_values('tin').tin.values[int(np.nanargmax(ta))])[:19]
# combined per-year index
B['y']=B['T'].dt.year
def comb(k):
    nets=[];dds=[]
    for y,g in B.groupby('y'):
        prevE=B.E[B['T']<g['T'].iloc[0]]; E0=prevE.iloc[-1] if len(prevE) else 120000.0
        rc=g.E.values/E0-1
        d=I2.get(y)
        if d is None: ri=np.zeros(len(g))
        else:
            s=d.set_index('ts').balance; s=s[~s.index.duplicated(keep='last')]
            ri=s.reindex(g['T'].values,method='ffill').fillna(120000.0).values/120000-1
            # include I2 deals after last C1 bar of year (year-end)
            rfin=d.balance.iloc[-1]/120000-1; rc=np.r_[rc,rc[-1]]; ri=np.r_[ri,rfin]
        idx=np.r_[1.0,1+k*(rc+ri)]; nets.append(idx[-1]-1); dds.append(dd(idx))
    return sum(nets)*100,max(dds)
def c1_peryear_dd(k):
    return max(dd(np.r_[1.0,np.cumprod(1+k*r[(B.y==y).values])]) for y in sorted(B.y.unique()))
rows=[]
for k in KS:
    rows.append(dict(k=k,
      M1_C1_H24=k*c1_H24,M1_C1_H6=k*c1_H6,M2_I2=k*i2_L,M3_both_H24=k*(c1_H24+i2_L),M3_both_H6=k*(c1_H6+i2_L),M3_time_aligned=k*ta_max,
      C1_net=(np.prod(1+k*r)-1)*100,C1_dd_mtm=dd(120000*np.cumprod(1+k*r)),C1_dd_bal=dd(120000*np.cumprod(1+k*rb)),C1_gross=k*c1_maxgross,
      I2_net=k*sum(i2_net.values()),I2_closed_dd=max(i2_cdd(d,k) for d in I2.values()),I2_eqdd_lin=k*max(eqdd.values()),I2_lev=k*i2_lev,
      comb_net=comb(k)[0],C1_dd_mtm_within_year=c1_peryear_dd(k),comb_dd=comb(k)[1],comb_gross=k*(c1_maxgross+i2_lev)))
maxk={'M1_C1_H24':CAP/c1_H24,'M1_C1_H6':CAP/c1_H6,'M2_I2':CAP/i2_L,'M3_both_H24':CAP/(c1_H24+i2_L),'M3_both_H6':CAP/(c1_H6+i2_L),'M3_time_aligned':CAP/ta_max}
out=dict(prereg_sha256=P,sanity=san,sanity_expected=exp,sanity_ok=san_ok,c1=dict(L_H24=c1_H24,L_H6=c1_H6,L_H48=c1_H48,t_L_H24=c1_tH24,max_gross=c1_maxgross),
  i2=dict(maxL=i2_L,max_lev=i2_lev,worst=TA.loc[TA.L.idxmax(),['tin','side','h','lev']].astype(str).to_dict(),net_by_year=i2_net),
  time_aligned=dict(max=ta_max,at_I2_entry=ta_at),table=rows,max_k=maxk)
json.dump(out,open('/workspace/t426/RESULTS_t426.json','w'),indent=1,default=str)
print(json.dumps(out,indent=1,default=str))
