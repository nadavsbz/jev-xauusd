# t425 — fixed weekly MONITORING THRESHOLDS (measurement only, no experiment, K+0). Read-only inputs.
import pandas as pd, numpy as np, json, glob
R={}
def pct(s): s=np.asarray(s,float); return dict(n=len(s),P5=round(float(np.percentile(s,5)),2),P50=round(float(np.percentile(s,50)),2),P95=round(float(np.percentile(s,95)),2),min=round(float(s.min()),2),max=round(float(s.max()),2))
def consec(mon):
    x=(mon<np.percentile(mon,5)); best=cur=0
    for v in x: cur=cur+1 if v else 0; best=max(best,cur)
    return int(best)
def ddmax(e): e=np.asarray(e,float); pk=np.maximum.accumulate(e); return float(((pk-e)/pk).max()*100)
# ---------- C1 (H6 bars, E = balance + Binance MtM float) ----------
def c1(bars,deals,name,cap,tester_dd):
    b=pd.read_csv(bars,usecols=['T','bal','E','gross'],parse_dates=['T']).set_index('T')
    d=pd.read_csv(deals,parse_dates=['ts'])
    me=b.E.resample('ME').last().dropna()
    prev=np.r_[120000.0,me.values[:-1]]; r=(me.values/prev-1)*100
    mon=pd.Series(r,index=me.index.strftime('%Y-%m'))
    # leverage cross-check from deals: volume*price*cs/balance (cs BTC1 ETH10, VERIFIED in t418)
    cs=d.symbol.map({'BTCUSD':1,'ETHUSD':10})
    R[name]=dict(period=f"{b.index.min()}..{b.index.max()}",n_bars=len(b),n_deals=len(d),
        dd_recon_H6=round(ddmax(np.r_[120000.0,b.E.values]),2),dd_balance=round(ddmax(np.r_[120000.0,d.balance.values]),2),
        tester_dd=tester_dd,gross_max=round(float(b.gross.max()),3),gross_max_T=str(b.gross.idxmax()),gross_p99=round(float(b.gross.quantile(.99)),3),cap=cap,
        months=pct(mon),months_first=mon.index[0],months_last=mon.index[-1],worst_month=mon.idxmin(),
        n_months_lt_P5=int((mon<np.percentile(mon,5)).sum()),
        max_consec_lt_P5=int(max((g.sum() for _,g in (mon<np.percentile(mon,5)).groupby(((mon<np.percentile(mon,5))!=(mon<np.percentile(mon,5)).shift()).cumsum())),default=0)))
c1('/workspace/t418/bars_t418_AV0.075.csv.gz','/workspace/t418/c1_ecn_av075_full_deals.csv.gz','C1_base_MG3',3.0,14.06)
c1('/workspace/t420/bars_t420_A4_MG0.5_drift.csv.gz','/workspace/t420/t420_A4_deals.csv.gz','C1_alt_A4_MG0.5',0.5,None)
# ---------- I2 current (TV0.075 MaxLev5) proxy = t402 TV0.15 deals x0.5 ----------
d=pd.read_csv('/workspace/t402/in/i2_deals_2020_2026.csv',parse_dates=['ts'])
d['net']=(d.profit_pct+d.swap_pct+d.commission_pct)*0.5
mon=[];dds=[];levs=[];yrs={}
for y,g in d.groupby('year'):
    g=g.sort_values('ts',kind='stable'); E=100+g.net.cumsum()
    Eb=np.r_[100.0,E.values[:-1]]  # equity before each deal
    ins=g.dir.values=='in'
    lev=(g.vol_per_100k.values*0.5*g.price.values/1e5)/(Eb/100)  # notional/equity, 1 lot = 1 index unit (VERIFIED vs t424 2020 first trade)
    levs+=list(lev[ins])
    if y==2023: lev2023=float(lev[ins].max())
    outs=g[g.dir=='out']; Eo=100+outs.net.cumsum()*0+E[g.dir=='out']
    dds.append(ddmax(np.r_[100.0,E[g.dir=='out'].values])); yrs[int(y)]=round(float(g.net.sum()),2)
    m=g.set_index('ts').net.resample('ME').sum(); e=100+m.cumsum(); p=np.r_[100.0,e.values[:-1]]
    mon+=list(zip(m.index.strftime('%Y-%m'),m.values/p*100))
