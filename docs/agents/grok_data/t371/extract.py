import re,html,sys
for id in sys.argv[1:]:
    h=open(f'{id}.html',encoding='utf8').read()
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',h,flags=re.S)
    t=html.unescape(re.sub(r'<[^>]+>','\n',t))
    t='\n'.join(l.strip() for l in t.split('\n') if l.strip())
    open(f'{id}.txt','w').write(t)
    a=t.find('Growth:'); b=t.find('Distribution'); c=t.find('To see trades in realtime',b); d=t.find('Signal\nPrice\nGrowth',c)
    print('=====',id); print(t[a:a+900].replace('\n',' | ')); print(t[t.find('Trades:',a+900):b+700].replace('\n',' | '))
    print('DESC:',t[c:d][:2500].replace('\n',' | ') if c>0 else '')
