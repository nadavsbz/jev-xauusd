#!/usr/bin/env python3
"""t292 (Grok): static test of 'start of correction' signals on BD clone baskets (base17, RF 2022-2025).
Pre-registered in PREREG_t292.md (sha256 530078cc...a7e936). Pure python, read-only.
Usage: python t292_correction_test.py OUT.json REPORTDIR BARSDIR"""
import re, sys, json, csv, math, datetime, hashlib, os, html
K = 100.0; KLEV = 5; X = 1.0; NBR = 4; M = 1.0; ATRN = 14
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
def bars(path):
    B = []
    with open(path) as f:
        for r in csv.DictReader(f):
            B.append((int(r["time"]), float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]), float(r["spread"]) * 0.01))
    B.sort(); return B
def auc(pos_, neg_):
    if not pos_ or not neg_: return None
    allv = sorted([(v, 1) for v in pos_] + [(v, 0) for v in neg_]); ranks = {}; i = 0
    r = [0.0] * len(allv)
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1][0] == allv[i][0]: j += 1
        for k in range(i, j + 1): r[k] = (i + j) / 2 + 1
        i = j + 1
    sp = sum(r[k] for k in range(len(allv)) if allv[k][1] == 1); n1 = len(pos_); n0 = len(neg_)
    return round((sp - n1 * (n1 + 1) / 2) / (n1 * n0), 3)
def fisher(a, b, c, d):
    n = a + b + c + d; r1 = a + b; c1 = a + c
    def p(x): return math.comb(r1, x) * math.comb(n - r1, c1 - x) / math.comb(n, c1)
    p0 = p(a); lo = max(0, c1 - (n - r1)); hi = min(r1, c1)
    return round(sum(p(x) for x in range(lo, hi + 1) if p(x) <= p0 * (1 + 1e-9)), 4)
def analyze_basket(b, B, times):
    import bisect
    sg = 1 if b["side"] == "buy" else -1
    pos = b["pos"]; tk = pos[KLEV - 1]["t0"]
    i0 = max(bisect.bisect_right(times, b["t0"]) - 1, 0)
    ik = bisect.bisect_left(times, tk)               # first bar with open >= t_k
    res = dict(F1=0.0, F2=0, S1=None, S2=None)
    E = None; ranges = []
    for i in range(i0, len(B)):
        t, o, h, l, c, sp = B[i]
        if t + 900 > b["t1"]: break
        E = (l if E is None else min(E, l)) if sg == 1 else (h if E is None else max(E, h))
        lo14 = B[max(0, i - ATRN + 1):i + 1]; atr = sum(x[2] - x[3] for x in lo14) / len(lo14)
        retr = (c - E) / atr if sg == 1 else (E - c) / atr
        prev = B[i - NBR:i] if i >= NBR else []
        s2 = bool(prev) and ((c > max(x[2] for x in prev)) if sg == 1 else (c < min(x[3] for x in prev)))
        s1 = retr >= X
        if i < ik:
            res["F1"] = max(res["F1"], retr); res["F2"] += int(s2)
        else:
            for nm, fired in (("S1", s1), ("S2", s2)):
                if fired and res[nm] is None:
                    res[nm] = dict(i=i, ts=t + 900, ps=c, E=E, sp=sp)
    return res
def action_a(b, sig, B, times):
    import bisect
    sg = 1 if b["side"] == "buy" else -1
    openl = [p for p in b["pos"] if p["t0"] <= sig["ts"]]
    vol = M * openl[-1]["vol"]
    entry = sig["ps"] + (sig["sp"] if sg == 1 else 0.0)      # buy at ask
    exitp = None
    for j in range(sig["i"] + 1, len(B)):
        t, o, h, l, c, sp = B[j]
        if t >= b["t1"]: break
        if sg == 1 and l <= sig["E"]: exitp = sig["E"]; break
        if sg == -1 and h + sp >= sig["E"]: exitp = sig["E"]; break
    if exitp is None:
        last = max(b["pos"], key=lambda p: p["t1"]); exitp = last["p1"]
        if sg == -1: exitp += 0.0
    pnl = sg * (exitp - entry) * vol * K
    if sg == -1: pnl -= sig["sp"] * vol * K * 0  # sell entry at bid; exit at ask approximated by SL rule / basket close price
    return pnl, vol, exitp == sig["E"]
def action_b(b, sig, B, times):
    sg = 1 if b["side"] == "buy" else -1
    for j in range(sig["i"] + 1, len(B)):
        t, o, h, l, c, sp = B[j]
        if t >= b["t1"]: break
        op = [p for p in b["pos"] if p["t0"] <= t and p["t1"] > t]
        if not op: continue
        be = sum(p["p0"] * p["vol"] for p in op) / sum(p["vol"] for p in op)
        hit = (h >= be) if sg == 1 else (l + sp <= be)
        if hit:
            realized = sum(p["net"] for p in b["pos"] if p["t1"] <= t)
            return realized - b["net"], True
    return 0.0, False
