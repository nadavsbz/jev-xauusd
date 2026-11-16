"""Round 86 (prereg docs/prereg/r86_bd_user_settings_hold.md): user's live settings in the tester vs candidate vs live crash days, 27.10.2025-30.10.2026.
Usage: py -3.12 research/bd1/r86_compare.py"""
import sys, os, pandas as pd
sys.path.insert(0, 'research/btc'); sys.path.insert(0, 'research/stable')
from guardian_sim import deals
LIVE = ['2026-05-28', '2026-06-05', '2026-07-01', '2026-07-30', '2026-08-10', '2026-08-27', '2026-10-12']
RUNS = {'U-RF': 'ev86_rf_hold_user', 'U-C': 'ev86_c_hold_user', 'cand': 'ev14_rf_hold_ms20_h1119'}
for k, f in RUNS.items():
    p = f"C:/MT5_JEV_TEST/{f}.htm"
    if not os.path.exists(p): print(k, 'missing'); continue
    x = deals(p); x['day'] = pd.to_datetime(x.t, unit='s').dt.normalize(); x['net'] = x.profit + x.swap + x.commission
    d = x.groupby('day').net.sum(); eq = 120000 + d.cumsum(); r = d / eq.shift(1).fillna(120000)
    cut = r[r < -0.02]
    print(f"\n{k}: return {(eq.iloc[-1] / 120000 - 1) * 100:+.0f}%  cuts {len(cut)}  closed-MDD {((eq / eq.cummax()) - 1).min() * 100:.0f}%")
    for dd, v in cut.items(): print(f"   cut {dd.date()} {dd.day_name()[:3]} {v * 100:+.1f}%")
    hit = [l for l in LIVE if any(abs((c - pd.Timestamp(l)).days) <= 1 for c in cut.index)]
    print(f"   live crash days matched (+-1d): {len(hit)}/{len(LIVE)} {hit}")
