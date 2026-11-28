import pandas as pd, numpy as np, sys
EVT={'A3_20260416':'21.4','A3_20260421':'23.4','A4_20260416':'23.4','A4_20260424':'30.4','A5_20260415':'30.4','A6_20260415':'30.4','A4_20260524':'5.6','A6_20260430':'1.5'}
def kap(L,T):
    L=np.array(L,bool);T=np.array(T,bool); return L,T
res={}
for M in ['primary','t389','rfask']:
    X=pd.read_csv(f'out/t390_windows_{M}.csv')
    for v in ['b','b50']:
        rows=[]
        for _,r in X.iterrows():
            cov=r[f'{v}_coverage']; hasF=pd.notna(r.G_FloorPct); cut=pd.notna(r.live_cut)
            tc=r.get(f'{v}_acct_cross'); tc=tc if isinstance(tc,str) and tc not in ('','nan','None') else None
            rows.append(dict(seg=r.seg_id,evt=EVT.get(r.seg_id,''),floor=hasF,cut=cut,cv=cov,tcross=tc,
                match=(r[f'{v}_acct_match'] if cov=='deal' or cov=='report' else np.nan),basket=r.get(f'{v}_basket')))
        R=pd.DataFrame(rows); res[(M,v)]=R
        def stat(S):
            S=S[S.floor&S.cv.isin(['deal','report'])]
            L=S.cut.values; T=S.tcross.notna().values
            agree=S.match.astype(bool).values; po=agree.mean(); pl=L.mean(); pt=T.mean(); pe=pl*pt+(1-pl)*(1-pt)
            k=(po-pe)/(1-pe) if pe<1 else np.nan
            return dict(n=len(S),agree=round(po,3),kappa=round(k,3),live_only=int((L&~T).sum()),tester_only=int((T&~L).sum()),
                        cut_match=int((S.cut&S.match.astype(bool)).sum()),n_cut=int(S.cut.sum()),uncut_tester_cross=int((~S.cut&T).sum()),
                        same_similar=int(S.basket.isin(['SAME','SIMILAR']).sum()))
        a=stat(R); b=stat(R[R.evt!='30.4'])
        print(M,v,'ALL',a,'| no30.4',b)
        if M=='primary': print(R.to_string())
pd.to_pickle(res,'out/summ.pkl')
