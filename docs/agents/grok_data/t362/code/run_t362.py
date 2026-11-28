# usage: run_t362.py stage   stage in {main, holdout}
import sys, json, numpy as np, pandas as pd, hashlib
sys.path.insert(0,'/workspace/t362/code'); from bt_t362 import *
stage=sys.argv[1]
b=indicators(load_bars())
I2=pd.read_csv('/workspace/independent_review/results/i2_USATECHIDXUSD_daily.csv'); I2['date']=I2['date'].str[:10]; I2=I2.set_index('date')['pnl']
def full(start,end,label,cm=1.0):
    tr=finalize(run(b,start,end,cm),cm); ds=daily_series(b,tr,start,end,cm)
    out=stats(tr,ds,label); out['costmult']=cm
    yrs={}
    for y in sorted(set(d[:4] for d in ds.index)):
        dy=ds[[d.startswith(y) for d in ds.index]]; ty=[t for t in tr if t['xdate'].startswith(y)]
        yrs[y]=stats(ty,dy,y)
    out['years']=yrs
    for side,nm in [(1,'long'),(-1,'short')]:
        ts_=[t for t in tr if t['dir']==side]; net=np.array([t['net'] for t in ts_])
        out[nm]=dict(trades=len(ts_),sum_net_1x=float(net.sum()),win=float((net>0).mean()) if len(net) else None,
            pf=float(net[net>0].sum()/-net[net<0].sum()) if (net<0).any() else None,usd=float(sum(t['usd'] for t in ts_)))
    totr=ds['r'].sum(); out['overnight']=dict(n_trades_overnight=int(sum(t['overnight'] for t in tr)),
        sum_overnight_gap_1x=float(ds['on'].sum()),sum_total_1x=float(totr),share_gap=float(ds['on'].sum()/totr) if totr!=0 else None,
        sum_net_trades_held_overnight=float(sum(t['net'] for t in tr if t['overnight'])),sum_net_intraday_trades=float(sum(t['net'] for t in tr if not t['overnight'])),
        usd_gap=float(ds['onusd'].sum()),usd_total=float(ds['usd'].sum()))
    # I2 comparison
    j=pd.concat([ds['r'],I2],axis=1,join='inner').dropna(); j.columns=['s','i2']
    out['i2']=dict(n_common=len(j),corr_all=float(j['s'].corr(j['i2'])) if len(j)>20 else None,
        corr_active_days=float(j[(j['s']!=0)&(j['i2']!=0)].corr().iloc[0,1]) if ((j['s']!=0)&(j['i2']!=0)).sum()>20 else None,
        i2_mean_on_strat_active=float(j.loc[j['s']!=0,'i2'].mean()),i2_mean_on_strat_flat=float(j.loc[j['s']==0,'i2'].mean()),
        sign_agree_both_active=float((np.sign(j['s'])==np.sign(j['i2']))[(j['s']!=0)&(j['i2']!=0)].mean()),
        i2_sum=float(j['i2'].sum()),strat_sum=float(j['s'].sum()))
    # their leverage
    rthb=b[b['rth']&b['last']].set_index('date')['c']
    px=rthb.loc[ds.index]; E=10000+ds['usd'].cumsum().shift(1).fillna(0)
    out['leverage_3mes']=dict(notional_over_10k_mean=float((150*px/10000).mean()),notional_over_equity_mean=float((150*px/E).mean()),
        notional_over_equity_max=float((150*px/E).max()))
    out['n_open_at_end']=sum(1 for t in tr if t.get('open_at_end'))
    return out,tr,ds
def cov(start,end):
    r=b[b['rth']&(b['date']>=start)&(b['date']<=end)]
    cnt=r.groupby('date').size(); exp=((r.groupby('date')['cm'].first()-r.groupby('date')['om'].first())/3)
    f=cnt/exp; return dict(days=len(cnt),days_lt90=int((f<0.9).sum()),days_lt50=int((f<0.5).sum()),min_frac=float(f.min()))
res={}
if stage=='main':
    res['coverage']={'repl':cov('2023-01-01','2026-09-30'),'dev':cov('2019-01-01','2020-12-31')}
    for nm,(s,e) in {'repl':('2023-01-01','2026-09-30'),'dev':('2019-01-01','2020-12-31')}.items():
        for cm in (1.0,2.0):
            o,tr,ds=full(s,e,nm,cm); res[f'{nm}_x{cm:g}']=o
            if cm==1.0:
                pd.DataFrame(tr).to_csv(f'/workspace/t362/trades_{nm}.csv',index=False); ds.to_csv(f'/workspace/t362/daily_{nm}.csv')
    d=res['dev_x1']; y=d['years']
    dens=d['trades']>=100 and all(y[k]['trades']>=40 for k in ('2019','2020'))
    g=dict(density=dens,pf=d['pf_1x']>=1.3,sharpe=d['sharpe_1x']>=0.8,y2019=y['2019']['ret_1x']>0,y2020=y['2020']['ret_1x']>0,
        corr_proxy=(d['i2']['corr_all'] is not None and d['i2']['corr_all']<=0.5))
    res['dev_gates']=g; res['dev_pass_excl_corr']=all(v for k,v in g.items() if k!='corr_proxy')
    p=res['repl_x1']
    res['repl_match']=dict(trades=abs(p['trades']-396)<=0.25*396,pf=abs(p['pf_usd']-1.84)<=0.30 if p['pf_usd'] else False,
        win=abs(p['win_usd']-0.566)<=0.05,usd=(p['usd_net']>0 and abs(p['usd_net']-29985)<=0.5*29985))
    res['repl_replicates']=all(res['repl_match'].values())
    json.dump(res,open('/workspace/t362/results_t362_main.json','w'),indent=1,default=float)
elif stage=='holdout':
    m=json.load(open('/workspace/t362/results_t362_main.json'))
    assert m['dev_pass_excl_corr'], 'DEV failed: holdout must not run'
    res['coverage']=cov('2021-01-01','2022-12-31')
    for cm in (1.0,2.0):
        o,tr,ds=full('2021-01-01','2022-12-31','holdout',cm); res[f'holdout_x{cm:g}']=o
    json.dump(res,open('/workspace/t362/results_t362_holdout.json','w'),indent=1,default=float)
print(json.dumps({k:v for k,v in res.items() if not isinstance(v,dict) or k in('dev_gates','repl_match','coverage')},default=float))
