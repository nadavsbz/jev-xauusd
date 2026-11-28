import pandas as pd, numpy as np
out=[]
for m in ['2026-02','2026-03','2026-04','2026-05','2026-06','2026-07']:
    t=pd.read_csv(f'/workspace/algotrade/data/ticks/xauusd_ticks_{m}.csv.gz',usecols=['timestamp','bidPrice','askPrice'])
    ts=pd.to_datetime(t.timestamp.str.slice(0,19),format='%Y-%m-%d %H:%M:%S')
    s=pd.Series((t.askPrice-t.bidPrice).values,index=ts.dt.floor('min'))
    out.append(s.groupby(level=0).median()); print(m,len(t),flush=True)
S=pd.concat(out).sort_index(); S=S[~S.index.duplicated()]
S.to_frame('spread').to_csv('duk_spread_m1.csv')
print(S.describe())
