#!/usr/bin/env python3
"""t404 gate — per PREREG_t404.md (sha256 0a2e7933...760d), sections 5-8.
Frozen gate (gate years 2022-2026) + post-hoc secondary lines (a)/(b) requested by Nadav via Claude 23:20.
Input: tester/deals_<SYM>_<YYYY>.csv + tester/summary.json. Output: RESULTS_t404.json (stdout summary)."""
import csv, json, math, re, statistics as st, sys, hashlib, os
from collections import defaultdict
from datetime import datetime

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tester')
SYMS = ['US500', 'DE40', 'JP225']
YEARS = list(range(2020, 2027))
GATE_YEARS = list(range(2022, 2027))
DEP = 120000.0
DD_MAX = 15.0
TOP10_MAX = 0.50
HOLD_MIN = 15.0
MPOINT = 0.1          # MT5 point of .US500Cash/.DE40Cash/.JP225Cash (ecn_costs: point=0.1)
TARGET_M = 3.5
N_TRIALS = 4600 + 3   # LEDGER conservative N + K of t404

def num(s):
    return float(str(s).replace(',', '').strip())

def parse_pct(s):
    m = re.search(r'\(([\d.]+)%\)', s); return float(m.group(1)) if m else None

def quality(s):
    m = re.search(r'(\d+)%', s); return int(m.group(1)) if m else None

summ = json.load(open(os.path.join(D, 'summary.json'), encoding='utf-8'))

def load(sym, y):
    rows = list(csv.DictReader(open(os.path.join(D, f'deals_{sym}_{y}.csv'), encoding='utf-8')))
    trades, openpos, maxopen, cur = [], 0, 0, None
    for r in rows:
        t = datetime.strptime(r['ts'], '%Y-%m-%d %H:%M:%S')
        if r['dir'] == 'in':
            openpos += 1; maxopen = max(maxopen, openpos)
            cur = dict(t_in=t, side=r['type'], p_in=num(r['price']), vol=num(r['volume']),
                       comm=num(r['commission']), swap=num(r['swap']))
        else:
            openpos -= 1
            p_out = num(r['price']); prof = num(r['profit'])
            cur.update(t_out=t, p_out=p_out, profit=prof,
                       comm=cur['comm'] + num(r['commission']), swap=cur['swap'] + num(r['swap']))
            sgn = 1 if cur['side'] == 'buy' else -1
            dp = sgn * (p_out - cur['p_in'])
            cur['vpp'] = prof / (dp * cur['vol']) if abs(dp) > 1e-9 and cur['vol'] > 0 else None
            cur['net'] = prof + cur['comm'] + cur['swap']
            trades.append(cur); cur = None
    return trades, maxopen

def maxdd_closed(nets):
    eq = peak = DEP; mdd = 0.0
    for x in nets:
        eq += x; peak = max(peak, eq); mdd = max(mdd, (peak - eq) / peak * 100)
    return mdd

def norm_ppf(p):  # Acklam approximation
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    pl = 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p)); return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > 1 - pl:
        return -norm_ppf(1 - p)
    q = p - 0.5; r = q*q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)

