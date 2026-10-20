import os,re,sys,json,html,glob
sys.stdout.reconfigure(encoding='utf-8')
L={x['id']:x for x in json.load(open('mfx/list.json',encoding='utf-8'))}
res=[]
for p in glob.glob('mfx/h*.html'):
    i=os.path.basename(p)[1:-5]; x=L.get(i)
    if not x: continue
    s=open(p,encoding='utf-8').read()
    b={m.group(1):('checked' in m.group(2)) for m in re.finditer(r'<div id="(trackRecordDiv|tradingPrivilegesDiv)" class="([^"]*)"',s)}
    t=re.sub(r'<script.*?</script>|<style.*?</style>',' ',s,flags=re.S); t=re.sub(r'<[^>]+>',' ',t); t=re.sub(r'\s+',' ',html.unescape(t))
    g=lambda pat:(re.search(pat,t) or [None,''])[1]
    br=re.search(r'(Real|Demo) \((\w+)\),\s*([^,]{2,40}),\s*(1:\d+)',t)
    syms=re.findall(r'<input[^>]*type="checkbox"[^>]*>\s*([A-Z][A-Za-z0-9\.\-#_]{2,14})\s*<',s)
    sym_tbl=re.findall(r'([A-Z][A-Z0-9\.]{4,12}) (\d+) [\d\.]+% ',t)
    res.append(dict(id=i,name=x['name'],url=x['url'],gain=x['gain'],dd=x['dd'],months=x.get('months'),cagr=x.get('cagr'),ytd=x['yearly'],
      track=b.get('trackRecordDiv'),priv=b.get('tradingPrivilegesDiv'),acct=br.group(1) if br else '',broker=br.group(3) if br else '',lev=br.group(4) if br else '',
      avgwin=g(r'Average Win: (.{0,30}?) Average Loss'),avgloss=g(r'Average Loss: (.{0,30}?) Lots'),pf=g(r'Profit Factor: ([\d\.]+)'),
      worst=g(r'Worst Trade \(\$\): (\(\w+ \d+\) [\-\d,\.]+)'),best=g(r'Best Trade \(\$\): (\(\w+ \d+\) [\-\d,\.]+)'),
      bal=g(r'Balance: (\$?[\d,\.]+)'),dep=g(r'Deposits: (\S+)'),wd=g(r'Withdrawals: (\S+)'),length=g(r'Avg\. Trade Length: (.{0,12}?) Profit Factor'),
      sub=g(r'(Subscribe \$[\d,]+/m)'),longs=g(r'Longs Won: (\S+ \S+)'),shorts=g(r'Shorts Won: (\S+ \S+)'),syms=' '.join(dict.fromkeys(syms))[:80]))
json.dump(res,open('mfx/acc_parsed.json','w',encoding='utf-8'),indent=0,ensure_ascii=False)
for r in sorted(res,key=lambda r:-(r['cagr'] or 0)/max(r['dd'],1)):
    print(r['id'],r['name'][:28],'|',r['acct'],r['broker'][:16],r['lev'],'|T',r['track'],'P',r['priv'],'| G',r['gain'],'DD',r['dd'],'mo',r['months'],'cagr',r['cagr'],'ytd',r['ytd'],'| W',r['avgwin'],'L',r['avgloss'],'pf',r['pf'],'| worst',r['worst'],'best',r['best'],'| bal',r['bal'],'dep',r['dep'],'wd',r['wd'],'|',r['length'],'|',r['sub'],'|',r['syms'])
