
import os
src=open('/workspace/t399/t399.py').read()
src=src.replace("ZONE='Europe/Athens'; K=0.1","ZONE='Europe/Athens'; K=0.1; SEG={}")
src=src.replace("""    d=pd.read_csv(f'/workspace/t396/in/{y}_b{v}.csv.gz',parse_dates=['ts']).reset_index(drop=True)""",
"""    d=pd.read_csv(f'/workspace/t396/in/{y}_b{v}.csv.gz',parse_dates=['ts'])
    if y in (2023,2024,2025):
        parts=[d]; SEG[y]=[(pd.Timestamp(f'{y}-01-01'),d.ts.max())]
        for suf in ['','b','c']:
            fn=f'/workspace/t400/in/{y}{suf}_b50_tail.csv'
            if os.path.exists(fn):
                t=pd.read_csv(fn,parse_dates=['ts']); parts.append(t); SEG[y].append((t.ts.min().normalize(),t.ts.max()))
        for p in parts[:-1]: p['comment']=p.comment.fillna('').str.replace('^so ','so1 ',regex=True)
        d=pd.concat(parts,ignore_index=True)
    d=d.sort_values('ts',kind='stable').reset_index(drop=True)""")
src=src.replace("import pandas as pd, numpy as np, json, sys","import pandas as pd, numpy as np, json, sys, os")
src=src.replace("    cov_end=srv[-1]; cov=(cov_end-start)/(pend-start)",
"""    cov_end=srv[-1]
    if y in SEG:
        SEG[y][-1]=(SEG[y][-1][0],min(cov_end,SEG[y][-1][1]) if t_so is not None else cov_end); covd=sum((b-a).total_seconds() for a,b in SEG[y])/86400
    else: covd=(cov_end-start).total_seconds()/86400
    cov=min(1.0,covd/((pend-start).total_seconds()/86400)); print(y,'segments',[(str(a),str(b)) for a,b in SEG.get(y,[])],'coverage',round(cov*100,1),flush=True)""")
src=src.replace("            full = (m.end_time.normalize() <= cov_end) or (t_so is None)",
"""            full = ((m.end_time.normalize() <= cov_end) or (t_so is None)) and (y not in SEG or any(a<=m.start_time and m.end_time<=b+pd.Timedelta(days=1) for a,b in SEG[y]))""")
src=src.replace("        ncov=len(mr) if t_so is None else (cov_end-start).days/30.4375","        ncov=len(mr) if (t_so is None and y not in SEG) else covd/30.4375")
src=src.replace("'t399_","'t400_")
open('/workspace/t400/t400.py','w').write(src)
