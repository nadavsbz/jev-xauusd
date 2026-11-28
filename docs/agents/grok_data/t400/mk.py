
import re
src=open('/workspace/t399/t399.py').read()
# load: concat original + tail for 2023-2025; original so renamed so horizon = tail so
src=src.replace("""    d=pd.read_csv(f'/workspace/t396/in/{y}_b{v}.csv.gz',parse_dates=['ts']).reset_index(drop=True)""",
"""    d=pd.read_csv(f'/workspace/t396/in/{y}_b{v}.csv.gz',parse_dates=['ts'])
    if y in (2023,2024,2025):
        d['comment']=d.comment.fillna('').str.replace('^so ','so1 ',regex=True)
        global SEG; SEG[y]=[(pd.Timestamp(f'{y}-01-01'),d.ts.max())]
        t=pd.read_csv(f'/workspace/t400/in/{y}_b50_tail.csv',parse_dates=['ts'])
        SEG[y].append((t.ts.min().normalize(),None)); d=pd.concat([d,t],ignore_index=True)
    d=d.sort_values('ts',kind='stable').reset_index(drop=True)""")
src=src.replace("ZONE='Europe/Athens'; K=0.1","ZONE='Europe/Athens'; K=0.1; SEG={}")
src=src.replace("    cov_end=srv[-1]; cov=(cov_end-start)/(pend-start)",
"""    cov_end=srv[-1]
    if y in SEG:
        SEG[y][1]=(SEG[y][1][0],cov_end); covd=sum((b-a).total_seconds() for a,b in SEG[y])/86400
    else: covd=(cov_end-start).total_seconds()/86400
    cov=covd/((pend-start).total_seconds()/86400); print(y,'segments',SEG.get(y),'coverage',round(cov*100,1),flush=True)""")
src=src.replace("            full = (m.end_time.normalize() <= cov_end) or (t_so is None)",
"""            full = ((m.end_time.normalize() <= cov_end) or (t_so is None)) and (y not in SEG or any(a<=m.start_time and m.end_time<=b+pd.Timedelta(days=1) for a,b in SEG[y]))""")
src=src.replace("        ncov=len(mr) if t_so is None else (cov_end-start).days/30.4375","        ncov=len(mr) if t_so is None else covd/30.4375")
src=src.replace("'t399_","'t400_")
open('/workspace/t400/t400.py','w').write(src)
