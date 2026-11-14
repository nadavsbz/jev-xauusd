"""Growth search round 2 (pre-registered 3.11.2026 in docs/GROWTH_SEARCH_PLAN.md), same bar as round 1:
  CX1 BTCUSD noise area anchored 16   CX2 ETHUSD anchored 16   CX3 BTCUSD anchored 10 (exit at the bar-22 close, no swap)
  R1/R2 Connors RSI(2) on .USTECHCash / .US500Cash: buy at the 22:00 close when RSI(2) < 10 and close > SMA200, out when
  close > SMA5; 0.015% per side, swap 8.6%/yr per calendar day held. Usage: python research/growth/grow2.py [hold]"""
import sys
import numpy as np, pandas as pd
HOLD = len(sys.argv) > 1 and sys.argv[1] == "hold"
sys.argv = sys.argv[:1]; sys.path.insert(0, "research/stable"); sys.path.insert(0, "research/growth")
import second4 as S4
import noise_more as N
S2 = S4.S2

def rsi2(s):
    h = N.bars(s); c = h.close[h.index.hour == 22]; c.index = c.index.normalize()
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1 / 2, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / 2, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn); m200 = c.rolling(200).mean(); m5 = c.rolling(5).mean()
    pos = pd.Series(0, index=c.index); q = 0
    for t in c.index:
        if q == 0 and rsi[t] < 10 and c[t] > m200[t]: q = 1
        elif q == 1 and c[t] > m5[t]: q = 0
        pos[t] = q
    held = pos.shift(1).fillna(0); days = pd.Series(c.index, index=c.index).diff().dt.days.fillna(1)
    return held * c.pct_change().fillna(0) - held * days * 0.086 / 365 - pos.diff().abs().fillna(0) * 0.00015

COMP = {"CX1": lambda: N.strat("BTCUSD", 16, 21, 22), "CX2": lambda: N.strat("ETHUSD", 16, 21, 22),
        "CX3": lambda: N.strat("BTCUSD", 10, 21, 22), "R1": lambda: rsi2(".USTECHCash"), "R2": lambda: rsi2(".US500Cash")}

if __name__ == "__main__":
    base = S4.C["C1"] + S4.C["I2"]; idx = base.index; sh = N.sharpe
    a, b = ("2025-10-25", "2026-10-30") if HOLD else ("2018", "2025-10-24")
    print(f"--- {'HOLDOUT' if HOLD else 'EXPLORATION'} {a}..{b}"); S2.rep(base, "C1+I2", a, b)
    for nm, f in COMP.items():
        if HOLD and nm not in sys.argv[1:] and len(sys.argv) > 1: continue
        x = S4.scale_s(f()).reindex(idx).fillna(0); xs = x.loc[a:b]
        y = xs.groupby(xs.index.year).apply(lambda z: (1 + z).prod() - 1); lift = sh((base + 0.5 * x).loc[a:b]) - sh(base.loc[a:b])
        S2.rep(x, nm, a, b); S2.rep(base + 0.5 * x, f"  +0.5x{nm}", a, b)
        print(f"     corr C1 {S4.C['C1'].loc[a:b].corr(xs):+.2f} I2 {S4.C['I2'].loc[a:b].corr(xs):+.2f} | lift {lift:+.2f} | "
              f"pass: Sh {sh(xs) >= 0.5} years {(y > 0).mean() >= 0.6} lift {lift >= 0.1}")
