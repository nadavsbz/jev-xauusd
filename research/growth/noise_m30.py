"""I2 on M30 bars as in the paper (pre-registered 3.11.2026 in docs/GROWTH_SEARCH_PLAN.md). Server = NY + 7:
O = open of the 16:30 bar (NY 9:30); checks at the bar closes 17:00..22:30 (NY 10:00..15:30); flat at the 23:00 close (NY 16:00).
sigma_k = mean |close_k/O - 1| over the prior 14 days per check time; bands as I2 (max/min of O and the prior day's last close).
  M1  the I2 rule on M30          M2  M1 + the paper's VWAP stop (long out below max(upper, VWAP), short out above min(lower, VWAP))
Costs as I2 (0.015% per change). Usage: python research/growth/noise_m30.py [hold]"""
import sys
import numpy as np, pandas as pd
HOLD = len(sys.argv) > 1 and sys.argv[1] == "hold"
sys.argv = sys.argv[:1]; sys.path.insert(0, "research/stable"); sys.path.insert(0, "research/growth")
import second4 as S4
import noise_more as N
S2 = S4.S2
A = 16 * 60 + 30; CHK = list(range(17 * 60, 23 * 60, 30)); EX = 23 * 60     # minutes of the day at bar CLOSE

def strat(s, vwap=False, lb=14):
    h = pd.read_csv(f"data/derived/intraday/{s}_M30.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
    m = h.index.hour * 60 + h.index.minute + 30                                    # close minute of each bar
    sel = (m > A) & (m <= EX); d = h.index.normalize()
    O = h.open[m == A + 30]; O.index = O.index.normalize()
    piv = lambda col: pd.DataFrame({"v": col[sel], "d": d[sel], "k": m[sel]}).pivot_table(index="d", columns="k", values="v")
    Cl = piv(h.close).dropna(); Cl = Cl[Cl.index.isin(O.index)]; o = O.reindex(Cl.index)
    tp = (h.high + h.low + h.close) / 3; V = piv(h.tick_volume.astype(float)).reindex(Cl.index); PV = piv(tp * h.tick_volume).reindex(Cl.index)
    VW = PV.cumsum(1) / V.cumsum(1)
    prev = Cl[EX].shift(1); sig = Cl[CHK].div(o, axis=0).sub(1).abs().rolling(lb).mean().shift(1)
    up = pd.concat([o, prev], axis=1).max(1); lo = pd.concat([o, prev], axis=1).min(1); tc = N.cost(s)
    out = pd.Series(0.0, index=Cl.index)
    for day in Cl.index[16:]:
        if np.isnan(prev[day]) or sig.loc[day].isna().any(): continue
        q = 0; r = 0.0; last = None
        for k in CHK + [EX]:
            c = Cl.at[day, k]
            if last is not None and q != 0: r += q * (c / last - 1)
            last = c
            if k == EX: nq = 0
            else:
                U = up[day] * (1 + sig.at[day, k]); L = lo[day] * (1 - sig.at[day, k])
                if vwap: w = VW.at[day, k]; U, L = max(U, w), min(L, w)     # the stop level is also the (re-)entry level
                nq = 1 if c > U else (-1 if c < L else 0)
            r -= abs(nq - q) * tc; q = nq
        out[day] = r
    return out

if __name__ == "__main__":
    a, b = ("2025-10-25", "2026-10-30") if HOLD else ("2018", "2025-10-24")
    C1, I2 = S4.C["C1"], S4.C["I2"]; idx = C1.index
    print(f"--- {'HOLDOUT' if HOLD else 'EXPLORATION'} {a}..{b}")
    S2.rep(I2, "I2 (H1)", a, b); S2.rep(C1 + I2, "C1+I2", a, b)
    for s in (".USTECHCash", ".US500Cash"):
        for nm, vw in (("M1", False), ("M2", True)):
            x = S4.scale_s(strat(s, vw)).reindex(idx).fillna(0)
            S2.rep(x, f"{nm} {s[1:4]}", a, b)
            if s == ".USTECHCash":
                S2.rep(C1 + x, f"  C1+{nm}", a, b); print(f"     corr with I2 {x.loc[a:b].corr(I2.loc[a:b]):+.2f}")
