import pandas as pd,glob,re,numpy as np
rows=[]
for f in sorted(glob.glob("*_deals.csv")):
    acc=f.replace("_deals.csv","").replace("Black_Dragon_","BD")
    d=pd.read_csv(f); d['t']=pd.to_datetime(d.time,format="%Y.%m.%d %H:%M:%S")
    d=d.sort_values(['time_msc','ticket']).reset_index(drop=True)
    d['net']=d.profit+d.commission+d.swap+d.fee
    d['bal']=d.net.cumsum()
    d['isn']=d.comment.astype(str).str.match(r"^n_[\d.]+_v$")
    n=d[d.isn]
    if not len(n): continue
    # price match
    cp=n.comment.str.extract(r"n_([\d.]+)_v")[0].astype(float)
    diff=(cp-n.price).abs()
    # cluster by 30-min gap
    ev=(n.t.diff()>pd.Timedelta(minutes=30)).cumsum()
    deps=d[d.type==2]
    for k,g in n.groupby(ev):
        i0=g.index.min(); i1=g.index.max()
        bal_before=d.bal[i0-1] if i0>0 else 0
        bal_after=d.bal[i1]
        hist=d.loc[:i0-1]
        peak=hist.bal.max()
        cumdep=hist[hist.type==2].net.sum()
        # open positions after event: entries in minus outs by position_id up to i1
        sub=d.loc[:i1]; tr=sub[sub.type.isin([0,1])]
        vin=tr[tr.entry==0].groupby('position_id').volume.sum(); vout=tr[tr.entry.isin([1,3])].groupby('position_id').volume.sum()
        op=(vin.sub(vout,fill_value=0)>1e-9).sum()
        # did trading continue within 1h after? (new entries by any magic)
        nxt=d[(d.t>g.t.max())&(d.t<=g.t.max()+pd.Timedelta(hours=1))&(d.entry==0)&(d.type.isin([0,1]))]
        rows.append(dict(acc=acc,start=g.t.min(),end=g.t.max(),n=len(g),dur_s=(g.t.max()-g.t.min()).total_seconds(),
          realized=g.net.sum(),bal_before=bal_before,bal_after=bal_after,peak_bal=peak,cumdep=cumdep,
          open_after=op,new_entries_1h=len(nxt),cp_diff_max=diff[g.index].max(),
          syms=",".join(g.symbol.unique()),dirs=",".join(map(str,g.type.unique()))))
r=pd.DataFrame(rows)
r['loss_pct_bal']=-r.realized/r.bal_before*100
r['eq_vs_peak']=(r.bal_after/r.peak_bal-1)*100
r.to_csv("/tmp/t376_events.csv",index=False)
pd.set_option('display.width',250); pd.set_option('display.max_rows',500)
print(r[['acc','start','n','dur_s','realized','bal_before','loss_pct_bal','eq_vs_peak','open_after','new_entries_1h','cp_diff_max','dirs']].round(2).to_string())
