# t379 aggregation: events_basket.csv + counterfactual.csv. k=100 (cent) -> USD.
import pandas as pd, numpy as np
K=100.0
e=pd.read_csv('/tmp/t379_events.csv'); e['start']=pd.to_datetime(e.start)
b=pd.read_csv('/tmp/t379_baskets.csv',parse_dates=['t0','closed'])
c=pd.concat([pd.read_csv('/tmp/t379_cf_raw.csv'),pd.read_csv('/tmp/t379x_cf_raw.csv').assign(exploratory=True)],ignore_index=True)
c['exploratory']=c.exploratory.fillna(False).astype(bool)
# map crash baskets -> event (same acc, basket closed within [start, start+2h])
cb=b[b.crash].copy(); cb['event_start']=pd.NaT
for i,r in cb.iterrows():
    ee=e[(e.acc==r.acc)&(e.start<=r.closed)&(e.start>=r.closed-pd.Timedelta(hours=2))]
    if len(ee): cb.at[i,'event_start']=ee.start.max()
ev_map=cb.set_index(['acc','bid']).event_start
c['event_start']=[ev_map.get((a,x),pd.NaT) for a,x in zip(c.acc,c.bid)]
main=c[((c.rule.str.startswith('L'))&(c.scope=='5555')&(c.spread==0.3))|((c.rule.str.startswith('D'))&(c.scope=='pess'))]
for rule in ['L4','L5','L6','D5','D8']:
    g=main[main.rule==rule].groupby(['acc','event_start']).delta.sum()
    e[f'saved_{rule}_cents']=[round(g.get((a,s),0.0)) for a,s in zip(e.acc,e.start)]
e['k']=100; e['prot_loss_usd']=(e.prot_loss/K).round(2); e['bal_before_usd']=(e.bal_before/K).round(2)
for rule in ['L4','L5','L6','D5','D8']: e[f'saved_{rule}_usd']=(e[f'saved_{rule}_cents']/K).round(2)
e.to_csv('t379_events_basket.csv',index=False)
rows=[]
for (rule,scope,spread,ex),g in c.groupby(['rule','scope','spread','exploratory']):
    cr=g[g.crash]; nc=g[~g.crash]; accs=g.groupby('acc').delta.sum(); crash_accs=b[b.crash].acc.unique()
    rows.append(dict(rule=rule,scope=scope,spread_usd=spread,exploratory=ex,k=100,
        crash_baskets_hit=len(cr),crash_actual_cents=round(cr.actual.sum()),crash_rule_cents=round(cr.rule_res.sum()),
        crash_saved_cents=round(cr.delta.sum()),noncrash_cut=len(nc),noncrash_cut_profitable=int((nc.actual>0).sum()),
        profit_forgone_cents=round(nc.delta.sum()),net_cents=round(g.delta.sum()),
        accounts_net_pos=f"{int((accs.reindex(crash_accs).fillna(0)>0).sum())}/{len(crash_accs)}",
        crash_saved_usd=round(cr.delta.sum()/K,2),profit_forgone_usd=round(nc.delta.sum()/K,2),net_usd=round(g.delta.sum()/K,2)))
cf=pd.DataFrame(rows); cf.to_csv('t379_counterfactual.csv',index=False)
pd.set_option('display.width',250); print(cf.to_string())
print(e[['level_at_m5pct','level_at_m10pct','hours_m5_to_trig','hours_m10_to_trig']].describe().round(1))
bd=e.lead_is_bd==True; print('lead BD',bd.sum())
for s in ['buy','sell']:
    print(s, e[[f'{s}_levels',f'{s}_maxlot_over_first',f'{s}_adverse_dist_usd',f'{s}_adverse_dist_atr',f'{s}_hours_first_to_trig',f'{s}_ratio_med']].where(e[f'{s}_levels']>0).describe().round(2).to_string())
print('ATR nan',e.atr14_h1.isna().sum(), 'unmapped crash baskets', cb.event_start.isna().sum(), len(cb))
print('per-event L4 saved>0',(e.saved_L4_cents>0).sum(),'L5',(e.saved_L5_cents>0).sum(),'D5',(e.saved_D5_cents>0).sum())
print('prot loss total',e.prot_loss.sum(), 'BD lead', e[bd].prot_loss.sum())
# 5555 basket level distribution
bb=b[(b.magic==5555)&b.symbol.str.startswith('XAU')]
print(bb.groupby(pd.cut(bb.levels,[0,3,4,5,6,8,10,12,40])).agg(n=('net','size'),net=('net','sum'),crash=('crash','sum'),pos=('net',lambda x:(x>0).sum())))
