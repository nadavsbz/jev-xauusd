import alp, pandas as pd, os
from cfg import D, FIRST, LAST
from concurrent.futures import ThreadPoolExecutor
u=pd.read_csv(D+'universe_dev.csv',keep_default_na=False)['symbol'].tolist()
for adj in ['raw','split']:
    fn=D+f'daily_{adj}.parquet'
    if os.path.exists(fn): continue
    rows=[]
    def job(i):
        b=alp.bars(u[i:i+100],'1Day',FIRST,LAST,adjustment=adj)   # asof='-' inside alp.bars
        return pd.DataFrame([(s,x['t'][:10],x['o'],x['h'],x['l'],x['c'],x['v']) for s,bs in b.items() for x in bs],columns=['symbol','date','o','h','l','c','v'])
    with ThreadPoolExecutor(5) as ex:
        for k,r in enumerate(ex.map(job,range(0,len(u),100))):
            rows.append(r)
            if k%20==0: print('daily',adj,'chunk',k,'of',len(u)//100+1,'rows',sum(map(len,rows)),flush=True)
    df=pd.concat(rows,ignore_index=True); del rows
    assert df.date.max()<=LAST
    df.to_parquet(fn); print(adj,'done',len(df),df.symbol.nunique(),flush=True)
