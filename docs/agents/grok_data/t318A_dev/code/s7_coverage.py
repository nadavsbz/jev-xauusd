# survivorship coverage report (PREREG §8ב): universe symbols not active at Alpaca today, and whether they have DEV data
import pandas as pd, json
from cfg import D, P
u=pd.read_csv(D+'universe_dev.csv',keep_default_na=False)
have=set(pd.read_parquet(D+'daily_raw.parquet',columns=['symbol']).symbol.unique())
A=json.load(open('/workspace/t318A_data/assets_all.json')); active={a['symbol'] for a in A if a['status']=='active'}
U=set(u.symbol); gone=U-active
cand=set(json.load(open(D+'cand_symbols.json')))
r=dict(universe=len(U),with_dev_data=len(U&have),not_active_today=len(gone),not_active_with_dev_data=len(gone&have),
       finra_only=int(u.sources.eq('finra').sum()),candidates_pass_filter=len(cand),candidates_not_active_today=len(cand&gone))
json.dump(r,open(P+'coverage_delisted.json','w'),indent=1); print('S7',r,flush=True)
