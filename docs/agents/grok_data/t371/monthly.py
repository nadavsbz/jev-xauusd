import re,sys,math
for id in sys.argv[1:]:
    h=open(f'{id}.html',encoding='utf8').read()
    i=h.find('window.growthChart(');
    if i<0: print(id,'no table'); continue
    seg=h[i:h.find('],total',i)]
    ms=[]
    for y,body in re.findall(r'\{year:(\d+),yearly:[-\d.e]+,months:\{(.*?)\}\}',seg):
        for mo,v in re.findall(r'"(\d+)":(-?[\d.e]+)',body): ms.append((int(y),int(mo)+1,float(v)))
    ms.sort()
    def geo(xs): 
        p=1
        for x in xs: p*=1+x
        return (p**(1/len(xs))-1)*100 if xs else float('nan')
    v=[x[2] for x in ms]
    print(f'== {id} months={len(ms)} first={ms[0][:2]} last={ms[-1][:2]} geo_all={geo(v):.2f}%/mo  last24={geo(v[-24:]):.2f} last12={geo(v[-12:]):.2f} worst_month={min(v)*100:.2f}% best={max(v)*100:.2f}%')
    print('   ', ' '.join(f'{y%100}-{m:02d}:{x*100:.1f}' for y,m,x in ms))
    # weekly
    j=h.find('renderMiniChart('); w=re.search(r'"W1",\[(.*?)\]',h[j:j+200000])
    if w:
        a=[float(x) for x in w.group(1).split(',') if x.strip()]
        ts=a[0::2]; g=a[1::2]
        lv=[math.log(1+x/100) for x in g]
        inc=[lv[k]-lv[k-1] for k in range(1,len(lv))]
        tot=lv[-1]-lv[0]; top=sorted(inc,reverse=True)[:10]
        print(f'    weekly pts={len(g)} top10weeks share of log-growth={sum(top)/tot*100:.1f}%  worst week={min(inc)*100:.2f}%log')
