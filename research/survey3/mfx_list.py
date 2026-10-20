import os,re,sys,time,urllib.request
D=os.path.join(os.path.dirname(os.path.abspath(__file__)),'mfx')
def ok(p): return os.path.exists(p) and open(p,encoding='utf-8',errors='replace').read().count('Subscribe')+open(p,encoding='utf-8',errors='replace').read().count('View Details')>=3
for k in range(4):
    for pg in range(2,43):
        p=os.path.join(D,'p%d.md'%pg)
        if ok(p): continue
        try:
            s=urllib.request.urlopen('https://r.jina.ai/https://www.myfxbook.com/systems/%d'%pg,timeout=120).read().decode('utf-8','replace')
            open(p,'w',encoding='utf-8').write(s)
        except Exception as e: print('ERR',pg,e)
        time.sleep(8)
print([pg for pg in range(1,43) if not ok(os.path.join(D,'p%d.md'%pg))])
