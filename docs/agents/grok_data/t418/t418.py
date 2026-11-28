#!/usr/bin/env python3
"""t418 STRESS - implements PREREG_t418.md (sha256 1758fc09...31b6). K=0 risk test."""
import pandas as pd, numpy as np, hashlib, json, sys
W='/workspace/t418/'; KL='/workspace/t417_kL/'
FILES={'AV0.15':'t417_av15_tv20_deals.csv.gz','AV0.075':'c1_ecn_av075_full_deals.csv.gz'}
TESTER_DD={'AV0.15':18.6,'AV0.075':14.06}
SYM={'BTCUSD':'BTCUSDT','ETHUSD':'ETHUSDT'}
DEP=120000.0; CAP=0.25; H={'H6':1,'H24':4,'H48':8}
SHIFT_H=0  # chosen by min median |deal price / Binance close -1| over shifts -6..+6h (0 and +3 tie; 0 used)

# ---- prices ----
px={}
for s,f in SYM.items():
    b=pd.read_csv(KL+f+'_6h.csv',parse_dates=['time'])
    b['ct']=b.time.dt.tz_localize(None)+pd.Timedelta(hours=6)   # bar close time UTC
    b=b[(b.time>='2018-06-01')&(b.time<'2026-11-01')]
    px[s]=b.set_index('ct').close
P=pd.DataFrame(px).dropna()
# scenario set: all joint overlapping windows of h bars in Binance 2018-06..2026-10
SC={}
for k,h in H.items():
    r=(P.shift(-h)/P-1).dropna()
    SC[k]=(r.index.values, r['BTCUSD'].values, r['ETHUSD'].values)

def book_replay(d, cs, mode):
    """position-level book per symbol & side; returns list of (implied cs per out deal)"""
    books={s:{1:[],-1:[]} for s in SYM}; imp=[]
    for row in d.itertuples():
        sg=1 if row.type=='buy' else -1
        bk=books[row.symbol]
        if row.dir=='in':
            bk[sg].append([row.volume,row.price])
        else:
            side=-sg; v=row.volume; num=0.0
            L=bk[side]
            while v>1e-9 and L:
                i=0 if mode=='FIFO' else -1
                q=min(v,L[i][0]); num+=q*(row.price-L[i][1])*side
                L[i][0]-=q; v-=q
                if L[i][0]<=1e-9: L.pop(i)
            if abs(num)>1e-9 and row.profit!=0: imp.append((row.symbol,row.profit/num))
    return imp

