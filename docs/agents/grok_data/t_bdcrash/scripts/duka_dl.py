# Sequential polite downloader for Dukascopy public datafeed (no account). Usage: duka_dl.py outdir url_list_file
import sys, os, time, urllib.request
out=sys.argv[1]; urls=[l.split() for l in open(sys.argv[2]) if l.strip()]
for url,fn in urls:
    p=os.path.join(out,fn)
    if os.path.exists(p) and os.path.getsize(p)!=109: continue
    os.makedirs(os.path.dirname(p),exist_ok=True)
    for a in range(8):
        try:
            r=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60)
            d=r.read(); open(p,'wb').write(d); break
        except urllib.error.HTTPError as e:
            if e.code==404: open(p,'wb').write(b''); break
            time.sleep(20*(a+1))
        except Exception as e: time.sleep(20*(a+1))
    time.sleep(2.0)
print('done',flush=True)
