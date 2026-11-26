#!/usr/bin/env python3
"""t407 STAGE 1 — source screen (PREREG_t407 §2, §3, §4, §4.1). Grok (המאסטרו), 26.11.2026.
Frozen PREREG sha256 aace08619f60729f7247a4d98b0bdebdd2aa5fd1efd1ac056b9d6ef068157765.
Stage 1 runs on the FULL tape (PREREG §3: "שלב 1 רץ על הטייפ כולו"). No stage 2, no features, no bars.

Interpretation choices fixed BEFORE running (all ASSUMED, written here so the sha pins them):
 A1 Position = same symbol+side tickets, chained: ticket joins current group if its open is <=2 min after
    the previous ticket of that group. Values lot-weighted (net pips/bp), hold = median of ticket holds.
 A2 Scale-in = a position opened while >=1 earlier same symbol+side position is still open (open<P.open<close).
    Averaging-down = scale-in whose price is worse than the lot-weighted avg entry of the open positions
    (buy: lower, sell: higher). Stack = number of open same-side positions incl. the new one.
 A3 Martingale 1a: per symbol, consecutive positions by open time; win/loss of previous = sign of source Profit sum.
 A4 Hold: ticket hold = close-open (minutes) from timestamps; if Duration column is 'Ns', use seconds.
 A5 FX recost PRIMARY (conservative, COST_PRESCREEN convention): net = Pips_IC_net - spread_table - comm + swap,
    spread_table = IC Raw night (entry 22:00-04:59 broker) / IC Raw day otherwise (the COST_PRESCREEN table,
    used there as RF-proxy); comm = 0.2bp RT of entry price in pips. Reason: the literal formula
    max(0, spread_RF - spread_IC) is degenerate because the table's RF proxy IS the IC Raw number (=> 0).
    SENSITIVITY (reported, not used for verdict): L0 literal-degenerate (spread add 0);
    L1 max(0, RF official 24h avg - IC Raw window spread).
 A6 Swap: no RF swap table in repo => swap derived from source Profit (PREREG §4.1 fallback). Per symbol,
    regress Profit/lots = k*move - c on tickets that do not cross broker 00:00; swap = residual on crossing
    tickets, converted to pips/bp via k. Non-crossing tickets: swap = 0.
 A7 Gold (S2): gross bp = sign*(close-open)/open*1e4 ; net = gross - 1.64 + swap_bp. Stress +$0.10/position.
 A8 Daily/yearly/quarterly aggregation by position CLOSE date (broker time), uniform size (1 unit/position).
 A9 1g S2 primary: all calendar quarters with >=1 closed position (literal); full-quarters-only reported.
 A10 1f: share = sum of top-10 daily net / total net; if total net <= 0 => FAIL.
"""
import json, hashlib, sys, re, os
import numpy as np, pandas as pd

SRC = '/workspace/t407/src'
OUT = '/workspace/t407/stage1'
FXBM = '/workspace/research_new_component/results_ferrari/fxbm_ic_raw_30d.json'
CS = '/workspace/research_new_component/results_ferrari/cost_screen.csv'
EXPECT = {'ferrari2009_history.csv': '111c627cc8846279838387cff4a29a09031e678bc5efb34b9d05dd260188db89',
          'goldreaper_history.csv': 'be5b30b2974e012e321e0032269a2de8137dace2740ba902dfc62647b4e5ce7c'}

def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()

def load(fn):
    p = os.path.join(SRC, fn); assert sha(p) == EXPECT[fn], 'sha mismatch ' + fn
    d = pd.read_csv(p, thousands=',', dtype={'Duration': str})
    d = d[d.Action.isin(['Buy', 'Sell'])].copy()
    d.columns = [c.split(' (')[0] for c in d.columns]
    d['o'] = pd.to_datetime(d['Open Date'], format='%m.%d.%Y %H:%M')
    d['c'] = pd.to_datetime(d['Close Date'], format='%m.%d.%Y %H:%M')
    d['side'] = np.where(d.Action == 'Buy', 1, -1)
    def hold(r):
        s = str(r.Duration).strip()
        if re.fullmatch(r'\d+s', s): return int(s[:-1]) / 60.0
        return (r.c - r.o).total_seconds() / 60.0
    d['hold_min'] = d.apply(hold, axis=1)
    d['cross'] = d.c.dt.normalize() > d.o.dt.normalize()
    def hassl(x):
        try: return abs(float(str(x).replace(',', ''))) > 0
        except: return False
    d['has_sl'] = d.SL.map(hassl)
    return d.sort_values('o').reset_index(drop=True)

