import re, sys, os, time, json, html, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'mql')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
def page(i):
    p=os.path.join(D,'sig',i+'.html')
    if not os.path.exists(p):
        s=urllib.request.urlopen(urllib.request.Request('https://www.mql5.com/en/signals/'+i,headers=UA),timeout=40).read().decode('utf-8','replace')
        open(p,'w',encoding='utf-8').write(s); time.sleep(4.0)
    s=open(p,encoding='utf-8').read()
    t=re.sub(r'<script.*?</script>|<style.*?</style>',' ',s,flags=re.S); t=re.sub(r'<[^>]+>',' ',t); return re.sub(r'\s+',' ',html.unescape(t))
def g(t,pat):
    m=re.search(pat,t); return m.group(1).strip() if m else ''
out=[]
for i in sys.argv[1:]:
    try: t=page(i)
    except Exception as e: print("ERR",i,e,file=sys.stderr); time.sleep(30); continue
    dist=g(t,r'Distribution Symbol Deals Sell Buy (.*?) \d+ \d+ \d+ ')
    pairs=re.findall(r'([A-Z][A-Za-z0-9\.\-_#!]{2,15}) (\d[\d ]*?)(?= [A-Z]|$)',dist)
    r=dict(id=i,name=g(t,r'^(.*?) - ') ,growth=g(t,r'Growth: ([\-\d \.,]+%)'),init=g(t,r'Initial Deposit: ([\d \.,]+ \w+)'),wd=g(t,r'Withdrawals: ([\d \.,]+ \w+)'),dep=g(t,r'Deposits: ([\d \.,]+ \w+)'),
      equity=g(t,r'Equity: ([\d \.,\-]+ \w+)'),started=g(t,r'Started: ([\d\.]+)'),weeks=g(t,r'Weeks: (\d+)'),trades=g(t,r'Trades: ([\d ]+) Profit'),win=g(t,r'Profit Trades: [\d ]+ \(([\d\.]+%)'),
      load=g(t,r'Max deposit load: ([\d\.]+%)'),hold=g(t,r'Avg holding time: (.*?) (?:Subscribers|Recovery|Weeks)'),ddb=g(t,r'By Balance: ([\d\.]+%)'),dde=g(t,r'By Equity: ([\d\.]+%)'),
      avgp=g(t,r'Average Profit: ([\d \.,]+ \w+)'),avgl=g(t,r'Average Loss: ([\-\d \.,]+ \w+)'),worst=g(t,r'Worst trade: ([\-\d \.,]+ \w+)'),best=g(t,r'Best trade: ([\d \.,]+ \w+)'),
      latest=g(t,r'Latest trade: (.*?) Trades per week'),algo=g(t,r'Algo trading: (\d+%)'),pf=g(t,r'Profit Factor: ([\d\.]+)'),maxcl=g(t,r'Maximal consecutive loss: ([\-\d \.,]+ \w+)'),
      lev=g(t,r'growth since \d{4} [\d ]+% (.*?) How to subscribe'),since=g(t,r'growth since (\d{4})'),swap=('No swaps are charged' in t),author=g(t,r'Watch the video tutorials about trading signals on YouTube (.*?) \d'),
      syms=dist[:300])
    out.append(r); print(json.dumps(r,ensure_ascii=False))
json.dump(out,open(os.path.join(D,'sig_%d.json'%int(time.time())),'w'),indent=1)
