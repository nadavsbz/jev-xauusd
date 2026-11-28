
import pandas as pd, numpy as np
c1=pd.read_csv('in/c1_monthly.csv'); i2=pd.read_csv('in/i2_monthly.csv')
a=pd.read_csv('/workspace/t399/t399_monthly.csv'); a=a[a.arm=='A7'].copy(); a['r']=a.ret_pct/100
S={'C1':c1.set_index('month').c1_ret,'I2':i2.set_index('month').i2_ret}
A=a.set_index('month').r
def st(r):
  eq=(1+r).cumprod(); dd=(1-eq/np.maximum.accumulate(np.r_[1,eq.values])[1:]).max()
  g=(eq.iloc[-1])**(1/len(r))-1
  yrs=r.groupby(r.index.str[:4]).apply(lambda x:(1+x).prod()-1)
  return dict(n=len(r),mean=round(r.mean()*100,2),geo=round(g*100,2),med=round(r.median()*100,2),pos=round((r>0).mean()*100,1),maxDD=round(dd*100,1),yrs_pos=f"{(yrs>0).sum()}/{len(yrs)}",worst=round(r.min()*100,1),first=r.index[0],last=r.index[-1])
for k,r in S.items():
  print(k,'ALL',st(r)); w=r[r.index>='2022-01']; print(k,'2022+',st(w))
  y=r.groupby(r.index.str[:4]).apply(lambda x:round(((1+x).prod()-1)*100,1)); print(k,'years',dict(y))
  j=pd.concat([A,r],axis=1,join='inner').dropna(); 
  print(k,'vsA7 n',len(j),'pearson',round(j.corr().iloc[0,1],2),'spearman',round(j.corr('spearman').iloc[0,1],2))
  worst=A.nsmallest(5); print(k,'in A7 worst5',[(m,round(A[m]*100,1),round(r.get(m,np.nan)*100,1)) for m in worst.index])
  g1=st(r); print(k,'GATE geo>=3.5',g1['geo']>=3.5,'DD<=25',g1['maxDD']<=25,'n>=18',g1['n']>=18,'pos>=60',g1['pos']>=60)
