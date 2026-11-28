# Build M1 BID OHLC (UTC) from local Dukascopy ticks. Read-only on source.
import pandas as pd, sys
from multiprocessing import Pool
MON=['2025-09','2025-10','2025-11','2025-12']+[f'2026-{m:02d}' for m in range(1,11)]
def one(m):
    f=f'/workspace/algotrade/data/ticks/xauusd_ticks_{m}.csv.gz'
    t=pd.read_csv(f,usecols=['timestamp','bidPrice'])
    t['ts']=pd.to_datetime(t.timestamp.str.slice(0,19))
    g=t.set_index('ts').bidPrice.resample('1min').ohlc().dropna()
    g.to_csv(f'm1data/m1_{m}.csv'); return m,len(t),len(g)
if __name__=='__main__':
    with Pool(4) as p:
        for r in p.imap_unordered(one,MON): print(r,flush=True)
