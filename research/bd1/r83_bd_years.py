"""Round 83 groundwork (16.11.2026): BD ms20_h1119 per year - floor-cut days (<-2%), their side, gold daily range; trailing 20d median range before each cut. Descriptive (in-sample)."""
import sys, numpy as np, pandas as pd
sys.path.insert(0,'research/btc');sys.path.insert(0,'research/stable');sys.path.insert(0,'research/scan')
from guardian_sim import deals
from r64_mass import loadh
h=loadh("XAUUSD"); dc=h.close.resample("1D").last().dropna(); rng=(h.high.resample("1D").max()-h.low.resample("1D").min()).reindex(dc.index)
rows=[]
for y in range(2016,2026):
    x=deals(f"C:/MT5_JEV_TEST/{'ev18' if y<=2018 else 'ev12'}_rf{y}_ms20_h1119.htm")
    x["day"]=pd.to_datetime(x.t,unit="s").dt.normalize(); x["net"]=x.profit+x.swap+x.commission
    o=x[x.dir=="out"]
    d=x.groupby("day").net.sum(); eq=120000+d.cumsum(); r=d/eq.shift(1).fillna(120000)
    stop=r[r<-0.02]  # big loss days
    # side of the losing basket on stop days: closing deal type buy = closing a short
    sides=[]
    for day in stop.index:
        z=o[(o.day==day)&(o.net<0)]; sides.append("S" if (z.type=="buy").sum()>=(z.type=="sell").sum() else "L")
    g=dc[str(y)]; gr=rng[str(y)]
    rows.append(dict(y=y,ret=round((eq.iloc[-1]/120000-1)*100), days=len(d), win_days=round(r[r>=0].sum()*100), loss_days=round(r[r<0].sum()*100),
        n_stop=len(stop), stop_sum=round(stop.sum()*100), sides="".join(sides), gold_yr=round((g.iloc[-1]/g.iloc[0]-1)*100),
        rng_usd=round(gr.median(),1), rng_pct=round((gr/g).median()*100,2), avg_win_day=round(r[r>0].mean()*100,3), lots=round(x[x.dir=="in"].volume.mean(),2)))
print(pd.DataFrame(rows).to_string(index=False))
# exploratory: trailing 20d median $ range known before the day
tr=rng.rolling(20).median().shift(1); tp=(rng/dc).rolling(20).median().shift(1)*100
for y in range(2016,2026):
    x=deals(f"C:/MT5_JEV_TEST/{'ev18' if y<=2018 else 'ev12'}_rf{y}_ms20_h1119.htm")
    x["day"]=pd.to_datetime(x.t,unit="s").dt.normalize(); x["net"]=x.profit+x.swap+x.commission
    d=x.groupby("day").net.sum(); eq=120000+d.cumsum(); r=d/eq.shift(1).fillna(120000)
    st=r[r<-0.02]
    print(y, "stop days trailing range $:", [round(tr.get(k,np.nan),1) for k in st.index], " %:",[round(tp.get(k,np.nan),2) for k in st.index],
          "| year median trailing $", round(tr[str(y)].median(),1))
