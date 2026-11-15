"""Round 54 (user's idea, fixed in advance, no tuning): x2 book in two separate accounts (C1 x2 = AssetVol 0.30/TV 0.40/MG 6,
I2 x2 = TargetVol 0.30), each with an external equity guard at -22% from its own peak (daily closes; intraday breach is
worse in reality). Variants fixed before running:
  G0 no guard;  G1 guard hit -> account flat forever;  G2 guard hit -> flat until the next month start, then restart with the
  peak reset to the equity at restart (like the BD guard: protection, then resume).
Pass if G1 or G2 keeps book >=3%/mo AND each account MDD <=25% AND book MDD <=20%.
Usage: py -3.12 research/stable/r54_guard22.py"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); sys.path.insert(0, "research/stable")
from x2_check import i2, c
from book_tester import show

def guard(r, lim=0.22, mode=1):
    eq, pk, off, out, hits, mon = 1.0, 1.0, False, [], 0, None
    for d, x in r.items():
        if off:
            if mode == 2 and d.month != mon: off, pk = False, eq
            else: out.append(0.0); continue
        out.append(x); eq *= 1 + x; pk = max(pk, eq)
        if eq / pk - 1 <= -lim: off, mon, hits = True, d.month, hits + 1
    return pd.Series(out, index=r.index), hits

if __name__ == "__main__":
    C = c("c1_ecn_av30_tv40_mg6_full"); I = i2("in2dst_tv30_t").reindex(C.index).fillna(0)
    for name, m in [("G0", 0), ("G1", 1), ("G2", 2)]:
        if m: (cg, hc), (ig, hi) = guard(C, mode=m), guard(I, mode=m)
        else: cg, ig, hc, hi = C, I, 0, 0
        print(f"--- {name}  hits C1 {hc}  I2 {hi}")
        show(cg, f"{name} C1 x2 account"); show(ig, f"{name} I2 x2 account"); show(0.5 * cg + 0.5 * ig, f"{name} book")
