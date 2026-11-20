import json,re,glob,os,csv
from pathlib import Path
T=Path('/workspace/research_new_component/results_t253')
C={e['key']:e for e in json.load(open(T/'classified_aged.json'))}
U=json.load(open(T/'universe_listed.json'))
files={}
for f in glob.glob(str(T/'raw/cards/*_stats.json')): 
    k=os.path.basename(f).replace('_stats.json',''); files[k]=f
for f in glob.glob('raw_stats/*.json'): files[os.path.basename(f)[:-5]]=f
TG=re.compile(r'(?:https?://)?(?:t\.me|telegram\.me|telegram\.dog)/(?:s/)?([A-Za-z0-9_+\-]{3,}|joinchat/[A-Za-z0-9_\-]+)',re.I)
OTHER=re.compile(r'https?://[^\s\)\]>"]+',re.I)
AT=re.compile(r'(?<![\w.])@([A-Za-z][A-Za-z0-9_]{4,31})')
out=[]
for k,f in files.items():
    try: d=json.load(open(f)).get('data') or {}
    except Exception: continue
    desc=(d.get('strategy_desc') or '')
    blob=desc+' '+(d.get('strategy') or '')+' '+(d.get('name') or '')
    tg=sorted(set(m.group(1) for m in TG.finditer(blob)))
    mentions_tg=bool(re.search(r'telegram|телеграм|телеграмм|tg\b',blob,re.I))
    ats=sorted(set(AT.findall(desc))) if mentions_tg else []
    urls=sorted(set(u for u in OTHER.findall(desc) if 't.me' not in u))
    key=k.replace('_','/',1)
    c=C.get(key,{})
    out.append(dict(key=key,name=d.get('name'),strategy=d.get('strategy'),platform=d.get('platform'),reg=(d.get('registration_time') or '')[:10],
        age_m=round(c.get('age_months',0),1) if c else None, cls=c.get('class'), fails=';'.join(c.get('fails',[])) if c else '',
        card_dd=d.get('dd_max'), card_yield=d.get('profit_percent'), honest_mo=c.get('honest_monthly'), stricter_dd=c.get('stricter_dd'),
        subs=d.get('subscriber_count'), tg=';'.join(tg), tg_mention=mentions_tg, ats=';'.join(ats), urls=';'.join(urls[:5]), desc=desc))
json.dump(out,open('all_stats_extract.json','w'),ensure_ascii=False,indent=1)
w=[o for o in out if o['tg'] or o['ats'] or o['tg_mention']]
print('cards',len(out),'with tg link/mention',len(w), 'with t.me link',sum(1 for o in out if o['tg']))