def swap_fit(d, move):
    """A6: returns swap in move units per ticket."""
    out = pd.Series(0.0, index=d.index); info = {}
    for s, g in d.groupby('Symbol'):
        nc = g[~g.cross & (g.Lots > 0)]
        if len(nc) >= 5:
            y = nc.Profit / nc.Lots; X = np.c_[move[nc.index], np.ones(len(nc))]
            (k, b), *_ = np.linalg.lstsq(X, y, rcond=None)
        else: k, b = np.nan, 0.0
        cr = g[g.cross]
        if len(cr) and np.isfinite(k) and k > 0:
            resid = cr.Profit / cr.Lots - (k * move[cr.index] + b)
            out[cr.index] = resid / k
        info[s] = {'k_per_lot_per_unit': None if not np.isfinite(k) else round(float(k), 4),
                   'c_per_lot': round(float(-b), 4), 'n_fit': int(len(nc)), 'n_cross': int(len(cr)),
                   'mean_swap_units_cross': round(float(out[cr.index].mean()), 4) if len(cr) else 0.0}
    return out, info

def positions(d, netcols):
    rows = []
    for (s, sd), g in d.groupby(['Symbol', 'side']):
        g = g.sort_values('o'); gid = -1; last = None; ids = []
        for t in g.o:
            if last is None or (t - last).total_seconds() > 120: gid += 1
            ids.append(gid); last = t
        g = g.assign(gid=ids)
        for _, h in g.groupby('gid'):
            w = h.Lots / h.Lots.sum()
            r = {'Symbol': s, 'side': sd, 'o': h.o.min(), 'c': h.c.max(), 'lots': h.Lots.sum(),
                 'price': float((h['Open Price'] * w).sum()), 'hold': float(h.hold_min.median()),
                 'profit_src': float(h.Profit.sum()), 'n_tix': len(h), 'has_sl': bool(h.has_sl.all()),
                 'night': bool(h.night.iloc[0]) if 'night' in h else False}
            for c in netcols: r[c] = float((h[c] * w).sum())
            rows.append(r)
    P = pd.DataFrame(rows).sort_values('o').reset_index(drop=True)
    # A2 scale-in / averaging-down
    P['scalein'] = False; P['avgdown'] = False; P['stack'] = 1
    for (s, sd), g in P.groupby(['Symbol', 'side']):
        for i in g.index:
            op = g[(g.o < P.at[i, 'o']) & (g.c > P.at[i, 'o'])]
            if len(op):
                P.at[i, 'scalein'] = True; P.at[i, 'stack'] = len(op) + 1
                ref = (op.price * op.lots).sum() / op.lots.sum()
                P.at[i, 'avgdown'] = (P.at[i, 'price'] < ref) if sd == 1 else (P.at[i, 'price'] > ref)
    return P

