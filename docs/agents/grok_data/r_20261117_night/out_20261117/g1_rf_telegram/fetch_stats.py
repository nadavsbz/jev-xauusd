import json,time,urllib.request
from pathlib import Path
T253=Path('/workspace/research_new_component/results_t253')
U=json.load(open(T253/'universe_listed.json'))
OUT=Path('raw_stats')
H={"Accept":"application/json","Content-Type":"application/json","X-Requested-With":"XMLHttpRequest","Origin":"https://roboforex.com","Referer":"https://roboforex.com/copy-trading/","User-Agent":"Mozilla/5.0 (research; read-only public API)"}
keys=[k for k,v in U.items() if (v.get('registration_time') or '9')[:10]<='2025-05-17']
print(len(keys),flush=True)
n=0
for k in keys:
    tag=k.replace('/','_')
    if (T253/'raw/cards'/f'{tag}_stats.json').exists() or (OUT/f'{tag}.json').exists(): continue
    sid,login=k.split('/')
    req=urllib.request.Request("https://roboforex.com/api/copy/ratingCard/getAccountStats",data=json.dumps({"account":{"source_id":sid,"login":int(login)},"period":0}).encode(),headers=H,method="POST")
    try:
        with urllib.request.urlopen(req,timeout=30) as r: (OUT/f'{tag}.json').write_bytes(r.read())
    except Exception as e: print('ERR',k,e,flush=True)
    n+=1
    if n%100==0: print(n,flush=True)
    time.sleep(0.15)
print('done',n)