def run(av):
    d=pd.read_csv(W+FILES[av],parse_dates=['ts'])
    d['ta']=(d.ts+pd.Timedelta(hours=SHIFT_H)).dt.floor('6h')  # aligned to H6 close grid
    d['sv']=np.where(d.type=='buy',1,-1)*np.where(d.dir=='in',1,1)*d.volume  # signed lots flow
    # ---- contract size inference ----
    csinfo={}
    best=None
    for mode in ['FIFO','LIFO']:
        imp=pd.DataFrame(book_replay(d,None,mode),columns=['s','c'])
        med=imp.groupby('s').c.median(); mad=imp.groupby('s').c.apply(lambda x:(x-x.median()).abs().median())
        csinfo[mode]={s:(float(med[s]),float(mad[s]),int((imp.s==s).sum())) for s in med.index}
        if best is None or mad.sum()<best[1]: best=(mode,mad.sum())
    mode=best[0]
    cs={s:csinfo[mode][s][0] for s in SYM}
    # matching-independent aggregate check: total profit / total -(signed vol*price) when flat
    agg={}
    for s in SYM:
        x=d[d.symbol==s]; flow=(x.sv*x.price).sum(); agg[s]=float(x.profit.sum()/(-flow)) if flow else np.nan
    # round cs to a clean value if close
    csr={s:(round(cs[s]) if abs(cs[s]-round(cs[s]))<0.02*max(1,abs(cs[s])) else cs[s]) for s in SYM}
    # ---- replay book to H6 grid ----
    grid=P.index[(P.index>='2020-01-01')&(P.index<='2026-10-31 18:00')]
    books={s:{1:[],-1:[]} for s in SYM}
    rows=[]; di=0; D=d.reset_index(drop=True); n=len(D); bal=DEP
    flat_checks=[]
    for T in grid:
        while di<n and D.ta[di]<=T:
            r=D.loc[di]; sg=1 if r.type=='buy' else -1; bk=books[r.symbol]
            if r.dir=='in': bk[sg].append([r.volume,r.price])
            else:
                side=-sg; v=r.volume; L=bk[side]
                while v>1e-9 and L:
                    i=0 if mode=='FIFO' else -1
                    q=min(v,L[i][0]); L[i][0]-=q; v-=q
                    if L[i][0]<=1e-9: L.pop(i)
            bal=r.balance; di+=1
        net={}; fl=0.0; gross_lots=0
        for s in SYM:
            p=P.loc[T,s]; nl=0.0
            for side in (1,-1):
                for v,e in books[s][side]:
                    nl+=side*v; fl+=side*v*csr[s]*(p-e)
            net[s]=nl
        E=bal+fl
        Ns={s:net[s]*csr[s]*P.loc[T,s] for s in SYM}
        rows.append(dict(T=T,bal=bal,float=fl,E=E,lotsB=net['BTCUSD'],lotsE=net['ETHUSD'],NB=Ns['BTCUSD'],NE=Ns['ETHUSD'],
                         gross=(abs(Ns['BTCUSD'])+abs(Ns['ETHUSD']))/E))
    R=pd.DataFrame(rows).set_index('T')
    final_open={s:(sum(v for v,_ in books[s][1]),sum(v for v,_ in books[s][-1])) for s in SYM}
    # ---- scenario losses ----
    for k,(wt,rb,re_) in SC.items():
        NB=R.NB.values; NE=R.NE.values; L=np.empty(len(R)); arg=np.empty(len(R),int)
        for a in range(0,len(R),500):
            pnl=NB[a:a+500,None]*rb[None,:]+NE[a:a+500,None]*re_[None,:]
            j=pnl.argmin(1); L[a:a+500]=-pnl[np.arange(len(j)),j]; arg[a:a+500]=j
        R['L_'+k]=L/R.E.values; R['W_'+k]=pd.to_datetime(wt[arg])
    # ---- sanity: equity vs balance at flat moments; deal-time flat check ----
    flatmask=(R.lotsB.abs()<1e-9)&(R.lotsE.abs()<1e-9)
    # maxDD
    eq=R.E; dd=(1-eq/eq.cummax()).max()*100; ddT=(1-eq/eq.cummax()).idxmax()
    return dict(d=d,R=R,cs=csr,csraw=cs,csinfo=csinfo,mode=mode,agg=agg,final_open=final_open,
                flat_n=int(flatmask.sum()),flat_maxdiff=float((R.E-R.bal)[flatmask].abs().max()) if flatmask.any() else None,
                dd=dd,ddT=ddT,final_bal=float(d.balance.iloc[-1]),final_E=float(R.E.iloc[-1]))

def wfmt(T,h):  # scenario window: start close time -> end close time
    T=pd.Timestamp(T); return f"{T:%Y-%m-%d %H:%M}->{T+pd.Timedelta(hours=6*h):%Y-%m-%d %H:%M}"

out=[]; summ={}
out.append('# RESULTS t418-STRESS (PREREG_t418.md sha256 1758fc099cc6ab4a29d930482e68578cd996f574dcb5ffb8ac2f89619a8231b6)\n')
out.append(f'Generated by t418.py. Times UTC (Binance H6 close times). Deal timestamp shift applied: {SHIFT_H:+d}h then floor to 6h '
           '(ASSUMED: tester server-time grid already coincides with Binance 00/06/12/18 UTC closes; shift chosen by min median |deal price/Binance close-1| '
           'among -6,-3,0,+3,+6h; 0 and +3 tie because deals sit on exact hours; 0 used). Deals at 23:59:56 / :01-:02 floored into the same 6h bucket.\n')
out.append('Scenario set: all overlapping joint (rBTC,rETH) windows from Binance closes 2018-06..2026-10; H6=1 bar, H24=4, H48=8; no rebalancing inside window. '
           'Evaluation grid: every H6 close 2020-01-01 00:00 .. 2026-10-31 18:00 UTC. E = tester balance column (last deal <= T) + floating MtM at Binance close vs position entry prices.\n')
