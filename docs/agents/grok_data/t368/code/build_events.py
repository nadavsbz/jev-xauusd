#!/usr/bin/env python3
"""t368 step 1 (NO PRICES): build and freeze the tariff-announcement event list from TiRADE v1.10.
Uses only the TiRADE CSV and the exchange trading calendar (dates/hours, no prices)."""
import pandas as pd, json, hashlib, sys
from pathlib import Path
D = Path('/workspace/t368/data')
src = D/'tirade-v1.10-rate-statements.csv'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='73153ba2abb489ebbf872298826ace0eb7dbb2469a5298b1f5a18b9466c777f1'
t = pd.read_csv(src)
cal = pd.DataFrame(json.load(open(D/'calendar_2025_2026.json')))
cal['date']=pd.to_datetime(cal['date'])
cal['close_dt']=pd.to_datetime(cal['date'].dt.strftime('%Y-%m-%d')+' '+cal['close'])
sess = cal.sort_values('date').reset_index(drop=True)
PRES = {'Speech','Social','Executive Order','White House statement'}
ROLE = {'first_statement','modification'}
TAG = {'signal','instrument'}
def okev(s):
    s=str(s); return any(k in s for k in ('Threatened','Announced','Implemented')) and s!='Announced (deal)'
pres = t[t.source_type.isin(PRES)].copy()
q = pres[pres.role.isin(ROLE) & pres.tag.isin(TAG) & pres.event_type.map(okev) & (pres.rate_value>0)]
pres['ts'] = pd.to_datetime(pres.date+' '+pres.time_eastern.fillna('00:00'))
timed = pres[pres.time_eastern.notna()]
ev=[]
for eid, rows in q.groupby('event_id'):
    allr = pres[pres.event_id==eid]
    tr = allr[allr.time_eastern.notna()]
    if len(tr):
        ts=tr.ts.min(); how='T1_event_id_earliest_timed'
    else:
        d0=allr.date.min(); same=timed[timed.date==d0]
        if len(same): ts=same.ts.min(); how='T2_same_date_earliest_timed_tariff_row'
        else: ts=pd.Timestamp(d0+' 00:00'); how='T3_untimed'
    ev.append({'event_id':eid,'row_id':';'.join(rows.row_id),'date':str(ts.date()),'time_eastern':None if how=='T3_untimed' else ts.strftime('%H:%M'),
               'how':how,'timed':how!='T3_untimed','source_type':';'.join(sorted(set(rows.source_type))),'event_type':';'.join(sorted(set(rows.event_type))),
               'tag':';'.join(sorted(set(rows.tag))),'role':';'.join(sorted(set(rows.role))),'countries':';'.join(rows.countries.astype(str)),
               'sectors':';'.join(sorted(set(rows.sectors.astype(str)))),'rate_value':rows.rate_value.max(),'link':rows.link.iloc[0]})
f=pd.DataFrame(ev)
def map_row(r):
    ts = pd.Timestamp(f"{r.date} {r.time_eastern if isinstance(r.time_eastern,str) else '00:00'}")
    after = sess[sess.close_dt > ts]
    before = sess[sess.close_dt <= ts]
    d1 = after.iloc[0]['date']; base = before.iloc[-1]['date']
    return pd.Series({'ts_et':ts,'day1':d1.date(),'base':base.date()})
f = pd.concat([f, f.apply(map_row, axis=1)], axis=1)
f = f[pd.to_datetime(f.day1) <= pd.Timestamp('2026-11-12')]
cols=['event_id','how','row_id','date','time_eastern','ts_et','base','day1','source_type','event_type','tag','role','countries','sectors','rate_value','link']
f[cols].sort_values('ts_et').to_csv(D/'events_rows_all.csv', index=False)
def collapse(df):
    g = df.sort_values('ts_et').groupby('day1').agg(base=('base','first'), first_ts_et=('ts_et','first'), n_rows=('row_id','size'),
        row_ids=('row_id',lambda x:';'.join(x)), source_types=('source_type',lambda x:';'.join(sorted(set(x)))),
        max_rate=('rate_value','max')).reset_index()
    return g
P = collapse(f[f.timed]); P['set']='PRIMARY_timed'
S = collapse(f); S['set']='SECONDARY_all'
P.to_csv(D/'EVENTS_PRIMARY_locked.csv', index=False); S.to_csv(D/'EVENTS_SECONDARY_locked.csv', index=False)
# decluster for 5d (keep earliest; drop events whose day1 is within 5 sessions after a kept day1)
idx = {d.date():i for i,d in enumerate(sess.date)}
def declust(df):
    keep=[]; last=-10**9
    for d in sorted(df.day1):
        i=idx[d]
        if i-last>=5: keep.append(d); last=i
    return df[df.day1.isin(keep)]
P5 = declust(P); P5.to_csv(D/'EVENTS_PRIMARY_dc5_locked.csv', index=False)
print('events(event_id)',len(f),'by how',f.how.value_counts().to_dict())
print('PRIMARY unique day1',len(P),' dc5',len(P5),' SECONDARY',len(S))
print('PRIMARY by year', pd.to_datetime(P.day1).dt.year.value_counts().to_dict(), 'dc5 by year', pd.to_datetime(P5.day1).dt.year.value_counts().to_dict())
print('sessions in universe', len(sess[(sess.date>='2025-01-21')&(sess.date<='2026-11-12')]))