def common_checks(P, net, stress, kind):
    R = {}
    # 1a
    ratios, up_loss, up_win, nl, nw = [], 0, 0, 0, 0
    for s, g in P.groupby('Symbol'):
        g = g.sort_values('o')
        for a, b in zip(g.itertuples(), list(g.itertuples())[1:]):
            r = b.lots / a.lots
            if a.profit_src < 0: ratios.append(r); nl += 1; up_loss += r > 1.0 + 1e-9
            elif a.profit_src > 0: nw += 1; up_win += r > 1.0 + 1e-9
    med = float(np.median(ratios)) if ratios else float('nan')
    pl = up_loss / nl if nl else 0; pw = up_win / nw if nw else 0
    R['1a'] = {'median_lot_ratio_after_loss': round(med, 4), 'pct_up_after_loss': round(pl, 4), 'pct_up_after_win': round(pw, 4),
               'n_after_loss': nl, 'n_after_win': nw, 'pass': bool(med <= 1.2 and pl <= pw + 0.10)}
    # 1b
    ad = float(P.avgdown.mean()); st = P.loc[P['stack'] > 1, 'stack']
    ms = float(st.median()) if len(st) else 1.0
    R['1b'] = {'pct_avgdown_positions': round(ad, 4), 'pct_scalein_positions': round(float(P.scalein.mean()), 4),
               'median_stack_when_stacked': ms, 'max_stack': int(P['stack'].max()), 'pass': bool(ad <= 0.20 and ms <= 3)}
    # 1c
    mh = float(P.hold.median()); s1 = float((P.hold < 1.0).mean())
    R['1c'] = {'median_hold_min': round(mh, 2), 'pct_hold_lt_1min': round(s1, 4), 'pass': bool(mh >= 15 and s1 <= 0.10)}
    # 1d
    thr = 4.0 if kind == 'fx' else 10.0
    m = float(P[net].mean())
    R['1d'] = {'mean_net_per_position': round(m, 4), 'unit': 'pips' if kind == 'fx' else 'bp', 'threshold': thr, 'pass': bool(m >= thr)}
    # 1e
    ssum = float(P[stress].sum())
    R['1e'] = {'sum_net_stress': round(ssum, 2), 'mean_net_stress': round(float(P[stress].mean()), 4), 'pass': bool(ssum > 0)}
    # 1f
    day = P.groupby(P.c.dt.date)[net].sum(); tot = float(day.sum())
    top = float(day.sort_values(ascending=False).head(10).sum())
    sh = top / tot if tot > 0 else float('inf')
    R['1f'] = {'total_net': round(tot, 2), 'top10_days_net': round(top, 2), 'share': round(sh, 4) if np.isfinite(sh) else None, 'pass': bool(tot > 0 and sh < 0.5)}
    # 1h
    R['1h'] = {'pct_positions_with_sl': round(float(P.has_sl.mean()), 4), 'report_only': True}
    return R

def sens_1d(P, cols, thr):
    return {c: {'mean': round(float(P[c].mean()), 4), 'pass_1d': bool(P[c].mean() >= thr)} for c in cols}

def run_s1():
    d = load('ferrari2009_history.csv')
    n_all = len(d)
    d = d[~d.Symbol.isin(['EURSGD', 'XAUUSD'])].copy()   # PREREG §4 universe
    fx = json.load(open(FXBM)); cs = pd.read_csv(CS)
    off = cs[(cs.account == 'Prime') & (cs.cost_case == 'official_avg_no_night_markup')].set_index('symbol').official_avg_spread_pips.to_dict()
    pipsz = np.where(d.Symbol.str.endswith('JPY'), 0.01, 0.0001)
    h = d.o.dt.hour; d['night'] = (h >= 22) | (h <= 4)
    night = d.Symbol.map(fx['night']); dayv = d.Symbol.map(fx['day'])
    missing = sorted(set(d.Symbol) - set(fx['night']))
    sp_tab = np.where(d.night, night, dayv)
    comm = 0.2e-4 * d['Open Price'] / pipsz
    swp, swinfo = swap_fit(d, d.Pips)
    # full RF spread for symbols without row (none expected) -> handled via NaN check
    assert not missing, missing
    d['net'] = d.Pips - sp_tab - comm + swp
    d['net_stress'] = d.net - 1.0
    d['net_L0'] = d.Pips - comm + swp
    rf_off = d.Symbol.map(off).astype(float)
    d['net_L1'] = d.Pips - np.maximum(0, rf_off - sp_tab) - comm + swp
    P = positions(d, ['net', 'net_stress', 'net_L0', 'net_L1'])
    R = common_checks(P, 'net', 'net_stress', 'fx')
    yr = P.groupby(P.c.dt.year)['net'].sum()
    full = {int(y): round(float(yr.get(y, 0.0)), 2) for y in range(2020, 2026)}
    npos = sum(v > 0 for v in full.values())
    y26 = float(yr.get(2026, 0.0)); y19 = float(yr.get(2019, 0.0))
    R['1g'] = {'net_by_year_pips_uniform': {int(k): round(float(v), 2) for k, v in yr.items()}, 'positive_full_years_2020_2025': f'{npos}/6',
               'ytd_2026': round(y26, 2), 'partial_2019': round(y19, 2), 'pass': bool(npos >= 5 and (y26 > 0 or y19 > 0))}
    R['sens_1d'] = sens_1d(P, ['net_L0', 'net_L1'], 4.0)
    R['meta'] = {'tickets_all': n_all, 'tickets_universe': len(d), 'positions': len(P), 'symbols': sorted(d.Symbol.unique().tolist()),
                 'pct_night_entries': round(float(d.night.mean()), 4), 'mean_spread_table_pips': round(float(np.mean(sp_tab)), 4),
                 'mean_comm_pips': round(float(comm.mean()), 4), 'mean_swap_pips_ticket': round(float(swp.mean()), 4),
                 'mean_Pips_IC_net_ticket': round(float(d.Pips.mean()), 4), 'swap_fit': swinfo,
                 'by_symbol_mean_net': P.groupby('Symbol')['net'].agg(['count', 'mean']).round(3).reset_index().to_dict('records')}
    return R, P

