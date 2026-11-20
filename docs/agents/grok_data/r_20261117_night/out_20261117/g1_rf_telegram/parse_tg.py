import re,glob,os,json
from bs4 import BeautifulSoup
res={}
for f in sorted(glob.glob('tg_html/*.html')):
    n=os.path.basename(f)[:-5]; s=open(f,encoding='utf-8',errors='replace').read()
    b=BeautifulSoup(s,'lxml')
    msgs=[]
    for m in b.select('.tgme_widget_message'):
        t=m.select_one('.tgme_widget_message_text'); d=m.select_one('time[datetime]')
        doc=m.select_one('.tgme_widget_message_document_title')
        msgs.append(dict(date=d.get('datetime') if d else None,text=t.get_text('\n') if t else '',doc=doc.get_text() if doc else None))
    title=b.select_one('.tgme_channel_info_header_title') or b.select_one('.tgme_page_title')
    cnt=b.select('.tgme_channel_info_counter')
    desc=b.select_one('.tgme_channel_info_description') or b.select_one('.tgme_page_description')
    extra=b.select_one('.tgme_page_extra')
    res[n]=dict(public_preview=bool(b.select('.tgme_channel_info')),title=title.get_text(strip=True) if title else None,
      counters=[c.get_text(' ',strip=True) for c in cnt], extra=extra.get_text(' ',strip=True) if extra else None,
      desc=desc.get_text('\n',strip=True) if desc else None, n_msgs=len(msgs), msgs=msgs)
json.dump(res,open('tg_parsed.json','w'),ensure_ascii=False,indent=1)
pub=[k for k,v in res.items() if v['public_preview']]
print('fetched',len(res),'public previews',len(pub))
for k in pub: v=res[k]; print(k,'|',v['title'],'|',v['counters'],'| msgs',v['n_msgs'],'| last',v['msgs'][-1]['date'] if v['msgs'] else None)
print('NOT public:',[(k,res[k]['extra']) for k in res if not res[k]['public_preview']])
