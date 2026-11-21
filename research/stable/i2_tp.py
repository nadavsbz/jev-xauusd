"""Descriptive (user question 14.11): I2 with a fixed take-profit in index points (100..300) checked on H1 high/low; after a TP
the day stays flat. Same costs and vol target as second4. Usage: py -3.12 research/stable/i2_tp.py"""
import sys
import numpy as np, pandas as pd
sys.argv = sys.argv[:1]; sys.path.insert(0, "research/stable")
import second4 as S4
S2 = S4.S2; CHK, EXIT, E = S4.CHK, S4.EXIT, S4.E

def strat_tp(s, TP, lb=14):
    h = pd.read_csv(f"data/derived/intraday/{s}_H1.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
    tc = max(float(E.loc[s, "med_spread_2026"]), 0.0001) + 0.00005
    w = h[(h.index.hour >= 16) & (h.index.hour <= EXIT)].copy(); w["d"] = w.index.normalize(); w["k"] = w.index.hour
    P = {c: w.pivot_table(index="d", columns="k", values=c) for c in ("close", "high", "low")}
    Cl = P["close"].dropna(); Hi = P["high"].reindex(Cl.index); Lo = P["low"].reindex(Cl.index)
    O = h.open[h.index.hour == 16]; O.index = O.index.normalize(); Cl = Cl[Cl.index.isin(O.index)]; o = O.reindex(Cl.index)
    prev = Cl[EXIT].shift(1); sig = Cl[CHK].div(o, axis=0).sub(1).abs().rolling(lb).mean().shift(1)
    up = pd.concat([o, prev], axis=1).max(1); lo = pd.concat([o, prev], axis=1).min(1)
    out = pd.Series(0.0, index=Cl.index); ntp = 0
    for d in Cl.index[16:]:
        if np.isnan(prev[d]) or sig.loc[d].isna().any(): continue
        q = 0; r = 0.0; last = None; e = None; done = False
        for k in CHK + [EXIT]:
            c = Cl.at[d, k]
            if q != 0 and last is not None:
                tgt = e + q * TP if TP else None
                if tgt is not None and ((q > 0 and Hi.at[d, k] >= tgt) or (q < 0 and Lo.at[d, k] <= tgt)):
                    r += q * (tgt / last - 1) - tc; q = 0; done = True; ntp += 1; last = c; continue
                r += q * (c / last - 1)
            last = c
            if k == EXIT or done: nq = 0
            else:
                U = up[d] * (1 + sig.at[d, k]); L = lo[d] * (1 - sig.at[d, k])
                nq = 1 if c > U else (-1 if c < L else 0)
            if nq != q:
                r -= abs(nq - q) * tc
                if nq != 0 and (q == 0 or np.sign(nq) != np.sign(q)): e = c
            q = nq
        out[d] = r
    return out, ntp

if __name__ == "__main__":
    for a, b, nm in (("2018", "2025-10-24", "EXPLORATION"), ("2025-10-25", "2026-10-30", "HOLDOUT (descriptive)")):
        print("---", nm)
        for TP in (None, 100, 150, 200, 250, 300):
            r, n = strat_tp(".USTECHCash", TP); x = S4.scale_s(r).reindex(S4.C["C1"].index).fillna(0)
            S2.rep(x, f"TP {TP or 'none'} (hits {n})", a, b)