def run_s2():
    d = load('goldreaper_history.csv'); d['night'] = False
    move = d.side * (d['Close Price'] - d['Open Price'])
    d['gross_bp'] = move / d['Open Price'] * 1e4
    swp, swinfo = swap_fit(d, move)
    d['swap_bp'] = swp / d['Open Price'] * 1e4
    d['net'] = d.gross_bp - 1.64 + d.swap_bp
    d['net_stress'] = d.net - 0.10 / d['Open Price'] * 1e4
    d['net_noswap'] = d.gross_bp - 1.64
    P = positions(d, ['net', 'net_stress', 'net_noswap', 'gross_bp'])
    R = common_checks(P, 'net', 'net_stress', 'gold')
    q = P.groupby(P.c.dt.to_period('Q'))['net'].sum()
    first, last = P.c.min(), P.c.max()
    fullq = q[[ (p.start_time >= first.normalize() - pd.Timedelta(days=0)) and (p.end_time <= last) for p in q.index]]
    fullq = q[[p.start_time >= first and p.end_time <= last for p in q.index]]
    pq = float((q > 0).mean()); pfq = float((fullq > 0).mean()) if len(fullq) else float('nan')
    R['1g'] = {'net_by_quarter_bp_uniform': {str(k): round(float(v), 1) for k, v in q.items()}, 'pct_positive_quarters_all': round(pq, 4),
               'n_quarters_all': int(len(q)), 'pct_positive_full_quarters_only': round(pfq, 4), 'n_full_quarters': int(len(fullq)), 'pass': bool(pq >= 0.70)}
    R['sens_1d'] = sens_1d(P, ['net_noswap', 'gross_bp'], 10.0)
    R['meta'] = {'tickets': len(d), 'positions': len(P), 'mean_gross_bp_ticket': round(float(d.gross_bp.mean()), 4),
                 'mean_gross_bp_position': round(float(P.gross_bp.mean()), 4), 'mean_swap_bp_ticket': round(float(d.swap_bp.mean()), 4),
                 'pct_cross_rollover': round(float(d.cross.mean()), 4), 'swap_fit': swinfo,
                 'mean_tickets_per_position': round(float(P.n_tix.mean()), 3)}
    return R, P

def verdict(R):
    keys = ['1a', '1b', '1c', '1d', '1e', '1f', '1g']
    fails = [k for k in keys if not R[k]['pass']]
    return ('PASS' if not fails else 'KILL'), fails

if __name__ == '__main__':
    self_sha = sha(__file__)
    res = {'script_sha256': self_sha, 'prereg_sha256': sha('/workspace/t407/out/PREREG_t407.md'),
           'inputs': EXPECT, 'scope': 'full tape (PREREG §3)'}
    for name, fn in [('S1_Ferrari2009', run_s1), ('S2_GoldReaper', run_s2)]:
        R, P = fn(); v, f = verdict(R); R['verdict'] = v; R['failed_checks'] = f; res[name] = R
        P.to_csv(os.path.join(OUT, f'positions_{name}.csv'), index=False)
    json.dump(res, open(os.path.join(OUT, 'RESULTS_t407_stage1.json'), 'w'), indent=1, default=str, ensure_ascii=False)
    print(json.dumps(res, indent=1, default=str, ensure_ascii=False))
