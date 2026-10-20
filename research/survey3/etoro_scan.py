import json, os, sys, time, urllib.request, urllib.error
sys.stdout.reconfigure(encoding='utf-8')
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'et')
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120'}
def get(url,fn):
    p=os.path.join(D,fn)
    if os.path.exists(p): return json.load(open(p,encoding='utf-8'))
    for k in range(6):
        try:
            s=urllib.request.urlopen(urllib.request.Request(url,headers=UA),timeout=60).read().decode('utf-8'); break
        except urllib.error.HTTPError as e:
            if e.code!=429: raise
            time.sleep(20*(k+1))
    else: raise Exception('429 persistent')
    open(p,'w',encoding='utf-8').write(s); time.sleep(2.0); return json.loads(s)
items=[]
for pg in range(1,20):
    d=get(f'https://www.etoro.com/sapi/rankings/rankings/?Period=LastTwoYears&page={pg}&pagesize=500&popularinvestor=true&istestaccount=false&peaktovalleymin=-25','rank_%d.json'%pg)
    it=d.get('Items',[]); items+=it
    if len(it)<500: break
print('ranked',len(items),file=sys.stderr)
pre=[x for x in items if x['WeeksSinceRegistration']>=156 and x['PeakToValley']>=-20 and not x['CopyBlock'] and x['AnnualizedReturn']>=8]
pre.sort(key=lambda x:-x['AnnualizedReturn']/max(1,-x['PeakToValley']))
pre=pre[:350]
print('pre',len(pre),file=sys.stderr)
out=[]
for x in pre:
    try: h=get(f"https://www.etoro.com/sapi/userstats/gain/cid/{x['CustomerId']}/history",'h_%d.json'%x['CustomerId'])
    except Exception as e: print('ERR',x['UserName'],e,file=sys.stderr); continue
    m=[r for r in h.get('monthly',[]) if not r.get('isSimulation')]
    if len(m)<37: continue
    eq=1; pk=1; dd=0; sims=sum(1 for r in h.get('monthly',[]) if r.get('isSimulation'))
    yrs={}
    for r in m:
        eq*=1+r['gain']/100; pk=max(pk,eq); dd=min(dd,eq/pk-1); yrs.setdefault(r['start'][:4],1); yrs[r['start'][:4]]*=1+r['gain']/100
    n=len(m)/12; cagr=eq**(1/n)-1
    l36=m[-36:]; e3=1;p3=1;d3=0
    for r in l36: e3*=1+r['gain']/100;p3=max(p3,e3);d3=min(d3,e3/p3-1)
    out.append(dict(user=x['UserName'],cid=x['CustomerId'],months=len(m),sims=sims,first=m[0]['start'][:10],cagr=round(cagr*100,1),mdd_monthly=round(dd*100,1),
      cagr3=round((e3**(1/3)-1)*100,1),mdd3=round(d3*100,1),ptv2y=x['PeakToValley'],dailydd2y=x['DailyDD'],risk=x['RiskScore'],maxmrisk=x['MaxMonthlyRiskScore'],
      copiers=x['Copiers'],aum=x['AUMTierDesc'],copyblock=x['CopyBlock'],long=x['LongPosPct'],lev_high=x['HighLeveragePct'],exposure=x['Exposure'],
      topasset=x['TopTradedAssetClassId'],topinst=x['TopTradedInstrumentId'],toppct=x['TopTradedInstrumentPct'],trades=x['Trades'],win=x['WinRatio'],country=x['Country'],
      years={k:round((v-1)*100,1) for k,v in yrs.items()}))
json.dump(out,open(os.path.join(D,'scan.json'),'w'),indent=0)
print(len(out))
