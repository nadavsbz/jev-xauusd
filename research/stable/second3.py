"""Second component for C1, round 3: crypto hour-of-day (pre-registered 1.11.2026 in docs/STABLE_SYSTEM_PLAN.md).
Padysak & Vojtko (Quantpedia; Gemini 10.2015-2.2022): BTC's 22:00 and 23:00 UTC hours are the strongest; rule: buy 21:00 UTC,
sell 23:00 UTC. After their sample (3.2022-24.10.2025) is the test; 2018-2.2022 is a replication only.
  B1  long BTCUSD 21:00-23:00 UTC daily   B2  same on ETHUSD   B3  half B1 + half B2
RF server time = New York time + 7h (daily break of gold at server 00:00 = 17:00 NY), converted to UTC. Crypto trades 24/7 there,
so there is no reopen bar. Costs: median 2026 spread at entry and exit + one day of financing (the hold crosses server midnight).
Each scaled to 10% annual vol by its own lagged 90-day vol. Usage: python research/stable/second3.py [hold]"""
import sys
import numpy as np, pandas as pd
HOLD = len(sys.argv) > 1 and sys.argv[1] == "hold"; sys.argv = sys.argv[:1]
import second as S2
T = S2.T

def hours_utc(s, a, b):
    h = pd.read_csv(f"data/derived/intraday/{s}_H1.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
    u = (h.index - pd.Timedelta("7h")).tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT").tz_convert("UTC")
    h = h[~u.isna()]; u = u[~u.isna()]; h.index = u.tz_localize(None)
    x = h[(h.index.hour >= a) & (h.index.hour < b)]
    d = x.groupby(x.index.normalize()).agg(o=("open", "first"), c=("close", "last"), n=("close", "size"))
    d = d[d.n == b - a]
    return d.c / d.o - 1 - 2 * T.TC[s] - T.fin(s, 1) / 365

def scale_s(r):
    v = r.rolling(90, min_periods=60).std().shift(1) * np.sqrt(365)
    return r * (0.10 / v).clip(upper=5).fillna(0)

B1 = scale_s(hours_utc("BTCUSD", 21, 23)); B2 = scale_s(hours_utc("ETHUSD", 21, 23))
C = {"C1": S2.S["C1"]}
C["B1"] = B1.reindex(C["C1"].index).fillna(0); C["B2"] = B2.reindex(C["C1"].index).fillna(0); C["B3"] = (C["B1"] + C["B2"]) / 2

if __name__ == "__main__":
    for a, b, nm in ((("2025-10-25", "2026-10-30", "HOLDOUT"),) if HOLD else (("2018", "2022-02-28", "replication"), ("2022-03-01", "2025-10-24", "TEST"))):
        print(f"--- {nm} {a}..{b}")
        for k, x in C.items(): S2.rep(x, k, a, b)
        print("corr with C1:", {k: round(C["C1"].loc[a:b].corr(v.loc[a:b]), 2) for k, v in C.items() if k != "C1"})
        for k in ("B1", "B2", "B3"): S2.rep(C["C1"] + 0.5 * C[k], f"C1+0.5x{k}", a, b)
