"""I2 base (in2dst_t_YYYY) vs IndexNoiseTP TPPct=1.25 (in2tp125_t_YYYY), RF-ECN real ticks, one tester run a year, 120K deposit.
Usage: py -3.12 research/stable/i2_tp_tester_cmp.py"""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals

def daily(tag):
    out, yr = [], {}
    for y in range(2018, 2027):
        f = f"C:/MT5_JEV_TEST/{tag}_{y}.htm"
        if not os.path.exists(f): continue
        x = deals(f); x = x[x.symbol == ".USTECHCash"]
        x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize()
        pnl = (x.profit + x.swap + x.commission).groupby(x.day).sum()
        eq = 120000 + pnl.cumsum(); r = pnl / eq.shift(1).fillna(120000); out.append(r)
        yr[y] = round(pnl.sum() / 1200, 1); yr[f"n{y}"] = int((x.profit != 0).sum())
    return pd.concat(out) if out else pd.Series(dtype=float), yr

for tag in ("in2dst_t", "in2tp125_t"):
    r, yr = daily(tag)
    if not len(r): print(tag, "no reports"); continue
    eq = (1 + r).cumprod(); dd = (eq / eq.cummax() - 1).min()
    print(f"{tag:12s} Sh {r.mean()/r.std()*np.sqrt(252):.2f}  MDD {dd*100:.1f}%  years % {{{', '.join(f'{k}:{v}' for k, v in yr.items() if not str(k).startswith('n'))}}}")
    print("             closes per year", {k[1:]: v for k, v in yr.items() if str(k).startswith('n')})