for av in FILES:
    r=run(av); R=r['R']
    g={}
    out.append(f'\n## {av}  ({FILES[av]})\n')
    out.append('| metric | value | timestamp (UTC) | worst scenario window |\n|---|---|---|---|')
    i=R.gross.idxmax(); out.append(f"| max gross (sum|N|/E) | {R.gross.max():.3f} | {i:%Y-%m-%d %H:%M} | - |")
    for k,h in H.items():
        c='L_'+k; i=R[c].idxmax()
        out.append(f"| max L_{k} | {R[c].max()*100:.2f}% | {i:%Y-%m-%d %H:%M} | {wfmt(R.loc[i,'W_'+k],h)} |")
        out.append(f"| % bars L_{k} > 25% | {(R[c]>CAP).mean()*100:.3f}% ({int((R[c]>CAP).sum())} of {len(R)}) | - | - |")
        g[k]=float(R[c].max())
    out.append('\nPer-year max:\n\n| year | max gross | max L_H6 | max L_H24 | max L_H48 |\n|---|---|---|---|---|')
    for y,x in R.groupby(R.index.year):
        out.append(f"| {y} | {x.gross.max():.3f} | {x.L_H6.max()*100:.2f}% | {x.L_H24.max()*100:.2f}% | {x.L_H48.max()*100:.2f}% |")
    G1=g['H6']<=CAP; G2=g['H24']<=CAP
    out.append(f"\n**Gates:** G1 (max L_H6 <= 25%): **{'PASS' if G1 else 'FAIL'}** ({g['H6']*100:.2f}%); "
               f"G2 (max L_H24 <= 25%): **{'PASS' if G2 else 'FAIL'}** ({g['H24']*100:.2f}%); H48 info: {g['H48']*100:.2f}%. "
               f"Stress-OK for 25% cap (G1 AND G2): **{'YES' if G1 and G2 else 'NO'}**.\n")
    out.append('Sanity checks:\n')
    out.append(f"- Contract size inferred (median profit/(vol x dPrice vs matched entry), matching={r['mode']} chosen by lower MAD): "
               + ', '.join(f"{s}: median {v[0]:.4f} (MAD {v[1]:.4f}, n={v[2]})" for s,v in r['csinfo'][r['mode']].items())
               + f"; other matching: " + ', '.join(f"{s}: {v[0]:.4f} (MAD {v[1]:.4f})" for s,v in r['csinfo'][[m for m in r['csinfo'] if m!=r['mode']][0]].items())
               + f". Matching-independent aggregate (sum profit / -sum signed vol*price): " + ', '.join(f"{s}: {v:.4f}" for s,v in r['agg'].items())
               + f". Used cs = {r['cs']}.")
    fo=r['final_open']; flat=all(a<1e-9 and b<1e-9 for a,b in fo.values())
    out.append(f"- Reconstructed final position: {'FLAT' if flat else 'NOT FLAT'} (open long/short lots per symbol: {fo}).")
    out.append(f"- Equity vs balance at flat H6 moments: {r['flat_n']} flat bars, max |E-balance| = {r['flat_maxdiff']} (by construction 0 when no open positions). "
               f"Final reconstructed E {r['final_E']:.2f} vs final balance column {r['final_bal']:.2f}.")
    out.append(f"- maxDD of reconstructed H6 equity (Binance MtM): {r['dd']:.2f}% (trough {r['ddT']:%Y-%m-%d %H:%M}) vs tester-reported {TESTER_DD[av]}%. "
               f"Info: maxDD of the tester balance column itself = {(1-r['d'].balance/r['d'].balance.cummax()).max()*100:.2f}%. "
               f"Gap vs tester is attributed to Binance-vs-tester price basis and H6-close-only sampling (ASSUMED, not verified).")
    summ[av]=dict(G1=G1,G2=G2,maxL=g,maxgross=float(R.gross.max()),dd=r['dd'],cs=r['cs'],flat=flat)
    R.to_csv(W+f'bars_t418_{av}.csv.gz')
out.append('\nDeviations from PREREG: none in method/gates. Implementation choices (not in PREREG): timestamp shift 0h (see header); '
           'position matching for cs/floating chosen between FIFO/LIFO by lower dispersion of implied cs; cs rounded to nearest integer when within 2%.\n')
open(W+'RESULTS_t418.md','w').write('\n'.join(out))
print('\n'.join(out)); print(json.dumps(summ,default=str))
