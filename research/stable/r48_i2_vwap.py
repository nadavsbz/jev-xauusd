"""Round 48 of docs/SCAN_PLAN.md (pre-registered 14.11.2026): I2 (second4.strat on .USTECHCash) + the paper's VWAP trailing stop.
Usage: py -3.12 research/stable/r48_i2_vwap.py [hold]"""
import sys
import numpy as np, pandas as pd
HOLD = len(sys.argv) > 1 and sys.argv[1] == "hold"; sys.argv = sys.argv[:1]
sys.path.insert(0, "research/stable")
import second4 as S4
S2 = S4.S2; CHK, EXIT, E = S4.CHK, S4.EXIT, S4.E

def strat_v(s, lb=14):
    h = pd.read_csv(f"data/derived/intraday/{s}_H1.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
    tc = max(float(E.loc[s, "med_spread_2026"]), 0.0001) + 0.00005
    w = h[(h.index.hour >= 16) & (h.index.hour <= EXIT)].copy(); w["d"] = w.index.normalize(); w["k"] = w.index.hour
    w["tp"] = (w.high + w.low + w.close) / 3; w["pv"] = w.tp * w.tick_volume.clip(lower=1)
    w["vw"] = w.groupby("d").pv.cumsum() / w.groupby("d").tick_volume.apply(lambda x: x.clip(lower=1).cumsum()).values
    Cl = w.pivot_table(index="d", columns="k", values="close").dropna(); VW = w.pivot_table(index="d", columns="k", values="vw").reindex(Cl.index)
    O = h.open[h.index.hour == 16]; O.index = O.index.normalize(); Cl = Cl[Cl.index.isin(O.index)]; o = O.reindex(Cl.index)
    prev = Cl[EXIT].shift(1)
    sig = Cl[CHK].div(o, axis=0).sub(1).abs().rolling(lb).mean().shift(1)
    up = pd.concat([o, prev], axis=1).max(1); lo = pd.concat([o, prev], axis=1).min(1)
    out = pd.Series(0.0, index=Cl.index)
    for d in Cl.index[16:]:
        if np.isnan(prev[d]) or sig.loc[d].isna().any(): continue
        q = 0; r = 0.0; last = None
        for k in CHK + [EXIT]:
            c = Cl.at[d, k]
            if last is not None and q != 0: r += q * (c / last - 1)
            last = c
            if k == EXIT: nq = 0
            else:
                U = up[d] * (1 + sig.at[d, k]); L = lo[d] * (1 - sig.at[d, k]); v = VW.at[d, k]
                nq = 1 if (c > U and c > v) else (-1 if (c < L and c < v) else 0)
            r -= abs(nq - q) * tc; q = nq
        out[d] = r
    return out

if __name__ == "__main__":
    base = S4.C["I2"]; v = S4.scale_s(strat_v(".USTECHCash")).reindex(base.index).fillna(0)
    a, b = ("2025-10-25", "2026-10-30") if HOLD else ("2018", "2025-10-24")
    print("---", "HOLDOUT" if HOLD else "EXPLORATION", a, b)
    S2.rep(base, "I2 base", a, b); S2.rep(v, "48a VWAP", a, b)
    print("corr", round(base.loc[a:b].corr(v.loc[a:b]), 2))
