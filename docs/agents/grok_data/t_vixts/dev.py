import pandas as pd,numpy as np
D='/workspace/research_new_component/data/yahoo/'
v=pd.read_csv(D+'VIX_daily.csv',parse_dates=['date']).set_index('date').close
v3=pd.read_csv(D+'VIX3M_daily.csv',parse_dates=['date']).set_index('date').close
def px(f):
    d=pd.read_csv(D+f);d.columns=[c.lower() for c in d.columns]
    d['date']=pd.to_datetime(d['date']);return d.set_index('date')['close']
out=[]
for name,f in [('US500','GSPC_daily.csv'),('USTECH','NDX_d.csv')]:
    p=px(f);df=pd.concat([p,v,v3],axis=1,keys=['p','v','v3']).dropna()
    df=df.loc['2006-08-01':'2015-12-31']
    ret=df.p.pct_change().shift(-1)  # return t->t+1
    days=pd.Series(df.index).diff().dt.days.shift(-1).values
    r=df.v/df.v3
    def sim(pos,L):
        pos=pos*L; sw=0.086/365*days*pos
        tc=np.abs(np.diff(np.r_[0,pos/L]))*0.0003*L
        x=(pos*ret-sw-tc).fillna(0); return x
    def stats(x):
        eq=(1+x).cumprod(); mdd=(eq/eq.cummax()-1).min()
        sh=x.mean()/x.std()*np.sqrt(252); m=eq.iloc[-1]**(1/(len(x)/21))-1
        return sh,mdd,m
    def fitL(pos):
        for L in np.arange(0.1,5,0.05):
            if stats(sim(pos,L))[1]< -0.20: return round(L-0.05,2)
        return 5
    bh=pd.Series(1.0,index=df.index)
    for k in ['BH',0.90,0.95,1.00]:
        pos=bh if k=='BH' else (r<k).astype(float)
        L=fitL(pos); sh,mdd,m=stats(sim(pos,L))
        out.append((name,k,L,round(sh,2),round(mdd*100,1),round(m*100,2),round(pos.mean(),2)))
print(pd.DataFrame(out,columns=['asset','k','L','Sharpe','MDD%','mo%','tim']).to_string(index=False))
