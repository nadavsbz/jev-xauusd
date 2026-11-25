import pandas as pd, numpy as np, json, sys, os
sys.path.insert(0,'/workspace/t396')
ZONE='Europe/Athens'; K=0.1; SEG={}
P=pd.read_pickle('/workspace/t396/P.pkl')
def toU(t): return pd.DatetimeIndex(pd.to_datetime(t)).tz_localize(ZONE,ambiguous='NaT',nonexistent='shift_forward').tz_convert('UTC').tz_localize(None)
def toS(t): return pd.DatetimeIndex(t).tz_localize('UTC').tz_convert(ZONE).tz_localize(None)
def load(y,v):
    d=pd.read_csv(f'/workspace/t396/in/{y}_b{v}.csv.gz',parse_dates=['ts'])
    if y in (2023,2024,2025):
        parts=[d]; SEG[y]=[(pd.Timestamp(f'{y}-01-01'),d.ts.max())]
        for suf in ['','b','c']:
            fn=f'/workspace/t400/in/{y}{suf}_b50_tail.csv'
            if os.path.exists(fn):
                t=pd.read_csv(fn,parse_dates=['ts']); parts.append(t); SEG[y].append((t.ts.min().normalize(),t.ts.max()))
        for p in parts[:-1]: p['comment']=p.comment.fillna('').str.replace('^so ','so1 ',regex=True)
        d=pd.concat(parts,ignore_index=True)
    d=d.sort_values('ts',kind='stable').reset_index(drop=True)
    d['side']=np.where(((d.dir=='in')&(d.type=='buy'))|((d.dir!='in')&(d.type=='sell')),'buy','sell')
    d['q']=np.where(d.side=='buy',1,-1)*np.where(d.dir=='in',1,-1)*d.vol_per_100k
    d['ep']=''
    for side in ['buy','sell']:
        vol=0.0; ep=0; cur=None
        for i in d.index[d.side==side]:
            q=d.at[i,'vol_per_100k']
            if d.at[i,'dir']=='in':
                if vol<1e-9: ep+=1; cur=f'{side}{ep}'
                vol+=q
            else: vol-=q
            d.at[i,'ep']=cur
            if vol<1e-9: vol=0.0
    d['ep_first']=d.ep.map(d[d.dir=='in'].groupby('ep').ts.min())
    d['tu']=toU(d.ts)
    return d
def basis(d,bars):
    m=d[d.dir=='in'].copy(); m['bar']=m.tu.dt.floor('min')
    j=m.join(bars[['bc','ac']],on='bar').dropna()
    r=np.where(j.type=='sell',j.price-j.bc,j.price-j.ac)
    return float(np.median(r))
def curve3(w,bars,B,s=1.0):
    n=len(bars); bt=bars.index.values
    bi=np.searchsorted(bt,w.tu.values.astype('datetime64[ns]'),side='right')-1
    pos=np.clip(bi+1,0,n)
    def acc(vals,mask=None):
        a=np.zeros(n+1)
        if mask is None: np.add.at(a,pos,vals)
        else: np.add.at(a,pos[mask],vals[mask])
        return np.cumsum(a)[:n]
    isb=(w.side=='buy').values; q=w.q.values*s; qp=(w.q*w.price).values*s
    Qb=acc(q,isb); QPb=acc(qp,isb); Qs=acc(q,~isb); QPs=acc(qp,~isb); Cc=acc((w.swap_pct+w.commission_pct).values*s)
    f=lambda b,a:K*(Qb*(b+B)-QPb)+K*(Qs*(a+B)-QPs)+Cc
    return f(bars.bl.values,bars.al.values), f(bars.bh.values,bars.ah.values), f(bars.bc.values,bars.ac.values)

def sim(d,bars,srv,start,B,days,live=True):
    n=len(bars); per=((srv-start)/pd.Timedelta(days=days)).astype(int).values
    pers=np.unique(per)
    ptime={p:start+pd.Timedelta(days=days*int(p)) for p in pers}
    # cohort of each basket by reset period of its first entry
    d=d.copy(); d['coh']=((d.ep_first-start)/pd.Timedelta(days=days)).astype(int)
    A1=np.zeros(n);A2=np.zeros(n);AC=np.zeros(n)
    base=100.0; HW=100.0; eqc=np.full(n,np.nan); eql=np.full(n,np.nan)
    cuts=[]; resets=[]; flat_until=-1
    for p in pers:
        idx=np.where(per==p)[0]; i0=idx[0]
        Er=100.0 if i0==0 else eqc[i0-1]
        if p<=flat_until:
            eqc[idx]=base; eql[idx]=base; continue
        if p==flat_until+1 and flat_until>=0:
            A1[:]=0;A2[:]=0;AC[:]=0; Er=base; HW=base
        s=Er/100.0 if live else 1.0
        sub=d[d.coh==p]
        mx=float(sub.vol_per_100k.max()*1.2*s) if len(sub) else 0.0
        capd=int((sub.vol_per_100k>=4.1666).sum()) if len(sub) else 0
        if len(sub):
            e1,e2,ec=curve3(sub,bars,B,s); A1+=e1;A2+=e2;AC+=ec
        Lw=base+np.minimum(A1[idx],A2[idx]); Cw=base+AC[idx]
        hwa=np.maximum(HW,np.maximum.accumulate(Cw)); fla=0.85*np.r_[HW,hwa[:-1]]; fl=float(fla[0]); h=np.where(Lw<=fla)[0]
        resets.append(dict(period=int(p),t_reset=ptime[p],E_reset=Er,scale=s,lot=round(0.20*s,4),max_scaled_deal_lot=round(mx,3),flag_over_maxlot=mx>5.0001,deals_at_cap_orig=capd,n_baskets=int(sub.ep.nunique())))
        if len(h):
            j=h[0]; fl=float(fla[j]); eqc[idx[:j]]=Cw[:j]; eql[idx[:j]]=Lw[:j]; eqc[idx[j:]]=fl; eql[idx[j:]]=fl
            cuts.append(dict(period=int(p),t_cut=srv[idx[j]],E_reset=round(Er,2),floor=round(fl,2),bar_low=round(float(Lw[j]),2)))
            base=fl; flat_until=p; resets[-1]['cut']=True
        else:
            eqc[idx]=Cw; eql[idx]=Lw; HW=float(hwa[-1])
    return eqc,eql,cuts,resets

