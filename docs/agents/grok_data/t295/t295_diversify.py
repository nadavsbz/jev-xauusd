#!/usr/bin/env python3
"""t295 (Grok): BD diversification screen per PREREG_t295.md. stdlib only.
usage: python t295_diversify.py <in_dir> <base17_dir> <fleet_baskets.csv> <XAUUSD_H1.csv> <out.json>"""
import sys, os, csv, json, math, statistics, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t295_common import deals, pair, baskets, utc_to_server, load_fleet, sha, DAY
IND, B17, FLEET, XAU, OUT = sys.argv[1:6]
XS = [1.0, 1.5, 2.0, 2.5, 3.0]; YS = [0.25, 0.5, 0.75, 1.0]

def load(p):
    B = {}
    with open(p) as f:
        for r in csv.DictReader(f):
            B[int(r["time"])] = (float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]), float(r.get("spread") or 0))
    return [(t,) + B[t] for t in sorted(B)]

def prev_atr(bars):
    """server-day -> ATR20 of the PREVIOUS server day (D1 aggregated from H1)."""
    D = {}
    for t, o, h, l, c, s in bars:
        d = t // DAY
        if d not in D: D[d] = [o, h, l, c]
        else: a = D[d]; a[1] = max(a[1], h); a[2] = min(a[2], l); a[3] = c
    days = sorted(D); tr = []; res = {}
    for i, d in enumerate(days):
        o, h, l, c = D[d]; pc = D[days[i-1]][3] if i else c
        tr.append(max(h, pc) - min(l, pc))
        if i + 1 < len(days) and i >= 19: res[days[i+1]] = sum(tr[i-19:i+1]) / 20
    return res, days

def crash_days(bars, atr, X, Y):
    out = set(); st = None
    for t, o, h, l, c, s in bars:
        d = t // DAY; A = atr.get(d)
        if A is None or A <= 0: continue
        if st is None: st = dict(dir=1, start=l, ext=h, hit=False); continue
        if st["dir"] == 1:
            if l <= st["ext"] - Y * A: st = dict(dir=-1, start=st["ext"], ext=l, hit=False)
            else: st["ext"] = max(st["ext"], h)
        else:
            if h >= st["ext"] + Y * A: st = dict(dir=1, start=st["ext"], ext=h, hit=False)
            else: st["ext"] = min(st["ext"], l)
        if not st["hit"] and abs(st["ext"] - st["start"]) >= X * A:
            st["hit"] = True; out.add(d)
    return out

def win(cr, d): return (d in cr) or (d - 1 in cr)

