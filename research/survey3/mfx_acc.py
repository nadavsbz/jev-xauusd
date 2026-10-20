import os,re,sys,time,json,html,urllib.request
sys.stdout.reconfigure(encoding='utf-8')
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'mfx')
f=json.load(open(os.path.join(D,'f.json')))
extra=[x for x in json.load(open(os.path.join(D,'list.json'))) if re.search(r'gold|xau|reaper|dax|nas|dow|index|us30',x['name'],re.I) and x['dd']<=30]
seen=set(); todo=[]
for x in f+extra:
    if x['id'] in seen: continue
    seen.add(x['id']); todo.append(x)
res=[]
for x in todo:
    p=os.path.join(D,'h%s.html'%x['id'])
    for k in range(3):
        if os.path.exists(p) and os.path.getsize(p)>200000: break
        try:
            req=urllib.request.Request('https://r.jina.ai/'+x['url'],headers={'X-Return-Format':'html'})
            open(p,'w',encoding='utf-8').write(urllib.request.urlopen(req,timeout=150).read().decode('utf-8','replace'))
        except Exception as e: print('ERR',x['id'],e,file=sys.stderr)
        time.sleep(8)
    if not os.path.exists(p): continue
    s=open(p,encoding='utf-8').read()
    b={m.group(1):('checked' in m.group(2)) for m in re.finditer(r'<div id="(trackRecordDiv|tradingPrivilegesDiv)" class="([^"]*)"',s)}
    t=re.sub(r'<script.*?</script>|<style.*?</style>',' ',s,flags=re.S); t=re.sub(r'<[^>]+>',' ',t); t=re.sub(r'\s+',' ',html.unescape(t))
    g=lambda pat:(re.search(pat,t) or [None,''])[1]
    acct=g(r'(Real \(\w+\)|Demo \(\w+\))[^,]*,\s*([^,]+),')
    broker=(re.search(r'(?:Real|Demo) \(\w+\),\s*([^,]+),\s*(1:\d+)',t) or [None,'',''])
    syms=re.findall(r'- \[x\] (\w[\w\.\-#]+) ',t)
    res.append(dict(x, track=b.get('trackRecordDiv'), priv=b.get('tradingPrivilegesDiv'), acct=acct, broker=broker[1] if broker[0] else '',
        avgwin=g(r'Average Win: ([^A]+?) Average Loss'), avgloss=g(r'Average Loss: (.+?) Lots'), longs=g(r'Longs Won: (\S+ \S+)'), shorts=g(r'Shorts Won: (\S+ \S+)'),
        pf=g(r'Profit Factor: ([\d\.]+)'), worst=g(r'Worst Trade \(\$\): (\(\w+ \d+\) [\-\d,\.]+)'), best=g(r'Best Trade \(\$\): (\(\w+ \d+\) [\-\d,\.]+)'),
        bal=g(r'Balance: (\$?[\d,\.]+)'), dep=g(r'Deposits: (\S+)'), wd=g(r'Withdrawals: (\S+)'), interest=g(r'Interest: (\S+)'), length=g(r'Avg\. Trade Length: (.+?) Profit Factor'),
        sub=g(r'(Subscribe \$[\d,]+/m)'), syms=' '.join(re.findall(r'\[x\]\s+([A-Z][\w\.\-#]{2,14})\s',s.replace('<',' <'))[:12])))
    print(json.dumps(res[-1],ensure_ascii=False))
json.dump(res,open(os.path.join(D,'acc.json'),'w'),indent=0,ensure_ascii=False)
