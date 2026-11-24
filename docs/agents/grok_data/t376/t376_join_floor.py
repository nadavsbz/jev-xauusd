import pandas as pd, numpy as np
x=pd.read_csv('/workspace/algotrade/reports/adv2_reset_floors_from_excel.csv'); x['date']=pd.to_datetime(x.date); x=x[x.floor.notna()&(x.reset_equity>0)]
e=pd.read_csv('/tmp/t376_events2.csv',parse_dates=['start'])
amap={'BD1':'#1','BD2':'#2','BD3':'#3','BTC_Bot_4':'#4','BD5':'#5','BD6':'#6','BD7':'#7','BD8':'#8'}
out=[]
for i,r in e.iterrows():
    a=amap[r.acc]; h=x[(x.acct==a)&(x.date<r.start.normalize())]
    prev=e[(e.acc==r.acc)&(e.start<r.start)]
    base=dict(acc=r.acc,start=r.start,eqt=r.eq_trig,bal_before=r.bal_before,dd_vs_bal=r.dd_vs_bal,real_loss_pct=r.real_loss_pct,slip_pct=r.slip_pct)
    if len(h)==0: out.append(base); continue
    l=h.iloc[-1]
    stale = bool(len(prev)) and prev.start.max().normalize()>=l.date
    base.update(floor=l.floor,floor_date=l.date.date(),reset_eq=l.reset_equity,first_after_set=not stale,days=(r.start-l.date).days)
    out.append(base)
o=pd.DataFrame(out)
o['trig_vs_floor']=(o.eqt/o.floor-1)*100
o['floor_pct_reset']=(o.floor/o.reset_eq-1)*100
o.to_csv('/tmp/t376_join2.csv',index=False)
pd.set_option('display.width',250)
print(o[['acc','start','eqt','floor','floor_date','days','first_after_set','trig_vs_floor','floor_pct_reset','dd_vs_bal']].round(2).to_string())
f=o[(o.first_after_set==True)&(o.floor_pct_reset<0)]
print("fresh, below-equity floors n=",len(f)); print(f.trig_vs_floor.describe().round(2))
print("within 3%:",(f.trig_vs_floor.abs()<=3).sum(),"within 1%:",(f.trig_vs_floor.abs()<=1).sum())
print(f.floor_pct_reset.describe().round(2))
s=o[(o.first_after_set==False)]
print("stale (already triggered since setting) n=",len(s)); print(s.trig_vs_floor.describe().round(2))
