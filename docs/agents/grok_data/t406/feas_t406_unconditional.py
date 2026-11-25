# t406 cost-feasibility: UNCONDITIONAL stats only. Deliberately does NOT compute sign(signal)*return (no data peek).
import pandas as pd, numpy as np, sys
def us_dst(ts):
    # server = UTC+3 during US DST else UTC+2 (per t312/t323 notes; ASSUMED, validated below by volume peak)
    return ts
def load(fn,pip):
    d=pd.read_csv(fn); d['srv']=pd.to_datetime(d.time,unit='s')
    # server->UTC: try US-DST rule
    y=d.srv.dt.year
    utc_guess=d.srv-pd.Timedelta(hours=2)
    ny=utc_guess.dt.tz_localize('UTC').dt.tz_convert('America/New_York')
    off=np.where(ny.dt.strftime('%z')=='-0400',3,2)
    d['utc']=(d.srv-pd.to_timedelta(off,unit='h')).dt.tz_localize('UTC')
    d['ldn']=d.utc.dt.tz_convert('Europe/London')
    d['date']=d.ldn.dt.date; d['hm']=d.ldn.dt.strftime('%H:%M'); d['pip']=pip
    return d
out=[]
for sym,pip in [('EURUSD',1e-4),('USDJPY',1e-2)]:
    d=load(f'data/{sym}.csv',pip)
    # DST sanity: hour (London) of max avg tick volume by month Jan/Jul
    for m in (1,7):
        s=d[d.ldn.dt.month==m].groupby(d.ldn.dt.hour).tick_volume.mean()
        print(sym,'month',m,'top London hours by tickvol', s.sort_values(ascending=False).head(3).to_dict())
    def win(a,b):
        w=d[(d.hm>=a)&(d.hm<b)]
        g=w.groupby('date')
        r=pd.DataFrame({'n':g.size(),'o':g.open.first(),'c':g.close.last(),'h':g.high.max(),'l':g.low.min(),
                        'sp0':g.spread.first(),'year':g.ldn.first().dt.year})
        r=r[r.n==6]
        r['ret']=(r.c-r.o)/pip; r['rng']=(r.h-r.l)/pip
        return r
    L=win('15:30','16:00'); F=win('08:00','08:30')
    print(sym,'days last',len(L),'first',len(F))
    for nm,r in (('first0800',F),('last1530',L)):
        for per,rr in (('2017-2019',r[r.year<2020]),('2020-2026',r[r.year>=2020])):
            print(f"{sym} {nm} {per} N={len(rr)} sd_ret={rr.ret.std():.2f} mean|ret|={rr.ret.abs().mean():.2f} med|ret|={rr.ret.abs().median():.2f} med_rng={rr.rng.median():.2f} p90|ret|={rr.ret.abs().quantile(.9):.2f} spread_pts_med={rr.sp0.median():.1f}")
    Ly=L[L.year>=2020].groupby('year').ret.agg(['count','std',lambda x:x.abs().mean()])
    print(Ly.round(2))
    # spread at 15:30 London in points
