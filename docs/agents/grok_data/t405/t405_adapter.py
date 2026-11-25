#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""t405_adapter.py (Grok, 26.11.2026) - converts Claude's t405_tester upload into the layout the FROZEN t405_gate.py expects.
Gate logic is NOT touched. The adapter only renames/reshapes inputs and supplies three disclosed inputs that the upload lacked:
  (1) deals_<SYM>[_<NY|LDN>]_<YYYY|2020_2026>.csv  <- t405_i2_<SYM>_<ny|ldn>_<YYYY>.csv / t405_c1_<SYM>.csv  (byte-identical copy, rename only)
  (2) equity_<SYM>_daily.csv for C1 runs (PREREG s9 asked Claude for it; not uploaded) RECONSTRUCTED mark-to-market from the deals
      + RF ECN H1 bars in data/derived/intraday (<SYM>_H1.csv, end 2026-10-30 12:00 server). Hedging account: exact per-side cost basis from MT5 profit
      identity (see reconstruct()); vpp US500/USTECH 1.0, XAUUSD 100.0, DE40 = EURUSD daily (Yahoo EURUSD=X). EOD equity = balance + unrealized at last H1 close of day;
      equity_min = min over the day of balance + unrealized at the adverse H1 extreme (low for long, high for short) and at deal prices.
      Gap 2026-10-30 .. 2026-11-20: Yahoo daily (^GSPC/^NDX/^GDAXI/GC=F) scaled to the RF close on 2026-10-29; after Yahoo coverage,
      mark at that day's deal prices or carry. Accrued (unrealized) swap is NOT included (realized at close). [ASSUMED approximation]
  (3) summary.json: per-run 'quality_by_year' added for C1 runs (run-level quality only was uploaded):
      US500/USTECH run-level 100% -> 100 each year [ASSUMED]; DE40 run-level 95% -> per-year from t404_tester/summary.json same
      symbol/server (2020 0%, 2021 99%, 2022-26 100%) [VERIFIED source]; XAUUSD run-level 14% -> NOT supplied (unknown per year).
  (4) spec_t405.json with ONLY 'server_dst_check' (no cost fields): result of Grok's mechanical DST check (no P&L used) on RF ECN
      H1 bars, see dst_check() - mode STRICT omits it.
