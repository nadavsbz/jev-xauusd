# same rules as pilot s1 (addendum1 §1), extended to all DEV snapshots + FINRA CNMS symbols (PREREG §3)
import json, re, glob, collections, pandas as pd
from cfg import D
pat=re.compile(r'^[A-Z]{1,5}(\.[A-Z])?$')
bad=re.compile(r'warrant|\bright|\bunit|preferred|\bnotes\b|debenture',re.I)
etfre=re.compile(r'\bETF\b|ETN|iShares|ProShares|PowerShares')
syms={}; etf=set(); src=collections.defaultdict(set); excluded_named=set()
def add(sym,name,isetf,test,tag):
    if not sym: return
    sym=sym.strip()
    if isetf=='Y': etf.add(sym); return
    if test=='Y': return
    if not pat.match(sym): return
    if bad.search(name or '') or etfre.search(name or ''): excluded_named.add(sym); return
    syms.setdefault(sym,name); src[sym].add(tag.split('_')[0])
files=sorted(glob.glob(D+'symlists/*.txt'))+sorted(glob.glob('/workspace/t318A_data/symlists/*.txt'))
for f in files:
    tag=f.split('/')[-1][:-4]
    lines=open(f,errors='ignore').read().splitlines()
    if not lines or '|' not in lines[0]: continue
    h=lines[0].split('|')
    for l in lines[1:]:
        p=l.split('|')
        if len(p)<len(h): continue
        r=dict(zip(h,p))
        if tag.startswith('nasdaqtraded'): add(r['Symbol'],r['Security Name'],r.get('ETF','N'),r['Test Issue'],tag)
        elif tag.startswith('nasdaqlisted'): add(r['Symbol'],r['Security Name'],r.get('ETF','N'),r['Test Issue'],tag)
        else: add(r['ACT Symbol'],r['Security Name'],r.get('ETF','N'),r['Test Issue'],tag)
# FINRA CNMS (no names): symbol pattern only; excluded if flagged ETF / excluded by name anywhere else
fin=set()
for f in glob.glob(D+'finra/*.txt'):
    for l in open(f,errors='ignore').read().splitlines()[1:]:
        p=l.split('|')
        if len(p)>=2 and pat.match(p[1]): fin.add(p[1])
A=json.load(open('/workspace/t318A_data/assets_all.json'))
anames={a['symbol']:a.get('name') or '' for a in A}
for s in fin:
    if s in etf or s in excluded_named: continue
    n=anames.get(s)
    if n is not None and (bad.search(n) or etfre.search(n)): continue
    syms.setdefault(s,n); src[s].add('finra')
for a in A:
    if a['exchange'] not in ('NYSE','NASDAQ','AMEX','ARCA','BATS'): continue
    s=a['symbol']
    if s in etf or s in excluded_named or not pat.match(s) or bad.search(a.get('name') or '') or etfre.search(a.get('name') or ''): continue
    if s not in syms and a['exchange']=='ARCA': continue
    syms.setdefault(s,a.get('name')); src[s].add('alpaca_'+a['status'])
syms={s:n for s,n in syms.items() if s not in etf}
df=pd.DataFrame([(s,n,';'.join(sorted(src[s]))) for s,n in syms.items()],columns=['symbol','name','sources'])
df.to_csv(D+'universe_dev.csv',index=False)
print('universe',len(df),'etf excluded',len(etf),'finra symbols',len(fin),'finra-only',int(df.sources.eq('finra').sum()),'files',len(files),flush=True)