out=[];monthly=[];allcuts=[];allres=[];chk=[]
for y in [2022,2023,2024,2025,2026]:
    start=pd.Timestamp(f'{y}-01-01'); pend=pd.Timestamp(f'{y+1}-01-01') if y<2026 else pd.Timestamp('2026-11-01')
    d=load(y,50); so=d[d.comment.fillna('').str.startswith('so ')]
    t_so=so.ts.min() if len(so) else None
    tend=(t_so+pd.Timedelta(minutes=3)) if t_so is not None else pend
    bars=P.loc[toU([start])[0]:toU([tend])[0]-pd.Timedelta(seconds=1)]
    srv=toS(bars.index); B=basis(d,bars)
    cov_end=srv[-1]
    if y in SEG:
        SEG[y][-1]=(SEG[y][-1][0],min(cov_end,SEG[y][-1][1]) if t_so is not None else cov_end); covd=sum((b-a).total_seconds() for a,b in SEG[y])/86400
    else: covd=(cov_end-start).total_seconds()/86400
    cov=min(1.0,covd/((pend-start).total_seconds()/86400)); print(y,'segments',[(str(a),str(b)) for a,b in SEG.get(y,[])],'coverage',round(cov*100,1),flush=True)
    # sanity: fixed lot 7d must reproduce t396
    e,_,c,_=sim(d,bars,srv,start,B,7,live=False); chk.append(dict(year=y,fixed_cut_net=round(e[-1]-100,2),fixed_cuts=len(c)))
    for days,arm in [(7,'T7')]:
        eqc,eql,cuts,res=sim(d,bars,srv,start,B,days,True)
        for c in cuts: c.update(year=y,arm=arm)
        for r in res: r.update(year=y,arm=arm)
        allcuts+=cuts; allres+=res
        pk=np.maximum.accumulate(eqc); dd=np.nanmax((pk-eql)/pk*100)
        ser=pd.Series(eqc,index=srv); me=ser.groupby(ser.index.to_period('M')).last()
        prev=100.0; mr=[]
        for m,v in me.items():
            full = ((m.end_time.normalize() <= cov_end) or (t_so is None)) and (y not in SEG or any(a<=m.start_time and m.end_time<=b+pd.Timedelta(days=1) for a,b in SEG[y]))
            r=(v/prev-1)*100; mr.append(r)
            monthly.append(dict(year=y,arm=arm,month=str(m),end_E=round(v,2),ret_pct=round(r,2),complete=bool(full)))
            prev=v
        ncov=len(mr) if (t_so is None and y not in SEG) else covd/30.4375
        net=eqc[-1]-100
        geo=((eqc[-1]/100)**(1/ncov)-1)*100
        out.append(dict(year=y,arm=arm,horizon=str(cov_end),coverage_pct=round(cov*100,1),months_cov=round(ncov,2),net_pct=round(net,2),
          avg_month_arith=round(float(np.mean(mr)),2),geo_month=round(geo,2),cuts=len(cuts),minE=round(float(np.nanmin(eql)),2),maxDD=round(float(dd),2),
          months_pos=int(sum(x>0 for x in mr)),months_n=len(mr),worst_month=round(min(mr),2),best_month=round(max(mr),2),
          periods_over_maxlot=int(sum(r['flag_over_maxlot'] for r in res)),max_scale=round(max(r['scale'] for r in res),3),min_scale=round(min(r['scale'] for r in res),3)))
        print(out[-1],flush=True)
R=pd.DataFrame(out); R.to_csv('t403_years.csv',index=False)
pd.DataFrame(monthly).to_csv('t403_monthly.csv',index=False)
pd.DataFrame(allcuts).to_csv('t403_cuts.csv',index=False)
pd.DataFrame(allres).to_csv('t403_resets.csv',index=False)
C=pd.DataFrame(chk); print(C); C.to_csv('t403_sanity_fixedlot.csv',index=False)
ch=[]
for arm in ['A7','B14']:
    E=100.0
    for _,r in R[R.arm==arm].iterrows():
        E*=1+r.net_pct/100; ch.append(dict(arm=arm,year=r.year,E_end=round(E,2)))
pd.DataFrame(ch).to_csv('t403_chained.csv',index=False); print(pd.DataFrame(ch))