M=pd.Series(dict(mon)); last=d.ts.max(); M=M[M.index<last.strftime('%Y-%m')] if last.day<28 else M
R['I2_current_TV0.075_ML5_proxy']=dict(period=f"{d.ts.min()}..{d.ts.max()}",n_trades=int((d.dir=='in').sum()),year_net=yrs,
    dd_closed_max=round(max(dds),2),dd_closed_by_year=[round(x,2) for x in dds],lev_max=round(float(max(levs)),3),lev_p99=round(float(np.percentile(levs,99)),3),cap=5.0,
    lev_max_2023=round(lev2023,3),max_consec_lt_P5=consec(M),months=pct(M),months_first=M.index[0],months_last=M.index[-1],worst_month=M.idxmin(),excluded_partial=last.strftime('%Y-%m') if last.day<28 else None)
# ---------- I2 candidate MaxLev 1.90 (t424 real tester, yearly from 120K) ----------
S=json.load(open('/workspace/t424/tt/summary.json'))
mon=[];dds=[];levs=[];eqdd={}
for f in sorted(glob.glob('/workspace/t424/tt/t424_lev190_*.csv')):
    y=int(f[-8:-4]); g=pd.read_csv(f,parse_dates=['ts'])
    ins=g[g.dir=='in']; levs+=list(ins.volume*ins.price/(ins.balance-ins.commission))
    dds.append(ddmax(np.r_[120000.0,g.balance.values]))
    eqdd[y]=float(S[f't424_lev190_{y}']['eq_dd'].split('(')[1].rstrip('%)'))
    m=g.set_index('ts').balance.resample('ME').last().ffill(); p=np.r_[120000.0,m.values[:-1]]
    mon+=list(zip(m.index.strftime('%Y-%m'),(m.values/p-1)*100))
M=pd.Series(dict(mon)); M=M[M.index!='2026-11']  # 2026-11 partial (data ends 2026-11-20)
R['I2_candidate_ML1.90']=dict(period='2020..2026-11-20 (7 yearly runs from 120K)',n_trades=len(levs),tester_eq_dd_by_year=eqdd,tester_eq_dd_max=max(eqdd.values()),
    dd_closed_max=round(max(dds),2),lev_max=round(float(max(levs)),3),lev_p99=round(float(np.percentile(levs,99)),3),cap=1.90,sanity2023_ML5_maxlev=S['t424_sanity_2023']['maxlev'],sanity2023_ML5_eqdd=S['t424_sanity_2023']['eq_dd'],max_consec_lt_P5=consec(M),
    months=pct(M),months_first=M.index[0],months_last=M.index[-1],worst_month=M.idxmin(),excluded_partial='2026-11')
# ---------- BD: t400 b50 tester with virtual 15% floor resets (A7/B14) — INFO only ----------
b=pd.read_csv('/workspace/t400/t400_monthly.csv')
for arm,g in b.groupby('arm'):
    c=g[g.complete.astype(str)=='True']
    R[f'BD_t400_{arm}_INFO']=dict(n_all=len(g),n_complete=len(c),months=pct(c.ret_pct),worst_month=c.loc[c.ret_pct.idxmin(),'month'])
# ---------- thresholds ----------
T={}
def th(k,dd_hist,hardcap,gmax,cap,mo,tol=None):
    stop_dd=min(dd_hist,hardcap)
    if gmax<=cap: lw,ls,rule=round(gmax*1.05,3),cap,'warn=hist*1.05, stop=cap'
    else: lw,ls,rule=cap,round(min(gmax*1.05,tol if tol else 9e9),3),'hist>cap (drift): warn=cap, stop=min(hist*1.05, prereg tol)'
    return dict(dd_hist=dd_hist,dd_warn=round(0.75*dd_hist,2),dd_stop=round(stop_dd,2),
        lev_hist=gmax,lev_warn=lw,lev_stop=ls,lev_rule=rule,m_P5=mo['P5'],m_P50=mo['P50'],m_P95=mo['P95'],m_warn=mo['P5'],m_stop_single=mo['min'])
T['C1_base_MG3']=th('',14.06,25,R['C1_base_MG3']['gross_max'],3.0,R['C1_base_MG3']['months'])
T['C1_alt_A4_MG0.5']=th('',R['C1_alt_A4_MG0.5']['dd_recon_H6'],25,R['C1_alt_A4_MG0.5']['gross_max'],0.5,R['C1_alt_A4_MG0.5']['months'])
T['I2_current']=th('',R['I2_current_TV0.075_ML5_proxy']['dd_closed_max'],25,R['I2_current_TV0.075_ML5_proxy']['lev_max'],5.0,R['I2_current_TV0.075_ML5_proxy']['months'])
T['I2_candidate']=th('',R['I2_candidate_ML1.90']['tester_eq_dd_max'],25,R['I2_candidate_ML1.90']['lev_max'],1.90,R['I2_candidate_ML1.90']['months'],tol=1.989)
R['THRESHOLDS']=T
print(json.dumps(R,indent=1,default=str)); json.dump(R,open('/workspace/t425/t425_results.json','w'),indent=1,default=str)
