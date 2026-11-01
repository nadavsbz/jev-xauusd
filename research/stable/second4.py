"""Second component for C1, round 4: intraday index momentum (pre-registered 1.11.2026 in docs/STABLE_SYSTEM_PLAN.md).
Zarattini, Aziz & Barbon (2024, SSRN 4824172) 'noise area' breakout on SPY, adapted to RoboForex-ECN H1 bars (server = NY + 7h):
O = open of the server 16:00 bar (NY 9:00); checks at the closes of bars 16..21 (NY 10:00..15:00); flat at the bar-22 close
(NY 16:00), so no overnight swap. sigma_k = mean |close_k/O - 1| over the prior 14 days for check hour k;
upper = max(O, prev close) x (1 + sigma_k), lower = min(O, prev close) x (1 - sigma_k); long above upper, short below lower,
out when back inside. Cost per change: max(2026 median spread, 0.01%) + 0.005% commission (ASSUMED). 10% vol target.
  I1 US500   I2 USTECH   I3 mean of US500, USTECH, US30.   Usage: python research/stable/second4.py [hold]"""
import sys
import numpy as np, pandas as pd
HOLD = len(sys.argv) > 1 and sys.argv[1] == "hold"; sys.argv = sys.argv[:1]
import second as S2
E = pd.read_csv("data/derived/ecn_costs_20261030.csv").set_index("symbol")
CHK = list(range(16, 22)); EXIT = 22

def strat(s):
    h = pd.read_csv(f"data/derived/intraday/{s}_H1.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
    tc = max(float(E.loc[s, "med_spread_2026"]), 0.0001) + 0.00005
    day = h.index.normalize()
    O = h.open[h.index.hour == 16]; O.index = O.index.normalize()
    Cl = h.close[(h.index.hour >= 16) & (h.index.hour <= EXIT)].copy()
    Cl = Cl.to_frame("c").assign(d=day[(h.index.hour >= 16) & (h.index.hour <= EXIT)], k=Cl.index.hour).pivot_table(index="d", columns="k", values="c")
    Cl = Cl.dropna(); Cl = Cl[Cl.index.isin(O.index)]; o = O.reindex(Cl.index)
    prev = Cl[EXIT].shift(1)
    mv = Cl[CHK].div(o, axis=0).sub(1).abs(); sig = mv.rolling(14).mean().shift(1)
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
                U = up[d] * (1 + sig.at[d, k]); L = lo[d] * (1 - sig.at[d, k])
                nq = 1 if c > U else (-1 if c < L else 0)
            r -= abs(nq - q) * tc; q = nq
        out[d] = r
    return out

def scale_s(r):
    v = r.rolling(90, min_periods=60).std().shift(1) * np.sqrt(260)
    return r * (0.10 / v).clip(upper=5).fillna(0)

C = {"C1": S2.S["C1"]}
raw = {s: strat(s) for s in (".US500Cash", ".USTECHCash", ".US30Cash")}
C["I1"] = scale_s(raw[".US500Cash"]); C["I2"] = scale_s(raw[".USTECHCash"]); C["I3"] = scale_s(pd.DataFrame(raw).fillna(0).mean(1))
for k in ("I1", "I2", "I3"): C[k] = C[k].reindex(C["C1"].index).fillna(0)

if __name__ == "__main__":
    for a, b, nm in ((("2025-10-25", "2026-10-30", "HOLDOUT"),) if HOLD else (("2018", "2025-10-24", "EXPLORATION"), ("2024-06-01", "2025-10-24", "after publication"))):
        print(f"--- {nm} {a}..{b}")
        for k, x in C.items(): S2.rep(x, k, a, b)
        print("corr with C1:", {k: round(C["C1"].loc[a:b].corr(v.loc[a:b]), 2) for k, v in C.items() if k != "C1"})
        for k in ("I1", "I2", "I3"): S2.rep(C["C1"] + 0.5 * C[k], f"C1+0.5x{k}", a, b)