# ---------- gold cut days ----------
xau = load(XAU); xatr, xdays = prev_atr(xau); xvalid = set(xatr)
cuts = {}; cover = {}
b17sha = {}
for y in range(2016, 2026):
    p = os.path.join(B17, f"ev23_rf{y}_base17.htm"); d, dep = deals(p); Bk = baskets(pair(d), d); b17sha[y] = sha(p)
    t0 = min(r["t"] for r in d) // DAY; t1 = max(r["t"] for r in d) // DAY
    cover[f"b17_{y}"] = {x for x in xvalid if t0 <= x <= t1}
    cuts[f"b17_{y}"] = sorted({b["t1"] // DAY for b in Bk if b["net_pct"] <= -8.0} & cover[f"b17_{y}"])
F = load_fleet(FLEET)
f0 = datetime.date(2026, 4, 15); f1 = datetime.date(2026, 10, 30)
fd0 = (f0 - datetime.date(1970, 1, 1)).days; fd1 = (f1 - datetime.date(1970, 1, 1)).days
cover["fleet"] = {x for x in xvalid if fd0 <= x <= fd1}
fleet_cut_all = sorted({f["t1s"] // DAY for f in F if f["cut"]})
cuts["fleet"] = sorted(set(fleet_cut_all) & cover["fleet"])
GROUPS = {"DEV": [f"b17_{y}" for y in range(2016, 2022)], "HOLD_A": [f"b17_{y}" for y in range(2022, 2026)], "FLEET": ["fleet"]}
def gset(g, what): s = set(); [s.update(what[k]) for k in GROUPS[g]]; return s
GC = {g: gset(g, cuts) for g in GROUPS}; GV = {g: gset(g, cover) for g in GROUPS}
ALLCUT = set().union(*GC.values()); ALLCOV = set().union(*GV.values())

# ---------- calibration ----------
cal = []
for X in XS:
    for Y in YS:
        cr = crash_days(xau, xatr, X, Y); row = dict(X=X, Y=Y)
        for g in GROUPS:
            C = GC[g]; V = GV[g]
            rec = sum(win(cr, d) for d in C) / len(C) if C else None
            rate = len(cr & V) / len(V); b2 = sum(win(cr, d) for d in V) / len(V)
            row[g] = dict(n_cut=len(C), n_cov=len(V), recall=rec, daily_rate=rate, b2=b2, lift=(rec / b2 if b2 else None))
        cal.append(row)
elig = [r for r in cal if 0.03 <= r["DEV"]["daily_rate"] <= 0.15]
best = max(elig, key=lambda r: (r["DEV"]["recall"] - r["DEV"]["b2"], r["X"], r["Y"]))
X, Y = best["X"], best["Y"]
proxy_ok = all(best[g]["recall"] >= 0.5 and best[g]["lift"] >= 2 for g in ("HOLD_A", "FLEET"))
gold_cr = crash_days(xau, xatr, X, Y)

# ---------- costs ----------
E = {r["symbol"]: r for r in csv.DictReader(open(os.path.join(IND, "ecn_costs_20261030.csv")))}
FX = {s for s in E if s[:3] in ("EUR","GBP","AUD","NZD","USD","CAD","CHF","JPY") and s[3:] in ("EUR","GBP","AUD","NZD","USD","CAD","CHF","JPY")}
MET = {"XAGUSD", "XAUEUR"}; IDX = {".DE40Cash", ".US500Cash", ".US30Cash", ".USTECHCash", ".JP225Cash"}; OTH = {"BRENT", "WTI", "BTCUSD", "ETHUSD"}
def fpath(s):
    if s == "XAGUSD": return os.path.join(IND, "XAGUSD_H1.csv")
    return os.path.join(IND, s.lstrip(".") + ".csv")
costs = {}; series = {}
for s, e in E.items():
    if s == "XAUUSD": continue
    p = fpath(s)
    if not os.path.exists(p): costs[s] = dict(note="no H1 on disk"); continue
    bars = load(p); series[s] = bars
    pt = float(e["point"]); last = bars[-1][4]
    y26 = [b for b in bars if datetime.datetime.utcfromtimestamp(b[0]).year == 2026]
    spH1 = statistics.median(b[5] * pt / b[4] for b in y26) if y26 else None
    sp = float(e["med_spread_2026"]) if e["med_spread_2026"] else spH1
    com = 0.00002 if (s in FX or s in MET) else (0.00005 if (s in IDX or s in OTH) else 0.0002)
    cls = "FX" if s in FX else "metal" if s in MET else "index" if s in IDX else "energy/crypto" if s in OTH else "stock"
    swl, sws = float(e["swap_long"]), float(e["swap_short"])
    if e["swap_mode"] == "1": yl, ys = swl * pt * 365 / last * 100, sws * pt * 365 / last * 100
    else: yl, ys = swl, sws
    worst = max(0.0, -yl, -ys)
    side = sp + com
    costs[s] = dict(cls=cls, spread_pct=sp * 100, spread_src="ecn_costs" if e["med_spread_2026"] else "H1-2026", spread_h1_pct=(spH1 * 100 if spH1 is not None else None),
                    comm_pct=com * 100, side_pct=side * 100, swap_long_pct_yr=yl, swap_short_pct_yr=ys, worst_swap_charge=worst,
                    cheap=(side <= 0.0002 + 1e-12 and worst <= 5.5), cheap_strict5=(side <= 0.0002 + 1e-12 and worst <= 5.0))
cheap = sorted(s for s, c in costs.items() if c.get("cheap"))

# ---------- overlap ----------
def overlap(s):
    bars = series[s]; atr, days = prev_atr(bars); valid = set(atr)
    cr = crash_days(bars, atr, X, Y)
    C = [d for d in ALLCUT if d in valid]; V = [d for d in ALLCOV if d in valid]
    ocut = sum(win(cr, d) for d in C) / len(C) if C else None
    base = sum(win(cr, d) for d in V) / len(V) if V else None
    per = {}
    for g in GROUPS:
        Cg = [d for d in GC[g] if d in valid]
        per[g] = dict(n=len(Cg), O_cut=(sum(win(cr, d) for d in Cg) / len(Cg) if Cg else None))
    common = sorted(valid & xvalid)
    a = [d in gold_cr for d in common]; b = [d in cr for d in common]
    n = len(common); na = sum(a); nb = sum(b); nab = sum(x and y for x, y in zip(a, b))
    oprox = nab / na if na else None; brate = nb / n if n else None
    den = math.sqrt(na * (n - na) * nb * (n - nb)) if n else 0
    phi = (n * nab - na * nb) / den if den else None
    jac = nab / (na + nb - nab) if (na + nb - nab) else None
    res = dict(n_gold_cut_days=len(C), O_cut=ocut, base_win=base, lift_cut=(ocut / base if base else None), per_group=per,
               n_common_days=n, gold_proxy_days=na, inst_crash_days=nb, both=nab, O_proxy=oprox, inst_daily_rate=brate,
               lift_proxy=(oprox / brate if brate else None), phi=phi, jaccard=jac)
    if len(C) < 20: res["verdict"] = "undecidable(<20 cut days)"
    else: res["verdict"] = "PASS" if (ocut <= 0.30 and oprox is not None and oprox <= 0.30) else "FAIL"
    return res
ov = {s: overlap(s) for s in cheap}
# observation only: same metrics for non-cheap symbols with data (not part of decision)
ov_obs = {s: overlap(s) for s in sorted(series) if s not in cheap and costs[s]["cls"] != "stock"}
passing = [s for s in cheap if ov[s]["verdict"] == "PASS"]
verdict = "FAIL(<2 cheap)" if len(cheap) < 2 else ("PASS" if len(passing) >= 2 else "FAIL(<2 cheap instruments with overlap<=30%)")
rank = sorted(passing, key=lambda s: (ov[s]["lift_cut"], costs[s]["side_pct"]))
json.dump(dict(prereg_sha="see PREREG_t295.md", X=X, Y=Y, proxy_ok=proxy_ok, calibration=cal, chosen=best,
               gold_cut_days={g: len(GC[g]) for g in GROUPS}, gold_cover_days={g: len(GV[g]) for g in GROUPS},
               b17_cuts_by_year={k: len(v) for k, v in cuts.items()}, fleet_cut_days_all=len(fleet_cut_all),
               costs=costs, cheap=cheap, cheap_strict5=sorted(s for s, c in costs.items() if c.get("cheap_strict5")),
               overlap=ov, overlap_observation_noncheap=ov_obs, passing=passing, ranking=rank, verdict=verdict,
               inputs=dict(xau=sha(XAU), fleet=sha(FLEET), base17=b17sha)), open(OUT, "w"), indent=1, default=str)
print("X,Y", X, Y, "proxy_ok", proxy_ok, "verdict", verdict, "cheap", len(cheap), "passing", passing)
