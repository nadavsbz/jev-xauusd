#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""t405 gate - implements PREREG_t405.md (sha256 17c8b9ad7b8755ee8a19c6ba11fdcc5daa74b962e681e56e97f6cb103bd1d64f):
s4 cost/data pre-screen, s5 period, s6 per-engine gate 1-10 (PASS / PASS-WITH-FLAG / DD-ONLY), s7 kill, s8 K=8.
Written and frozen by Grok BEFORE any t405 tester output existed/was opened (26.11.2026). Deal parsing, DD, stress,
top-10, hold and DSR logic reused from t404_gate.py.

Usage:
  python t405_gate.py [--data DIR] [--out RESULTS_t405.json]
      DIR holds spec_t405.json, summary.json, deals_*.csv, equity_*_daily.csv (default: <script dir>/../t405_tester)
  python t405_gate.py --selftest      # synthetic fake data in a temp dir; never reads real t405 files
Every interpretation that needed a choice is an ASSUMED item (A1..A19) listed in ASSUMPTIONS and in the output JSON.
"""
import argparse, csv, glob, json, math, os, re, statistics as st, sys, tempfile, random, hashlib
from collections import defaultdict
from datetime import datetime, date, timedelta

PREREG_SHA = '17c8b9ad7b8755ee8a19c6ba11fdcc5daa74b962e681e56e97f6cb103bd1d64f'
DEP = 120000.0
YEARS = list(range(2020, 2027))           # s5: 2020-2026 all gate years (2026 partial to 2026.11.20)
END = date(2026, 11, 20)
DD_MAX = 15.0
TOP10_MAX = 0.50
HOLD_MIN = 15.0
TARGET_M = 3.5
N_TRIALS = 4611                           # s1
K = 8
QUAL_MIN = 99.0
C1_EA_SHA = '1069ea65827beae42ab20300ef6bcf05f97c0ada9aab72016e97ee1caa4cb9ff'
C1_SANITY = (428394.25, 3369)
I2_EA_PREFIX = 'ec559f30'
MAXGROSS = 3.0
GROSS_TOL = 0.02                          # A6
SIZING_RANGE = (0.3, 6.0)                 # s4 technical check -> INVALID
ENGINES = [  # key, family, base symbol, variant, class   (s1, fixed in advance)
    ('US500', 'F1', 'US500', None, 'IDX'), ('USTECH', 'F1', 'USTECH', None, 'IDX'), ('DE40', 'F1', 'DE40', None, 'IDX'),
    ('EURUSD_NY', 'F2', 'EURUSD', 'NY', 'FX'), ('GBPUSD_NY', 'F2', 'GBPUSD', 'NY', 'FX'),
    ('EURUSD_LDN', 'F2', 'EURUSD', 'LDN', 'FX'), ('GBPUSD_LDN', 'F2', 'GBPUSD', 'LDN', 'FX'),
    ('XAUUSD', 'F3', 'XAUUSD', None, 'XAU'),
]
FAMILY_K = {'F1': 3, 'F2': 4, 'F3': 1}
KILL_TEXT = {'F1': 'C1 on RF CFD indices CLOSED (joins rounds 3/17/r101); no retry with LongShare/TargetVol/other TF',
             'F2': 'I2 on FX CLOSED; no other sessions (Tokyo/Sydney), no other pairs',
             'F3': 'C1 on gold CLOSED (joins round 6/r58/r74)'}
COST_MAX = {'IDX': ('bp', 10.0), 'XAU': ('bp', 2.0), 'FX': ('pip', 1.0)}      # s4 round trip
SWAP_MAX_PCT = 10.0                                                            # s4 F1/F3
EXP_MIN = {'FX': ('pips_per_trade', 4.0), 'XAU': ('bp_of_traded_notional', 10.0), 'IDX': ('bp_of_traded_notional', 5.0)}  # s6.7
# s6.10 BD crash days: unique server dates of the 59 live protection events, t379_events_basket.csv (sha 23721b33...fc298)
BD_CRASH_DAYS = ['2025-10-28', '2025-11-11', '2026-04-21', '2026-04-23', '2026-04-30', '2026-05-01', '2026-05-04', '2026-05-06',
                 '2026-05-12', '2026-05-13', '2026-05-14', '2026-05-25', '2026-05-26', '2026-05-27', '2026-05-28', '2026-05-29',
                 '2026-06-02', '2026-06-05', '2026-06-09', '2026-06-30', '2026-07-01', '2026-07-30', '2026-08-05', '2026-08-06',
                 '2026-08-10', '2026-08-11', '2026-08-19', '2026-08-25', '2026-08-27', '2026-09-02', '2026-09-14', '2026-09-16', '2026-10-12']
BD_CRASH_T391 = ['2026-04-21', '2026-04-23', '2026-04-30', '2026-05-01', '2026-06-05']   # the 5 t391 crash windows (subset)

ASSUMPTIONS = [
    'A1 F1/F3 year result = change of end-of-day equity in the calendar year (s3 "years from daily equity"); s6.1 net=profit+commission+swap '
    'is applied literally to F2; F1/F3 closed-deal net per year is reported.',
    'A2 Valid year = real ticks >=99% (s4). Required positive years = valid-1 (6/7 or 5/6); <6 valid -> DATA-FAIL. Quality missing -> INCOMPLETE.',
    'A3 s6.3 stress: 0.5*unit*lots*value_per_point per deal (=1 unit per round trip); unit FX 0.0001, IDX max(1.0,1bp), XAU max(0.10,1bp) of deal '
    'price. Pass = total >0 AND #valid years with stressed result >0 >= required years of s6.1. F2 total over valid years; F1/F3 whole run.',
    'A4 F1/F3 DD: peak of end-of-day equity vs trough=min(intraday-min equity if supplied, EOD equity); gate uses that (conservative), EOD-only '
    'reported. F2 DD = report "equity DD %" per annual run, all valid years <=15%; if missing, closed-trade DD used + flag.',
    'A5 DE40 (EUR, no FX conversion in EA): DD gated on DD/EURUSD (EURUSD from spec or value_per_point/contract_size); raw reported; '
    'if not derivable, raw DD gated.',
    'A6 s6.5 gross<=3.0 "at every moment": checked after every exposure-increasing deal (notional=lots*price*value_per_point, '
    'equity=balance+unrealized at deal price), +2% tolerance for lot rounding; drift between rebalances not observable/not gated.',
    'A7 s6.4 top-10 days: F2 daily closed net over valid years; F1/F3 daily change of EOD equity over the whole run. Net<=0 -> fail.',
    'A8 s6.6 hold = position episode flat->flat (C1: first opening deal until position zero; reversal = close+open).',
    'A9 s6.7 F2 expectancy = mean over trades of net/(lots*value_per_pip); F1/F3 bp = closed-deal net / sum of entry notional (volume '
    'that increases |position|). Cost ratio = (|sum swap|+|sum commission|)/sum gross profit; gross<=0 -> fail.',
    'A10 s6.8 trade loss <=3% of balance before entry (F2 only, as written); worst day <=5% all: F2 day closed net / balance at day start; '
    'F1/F3 EOD equity change / previous EOD equity (intraday-min version reported).',
    'A11 s4 swap screen: annual swap COST of long and of short each <=10% (mode 5/6 = %/yr; points: pts*point*365/price; money: '
    'money/(contract*price)*365). Positive swap is not a cost.',
    'A12 s6.10 correlations need ref_daily_*.csv (date,ret|pnl|equity) in the data dir; absent -> UNKNOWN; PASS stays PASS with note.',
    'A13 BD crash days = 33 unique server dates of the 59 t379 events (5 t391 windows reported separately); F3 flag if sum <0.',
    'A14 F3 regime flag: equity change 2024-2026 / 2020-2026 >0.5 (total >0).',
    'A15 Monthly: F1/F3 geometric mean of month-end equity returns; F2 closed-trade months, each annual run restarting at 120K (t404), also x0.5.',
    'A16 Pre-screen failure computed from spec_t405.json -> COST-EXCLUDED even if a run exists (counts in K). Missing spec field -> UNKNOWN '
    '(reported, not excluded). summary COST/DATA-EXCLUDED list honoured.',
    'A17 F2 DST: spec says server follows US DST -> LDN variants DATA-EXCLUDED; DST check missing/unclear -> LDN INCOMPLETE.',
    'A18 C1 ea_sha256 != 1069ea65... -> INVALID unless summary["sanity"] reproduces +428,394.25 / 3369; set_sha reported only (Symbols '
    'input differs from c1.set by design). I2 ea_sha256 must start with ec559f30.',
    'A19 F2 any non-zero swap -> STOP (hours bug, s4).',
]

# ------------------------------------------------------------------ helpers
def num(s):
    if s is None: return None
    if isinstance(s, (int, float)): return float(s)
    s = str(s).replace('\u00a0', '').replace(' ', '').replace(',', '').strip()
    m = re.search(r'-?\d+(\.\d+)?([eE][-+]?\d+)?', s)
    return float(m.group(0)) if m else None

def pct_in(s):
    """'17,705.93 (11.38%)' -> 11.38 ; '11.38%' -> 11.38 ; 11.38 -> 11.38"""
    if s is None: return None
    if isinstance(s, (int, float)): return float(s)
    m = re.search(r'\(\s*([\d.,]+)\s*%\s*\)', str(s)) or re.search(r'([\d.,]+)\s*%', str(s))
    return float(m.group(1).replace(',', '')) if m else num(s)

TS_FMTS = ['%Y-%m-%d %H:%M:%S', '%Y.%m.%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M', '%Y.%m.%d %H:%M',
           '%Y-%m-%d', '%Y.%m.%d', '%d.%m.%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S']
def pts(s):
    s = re.sub(r'(\d:\d\d:\d\d)\.\d+$', r'\1', str(s).strip().replace('Z', ''))
    for f in TS_FMTS:
        try: return datetime.strptime(s, f)
        except ValueError: pass
    raise ValueError(f'bad timestamp {s!r}')

ALIASES = {
    'ts': ['ts', 'time', 'datetime', 'date', 'deal_time', 'timestamp', 'time_srv', 't'],
    'deal': ['deal', 'ticket', 'deal_id', 'id'],
    'type': ['type', 'side', 'deal_type', 'action'],
    'dir': ['dir', 'direction', 'entry', 'in_out', 'inout', 'deal_entry'],
    'volume': ['volume', 'vol', 'lots', 'lot', 'size'],
    'price': ['price', 'deal_price'],
    'profit': ['profit', 'pnl'],
    'commission': ['commission', 'comm', 'commissions'],
    'swap': ['swap', 'swaps', 'rollover'],
    'fee': ['fee', 'fees'],
    'balance': ['balance', 'bal'],
}
def colmap(header):
    low = {h.strip().lower().replace(' ', '_').replace('/', '_'): h for h in header if h is not None}
    out = {}
    for k, al in ALIASES.items():
        for a in al:
            if a in low: out[k] = low[a]; break
    return out

def norm_sym(s):
    return re.sub(r'(cash|ecn|\.|_|-|\+)', '', str(s).lower())

def read_deals(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        rd = csv.DictReader(f); cm = colmap(rd.fieldnames or [])
        miss = [k for k in ('ts', 'type', 'dir', 'volume', 'price', 'profit') if k not in cm]
        if miss: raise ValueError(f'{os.path.basename(path)}: missing columns {miss} (have {rd.fieldnames})')
        rows = []
        for i, r in enumerate(rd):
            g = lambda k: r.get(cm[k]) if k in cm else None
            typ = str(g('type') or '').strip().lower()
            if 'buy' in typ: typ = 'buy'
            elif 'sell' in typ: typ = 'sell'
            else: continue                                    # balance / credit rows
            d = re.sub(r'[\s_/]', '', str(g('dir') or '').lower())
            d = {'inout': 'inout', 'reverse': 'inout', '2': 'inout', 'in': 'in', '0': 'in', 'out': 'out', '1': 'out', 'outby': 'out', '3': 'out'}.get(d)
            if d is None: continue
            rows.append(dict(t=pts(g('ts')), deal=num(g('deal')) if 'deal' in cm else i, type=typ, dir=d,
                             vol=num(g('volume')) or 0.0, price=num(g('price')) or 0.0, profit=num(g('profit')) or 0.0,
                             comm=num(g('commission')) or 0.0, swap=num(g('swap')) or 0.0, fee=num(g('fee')) or 0.0,
                             bal=num(g('balance')) if 'balance' in cm else None, i=i))
    rows.sort(key=lambda x: (x['t'], x['deal'] if x['deal'] is not None else x['i'], x['i']))
    return rows

def process(rows, deposit=DEP):
    """Position engine for hedging or netting deal lists: episodes flat->flat, snapshots, grid/stacking flags, value-per-point samples."""
    EPS = 1e-9
    L = S = aL = aS = 0.0
    bal = deposit
    eps_, cur, snaps, vpps = [], None, [], []
    both_sides = stack_in = over_close = 0
    for r in rows:
        net = r['profit'] + r['comm'] + r['swap'] + r['fee']
        bal = r['bal'] if r['bal'] is not None else bal + net
        was_flat = L + S < EPS
        closed, opened, v = [], 0.0, r['vol']
        if r['dir'] == 'in':
            if not was_flat and v > 0: stack_in += 1
            if r['type'] == 'buy':
                aL = (aL * L + r['price'] * v) / (L + v) if L + v > 0 else 0.0; L += v
            else:
                aS = (aS * S + r['price'] * v) / (S + v) if S + v > 0 else 0.0; S += v
            opened = v
        elif r['dir'] == 'out':
            if r['type'] == 'sell':
                c = min(v, L); over_close += (v - c > 1e-6); closed.append((c, r['price'] - aL)); L -= c
            else:
                c = min(v, S); over_close += (v - c > 1e-6); closed.append((c, aS - r['price'])); S -= c
        else:   # inout = netting reversal
            if r['type'] == 'buy':
                c = min(v, S); closed.append((c, aS - r['price'])); S -= c; rest = v - c
                if rest > EPS: aL = r['price'] if L < EPS else (aL * L + r['price'] * rest) / (L + rest); L += rest; opened = rest
            else:
                c = min(v, L); closed.append((c, r['price'] - aL)); L -= c; rest = v - c
                if rest > EPS: aS = r['price'] if S < EPS else (aS * S + r['price'] * rest) / (S + rest); S += rest; opened = rest
        L = 0.0 if L < EPS else L; S = 0.0 if S < EPS else S
        if L > 0 and S > 0: both_sides += 1
        cv = sum(c[0] for c in closed)
        nz = [c for c in closed if c[0] > 0]
        if len(nz) == 1 and abs(nz[0][1]) > 1e-9 and abs(r['profit']) > 1e-9:
            vpps.append(r['profit'] / (nz[0][1] * nz[0][0]))
        reversal = r['dir'] == 'inout' and cv > 0 and opened > 0
        if was_flat and opened > 0:
            cur = dict(t_in=r['t'], bal_in=bal - net, net=0.0, entry_vol=0.0, side=r['type'])
        if cur is not None:
            cur['net'] += net
            if not reversal: cur['entry_vol'] += opened
            if L + S < EPS:
                cur['t_out'] = r['t']; eps_.append(cur); cur = None
            elif reversal:
                cur['t_out'] = r['t']; eps_.append(cur)
                cur = dict(t_in=r['t'], bal_in=bal, net=0.0, entry_vol=opened, side=r['type'])
        snaps.append(dict(t=r['t'], price=r['price'], vol=v, opened=opened, closed=cv, L=L, S=S, aL=aL, aS=aS,
                          bal=bal, net=net, profit=r['profit'], comm=r['comm'] + r['fee'], swap=r['swap']))
    return dict(episodes=eps_, open_at_end=cur, snaps=snaps, vpps=vpps, both_sides=both_sides, stack_in=stack_in, over_close=over_close)

def stress_unit(cls, price):
    if cls == 'FX': return 0.0001
    if cls == 'IDX': return max(1.0, 1e-4 * price)
    return max(0.10, 1e-4 * price)

# ------------------------------------------------------------------ stats (from t404)
def norm_ppf(p):  # Acklam
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    pl = 0.02425
    if p < pl:
        q = math.sqrt(-2 * math.log(p)); return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > 1 - pl: return -norm_ppf(1 - p)
    q = p - 0.5; r = q*q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)

def ncdf(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def dsr(daily):
    T = len(daily)
    if T < 3: return None, None
    mu = st.mean(daily); sd = st.pstdev(daily)
    if sd == 0: return None, None
    sr = mu / sd
    m3 = sum((x-mu)**3 for x in daily)/T/sd**3; m4 = sum((x-mu)**4 for x in daily)/T/sd**4
    g = 0.5772156649; N = N_TRIALS
    sr0 = math.sqrt(1.0/T) * ((1-g)*norm_ppf(1-1.0/N) + g*norm_ppf(1-1.0/(N*math.e)))
    z = (sr - sr0) * math.sqrt(T-1) / math.sqrt(max(1e-12, 1 - m3*sr + (m4-1)/4*sr*sr))
    return round(sr * math.sqrt(252), 3), round(ncdf(z), 4)

def bdays(d0, d1):
    out, d = [], d0
    while d <= d1:
        if d.weekday() < 5: out.append(d)
        d += timedelta(days=1)
    return out

def corr(a, b):
    ks = sorted(set(a) & set(b))
    if len(ks) < 30: return None
    x = [a[k] for k in ks]; y = [b[k] for k in ks]
    sx, sy = st.pstdev(x), st.pstdev(y)
    if sx == 0 or sy == 0: return None
    mx, my = st.mean(x), st.mean(y)
    return round(sum((p-mx)*(q-my) for p, q in zip(x, y)) / len(x) / sx / sy, 3)

def top10_share(daily):
    tot = sum(daily.values())
    if tot <= 0: return None, tot
    return sum(sorted(daily.values(), reverse=True)[:10]) / tot, tot

def geo_monthly(rets):
    if not rets or any(1 + r <= 0 for r in rets): return None
    return (math.prod(1 + r for r in rets) ** (1 / len(rets)) - 1) * 100

# ------------------------------------------------------------------ summary / spec
def load_json(p):
    with open(p, encoding='utf-8-sig') as f: return json.load(f)

def runs_list(summ):
    if isinstance(summ, list): return [(str(i), r) for i, r in enumerate(summ) if isinstance(r, dict)]
    if isinstance(summ, dict):
        for k in ('runs', 'results', 'items'):
            if isinstance(summ.get(k), list): return [(str(i), r) for i, r in enumerate(summ[k]) if isinstance(r, dict)]
            if isinstance(summ.get(k), dict): return [(kk, r) for kk, r in summ[k].items() if isinstance(r, dict)]
        return [(k, r) for k, r in summ.items() if isinstance(r, dict) and not re.search(r'(exclud|sanity)', k, re.I)]
    return []

def fget(d, *pats, default=None):
    if not isinstance(d, dict): return default
    for k, v in d.items():
        if all(re.search(p, k, re.I) for p in pats): return v
    return default

def run_matches(name, r, base, variant, year):
    blob = norm_sym(name + ' ' + str(r.get('symbol', '')))
    if norm_sym(base) not in blob: return False
    if variant:
        vtxt = (str(r.get('variant', '')) + ' ' + name).lower()
        other = 'ldn' if variant == 'NY' else 'ny'
        if not re.search(r'(^|[^a-z])' + variant.lower() + r'([^a-z]|$)', vtxt): return False
        if re.search(r'(^|[^a-z])' + other + r'([^a-z]|$)', vtxt): return False
    if year is not None and str(year) not in name + ' ' + str(r.get('from', '')): return False
    return True

def find_run(runs, base, variant, year=None):
    c = [(n, r) for n, r in runs if run_matches(n, r, base, variant, year)]
    return c[0] if c else (None, None)

def quality_by_year(r, year=None):
    out = {}
    for k, v in (r or {}).items():
        if not re.search(r'qual', k, re.I): continue
        if isinstance(v, dict):
            for yk, yv in v.items():
                m = re.search(r'(20\d\d)', str(yk))
                if m: out[int(m.group(1))] = pct_in(yv)
        elif isinstance(v, list):
            for it in v:
                if isinstance(it, dict) and num(fget(it, 'year')): out[int(num(fget(it, 'year')))] = pct_in(fget(it, 'qual') or fget(it, 'pct'))
        elif year is not None:
            out[year] = pct_in(v)
    return out

def summary_excluded(summ):
    out = {}
    if not isinstance(summ, dict): return out
    for k, v in summ.items():
        if not re.search(r'exclud', k, re.I): continue
        items = v if isinstance(v, list) else ([{'symbol': kk, 'reason': vv} for kk, vv in v.items()] if isinstance(v, dict) else [])
        for it in items:
            if isinstance(it, str): it = {'symbol': it, 'reason': k}
            kind = 'DATA' if re.search('data', k + ' ' + json.dumps(it, ensure_ascii=False), re.I) else 'COST'
            out[(norm_sym(it.get('symbol', '')), str(it.get('variant', '') or '').upper())] = (kind + '-EXCLUDED', str(it.get('reason', '')))
    return out

def spec_for(spec, base):
    if not isinstance(spec, dict): return {}
    pool = spec.get('symbols', spec)
    if isinstance(pool, list):
        return next((it for it in pool if isinstance(it, dict) and norm_sym(it.get('symbol', '')) == norm_sym(base)), {})
    for k, v in pool.items():
        if isinstance(v, dict) and (norm_sym(k) == norm_sym(base) or norm_sym(v.get('symbol', '')) == norm_sym(base)): return v
    return {}

def prescreen(cls, variant, sp, ref_price, vpp_data):
    """s4: spread + 2*commission (round trip) vs threshold; swap screen for F1/F3."""
    res = {'status': 'UNKNOWN', 'notes': []}
    if not sp: res['notes'].append('no spec entry'); return res
    dg = num(fget(sp, 'digits'))
    point = num(fget(sp, r'^point$')) or (10 ** -dg if dg is not None else None)
    contract = num(fget(sp, 'contract'))
    tv, tsz = num(fget(sp, r'tick_?value')), num(fget(sp, r'tick_?size'))
    vpp = (tv / tsz) if tv and tsz else (vpp_data or contract)
    price = num(fget(sp, r'^(ref_)?price$')) or num(fget(sp, r'^bid$')) or ref_price
    spread_px, src = None, None
    keys = [k for k in sp if re.search('spread', k, re.I)]
    if variant:
        keys = [k for k in keys if re.search(variant, k, re.I) or re.search('window', k, re.I)] or keys
    for k in keys:
        v = sp[k]
        if isinstance(v, dict):
            v = fget(v, 'median') or fget(v, 'typ') or (v.get(variant) if variant else None)
        v = num(v)
        if v is None: continue
        if re.search(r'bp', k, re.I) and price: spread_px = v * 1e-4 * price
        elif re.search(r'pip', k, re.I): spread_px = v * 0.0001
        elif re.search(r'(price|usd)', k, re.I): spread_px = v
        elif point: spread_px = v * point
        else: continue
        src = k; break
    comm_px = None
    for k in [k for k in sp if re.search('comm', k, re.I)]:
        v = num(sp[k]) if not isinstance(sp[k], dict) else num(fget(sp[k], 'lot') or fget(sp[k], 'value'))
        if v is None: continue
        if re.search(r'(pct|percent)', k, re.I) and price: comm_px = abs(v) / 100 * price
        elif vpp: comm_px = abs(v) / vpp
        if comm_px is not None and re.search(r'(round|_rt$|_rt_)', k, re.I): comm_px /= 2
        if comm_px is not None: break
    res.update(spread_key=src, point=point, value_per_point=vpp, ref_price=price)
    unit, mx = COST_MAX[cls]
    if spread_px is None or not price:
        res['notes'].append('spread or price missing')
    else:
        if comm_px is None: res['notes'].append('commission UNKNOWN (0 used in screen)')
        cpx = spread_px + 2 * (comm_px or 0.0)
        val = cpx / 0.0001 if unit == 'pip' else cpx / price * 1e4
        res.update(roundtrip_cost=round(val, 4), roundtrip_unit=unit, roundtrip_max=mx, cost_ok=val <= mx)
    if cls in ('IDX', 'XAU'):
        mode = str(fget(sp, r'swap_?mode') or '').lower()
        sl, ss = num(fget(sp, r'swap_?long')), num(fget(sp, r'swap_?short'))
        def ann(x):
            if x is None or not price: return None
            if mode in ('5', '6') or 'interest' in mode or 'percent' in mode: return x
            if mode == '1' or 'point' in mode: return x * point * 365 / price * 100 if point else None
            if mode in ('2', '3', '4') or 'currency' in mode or 'money' in mode: return x / (contract * price) * 365 * 100 if contract else None
            return None
        al, as_ = ann(sl), ann(ss)
        res['swap_annual_pct'] = {'long': None if al is None else round(al, 3), 'short': None if as_ is None else round(as_, 3), 'mode': mode}
        if al is None or as_ is None: res['notes'].append('swap annual UNKNOWN')
        else: res['swap_ok'] = max(0, -al) <= SWAP_MAX_PCT and max(0, -as_) <= SWAP_MAX_PCT
    flags = [res.get('cost_ok')] + ([res.get('swap_ok')] if cls != 'FX' else [])
    if any(f is False for f in flags): res['status'] = 'EXCLUDED'
    elif all(f is True for f in flags): res['status'] = 'PASS'
    return res

def dst_status(spec):
    v = None
    def scan(d):
        for k, x in d.items():
            if re.search('dst', k, re.I): return x
        return None
    if isinstance(spec, dict):
        v = scan(spec)
        if v is None and isinstance(spec.get('symbols'), dict):
            for s in spec['symbols'].values():
                if isinstance(s, dict) and scan(s) is not None: v = scan(s); break
    if v is None: return 'MISSING', None
    t = json.dumps(v, ensure_ascii=False).lower()
    if re.search(r'\b(us|usa|america|american)\b', t) and not re.search(r'\b(eu|europe|european)\b', t): return 'US', v
    if re.search(r'(\beu\b|europe|gmt\+2/\+3)', t): return 'EU', v
    return 'UNCLEAR', v

def read_equity(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        rd = csv.DictReader(f)
        low = {h.strip().lower(): h for h in (rd.fieldnames or [])}
        dk = next((low[k] for k in ('date', 'day', 'ts', 'time') if k in low), None)
        ek = next((low[k] for k in ('equity', 'equity_close', 'equity_eod', 'eq', 'equity_end') if k in low), None)
        mk = next((low[k] for k in low if re.search(r'(min|low)', k) and re.search('eq', k)), None)
        if not dk or not ek: raise ValueError(f'{os.path.basename(path)}: need date+equity columns, have {rd.fieldnames}')
        out = {}
        for r in rd:
            e = num(r[ek])
            if e is not None: out[pts(r[dk]).date()] = dict(eq=e, eqmin=num(r[mk]) if mk else None)
    return dict(sorted(out.items()))

def find_file(data, parts, exclude=()):
    out = []
    for p in sorted(glob.glob(os.path.join(data, '*.csv'))):
        nn = norm_sym(os.path.basename(p)[:-4])
        if all(norm_sym(t) in nn for t in parts) and not any(norm_sym(x) in nn for x in exclude): out.append(p)
    return out

# ------------------------------------------------------------------ F2 (I2 FX, annual runs)
def analyse_f2(data, base, variant, runs, cls):
    other = 'ldn' if variant == 'NY' else 'ny'
    per_year, flags = {}, []
    for y in YEARS:
        fs = find_file(data, ['deals', base, variant.lower(), str(y)], exclude=['deals' + norm_sym(base) + other])
        if fs: per_year[y] = (os.path.basename(fs[0]), process(read_deals(fs[0])))
    if not per_year: return None
    vpps = [v for y in per_year for v in per_year[y][1]['vpps']]
    vpp = st.median(vpps) if vpps else 100000.0
    if not vpps: flags.append('value_per_point not inferable; default 100000')
    Y, EP, prices = {}, {}, []
    for y in YEARS:
        if y not in per_year: Y[y] = {'missing': True}; continue
        fn, P = per_year[y]
        _, sm = find_run(runs, base, variant, y)
        E, snaps = P['episodes'], P['snaps']
        prices += [s['price'] for s in snaps if s['opened'] > 0]
        net = sum(s['net'] for s in snaps)
        stress = sum(0.5 * stress_unit(cls, s['price']) * s['vol'] * vpp for s in snaps)
        eq = peak = DEP; cdd = 0.0
        for e in E: eq += e['net']; peak = max(peak, eq); cdd = max(cdd, (peak - eq) / peak * 100)
        rep_dd = pct_in(fget(sm, r'eq', r'dd') or fget(sm, r'equity', r'draw')) if sm else None
        daily = defaultdict(float); dstart = {}
        for s in snaps:
            d = s['t'].date(); daily[d] += s['net']; dstart.setdefault(d, s['bal'] - s['net'])
        nes = [s['opened'] * s['price'] * vpp / (s['bal'] - s['net']) for s in snaps if s['opened'] > 0 and s['bal'] - s['net'] > 0]
        mon = defaultdict(float)
        for e in E: mon[e['t_out'].strftime('%Y-%m')] += e['net']
        eqm, mret = DEP, {}
        for m in sorted(mon): mret[m] = mon[m] / eqm; eqm += mon[m]
        Y[y] = dict(file=fn, run=_, quality_real_ticks_pct=quality_by_year(sm, y).get(y) if sm else None, trades=len(E),
                    net=round(net, 2), report_net=num(fget(sm, r'^net')) if sm else None, stress=round(stress, 2), net_after_stress=round(net - stress, 2),
                    equity_dd_pct_report=rep_dd, closed_dd_pct=round(cdd, 2), dd_used=rep_dd if rep_dd is not None else round(cdd, 2),
                    dd_source='report' if rep_dd is not None else 'closed-trade',
                    stack_in_events=P['stack_in'], both_sides_events=P['both_sides'], over_close_events=P['over_close'],
                    hold_median_min=round(st.median([(e['t_out'] - e['t_in']).total_seconds() / 60 for e in E]), 1) if E else None,
                    gross_profit=round(sum(s['profit'] for s in snaps), 2), commission=round(sum(s['comm'] for s in snaps), 2),
                    swap=round(sum(s['swap'] for s in snaps), 2),
                    worst_trade_loss_pct=round(max([-e['net'] / e['bal_in'] * 100 for e in E if e['bal_in'] > 0] + [0.0]), 3),
                    worst_day_loss_pct=round(max([-v / dstart[d] * 100 for d, v in daily.items() if dstart[d] > 0] + [0.0]), 3),
                    notional_to_equity_median=round(st.median(nes), 3) if nes else None, open_at_end=P['open_at_end'] is not None,
                    monthly=mret, _daily=daily)
        EP[y] = E
    return dict(Y=Y, EP=EP, vpp=vpp, flags=flags, median_price=st.median(prices) if prices else None)

# ------------------------------------------------------------------ F1/F3 (C1, one continuous run)
def analyse_c1(data, base, cls, runs, sp):
    fs = find_file(data, ['deals', base, '2020', '2026']) or find_file(data, ['deals', base])
    if not fs: return None
    efs = find_file(data, ['equity', base])
    flags = [] if efs else ['equity_<SYM>_daily.csv MISSING -> INCOMPLETE']
    P = process(read_deals(fs[0]))
    eqd = read_equity(efs[0]) if efs else None
    if P['vpps']: vpp = st.median(P['vpps'])
    else:
        tv, tsz = num(fget(sp, r'tick_?value')), num(fget(sp, r'tick_?size'))
        vpp = tv / tsz if tv and tsz else (num(fget(sp, 'contract')) or 1.0)
        flags.append('value_per_point from spec/default (no closed deal with price move)')
    contract = num(fget(sp, 'contract'))
    R = dict(files=[os.path.basename(fs[0])] + ([os.path.basename(efs[0])] if efs else []), value_per_point_per_lot=round(vpp, 6),
             implied_quote_per_usd=round(contract / vpp, 4) if contract else None)
    snaps = P['snaps']
    gmax, gviol, nes_y = 0.0, [], defaultdict(list)
    for s in snaps:                                       # A6
        if s['opened'] <= 0: continue
        eqe = s['bal'] + ((s['price'] - s['aL']) * s['L'] + (s['aS'] - s['price']) * s['S']) * vpp
        if eqe <= 0: continue
        g = (s['L'] + s['S']) * s['price'] * vpp / eqe
        gmax = max(gmax, g); nes_y[s['t'].year].append(g)
        if g > MAXGROSS * (1 + GROSS_TOL): gviol.append((str(s['t']), round(g, 3)))
    E = P['episodes']
    holds = [(e['t_out'] - e['t_in']).total_seconds() / 60 for e in E]
    stress_y, closed_y = defaultdict(float), defaultdict(float)
    for s in snaps:
        stress_y[s['t'].year] += 0.5 * stress_unit(cls, s['price']) * s['vol'] * vpp; closed_y[s['t'].year] += s['net']
    R.update(episodes=len(E), deals=len(snaps), closed_net=round(sum(s['net'] for s in snaps), 2),
             gross_profit=round(sum(s['profit'] for s in snaps), 2), commission=round(sum(s['comm'] for s in snaps), 2),
             swap=round(sum(s['swap'] for s in snaps), 2), entry_notional=round(sum(s['opened'] * s['price'] * vpp for s in snaps), 2),
             both_sides_events=P['both_sides'], over_close_events=P['over_close'], gross_max_after_entry=round(gmax, 3),
             n_gross_violations=len(gviol), gross_violations=gviol[:20], hold_median_min=round(st.median(holds), 1) if holds else None,
             open_at_end=P['open_at_end'] is not None, stress_total=round(sum(stress_y.values()), 2))
    rn, sm = find_run(runs, base, None)
    R['summary_run'] = rn
    qy = quality_by_year(sm) if sm else {}
    ye, dchg, rets, mr = {y: None for y in YEARS}, {}, {}, []
    if eqd:
        days = list(eqd); prev = DEP
        for y in YEARS:
            dy = [d for d in days if d.year == y]
            if dy: ye[y] = eqd[dy[-1]]['eq'] - prev; prev = eqd[dy[-1]]['eq']
        peak = DEP; dd_eod = dd_min = 0.0
        for d in days:
            e = eqd[d]['eq']; lo = min(e, eqd[d]['eqmin']) if eqd[d]['eqmin'] is not None else e
            dd_min = max(dd_min, (peak - lo) / peak * 100)
            peak = max(peak, e); dd_eod = max(dd_eod, (peak - e) / peak * 100)
        prev_e, worst, worst_min = DEP, 0.0, 0.0
        for d in days:
            e = eqd[d]['eq']; dchg[d] = e - prev_e; rets[d] = (e - prev_e) / prev_e
            worst = max(worst, -(e - prev_e) / prev_e * 100)
            if eqd[d]['eqmin'] is not None: worst_min = max(worst_min, -(eqd[d]['eqmin'] - prev_e) / prev_e * 100)
            prev_e = e
        me = {}
        for d in days: me[d.strftime('%Y-%m')] = eqd[d]['eq']
        pe = DEP
        for m in sorted(me): mr.append(me[m] / pe - 1); pe = me[m]
        R.update(dd_eod_pct=round(dd_eod, 2), dd_intraday_pct=round(dd_min, 2) if any(eqd[d]['eqmin'] is not None for d in days) else None,
                 dd_used=round(max(dd_eod, dd_min), 2), worst_day_eod_pct=round(worst, 3), worst_day_intraday_pct=round(worst_min, 3),
                 final_equity=round(eqd[days[-1]]['eq'], 2), last_day=str(days[-1]))
    R['years'] = {y: dict(quality_real_ticks_pct=qy.get(y), net_equity=None if ye[y] is None else round(ye[y], 2),
                          net_closed_deals=round(closed_y.get(y, 0.0), 2), stress=round(stress_y.get(y, 0.0), 2),
                          net_after_stress=None if ye[y] is None else round(ye[y] - stress_y.get(y, 0.0), 2),
                          notional_to_equity_median=round(st.median(nes_y[y]), 3) if nes_y.get(y) else None) for y in YEARS}
    prices = [s['price'] for s in snaps if s['opened'] > 0]
    return dict(R=R, EP=E, vpp=vpp, flags=flags, dchg=dchg, rets=rets, mr=mr, sm=sm, median_price=st.median(prices) if prices else None)

def ref_series(data):
    out = {}
    for p in glob.glob(os.path.join(data, 'ref_daily_*.csv')):
        with open(p, encoding='utf-8-sig', newline='') as f:
            rd = csv.DictReader(f); low = {h.lower(): h for h in rd.fieldnames}
            dk = next((low[k] for k in ('date', 'day', 'ts') if k in low), None)
            vk = next((k for k in ('ret', 'return', 'pnl', 'net', 'equity') if k in low), None)
            if not dk or not vk: continue
            s = {pts(r[dk]).date(): num(r[low[vk]]) for r in rd if num(r[low[vk]]) is not None}
        if vk == 'equity':
            ks = sorted(s); s = {ks[i]: s[ks[i]] / s[ks[i-1]] - 1 for i in range(1, len(ks))}
        out[os.path.basename(p)[10:-4]] = s
    return out

# ------------------------------------------------------------------ gate
def gate(data, out_path):
    sp_p, su_p = os.path.join(data, 'spec_t405.json'), os.path.join(data, 'summary.json')
    spec = load_json(sp_p) if os.path.exists(sp_p) else {}
    summ = load_json(su_p) if os.path.exists(su_p) else {}
    runs, excl, refs = runs_list(summ), summary_excluded(summ), ref_series(data)
    dst, dst_raw = dst_status(spec)
    res = dict(prereg_sha256=PREREG_SHA, gate_file_sha256=hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(),
               data_dir=os.path.abspath(data),
               input_sha256={os.path.basename(p): hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in sorted(glob.glob(os.path.join(data, '*'))) if os.path.isfile(p)},
               spec_present=bool(spec), summary_present=bool(summ), dst_check=dict(status=dst, raw=dst_raw),
               refs_available=sorted(refs), assumptions=ASSUMPTIONS, engines={})
    for key, fam, base, variant, cls in ENGINES:
        S = {'family': fam, 'class': cls, 'variant': variant, 'flags': [], 'verdict': None, 'verdict_reason': None}
        sp = spec_for(spec, base)
        pre_hard = excl.get((norm_sym(base), variant or '')) or excl.get((norm_sym(base), ''))
        if fam == 'F2' and variant == 'LDN':
            if dst == 'US': pre_hard = ('DATA-EXCLUDED', 'server follows US DST (s3 F2 rule, A17)')
            elif dst in ('MISSING', 'UNCLEAR'): S['flags'].append(f'DST check {dst} -> INCOMPLETE (A17)')
        try:
            A = analyse_f2(data, base, variant, runs, cls) if fam == 'F2' else analyse_c1(data, base, cls, runs, sp)
        except Exception as e:
            A = None; S['flags'].append(f'PARSE ERROR {type(e).__name__}: {e}')
        S['prescreen'] = prescreen(cls, variant, sp, A['median_price'] if A else None, A['vpp'] if A else None)
        if pre_hard: S['verdict'], S['verdict_reason'] = pre_hard
        elif S['prescreen']['status'] == 'EXCLUDED': S['verdict'], S['verdict_reason'] = 'COST-EXCLUDED', 'computed from spec_t405.json (s4, A16)'
        if A is None:
            S['verdict'] = S['verdict'] or ('INCOMPLETE' if S['flags'] else 'MISSING')
            res['engines'][key] = S; continue
        S['flags'] += A['flags']; vpp = A['vpp']
        # run metadata (A18)
        sm0 = (find_run(runs, base, variant, 2024)[1] or find_run(runs, base, variant)[1]) if fam == 'F2' else A['sm']
        sm0 = sm0 or {}
        ea = str(fget(sm0, r'^ea') or fget(sm0, r'ea_?sha') or '')
        S.update(ea_sha256=ea or None, set_sha256=fget(sm0, r'set_?sha'), build=fget(sm0, 'build'))
        meta_invalid = None
        if not ea: S['flags'].append('ea_sha256 missing in summary')
        elif fam == 'F2':
            if not ea.lower().startswith(I2_EA_PREFIX): meta_invalid = f'I2 ea_sha256 {ea[:8]} != {I2_EA_PREFIX}'
        elif ea.lower() != C1_EA_SHA:
            san = summ.get('sanity') if isinstance(summ, dict) else None
            ok = isinstance(san, dict) and num(fget(san, 'net')) is not None and abs(num(fget(san, 'net')) - C1_SANITY[0]) < 0.01 \
                and num(fget(san, 'trade')) == C1_SANITY[1]
            if ok: S['flags'].append('C1 ex5 != 1069ea65 but sanity reproduction matches')
            else: meta_invalid = f'C1 ea_sha256 {ea[:8]} != 1069ea65 and no matching sanity (+428,394.25/3369)'
        if fam == 'F2':
            Y, EP = A['Y'], A['EP']
            present = [y for y in YEARS if not Y[y].get('missing')]
            missing = [y for y in YEARS if Y[y].get('missing')]
            qmiss = [y for y in present if Y[y]['quality_real_ticks_pct'] is None]
            valid = [y for y in present if (Y[y]['quality_real_ticks_pct'] or 0) >= QUAL_MIN]
            yr_net = {y: Y[y]['net'] for y in valid}; yr_st = {y: Y[y]['net_after_stress'] for y in valid}
            daily = defaultdict(float)
            for y in valid:
                for d, v in Y[y]['_daily'].items(): daily[d] += v
            dd_val = max([Y[y]['dd_used'] for y in valid] + [0.0]); dd_ok = bool(valid) and dd_val <= DD_MAX
            if any(Y[y]['dd_source'] != 'report' for y in valid): S['flags'].append('report equity DD missing for some year -> closed-trade DD used')
            single_ok = all(Y[y]['stack_in_events'] == 0 and Y[y]['both_sides_events'] == 0 for y in present)
            holds = [(e['t_out'] - e['t_in']).total_seconds() / 60 for y in valid for e in EP[y]]
            hold = st.median(holds) if holds else None
            pips = [e['net'] / (e['entry_vol'] * vpp * 0.0001) for y in valid for e in EP[y] if e['entry_vol'] > 0]
            exp_val = st.mean(pips) if pips else None
            gp = sum(Y[y]['gross_profit'] for y in valid); cm = sum(Y[y]['commission'] for y in valid); sw = sum(Y[y]['swap'] for y in valid)
            worst_trade = max([Y[y]['worst_trade_loss_pct'] for y in valid] + [0.0]); worst_day = max([Y[y]['worst_day_loss_pct'] for y in valid] + [0.0])
            loss_ok = worst_trade <= 3.0 and worst_day <= 5.0
            swap_nonzero = any(abs(Y[y]['swap']) > 1e-9 for y in present)
            sizing = {y: Y[y]['notional_to_equity_median'] for y in present}
            geo = geo_monthly([Y[y]['monthly'][m] for y in valid for m in sorted(Y[y]['monthly'])])
            S['monthly_geo_pct'] = None if geo is None else round(geo, 3); S['monthly_geo_x0.5_pct'] = None if geo is None else round(geo / 2, 3)
            dl, rets = [], {}
            for y in valid:
                if not EP[y]: continue
                for d, v in Y[y]['_daily'].items(): rets[d] = v / DEP
                dl += [Y[y]['_daily'].get(d, 0.0) / DEP for d in bdays(date(y, 1, 1), max(e['t_out'].date() for e in EP[y]))]
            for y in present: Y[y].pop('_daily', None)
            total_net = sum(yr_net.values()); total_st = sum(yr_st.values())
            S['years'] = Y; S['value_per_point_per_lot'] = round(vpp, 4)
        else:
            R = A['R']; Y = R.pop('years')
            missing = [y for y in YEARS if Y[y]['net_equity'] is None]
            qmiss = [y for y in YEARS if y not in missing and Y[y]['quality_real_ticks_pct'] is None]
            valid = [y for y in YEARS if y not in missing and (Y[y]['quality_real_ticks_pct'] or 0) >= QUAL_MIN]
            yr_net = {y: Y[y]['net_equity'] for y in valid}; yr_st = {y: Y[y]['net_after_stress'] for y in valid}
            daily = dict(A['dchg'])
            dd_val = R.get('dd_used')
            if key == 'DE40' and dd_val is not None:
                fx = num(fget(sp, 'eurusd')) or (1.0 / R['implied_quote_per_usd'] if R.get('implied_quote_per_usd') else None)
                S['eurusd_used'] = fx
                if fx and 0.8 < fx < 1.6: dd_val = dd_val / fx; S['dd_normalized_pct'] = round(dd_val, 2)
                else: S['flags'].append('DE40 EURUSD not derivable -> raw DD gated (A5)')
            dd_ok = dd_val is not None and dd_val <= DD_MAX
            single_ok = R['both_sides_events'] == 0 and R['n_gross_violations'] == 0 and R['over_close_events'] == 0
            hold = R['hold_median_min']
            exp_val = R['closed_net'] / R['entry_notional'] * 1e4 if R['entry_notional'] > 0 else None
            gp, cm, sw = R['gross_profit'], R['commission'], R['swap']
            worst_trade = None; worst_day = R.get('worst_day_eod_pct')
            loss_ok = worst_day is not None and worst_day <= 5.0
            swap_nonzero = False
            sizing = {y: Y[y]['notional_to_equity_median'] for y in YEARS}
            geo = geo_monthly(A['mr']); S['monthly_geo_pct'] = None if geo is None else round(geo, 3)
            rets = A['rets']
            dl = [rets.get(d, 0.0) for d in bdays(min(rets), max(rets))] if rets else []
            total_net = (R['final_equity'] - DEP) if R.get('final_equity') is not None else None
            total_st = None if total_net is None else total_net - R['stress_total']
            S.update(R); S['years'] = Y
        S['missing_years'] = missing; S['quality_missing_years'] = qmiss
        nvalid = len(valid); need = nvalid - 1
        npos = sum(1 for y in valid if (yr_net.get(y) or 0) > 0)
        npos_st = sum(1 for y in valid if (yr_st.get(y) or 0) > 0)
        sh, _tot = top10_share(daily) if daily else (None, 0)
        cost_ratio = (abs(sw) + abs(cm)) / gp if gp > 0 else None
        thr_name, thr = EXP_MIN[cls]
        c = {
            '1_positive_years': nvalid >= 6 and npos >= need,
            '2_dd_le15': dd_ok,
            '3_stress_pos_total_and_years': total_st is not None and total_st > 0 and nvalid >= 6 and npos_st >= need,
            '4_top10_lt50': sh is not None and sh < TOP10_MAX,
            '5_single_net_position_no_grid': single_ok,
            '6_hold_median_ge15': hold is not None and hold >= HOLD_MIN,
            '7a_expectancy': exp_val is not None and exp_val >= thr,
            '7b_swap_comm_le50pct_gross': cost_ratio is not None and cost_ratio <= 0.5,
            '8_loss_limits': loss_ok,
        }
        S['conditions'] = c
        S['metrics'] = dict(valid_years=valid, n_valid=nvalid, positive_years=npos, required=need, stress_positive_years=npos_st,
                            total_net=None if total_net is None else round(total_net, 2), total_net_after_stress=None if total_st is None else round(total_st, 2),
                            dd_pct_gated=None if dd_val is None else round(dd_val, 2), top10_share=None if sh is None else round(sh, 4),
                            hold_median_min=None if hold is None else round(hold, 1), expectancy=None if exp_val is None else round(exp_val, 3),
                            expectancy_unit=thr_name, expectancy_min=thr, cost_ratio=None if cost_ratio is None else round(cost_ratio, 4),
                            gross_profit=round(gp, 2), commission=round(cm, 2), swap=round(sw, 2),
                            worst_trade_loss_pct=worst_trade, worst_day_loss_pct=worst_day, sizing_median_by_year=sizing)
        S['sharpe_daily_ann'], S['dsr_prob_N4611'] = dsr(dl) if dl else (None, None)
        S['label_vs_3.5pct_month'] = None if S.get('monthly_geo_pct') is None else ('engine' if S['monthly_geo_pct'] >= TARGET_M else 'stabilizer')
        cr = {n: corr(rets, s) for n, s in refs.items()}
        S['correlations'] = cr or 'UNKNOWN (no ref_daily_*.csv)'
        corr_flag = any(v is not None and v > 0.5 for v in cr.values())
        regime_flag = False
        if fam == 'F3':
            cd = {d: round(daily.get(date.fromisoformat(d), 0.0), 2) for d in BD_CRASH_DAYS}
            s_all = sum(cd.values())
            S['bd_crash_days'] = dict(per_day=cd, sum_33_days=round(s_all, 2), sum_t391_5_windows=round(sum(cd[d] for d in BD_CRASH_T391), 2),
                                      days_with_data=sum(1 for d in BD_CRASH_DAYS if date.fromisoformat(d) in daily), flag_not_protecting_fleet=s_all < 0)
            if s_all < 0: S['flags'].append('F3 BD crash-day P&L sum <0: does not protect the fleet')
            n2426 = sum(Y[y]['net_equity'] or 0 for y in (2024, 2025, 2026)); tn = sum(Y[y]['net_equity'] or 0 for y in YEARS)
            S['regime_share_2024_2026'] = round(n2426 / tn, 4) if tn > 0 else None
            regime_flag = tn > 0 and n2426 / tn > 0.5
        S['regime_flag'] = regime_flag; S['corr_flag'] = corr_flag
        bad_sz = [y for y, v in sizing.items() if v is not None and not (SIZING_RANGE[0] <= v <= SIZING_RANGE[1])]
        S['sizing_out_of_range_years'] = bad_sz
        if not S['verdict']:
            if meta_invalid: S['verdict'], S['verdict_reason'] = 'INVALID', meta_invalid
            elif swap_nonzero: S['verdict'], S['verdict_reason'] = 'STOP', 'F2 swap != 0 -> hours bug (s4, A19)'
            elif bad_sz: S['verdict'], S['verdict_reason'] = 'INVALID', f'notional/equity median outside 0.3-6 in {bad_sz} (s4 technical)'
            elif missing or qmiss or any('MISSING' in f or 'INCOMPLETE' in f for f in S['flags']):
                S['verdict'], S['verdict_reason'] = 'INCOMPLETE', f'missing years {missing}; quality missing {qmiss}; flags {S["flags"]}'
            elif nvalid < 6: S['verdict'], S['verdict_reason'] = 'DATA-FAIL', f'only {nvalid} valid years (<6)'
            elif all(c.values()):
                S['verdict'] = 'PASS-WITH-FLAG' if (regime_flag or corr_flag) else 'PASS'
                S['verdict_reason'] = ' '.join(x for x in ['regime>50% 2024-26' if regime_flag else '', 'corr>0.5' if corr_flag else '',
                                                           '' if cr else 'correlation UNKNOWN'] if x)
            elif not c['2_dd_le15'] and all(v for k, v in c.items() if k != '2_dd_le15') and dd_val:
                s_ = DD_MAX / dd_val
                S['verdict'], S['verdict_reason'] = 'DD-ONLY', 'only s6.2 failed; NOT a PASS -> candidate for new PREREG with TargetVol*s fixed in advance'
                S['dd_only'] = dict(s=round(s_, 4), monthly_x_s_pct=None if S.get('monthly_geo_pct') is None else round(S['monthly_geo_pct'] * s_, 3))
            else: S['verdict'], S['verdict_reason'] = 'FAIL', 'failed: ' + ', '.join(k for k, v in c.items() if not v)
        res['engines'][key] = S
    passed = [k for k, S in res['engines'].items() if S['verdict'] in ('PASS', 'PASS-WITH-FLAG')]
    res.update(n_pass=len(passed), passed=passed, K=K, report_line=f'{len(passed)} of 8 passed; chance expectation ~0.1-0.2')
    fams = {}
    for f in ('F1', 'F2', 'F3'):
        ks = [k for k, S in res['engines'].items() if S['family'] == f]
        np_ = sum(res['engines'][k]['verdict'] in ('PASS', 'PASS-WITH-FLAG') for k in ks)
        pend = [k for k in ks if res['engines'][k]['verdict'] in ('MISSING', 'INCOMPLETE')]
        fams[f] = dict(k=FAMILY_K[f], passed=np_, pending=pend,
                       action='forward demo RF ECN 3 months (6 with flag), forward gate t405-F written before start; real money = Nadav' if np_
                       else ('PENDING (incomplete engines)' if pend else 'KILL: ' + KILL_TEXT[f]))
    res['families'] = fams
    if not passed and not any(fams[f]['pending'] for f in fams):
        res['next_iteration'] = 't406 (separate PREREG): Gao, Han, Li & Zhou 2018 JFE intraday momentum (first half-hour predicts last) on USTECH/US500 in tester; Claude checks ledger first'
    with open(out_path, 'w', encoding='utf-8') as f: json.dump(res, f, ensure_ascii=False, indent=1, default=str)
    for k, S in res['engines'].items(): print(f"{k:11s} {S['family']} {S['verdict']:14s} {S.get('verdict_reason') or ''}")
    print(res['report_line']); print({f: v['action'][:60] for f, v in fams.items()})
    return res

# ------------------------------------------------------------------ synthetic self-test (fake data only)
def selftest():
    rnd = random.Random(405)
    tmp = tempfile.mkdtemp(prefix='t405_selftest_')
    spec = {'server_dst_check': 'EU DST (GMT+2/+3) verified', 'symbols': {
        '.US500Cash': dict(point=0.1, contract_size=1, tick_value=0.1, tick_size=0.1, spread_points=15, commission_per_lot_side=0.03, swap_mode=5, swap_long=-8.6, swap_short=-1.8, price=5000),
        '.USTECHCash': dict(point=0.1, contract_size=1, tick_value=0.1, tick_size=0.1, spread_points=8, commission_per_lot_side=0.03, swap_mode=5, swap_long=-8.6, swap_short=-1.8, price=18000),
        '.DE40Cash': dict(point=0.1, contract_size=1, tick_value=0.11, tick_size=0.1, spread_points=12, commission_per_lot_side=0.03, swap_mode=5, swap_long=-7.2, swap_short=-1.8, price=18000),
        'XAUUSD': dict(point=0.01, contract_size=100, tick_value=1, tick_size=0.01, spread_points=12, commission_per_lot_side=0.0, swap_mode=1, swap_long=-60, swap_short=19, price=3975),
        'EURUSD': dict(point=0.00001, contract_size=100000, tick_value=1, tick_size=0.00001, spread_NY_points=3, spread_LDN_points=2, commission_per_lot_side=2.0, swap_mode=1, swap_long=-9.8, swap_short=1.9, price=1.10),
        'GBPUSD': dict(point=0.00001, contract_size=100000, tick_value=1, tick_size=0.00001, spread_NY_points=9, spread_LDN_points=5, commission_per_lot_side=3.0, swap_mode=1, swap_long=-3.7, swap_short=-3.0, price=1.28)}}
    with open(os.path.join(tmp, 'spec_t405.json'), 'w') as f: json.dump(spec, f)
    summ = {'runs': {}, 'excluded': []}
    hdr = ['ts', 'deal', 'symbol', 'type', 'direction', 'volume', 'price', 'profit', 'commission', 'swap', 'balance', 'comment']
    def wcsv(name, header, rows):
        with open(os.path.join(tmp, name), 'w', newline='') as f:
            w = csv.writer(f); w.writerow(header); w.writerows(rows)
    for sym, px0, edge in (('EURUSD', 1.10, 0.0012), ('GBPUSD', 1.28, -0.0002)):
        for var in ('NY', 'LDN'):
            for y in YEARS:
                bal, deal, rows = DEP, 1, []
                d, last = date(y, 1, 2), (END if y == 2026 else date(y, 12, 31))
                while d <= last:
                    if d.weekday() < 5 and rnd.random() < 0.5:
                        side = rnd.choice(['buy', 'sell']); lots = round(bal * 1.5 / (px0 * 100000), 2)
                        p_in = px0 + rnd.gauss(0, 0.002); mv = rnd.gauss(edge, 0.004)
                        p_out = p_in + (mv if side == 'buy' else -mv)
                        prof = round((p_out - p_in) * (1 if side == 'buy' else -1) * lots * 100000, 2); com = -round(lots * 2.0, 2)
                        t_in = datetime(d.year, d.month, d.day, 16 if var == 'NY' else 10, 0, 5); t_out = t_in.replace(hour=22 if var == 'NY' else 17, second=0)
                        bal += com; rows.append([t_in.strftime('%Y.%m.%d %H:%M:%S'), deal, sym, side, 'in', lots, round(p_in, 5), 0, com, 0, round(bal, 2), '']); deal += 1
                        bal += prof + com; rows.append([t_out.strftime('%Y.%m.%d %H:%M:%S'), deal, sym, 'sell' if side == 'buy' else 'buy', 'out', lots, round(p_out, 5), prof, com, 0, round(bal, 2), '']); deal += 1
                    d += timedelta(days=1)
                wcsv(f'deals_{sym}_{var}_{y}.csv', hdr, rows)
                summ['runs'][f't405_{sym}_{var}_{y}'] = {'symbol': sym, 'variant': var, 'from': f'{y}.01.01', 'quality': f'real ticks {100 if y > 2020 else 99}%',
                                                         'ea_sha256': 'ec559f30' + '0' * 56, 'set_sha256': 'x', 'build': 5000, 'eq_dd': f'1000 ({rnd.uniform(3, 9):.2f}%)'}
    for base, sym, px0, vpp, drift in (('US500', '.US500Cash', 3200, 1.0, 0.0006), ('USTECH', '.USTECHCash', 8700, 1.0, 0.0001),
                                       ('DE40', '.DE40Cash', 13200, 1.1, 0.0002), ('XAUUSD', 'XAUUSD', 1520, 100.0, 0.0006)):
        px, bal, pos, avg, deal, rows, eqrows = px0, DEP, 0.0, 0.0, 1, [], []
        d = date(2020, 1, 2)
        while d <= END:
            if d.weekday() < 5:
                px *= 1 + rnd.gauss(drift, 0.011)
                eq = bal + (px - avg) * pos * vpp
                if d.weekday() in (0, 3):
                    t = datetime(d.year, d.month, d.day, 12).strftime('%Y-%m-%d %H:%M:%S')
                    want = round((1 if rnd.random() < 0.7 else -1) * 1.2 * eq / (px * vpp), 2)
                    if pos != 0 and (want > 0) != (pos > 0):        # flip: close fully first (hedging style)
                        prof = round((px - avg) * pos * vpp, 2); com = -round(abs(pos) * 0.03, 2); bal += prof + com
                        rows.append([t, deal, sym, 'sell' if pos > 0 else 'buy', 'out', abs(pos), round(px, 2), prof, com, 0, round(bal, 2), '']); deal += 1; pos = 0.0
                    dv = round(want - pos, 2)
                    if abs(dv) >= 0.01 and (pos == 0 or abs(dv) / abs(pos) > 0.3):
                        com = -round(abs(dv) * 0.03, 2)
                        if pos == 0 or (dv > 0) == (pos > 0):
                            bal += com; avg = (avg * abs(pos) + px * abs(dv)) / (abs(pos) + abs(dv)); pos = round(pos + dv, 2)
                            rows.append([t, deal, sym, 'buy' if dv > 0 else 'sell', 'in', abs(dv), round(px, 2), 0, com, 0, round(bal, 2), '']); deal += 1
                        else:
                            prof = round((px - avg) * (-dv) * vpp, 2); bal += prof + com; pos = round(pos + dv, 2)
                            rows.append([t, deal, sym, 'sell' if dv < 0 else 'buy', 'out', abs(dv), round(px, 2), prof, com, 0, round(bal, 2), '']); deal += 1
                eq = bal + (px - avg) * pos * vpp
                eqrows.append([d.isoformat(), round(bal, 2), round(eq, 2), round(eq - abs(pos) * px * vpp * abs(rnd.gauss(0, 0.004)), 2)])
            d += timedelta(days=1)
        wcsv(f'deals_{sym}_2020_2026.csv', hdr, rows)
        wcsv(f'equity_{sym}_daily.csv', ['date', 'balance', 'equity', 'equity_min'], eqrows)
        summ['runs'][f't405_{base}'] = {'symbol': sym, 'from': '2020.01.01', 'to': '2026.11.20', 'model': 4,
                                        'quality_by_year': {str(y): '100%' for y in YEARS}, 'ea_sha256': C1_EA_SHA, 'set_sha256': 'y', 'build': 5000}
    with open(os.path.join(tmp, 'summary.json'), 'w') as f: json.dump(summ, f)
    res = gate(tmp, os.path.join(tmp, 'RESULTS_t405_SELFTEST.json'))
    assert len(res['engines']) == 8 and all(S['verdict'] for S in res['engines'].values())
    assert res['engines']['GBPUSD_NY']['verdict'] == 'COST-EXCLUDED'          # 0.9 pip spread + 2*0.3 pip comm > 1.0 pip
    mk = lambda m, ty, dr, v, p, pr: dict(t=datetime(2024, 1, 1, 10, m), deal=m, type=ty, dir=dr, vol=v, price=p, profit=pr, comm=0, swap=0, fee=0, bal=None, i=m)
    P = process([mk(0, 'buy', 'in', 1.0, 100.0, 0), mk(10, 'buy', 'in', 1.0, 102.0, 0), mk(20, 'sell', 'inout', 3.0, 104.0, 600.0), mk(50, 'buy', 'out', 1.0, 103.0, 100.0)])
    assert len(P['episodes']) == 2 and P['stack_in'] == 1 and P['both_sides'] == 0 and all(abs(v - 100) < 1e-6 for v in P['vpps']), P['vpps']
    assert P['episodes'][0]['entry_vol'] == 2.0 and P['episodes'][1]['entry_vol'] == 1.0
    Q = process([mk(0, 'buy', 'in', 1.0, 100.0, 0), mk(5, 'sell', 'in', 1.0, 100.0, 0)])
    assert Q['both_sides'] == 1
    print('SELFTEST OK (synthetic data only):', tmp)
    return res

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument('--data', default=os.path.join(here, '..', 't405_tester'))
    ap.add_argument('--out', default=os.path.join(here, 'RESULTS_t405.json'))
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: selftest()
    elif not os.path.isdir(a.data): sys.exit(f'data dir not found: {a.data}')
    else: gate(a.data, a.out)
