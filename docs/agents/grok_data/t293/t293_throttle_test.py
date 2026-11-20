#!/usr/bin/env python3
"""t293 (Grok): static test of the post-cut throttle (PREREG_t293.md sha256 2e1ae1ff...c676).
Read-only. Usage: python t293_throttle_test.py REPORTDIR FLEET_BASKETS_CSV OUT.json"""
import re, sys, json, csv, math, datetime, hashlib, os
K = 100.0
def num(x):
    x = x.replace(" ", "").replace("\u00a0", "").replace(",", "")
    try: return float(x)
    except: return float("nan")
def epoch(s): return int((datetime.datetime.strptime(s, "%Y.%m.%d %H:%M:%S") - datetime.datetime(1970, 1, 1)).total_seconds())
def deals(path):
    t = open(path, "rb").read().decode("utf-16")
    out = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
        c = [re.sub("<.*?>", "", x).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
        if len(c) == 13 and re.match(r"\d{4}\.\d\d\.\d\d", c[0]) and c[3] != "balance":
            out.append(dict(t=epoch(c[0]), type=c[3], dir=c[4], vol=num(c[5]), price=num(c[6]), com=num(c[8]), swap=num(c[9]), profit=num(c[10]), bal=num(c[11])))
    dep = None
    m = re.search(r"<td[^>]*>\s*[\d\s]+\s*</td><td[^>]*>\s*</td><td[^>]*>\s*balance", t)
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
        c = [re.sub("<.*?>", "", x).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
        if len(c) == 13 and c[3] == "balance": dep = num(c[11]); break
    return out, dep
def pair(d):
    op = []; pos = []
    for r in d:
        if r["dir"] == "in":
            op.append(dict(side=r["type"], vol=r["vol"], t0=r["t"], p0=r["price"], cost=r["com"]))
        else:
            side = "buy" if r["type"] == "sell" else "sell"; s = 1 if side == "buy" else -1
            imp = r["price"] - s * r["profit"] / (K * r["vol"]) if r["vol"] else r["price"]
            cand = [i for i, p in enumerate(op) if p["side"] == side and abs(p["vol"] - r["vol"]) < 1e-9]
            if not cand: continue
            i = min(cand, key=lambda j: abs(op[j]["p0"] - imp)); p = op.pop(i)
            pos.append(dict(side=side, vol=p["vol"], t0=p["t0"], p0=p["p0"], t1=r["t"], p1=r["price"], net=r["profit"] + r["com"] + r["swap"] + p["cost"]))
    return pos
def baskets(pos, d):
    bal = sorted((r["t"], r["bal"]) for r in d if r["dir"] != "in")
    res = []
    for side in ("buy", "sell"):
        s = sorted([p for p in pos if p["side"] == side], key=lambda p: p["t0"]); grp = []; end = -1
        for p in s:
            if grp and p["t0"] > end: res.append(grp); grp = []
            grp.append(p); end = max(end, p["t1"]) if len(grp) > 1 else p["t1"]
        if grp: res.append(grp)
    out = []
    import bisect
    bt = [b[0] for b in bal]
    for g in res:
        t0 = min(p["t0"] for p in g); t1 = max(p["t1"] for p in g)
        i = bisect.bisect_left(bt, t0) - 1; b0 = bal[i][1] if i >= 0 else bal[0][1]
        net = sum(p["net"] for p in g)
        out.append(dict(side=g[0]["side"], t0=t0, t1=t1, pos=sorted(g, key=lambda p: p["t0"]), levels=len(g), net=net, net_pct=net / b0 * 100, b0=b0))
    return out

DAY=86400
def apply(Bk, trig, N, m, same_side):
    """trig: list of (t1, side). returns multipliers per basket (by index)."""
    out=[]
    for b in Bk:
        mm=1.0
        for (tc, sd) in trig:
            if tc < b["t0"] <= tc + N*DAY and (not same_side or sd == b["side"]):
                mm=m; break
        out.append(mm)
    return out
def maxdd(Bk, mult, dep):
    eq=dep; pk=dep; dd=0.0
    for b, mm in sorted(zip(Bk, mult), key=lambda x: x[0]["t1"]):
        eq += mm*b["net"]; pk=max(pk, eq); dd=max(dd, (pk-eq)/pk*100)
    return dd
def main():
    rd, fleetcsv, outp = sys.argv[1:4]
    R={"prereg_sha256":"2e1ae1ff144ca8017af1f57c3747458e3aca26188ad3f298993832ba4db5c676","years":{},"grid":{},"fleet":{}}
    allB={}; deps={}
    for y in range(2016, 2026):
        rp=os.path.join(rd, f"ev23_rf{y}_base17.htm")
        d, dep = deals(rp); pos=pair(d); Bk=baskets(pos, d)
        allB[y]=Bk; deps[y]=dep
        R["years"][y]=dict(report_sha256=hashlib.sha256(open(rp,"rb").read()).hexdigest(), deposit=dep, n_baskets=len(Bk),
                           net=round(sum(b["net"] for b in Bk),2), cuts=sum(b["net_pct"]<=-8 for b in Bk))
        print(y, R["years"][y], flush=True)
    trig=sorted((b["t1"], b["side"]) for y in allB for b in allB[y] if b["net_pct"] <= -8)
    rows=[]
    def run(N, m, ss, tag, keep_rows=False):
        res={}
        for y in allB:
            Bk=allB[y]; dep=deps[y]; mult=apply(Bk, trig, N, m, ss)
            d=sum((mm-1)*b["net"] for b,mm in zip(Bk,mult)); dc=sum((mm-1)*b["net"] for b,mm in zip(Bk,mult) if b["net_pct"]<=-8)
            ntr=sum(1 for (tc,sd) in trig if Bk and min(b["t0"] for b in Bk) <= tc <= max(b["t1"] for b in Bk))
            inw=[b for b,mm in zip(Bk,mult) if mm!=1]; outw=[b for b,mm in zip(Bk,mult) if mm==1]
            res[y]=dict(triggers=ntr, n_scaled=len(inw), delta=round(d,2), delta_pct=round(d/dep*100,2), delta_cut=round(dc,2), delta_noncut=round(d-dc,2),
                        dd_base=round(maxdd(Bk,[1]*len(Bk),dep),2), dd_rule=round(maxdd(Bk,mult,dep),2),
                        mean_pct_in=round(sum(b["net_pct"] for b in inw)/len(inw),3) if inw else None,
                        mean_pct_out=round(sum(b["net_pct"] for b in outw)/len(outw),3) if outw else None,
                        cutrate_in=f'{sum(b["net_pct"]<=-8 for b in inw)}/{len(inw)}', cutrate_out=f'{sum(b["net_pct"]<=-8 for b in outw)}/{len(outw)}')
            if keep_rows:
                for b,mm in zip(Bk,mult):
                    rows.append(dict(variant=tag, year=y, side=b["side"], t0=b["t0"], t1=b["t1"], levels=b["levels"], net=round(b["net"],2), net_pct=round(b["net_pct"],3), mult=mm))
        return res
    def verdict(res, ys):
        ty=[y for y in ys if res[y]["triggers"]>0]
        c1=sum(res[y]["delta"] for y in ys) > 0
        c2=(sum(res[y]["delta"]>=0 for y in ty) >= 0.6*len(ty)) if ty else False
        c3=all(res[y]["dd_rule"] <= res[y]["dd_base"]+1 for y in ys) and (sum(res[y]["dd_rule"] for y in ys) < sum(res[y]["dd_base"] for y in ys))
        ntrig=sum(res[y]["triggers"] for y in ys)
        return dict(c1_sum_delta_pos=c1, c2_60pct_years=c2, c3_dd=c3, triggers=ntrig, sum_delta=round(sum(res[y]["delta"] for y in ys),2),
                    sum_delta_cut=round(sum(res[y]["delta_cut"] for y in ys),2), sum_delta_noncut=round(sum(res[y]["delta_noncut"] for y in ys),2),
                    PASS=c1 and c2 and c3 and (ntrig>=6 or ys[0]>=2022))
    DEV=list(range(2016,2022)); HO=list(range(2022,2026))
    for tag,(N,m,ss) in {"V1":(10,0.5,False),"V2":(10,0.5,True)}.items():
        res=run(N,m,ss,tag,True); R[tag]=dict(per_year=res, DEV=verdict(res,DEV), HOLDOUT_A=verdict(res,HO))
        print(tag, json.dumps(R[tag]["DEV"]), json.dumps(R[tag]["HOLDOUT_A"]), flush=True)
    for N in (3,5,10,20,30):
        for m in (0.0,0.25,0.5):
            for ss in (False,True):
                res=run(N,m,ss,"g"); k=f"N{N}_m{m}_{'same' if ss else 'all'}"
                R["grid"][k]=dict(DEV=verdict(res,DEV)["sum_delta"], HO=verdict(res,HO)["sum_delta"],
                                  DEV_cut=verdict(res,DEV)["sum_delta_cut"], HO_cut=verdict(res,HO)["sum_delta_cut"])
    # fleet
    F=[]
    with open(fleetcsv) as f:
        for r in csv.DictReader(f):
            t0=datetime.datetime.fromisoformat(r["t0_utc"]).timestamp()
            cut=r["cut"]=="True"; F.append(dict(acc=r["acc"], t0=t0, cut=cut, pnl=float(r["pnl"]), tc=t0+float(r["age_h"])*3600 if cut else None))
    accs=sorted({x["acc"] for x in F}); anon={a:f"A{i+1}" for i,a in enumerate(accs)}
    def fleet(N, m, mode):
        cuts=[x for x in F if x["cut"]]; d=0.0; dc=0.0; n=0; hits=0
        for x in F:
            for c in cuts:
                if c is x: continue
                own = c["acc"]==x["acc"]
                if (mode=="own" and own) or (mode=="other" and not own):
                    if c["tc"] < x["t0"] <= c["tc"]+N*DAY:
                        d+=(m-1)*x["pnl"]; n+=1
                        if x["cut"]: dc+=(m-1)*x["pnl"]; hits+=1
                        break
        return dict(n_scaled=n, cuts_in_window=hits, delta=round(d,2), delta_cut=round(dc,2), delta_noncut=round(d-dc,2))
    base=sum(x["pnl"] for x in F)
    R["fleet"]=dict(n_baskets=len(F), n_accounts=len(accs), n_cuts=sum(x["cut"] for x in F), base_pnl=round(base,2), cut_pnl=round(sum(x["pnl"] for x in F if x["cut"]),2),
                    V1_own=fleet(10,0.5,"own"), V3_other=fleet(2,0.5,"other"),
                    grid={f"{mode}_N{N}_m{m}":fleet(N,m,mode) for mode in ("own","other") for N in (1,2,5,10,20) for m in (0.0,0.5)})
    v1=R["fleet"]["V1_own"]; v3=R["fleet"]["V3_other"]
    R["fleet"]["V1_PASS"]=v1["delta"]>0 and v1["delta_cut"]>0
    R["fleet"]["V3_PASS"]=v3["delta"]>0 and v3["cuts_in_window"]>=2
    # per-account cut timeline (anonymised): gaps between consecutive cuts in same account (days)
    gaps=[]
    for a in accs:
        cs=sorted(x["tc"] for x in F if x["cut"] and x["acc"]==a)
        gaps += [round((cs[i+1]-cs[i])/DAY,2) for i in range(len(cs)-1)]
    R["fleet"]["own_cut_gaps_days"]=sorted(gaps)
    print("FLEET", json.dumps({k:v for k,v in R["fleet"].items() if k!="grid"}), flush=True)
    json.dump(R, open(outp,"w"), indent=1)
    with open(outp.replace(".json","_rows.csv"),"w",newline="") as f:
        w=csv.DictWriter(f, list(rows[0].keys())); w.writeheader(); w.writerows(rows)
main()
