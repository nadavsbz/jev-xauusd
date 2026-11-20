# Velocity metrics on 17.11.2026 (Dukascopy ticks->M1) vs the empirical distribution of the same metrics in 2026-01..2026-10-19 (GitHub Dukascopy M1 mirror).
import pandas as pd, numpy as np
hist=pd.read_pickle('data/m1_all.pkl'); hist=hist['2026-01-01':]
hist=hist[(hist.h-hist.l)>0]
d=pd.read_csv('data/XAUUSD_m1_2026-11-17.csv',index_col=0); d.index=pd.to_datetime(d.index,utc=True)
d=d.rename(columns={'open':'o','high':'h','low':'l','close':'c'})[['o','h','l','c']]
def metrics(x):
    c=x.c
    out=pd.DataFrame(index=x.index)
    for w in (15,30,60,180):
        out[f'chg{w}']=c-c.shift(w)
    # G_Crash score of the clone: max(hi-close, close-lo) over 15 M1 bars / (avg M1 range of the previous 60 bars x sqrt(15))
    rng=(x.h-x.l); avg=rng.shift(15).rolling(60).mean()
    hi=x.h.rolling(15).max(); lo=x.l.rolling(15).min()
    out['gcrash']=np.maximum(hi-c,c-lo)/(avg*np.sqrt(15))
    return out
H=metrics(hist); D=metrics(d)
print('G_Crash (mult 3.0) fire minutes on 17.11 (UTC):', list(D.index[D.gcrash>3.0].strftime('%H:%M')))
q={}
for w in (15,30,60,180):
    s=H[f'chg{w}'].dropna(); q[w]=s
rows=[]
for lab,t in [('retail sales +10m (13:40)', '2026-11-17 13:40'),('pre-spike low 15:00 srv17:00','2026-11-17 15:00'),('spike top 15:43','2026-11-17 15:43'),
              ('srv 18:00 L1 (16:00)','2026-11-17 16:00'),('srv 18:52 (16:52)','2026-11-17 16:52'),('srv 19:30 L1 (17:30)','2026-11-17 17:30'),('srv 20:00 (18:00)','2026-11-17 18:00'),('srv 20:46 (18:46)','2026-11-17 18:46'),('srv 21:00 (19:00)','2026-11-17 19:00')]:
    t=pd.Timestamp(t,tz='UTC')
    if t not in D.index: continue
    r={'point':lab}
    for w in (15,30,60,180):
        v=D.loc[t,f'chg{w}']; r[f'chg{w}$']=round(v,2) if pd.notna(v) else None
        r[f'pct{w}']=round(100*(q[w]<=v).mean(),1) if pd.notna(v) else None
    r['gcrash']=round(D.loc[t,'gcrash'],2) if pd.notna(D.loc[t,'gcrash']) else None
    rows.append(r)
out=pd.DataFrame(rows); pd.set_option('display.width',250); print(out.to_string()); out.to_csv('data/velocity_1711.csv',index=False)
# 3h windows: how unusual was the 15:43->18:55 UTC decline
dec=d.loc['2026-11-17 15:43':'2026-11-17 18:55']
print('decline 15:43->18:55 UTC: high',d.loc['2026-11-17 15:43','h'],'low',d.loc['2026-11-17 18:55','l'])
s=H['chg180'].dropna(); print('2026 percentile of a -$%.2f 180-min change: %.1f%%'%(36.25,100*(s<=-36.25).mean()))
print('2026 median |chg15|, |chg60|, |chg180|:', H.chg15.abs().median().round(2), H.chg60.abs().median().round(2), H.chg180.abs().median().round(2))
# retail-sales impulse vs other release minutes 13:30 UTC in 2026
h2=pd.read_pickle('data/m1_all.pkl')['2025-01-01':]
imp=[]
for day,g in h2.groupby(h2.index.normalize()):
    try:
        o=g.loc[day+pd.Timedelta(hours=13,minutes=30),'o']; w=g.loc[day+pd.Timedelta(hours=13,minutes=30):day+pd.Timedelta(hours=13,minutes=44)]
        imp.append(max(o-w.l.min(), w.h.max()-o))
    except KeyError: pass
imp=pd.Series(imp); v=3857.04-3836.655
print('17.11 retail-sales 15-min max excursion $%.2f; percentile among all 13:30-13:44 UTC windows 2025-01..2026-10: %.1f%% (n=%d)'%(v,100*(imp<=v).mean(),len(imp)))