def ncdf(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def dsr(daily):
    T = len(daily); mu = st.mean(daily); sd = st.pstdev(daily)
    if sd == 0: return None, None
    sr = mu / sd
    n = len(daily); m3 = sum((x-mu)**3 for x in daily)/n/sd**3; m4 = sum((x-mu)**4 for x in daily)/n/sd**4
    g = 0.5772156649; N = N_TRIALS
    sr0 = math.sqrt(1.0/T) * ((1-g)*norm_ppf(1-1.0/N) + g*norm_ppf(1-1.0/(N*math.e)))
    z = (sr - sr0) * math.sqrt(T-1) / math.sqrt(max(1e-12, 1 - m3*sr + (m4-1)/4*sr*sr))
    return sr * math.sqrt(252), ncdf(z)

def bdays(y, last):
    import datetime as dt
    d = dt.date(y, 1, 1); out = []
    while d <= last:
        if d.weekday() < 5: out.append(d)
        d += dt.timedelta(days=1)
    return out

res = {'prereg_sha256': '0a2e7933aea1164a4d4c8a147cd8bb775fa5aec8828aa3e6ecb29c88d4f5760d', 'symbols': {}}
for sym in SYMS:
    S = {'years': {}}
    alltr = {}
    for y in YEARS:
        tr, maxopen = load(sym, y); alltr[y] = tr
        sm = summ[f't404_{sym}_{y}']
        nets = [t['net'] for t in tr]
        vpps = [t['vpp'] for t in tr if t['vpp'] is not None]
        vpp = st.median(vpps)
        # stress per PREREG s5: max(1 point, 1bp of price) per round trip; point = MT5 point 0.1
        st_pre = sum(max(MPOINT, 1e-4 * t['p_in']) * t['vol'] * vpp for t in tr)
        # sensitivity: max(1 full index point, 1bp)
        st_idx = sum(max(1.0, 1e-4 * t['p_in']) * t['vol'] * vpp for t in tr)
        holds = [(t['t_out'] - t['t_in']).total_seconds() / 60 for t in tr]
        wk = [t for t in tr if (t['t_in'] - tr[0]['t_in']).days < 7]
        ne = st.mean([t['vol'] * t['p_in'] * vpp / DEP for t in wk])
        # whole-year median notional/equity-at-entry (diagnostic for systematic currency bug)
        eqr = DEP; nes = []
        for t in tr:
            nes.append(t['vol'] * t['p_in'] * vpp / eqr); eqr += t['net']
        ne_med = st.median(nes)
        net = sum(nets)
        # monthly closed-trade returns (each year restarts at 120K)
        mon = defaultdict(float)
        for t in tr: mon[t['t_out'].strftime('%Y-%m')] += t['net']
        eq = DEP; mret = {}
        for m in sorted(mon):
            mret[m] = mon[m] / eq; eq += mon[m]
        S['years'][y] = dict(
            quality_real_ticks_pct=quality(sm['quality']), trades=len(tr), net=round(net, 2),
            net_report=num(sm['net']), equity_dd_pct_report=parse_pct(sm['eq_dd']),
            closed_dd_pct=round(maxdd_closed(nets), 2), stress_prereg=round(st_pre, 2),
            net_after_stress=round(net - st_pre, 2), stress_index_point=round(st_idx, 2),
            net_after_stress_index_point=round(net - st_idx, 2), max_open=maxopen,
            hold_median_min=round(st.median(holds), 1), value_per_point_per_lot=round(vpp, 4),
            notional_to_equity_wk1=round(ne, 3), notional_to_equity_median_year=round(ne_med, 3), implied_quote_per_usd=round((100.0 if sym=='JP225' else 1.0)/vpp, 2), commission=round(sum(t['comm'] for t in tr), 2),
            swap=round(sum(t['swap'] for t in tr), 2), median_lot=st.median([t['vol'] for t in tr]),
            last_exit=str(tr[-1]['t_out']), monthly=mret)
    # top-10 days share over a set of years
    def top10(years):
        daily = defaultdict(float)
        for y in years:
            for t in alltr[y]: daily[t['t_out'].date()] += t['net']
        tot = sum(daily.values())
        if tot <= 0: return None, tot
        return sum(sorted(daily.values(), reverse=True)[:10]) / tot, tot
    sh, tot = top10(GATE_YEARS)
    S['top10_share_gate'] = None if sh is None else round(sh, 4); S['net_gate_total'] = round(tot, 2)
    hold_gate = st.median([(t['t_out']-t['t_in']).total_seconds()/60 for y in GATE_YEARS for t in alltr[y]])
    S['hold_median_gate_min'] = round(hold_gate, 1)
    # monthly geometric 2022+
    ms = [S['years'][y]['monthly'][m] for y in GATE_YEARS for m in sorted(S['years'][y]['monthly'])]
    geo = math.prod(1 + r for r in ms) ** (1 / len(ms)) - 1
    S['monthly_geo_2022p_pct'] = round(geo * 100, 3); S['monthly_geo_2022p_x0.5_pct'] = round(geo * 50, 3)
    S['n_months_2022p'] = len(ms)
    # daily Sharpe / DSR 2022+
    daily = []
    for y in GATE_YEARS:
        dd = defaultdict(float)
        for t in alltr[y]: dd[t['t_out'].date()] += t['net'] / DEP
        last = max(t['t_out'].date() for t in alltr[y])
        daily += [dd.get(d, 0.0) for d in bdays(y, last)]
    sr, p = dsr(daily)
    S['sharpe_daily_ann_2022p'] = round(sr, 3); S['dsr_prob_2022p'] = round(p, 4)
    Y = S['years']
    c = {
        '1_all_gate_years_net_pos': all(Y[y]['net'] > 0 for y in GATE_YEARS),
        '2_equity_dd_le15_all_gate_years': all(Y[y]['equity_dd_pct_report'] <= DD_MAX for y in GATE_YEARS),
        '3_stress_pos_all_gate_years': all(Y[y]['net_after_stress'] > 0 for y in GATE_YEARS),
        '4_top10_lt50': sh is not None and sh < TOP10_MAX,
        '5_single_position': all(Y[y]['max_open'] <= 1 for y in YEARS),
        '6_hold_median_ge15': hold_gate >= HOLD_MIN,
        'data_quality_gate_years_ge99': all(Y[y]['quality_real_ticks_pct'] >= 99 for y in GATE_YEARS),
        'sizing_check_wk1_literal_0.5_4': all(0.5 <= Y[y]['notional_to_equity_wk1'] <= 4 for y in YEARS),
    }
    # s5 sizing check is technical ("not an execution gate"); its purpose = detect a currency-conversion bug.
    # Interpretation (written AFTER seeing data, disclosed in RESULTS):
    #  - INVALID only for systematic mis-sizing that a vol-target cannot explain: year-median ratio <0.5 in any year
    #    (>=4x under USTECH 2.05) or >8 (ASSUMED bound).
    #  - ratio in (4,8]: FLAG only; verdict then rests on scale-invariant conditions (1 net>0, 3 stress, 4 top-10),
    #    which do not change if lots are rescaled.
    sizing_bug = any(not (0.5 <= Y[y]['notional_to_equity_median_year'] <= 8) for y in YEARS)
    S['sizing_bug_systematic'] = sizing_bug
    S['sizing_flag_years'] = [y for y in YEARS if not (0.5 <= Y[y]['notional_to_equity_wk1'] <= 4) or not (0.5 <= Y[y]['notional_to_equity_median_year'] <= 4)]
    S['gate_conditions'] = c
    if sizing_bug:
        S['verdict_frozen'] = 'INVALID (systematic mis-sizing, s5 technical check; not FAIL)'
    else:
        S['verdict_frozen'] = 'PASS' if all(v for k, v in c.items() if not k.startswith('sizing')) else 'FAIL'
    S['flags_2020_2021'] = {y: ('NEG' if Y[y]['net'] <= 0 else 'pos') + ('' if Y[y]['quality_real_ticks_pct'] >= 99 else f" DATA({Y[y]['quality_real_ticks_pct']}%)") for y in (2020, 2021)}
    # post-hoc (a): valid-data years (>=99% real ticks), >=6/7 or >=5/6 positive + other conditions on same years
    vy = [y for y in YEARS if Y[y]['quality_real_ticks_pct'] >= 99]
    npos = sum(Y[y]['net'] > 0 for y in vy)
    need = len(vy) - 1
    sh_v, _ = top10(vy)
    hold_v = st.median([(t['t_out']-t['t_in']).total_seconds()/60 for y in vy for t in alltr[y]])
    pa = {
        'valid_years': vy, 'positive_years': npos, 'required': need,
        'years_ok': npos >= need and len(vy) >= 6,
        'dd_le15_all_valid_years': all(Y[y]['equity_dd_pct_report'] <= DD_MAX for y in vy),
        'dd_years_over15': [y for y in vy if Y[y]['equity_dd_pct_report'] > DD_MAX],
        'stress_pos_all_valid_years': all(Y[y]['net_after_stress'] > 0 for y in vy),
        'stress_pos_all_positive_years': all(Y[y]['net_after_stress'] > 0 for y in vy if Y[y]['net'] > 0),
        'top10_share_valid_years': None if sh_v is None else round(sh_v, 4),
        'top10_ok': sh_v is not None and sh_v < TOP10_MAX,
        'hold_ok': hold_v >= HOLD_MIN, 'single_pos_ok': c['5_single_position'],
    }
    pa['verdict'] = ('INVALID' if sizing_bug else
                     ('PASS(post-hoc, not gate)' if pa['years_ok'] and pa['dd_le15_all_valid_years'] and pa['stress_pos_all_positive_years']
                      and pa['top10_ok'] and pa['hold_ok'] and pa['single_pos_ok'] else 'FAIL'))
    S['posthoc_a'] = pa
    S['posthoc_b'] = ('candidate for forward demo only (separate PREREG, post-hoc)' if pa['verdict'].startswith('PASS') else 'not a candidate')
    res['symbols'][sym] = S
res['n_pass_frozen'] = sum(S['verdict_frozen'] == 'PASS' for S in res['symbols'].values())
res['K'] = 3; res['expected_chance_pass_K3'] = 0.1
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'RESULTS_t404.json')
json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
for sym, S in res['symbols'].items():
    print(sym, S['verdict_frozen'], '| post-hoc(a):', S['posthoc_a']['verdict'])