def main():
    outp, rd, bd = sys.argv[1:4]
    R = {"prereg_sha256": "530078cc8149ebc2ad1fce9866d83736a262a1e12dd1aeb697bdbf8888a7e936", "params": dict(k=KLEV, X=X, N=NBR, m=M, ATR=ATRN), "years": {}}
    for y in (2022, 2023, 2024, 2025):
        rp = os.path.join(rd, f"ev23_rf{y}_base17.htm"); bp = os.path.join(bd, f"bars_rf{y}_XAUUSD_PERIOD_M15.csv")
        sha = hashlib.sha256(open(rp, "rb").read()).hexdigest()
        d, dep = deals(rp); pos = pair(d); Bk = baskets(pos, d); B = bars(bp); times = [x[0] for x in B]
        lastbar = times[-1]
        Y = dict(report_sha256=sha, deposit=dep, n_positions=len(pos), n_baskets=len(Bk), cuts_all=sum(b["net_pct"] <= -8 for b in Bk),
                 net_all=round(sum(b["net"] for b in Bk), 2))
        pop = [b for b in Bk if b["levels"] >= KLEV and b["t1"] <= lastbar]
        Y["n_k"] = len(pop); Y["cuts_k"] = sum(b["net_pct"] <= -8 for b in pop); Y["cuts_excluded_after_bars"] = sum(b["net_pct"] <= -8 and b["t1"] > lastbar for b in Bk)
        rows = []
        for b in pop:
            r = analyze_basket(b, B, times); cut = b["net_pct"] <= -8
            row = dict(side=b["side"], t0=b["t0"], t1=b["t1"], levels=b["levels"], net=round(b["net"], 2), net_pct=round(b["net_pct"], 2), cut=cut, F1=round(r["F1"], 3), F2=r["F2"])
            for nm in ("S1", "S2"):
                s = r[nm]; row[nm + "_fired"] = s is not None
                if s:
                    pa, vol, slhit = action_a(b, s, B, times); pb, behit = action_b(b, s, B, times)
                    row.update({nm + "_ts": s["ts"], nm + "_a": round(pa, 2), nm + "_a_vol": vol, nm + "_a_sl": slhit, nm + "_b": round(pb, 2), nm + "_b_hit": behit})
            rows.append(row)
        cutv = [r for r in rows if r["cut"]]; ncut = [r for r in rows if not r["cut"]]
        Y["auc_F1"] = auc([r["F1"] for r in cutv], [r["F1"] for r in ncut]); Y["auc_F2"] = auc([r["F2"] for r in cutv], [r["F2"] for r in ncut])
        for nm in ("S1", "S2"):
            a = sum(r[nm + "_fired"] for r in cutv); c = sum(r[nm + "_fired"] for r in ncut)
            Y[nm] = dict(fired_cut=f"{a}/{len(cutv)}", fired_noncut=f"{c}/{len(ncut)}", fisher_p_biased=fisher(a, len(cutv) - a, c, len(ncut) - c))
            for act in ("a", "b"):
                k = nm + "_" + act
                tot = sum(r.get(k, 0) for r in rows); tc = sum(r.get(k, 0) for r in cutv)
                Y[nm]["d_" + act] = round(tot, 2); Y[nm]["d_" + act + "_cut"] = round(tc, 2); Y[nm]["d_" + act + "_noncut"] = round(tot - tc, 2)
                Y[nm]["d_" + act + "_pct_dep"] = round(tot / dep * 100, 2)
            al = [r[nm + "_a"] for r in rows if nm + "_a" in r]
            Y[nm]["a_worst"] = round(min(al), 2) if al else None; Y[nm]["a_worst_pct_dep"] = round(min(al) / dep * 100, 2) if al else None
            Y[nm]["a_sl_rate"] = round(sum(r.get(nm + "_a_sl", False) for r in rows) / max(1, len(al)), 3)
            Y[nm]["b_hit_cut"] = sum(r.get(nm + "_b_hit", False) for r in cutv); Y[nm]["b_hit_noncut"] = sum(r.get(nm + "_b_hit", False) for r in ncut)
        Y["cut_basket_net_k"] = round(sum(r["net"] for r in cutv), 2)
        R["years"][y] = Y
        with open(outp.replace(".json", f"_rows_{y}.csv"), "w", newline="") as f:
            ks = sorted({k for r in rows for k in r}); w = csv.DictWriter(f, ks); w.writeheader(); w.writerows(rows)
        print(y, json.dumps(Y), flush=True)
    def ok(nm, act, ys):
        c1 = all(R["years"][y][nm]["d_" + act] > 0 for y in ys)
        c2 = sum(R["years"][y][nm]["d_" + act + "_cut"] for y in ys) >= 0
        c3 = True if act == "b" else all((R["years"][y][nm]["a_worst_pct_dep"] or 0) >= -2 for y in ys)
        return dict(c1_each_year_pos=c1, c2_cut_not_worse=c2, c3_worst_lot=c3, PASS=c1 and c2 and c3)
    R["verdict"] = {f"{nm}_{act}": dict(DEV=ok(nm, act, (2022, 2023)), HOLDOUT_obs=ok(nm, act, (2024, 2025))) for nm in ("S1", "S2") for act in ("a", "b")}
    def aucok(f):
        a = [R["years"][y]["auc_" + f] for y in (2022, 2023)]
        return all(v is not None for v in a) and (all(v >= 0.6 for v in a) or all(v <= 0.4 for v in a))
    R["verdict"]["AUC_F1_separates_DEV"] = aucok("F1"); R["verdict"]["AUC_F2_separates_DEV"] = aucok("F2")
    json.dump(R, open(outp, "w"), indent=1); print(json.dumps(R["verdict"], indent=1))
main()
