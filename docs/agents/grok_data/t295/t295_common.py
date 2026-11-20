#!/usr/bin/env python3
"""t294 common (Grok): report parsing + basket split, copied verbatim from t293/t292; D1/ATR, server-time helpers. stdlib only."""
import re, sys, json, csv, math, datetime, hashlib, os, bisect
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


DAY = 86400
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def load_h1(p):
    B = []
    with open(p) as f:
        for r in csv.DictReader(f):
            B.append((int(r["time"]), float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    B.sort(); out = []; last = None
    for b in B:
        if b[0] != last: out.append(b); last = b[0]
    return out
def load_d1(p, h1):
    D = {}
    with open(p) as f:
        for r in csv.DictReader(f):
            D[int(r["time"]) // DAY] = (float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]))
    lastd = max(D); agg = {}
    for t, o, h, l, c in h1:
        d = t // DAY
        if d <= lastd: continue
        if d not in agg: agg[d] = [o, h, l, c]
        else: a = agg[d]; a[1] = max(a[1], h); a[2] = min(a[2], l); a[3] = c
    for d, a in agg.items(): D[d] = tuple(a)
    days = sorted(D); tr = []; atr = []
    for i, d in enumerate(days):
        o, h, l, c = D[d]; pc = D[days[i-1]][3] if i else c
        tr.append(max(h, pc) - min(l, pc))
        atr.append(sum(tr[i-19:i+1]) / 20 if i >= 19 else None)
    return days, atr, lastd
def atr_before(days, atr, d):
    i = bisect.bisect_left(days, d) - 1
    return (i, atr[i]) if i >= 0 else (None, None)
def last_sunday(y, m):
    d = datetime.date(y, m, 31 if m in (3, 10) else 30)
    while d.weekday() != 6: d -= datetime.timedelta(days=1)
    return d
def utc_to_server(ts):
    """ts: UTC epoch -> server epoch (GMT+2, +3 during EU DST)."""
    dt = datetime.datetime.utcfromtimestamp(ts); y = dt.year
    s = datetime.datetime.combine(last_sunday(y, 3), datetime.time(1)); e = datetime.datetime.combine(last_sunday(y, 10), datetime.time(1))
    return ts + (3 if s <= dt < e else 2) * 3600
def load_fleet(p):
    F = []
    with open(p) as f:
        for r in csv.DictReader(f):
            t0 = datetime.datetime.fromisoformat(r["t0_utc"]).timestamp(); cut = r["cut"] == "True"
            age = float(r["age_h"]) if r["age_h"] else 0.0
            F.append(dict(acc=r["acc"], t0s=int(utc_to_server(t0)), t1s=int(utc_to_server(t0 + age * 3600)) if cut else None, cut=cut, pnl=float(r["pnl"])))
    return F
def load_base17(rd, years):
    allB = {}; deps = {}; shas = {}
    for y in years:
        rp = os.path.join(rd, f"ev23_rf{y}_base17.htm"); d, dep = deals(rp); Bk = baskets(pair(d), d)
        allB[y] = Bk; deps[y] = dep; shas[y] = sha(rp)
    return allB, deps, shas
