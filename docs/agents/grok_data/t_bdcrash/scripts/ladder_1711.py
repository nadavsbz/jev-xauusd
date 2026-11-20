# Replays a BD-like BUY ladder on Dukascopy ticks of 17.11.2026 for each possible L1 M15 open (assumes buy signal), to see which start
# reproduces the reported 6-level ladder (x1.5, ~$3). Server time assumed GMT+2 (= Israel time on 17.11).
import pandas as pd, numpy as np
t=pd.read_csv('data/XAUUSD_ticks_2026-11-17.csv.gz',index_col=0); t.index=pd.to_datetime(t.index,utc=True,format='ISO8601'); t=t[['ask','bid']]
def ladder(start, maxlev=10):
    x=t[start:]; fills=[]; times=[]; lastbar=None; openbar=start.floor('15min')
    idx=x.index; A=x.ask.values; B=x.bid.values; bars=idx.floor('15min')
    avg=None
    for n in range(len(x)):
        ts=idx[n]; bar=bars[n]
        if not fills:
            fills=[A[n]]; times=[ts]; lastbar=bar; avg=A[n]; continue
        k=len(fills)
        if B[n]>=avg+0.6: return fills,times,ts,'closed'
        dist=3.0 if k<5 else 2.0*1.2**(k-5)
        if k<maxlev and bar!=lastbar and A[n]<=fills[-1]-dist:
            fills.append(A[n]); times.append(ts); lastbar=bar
            lots=[1.5**j for j in range(len(fills))]; avg=float(np.dot(lots,fills)/sum(lots))
    return fills,times,None,'open at end of data'
for st in pd.date_range('2026-11-17 14:45','2026-11-17 16:30',freq='15min',tz='UTC'):
    f,ti,cl,status=ladder(st)
    print((st+pd.Timedelta(hours=2)).strftime('srv %H:%M'), 'levels',len(f), [ (x+pd.Timedelta(hours=2)).strftime('%H:%M') for x in ti], [round(v,2) for v in f], status, cl+pd.Timedelta(hours=2) if cl is not None else '')

print('--- sequential chain of BUY baskets (one buy basket at a time; new basket at next M15 open after close) ---')
st=pd.Timestamp('2026-11-17 14:45',tz='UTC'); end=t.index[-1]
rows=[]
while st<end:
    f,ti,cl,status=ladder(st)
    lots=[round(0.26*1.5**j,2) for j in range(len(f))]
    rows.append(((st+pd.Timedelta(hours=2)).strftime('%H:%M'),len(f),[ (x+pd.Timedelta(hours=2)).strftime('%H:%M') for x in ti],[round(v,2) for v in f],status,(cl+pd.Timedelta(hours=2)).strftime('%H:%M:%S') if cl is not None else ''))
    if cl is None: break
    st=cl.ceil('15min') if cl!=cl.floor('15min') else cl+pd.Timedelta(minutes=15)
for r in rows:
    if r[1]>1 or True: print('srv',*r)