Usage: python3 t405_adapter.py --raw RAW --bars BARS --yf YFDIR --t404 t404_summary.json --out OUT [--strict]
"""
import argparse, csv, json, os, re, shutil, glob, hashlib, datetime as dt
from collections import defaultdict

BARS = {'US500': '.US500Cash_H1.csv', 'USTECH': '.USTECHCash_H1.csv', 'DE40': '.DE40Cash_H1.csv', 'XAUUSD': 'XAUUSD_H1.csv'}
YF = {'US500': 'yf_%5EGSPC.json', 'USTECH': 'yf_%5ENDX.json', 'DE40': 'yf_%5EGDAXI.json', 'XAUUSD': 'yf_GC%3DF.json'}

def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()

def load_bars(p):
    out = []
    for r in csv.DictReader(open(p)):
        t = dt.datetime(1970, 1, 1) + dt.timedelta(seconds=int(r['time']))
        out.append((t, float(r['open']), float(r['high']), float(r['low']), float(r['close'])))
    return out

def load_yf(p):
    j = json.load(open(p))['chart']['result'][0]; q = j['indicators']['quote'][0]; out = {}
    for t, h, l, c in zip(j['timestamp'], q['high'], q['low'], q['close']):
        if c is not None: out[(dt.datetime(1970, 1, 1) + dt.timedelta(seconds=t)).date()] = (h, l, c)
    return out

def load_deals(p):
    rows = []
    for r in csv.DictReader(open(p, encoding='utf-8-sig')):
        rows.append(dict(t=dt.datetime.strptime(r['ts'], '%Y-%m-%d %H:%M:%S'), dir=r['dir'], type=r['type'], price=float(r['price']),
                         vol=float(r['volume']), profit=float(r['profit']), bal=float(r['balance'])))
    rows.sort(key=lambda x: x['t']); return rows

def reconstruct(deals, bars, yf, dep=120000.0, vpp_fn=None):
    """Exact cost-basis tracking per side (hedging account), no lot matching needed: MT5 profit = (close-open)*lots*vpp, so the
    removed cost basis of a closing deal is q = price - side*profit/(lots*vpp). Volumes per side are exact from the deal list.
    vpp_fn(date): USD-quoted symbols -> constant (US500/USTECH 1.0, XAUUSD 100.0 = median of observed ratios);
    DE40 (EUR) -> EURUSD daily close (Yahoo EURUSD=X) [ASSUMED proxy for the tester conversion rate].
    Unrealized = ((px*VL - CL) + (CS - px*VS)) * vpp."""
    VL = CL = VS = CS = 0.0; bal = dep
    def unreal(px, d):
        return ((px * VL - CL) + (CS - px * VS)) * vpp_fn(d)
    def worst(lo, hi, d): return min(unreal(lo, d), unreal(hi, d))
    eod, emin = {}, {}
    def note(d, eq_close=None, eq_low=None):
        if eq_low is not None: emin[d] = min(emin.get(d, eq_low), eq_low)
        if eq_close is not None: eod[d] = eq_close
    def apply(r):
        nonlocal bal, VL, CL, VS, CS
        v, px, d = r['vol'], r['price'], r['t'].date()
        if r['dir'] == 'in':
            if r['type'] == 'buy': VL += v; CL += px * v
            else: VS += v; CS += px * v
        else:
            if r['type'] == 'sell':      # closes long
                q = px - r['profit'] / (v * vpp_fn(d)); VL -= v; CL -= q * v
                if VL < 1e-6: VL = CL = 0.0
            else:                        # closes short
                q = px + r['profit'] / (v * vpp_fn(d)); VS -= v; CS -= q * v
                if VS < 1e-6: VS = CS = 0.0
        bal = r['bal']
        note(d, eq_low=bal + unreal(px, d))
    i = 0; n = len(deals)
    for (t, o, h, l, c) in bars:
        if t.date() < deals[0]['t'].date(): continue
        if t > deals[-1]['t']: break
        while i < n and deals[i]['t'] <= t: apply(deals[i]); i += 1
        note(t.date(), eq_low=bal + worst(l, h, t.date()))
        while i < n and deals[i]['t'] < t + dt.timedelta(hours=1): apply(deals[i]); i += 1
        note(t.date(), eq_close=bal + unreal(c, t.date()), eq_low=bal + unreal(c, t.date()))
    last_bar_t = bars[-1][0]
    ref_d = dt.date(2026, 10, 29)
    rf_ref = [b[4] for b in bars if b[0].date() == ref_d][-1]
    scale = rf_ref / yf[ref_d][2] if ref_d in yf else 1.0
    d = last_bar_t.date(); endd = deals[-1]['t'].date(); last_mark = bars[-1][4]; gap_days = []
    while d <= endd:
        day_deals = []
        while i < n and deals[i]['t'].date() <= d: day_deals.append(deals[i]); apply(deals[i]); i += 1
        if d in yf:
            hh, ll, cc = [x * scale for x in yf[d]]
            note(d, eq_low=bal + worst(ll, hh, d)); last_mark = cc
            note(d, eq_close=bal + unreal(cc, d)); gap_days.append((str(d), 'yahoo'))
        elif day_deals:
            last_mark = day_deals[-1]['price']; note(d, eq_close=bal + unreal(last_mark, d)); gap_days.append((str(d), 'deal-price'))
        elif d.weekday() < 5:
            note(d, eq_close=bal + unreal(last_mark, d)); gap_days.append((str(d), 'carry'))
        d += dt.timedelta(days=1)
    rows = [(d, round(eod[d], 2), round(min(emin.get(d, eod[d]), eod[d]), 2)) for d in sorted(eod)]
    return rows, dict(scale_yahoo=round(scale, 6), gap_days=gap_days, final_balance=bal,
                      open_volume_end=dict(long=round(VL, 4), short=round(VS, 4), cost_long=round(CL, 2), cost_short=round(CS, 2)))

def make_vpp(sym, yfdir):
    if sym in ('US500', 'USTECH'): return lambda d: 1.0
    if sym == 'XAUUSD': return lambda d: 100.0
    fx = load_yf(os.path.join(yfdir, 'yf_EURUSD%3DX.json')); ks = sorted(fx)
    import bisect
    def f(d):
        j = bisect.bisect_right(ks, d) - 1
        return fx[ks[max(j, 0)]][2]
    return f

def maxdd(vals, dep=120000.0):
    peak = dep; m = 0.0
    for v in vals: peak = max(peak, v); m = max(m, (peak - v) / peak * 100)
    return round(m, 2)

def dst_check(bars_dir):
    """EU-vs-US DST of the server from RF ECN H1 bars (range only, no P&L): Xetra open 09:00 CET must stay at the same server
    hour in US/EU mismatch weeks if the server follows EU DST; NY open moves one server hour earlier in those weeks."""
    def sun(y, m, k):
        ds = [dt.date(y, m, x) for x in range(1, 32) if _ok(y, m, x) and dt.date(y, m, x).weekday() == 6]
        return ds[-1] if k == 'last' else ds[k - 1]
    def _ok(y, m, x):
        try: dt.date(y, m, x); return True
        except ValueError: return False
    def mism(d):
        y = d.year
        return sun(y, 3, 2) <= d < sun(y, 3, 'last') or sun(y, 10, 'last') <= d < sun(y, 11, 1)
    res = {}
    for sym, f in (('DE40', BARS['DE40']), ('US500', BARS['US500'])):
        agg = {True: defaultdict(list), False: defaultdict(list)}
        for (t, o, h, l, c) in load_bars(os.path.join(bars_dir, f)):
            if 2020 <= t.year <= 2026: agg[mism(t.date())][t.hour].append(h - l)
        out = {}
        for k in (False, True):
            a = {hh: sum(v) / len(v) for hh, v in agg[k].items()}
            j = max((a[hh] / a[hh - 1], hh) for hh in a if hh - 1 in a and a[hh - 1] > 0 and 8 <= hh <= 17)
            out['mismatch' if k else 'normal'] = dict(max_jump_hour=j[1], ratio=round(j[0], 3), mean_range={hh: round(a[hh], 2) for hh in range(8, 18) if hh in a})
        res[sym] = out
    de_same = res['DE40']['normal']['max_jump_hour'] == res['DE40']['mismatch']['max_jump_hour'] == 10
    us_shift = res['US500']['mismatch']['mean_range'][15] / res['US500']['normal']['mean_range'][15] > res['US500']['mismatch']['mean_range'][16] / res['US500']['normal']['mean_range'][16]
    verdict = 'EU DST (GMT+2/+3) - Grok mechanical check on RF ECN H1 bars' if de_same and us_shift else 'UNCLEAR'
    return verdict, res

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--raw'); ap.add_argument('--bars'); ap.add_argument('--yf'); ap.add_argument('--t404'); ap.add_argument('--out')
    ap.add_argument('--strict', action='store_true', help='rename only: no equity, no quality_by_year, no DST spec')
    ap.add_argument('--xau-quality-all-100', action='store_true', help='DIAGNOSTIC ONLY (non-binding): pretend XAU years are 100%%')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    log = dict(mode='STRICT' if a.strict else 'ADAPTED', inputs={}, renames=[], equity={}, quality_added={}, dst=None)
    for p in sorted(glob.glob(os.path.join(a.raw, '*'))): log['inputs'][os.path.basename(p)] = sha(p)
    for p in sorted(glob.glob(os.path.join(a.raw, 't405_*.csv'))):
        b = os.path.basename(p)[:-4]
        m = re.match(r't405_i2_([A-Z]+)_(ny|ldn)_(\d{4})$', b) or re.match(r't405_c1_([A-Z0-9]+)$', b)
        if not m: continue
        new = f'deals_{m.group(1)}_{m.group(2).upper()}_{m.group(3)}.csv' if len(m.groups()) == 3 else f'deals_{m.group(1)}_2020_2026.csv'
        shutil.copyfile(p, os.path.join(a.out, new)); log['renames'].append((os.path.basename(p), new))
    summ = json.load(open(os.path.join(a.raw, 'summary.json'), encoding='utf-8'))
    if not a.strict:
        t404 = json.load(open(a.t404, encoding='utf-8'))
        de = {int(k[-4:]): v['quality'] for k, v in t404.items() if k.startswith('t404_DE40_')}
        qmap = {'t405_c1_US500': {y: '100%' for y in range(2020, 2027)}, 't405_c1_USTECH': {y: '100%' for y in range(2020, 2027)},
                't405_c1_DE40': {y: re.search(r'(\d+)%', de[y]).group(0) for y in range(2020, 2027)}}
        if a.xau_quality_all_100: qmap['t405_c1_XAUUSD'] = {y: '100% (DIAGNOSTIC ASSUMPTION)' for y in range(2020, 2027)}
        for rn, q in qmap.items():
            summ['runs'][rn]['quality_by_year'] = {str(y): v for y, v in q.items()}; log['quality_added'][rn] = q
        for sym in ('US500', 'USTECH', 'DE40', 'XAUUSD'):
            deals = load_deals(os.path.join(a.raw, f't405_c1_{sym}.csv'))
            rows, info = reconstruct(deals, load_bars(os.path.join(a.bars, BARS[sym])), load_yf(os.path.join(a.yf, YF[sym])), vpp_fn=make_vpp(sym, a.yf))
            with open(os.path.join(a.out, f'equity_{sym}_daily.csv'), 'w', newline='') as f:
                w = csv.writer(f); w.writerow(['date', 'equity', 'equity_min']); w.writerows(rows)
            info.update(days=len(rows), dd_eod_pct=maxdd([r[1] for r in rows]), dd_intraday_pct=maxdd([r[2] for r in rows]),
                        tester_report_eq_dd=summ['runs'][f't405_c1_{sym}']['eq_dd'], final_equity=rows[-1][1],
                        tester_net=summ['runs'][f't405_c1_{sym}']['net'], bars_file=BARS[sym])
            info['gap_days'] = {'n': len(info['gap_days']), 'sources': sorted(set(s for _, s in info['gap_days']))}
            log['equity'][sym] = info
        v, raw = dst_check(a.bars)
        log['dst'] = dict(verdict=v, detail=raw)
        json.dump({'server_dst_check': v, 'dst_check_detail': raw, 'note': 'adapter-made; no cost fields (spec_t405.json not uploaded by Claude)'},
                  open(os.path.join(a.out, 'spec_t405.json'), 'w'), indent=1)
    json.dump(summ, open(os.path.join(a.out, 'summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(log, open(os.path.join(a.out, '..', f'adapter_log_{log["mode"]}{"_XAUDIAG" if a.xau_quality_all_100 else ""}.json'), 'w'), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: log[k] for k in ('mode', 'equity', 'dst')}, default=str, indent=1)[:6000])
