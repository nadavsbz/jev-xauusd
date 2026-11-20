#!/usr/bin/env python3
"""t291: per-comment / hour / weekday / hold-time breakdown of an MT5 tester report (Bull Scalper v4.7).
Read-only. Out deals carry no position id in the report, so each out deal is matched to the open
position (same volume, opposite side) whose open price best matches the implied open price
po = close -/+ profit/(vol*CS)  (CS=1, verified on .USTECHCash). Residuals reported."""
import re,html,sys,json,collections,datetime,statistics
def num(x): return float(x.replace(" ","").replace("\u00a0","")) if x.strip() else 0.0
def rows(path):
    s=open(path,"rb").read().decode("utf-16")
    k=s.rfind("<b>Deals</b>"); s=s[k:]
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>",s,re.S):
        c=[html.unescape(re.sub("<[^>]+>","",x)).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>",row,re.S)]
        if len(c)==13 and re.match(r"\d{4}\.\d\d\.\d\d",c[0]) and c[3]!="balance": yield c
def T(s): return datetime.datetime.strptime(s,"%Y.%m.%d %H:%M:%S")
def tag(cm):
    for k in ("Burst","Chain","DCA","First","Activity"):
        if cm.startswith(k): return k
    return cm.split()[0] if cm else "?"
def analyze(path,CS=1.0):
    opn=[]; trades=[]; resid=[]; maxopen=0
    for c in rows(path):
        t=T(c[0]); side=c[3]; d=c[4]; v=num(c[5]); px=num(c[6]); pnl=num(c[8])+num(c[9])+num(c[10])
        if d=="in":
            opn.append(dict(t=t,side=side,v=v,px=px,cm=tag(c[12]),nopen=len(opn),fee=num(c[8])+num(c[9])))
            maxopen=max(maxopen,len(opn))
        elif d.startswith("out") or d=="in/out":
            want="buy" if side=="sell" else "sell"
            po = px - num(c[10])/(v*CS) if want=="buy" else px + num(c[10])/(v*CS)
            cand=[(abs(o["px"]-po),i) for i,o in enumerate(opn) if o["side"]==want and abs(o["v"]-v)<1e-9]
            if not cand: cand=[(abs(o["px"]-po),i) for i,o in enumerate(opn) if o["side"]==want]
            if not cand: continue
            r,i=min(cand); o=opn.pop(i); resid.append(r)
            reason=c[12].split()[0] if c[12] else ""
            trades.append(dict(cm=o["cm"],ot=o["t"],ct=t,v=v,pnl=pnl+o["fee"],nopen=o["nopen"],reason=reason))
    return trades,resid,maxopen
def agg(trades,key):
    g=collections.defaultdict(lambda:[0,0.0,0,0.0,0.0])
    for x in trades:
        a=g[key(x)]; a[0]+=1; a[1]+=x["pnl"]
        if x["pnl"]>0: a[2]+=1; a[3]+=x["pnl"]
        else: a[4]+=x["pnl"]
    out={}
    for k,(n,p,w,gp,gl) in sorted(g.items(),key=lambda z:str(z[0])):
        out[str(k)]=dict(n=n,net=round(p,2),win_pct=round(100*w/n,1),gross_win=round(gp,2),gross_loss=round(gl,2),pf=(round(gp/-gl,2) if gl<0 else None))
    return out
def holdb(x):
    h=(x["ct"]-x["ot"]).total_seconds()/60
    for lim,lab in ((5,"<5m"),(30,"5-30m"),(120,"30m-2h"),(480,"2-8h"),(1440,"8-24h"),(4320,"1-3d")):
        if h<lim: return lab
    return ">3d"
def nopenb(x):
    n=x["nopen"]
    for lim,lab in ((5,"0-4"),(20,"5-19"),(50,"20-49"),(100,"50-99"),(200,"100-199")):
        if n<lim: return lab
    return "200+"
if __name__=="__main__":
    path,label=sys.argv[1],sys.argv[2]
    tr,res,mx=analyze(path)
    WD=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    o=dict(label=label,report=path.split("/")[-1],closed_trades=len(tr),net_closed=round(sum(x["pnl"] for x in tr),2),max_open_positions=mx,
      match_residual_points=dict(median=round(statistics.median(res),3),p95=round(sorted(res)[int(.95*len(res))-1],3),max=round(max(res),3),share_gt_1pt=round(sum(r>1 for r in res)/len(res),4)),
      by_comment=agg(tr,lambda x:x["cm"]),
      by_entry_hour_server=agg(tr,lambda x:f'{x["ot"].hour:02d}'),
      by_entry_weekday=agg(tr,lambda x:WD[x["ot"].weekday()]),
      by_hold=agg(tr,holdb),
      by_close_reason=agg(tr,lambda x:x["reason"]),
      by_open_positions_at_entry=agg(tr,nopenb),
      by_comment_x_openpos=agg(tr,lambda x:x["cm"]+"|"+nopenb(x)),
      by_close_day=agg(tr,lambda x:x["ct"].strftime("%Y.%m.%d")),
      by_comment_x_closeday=agg(tr,lambda x:x["cm"]+"|"+x["ct"].strftime("%Y.%m.%d")),
      lots_by_comment={k:sorted(set(x["v"] for x in tr if x["cm"]==k))[:10] for k in set(x["cm"] for x in tr)})
    print(json.dumps(o,ensure_ascii=False))
