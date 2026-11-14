"""Scan round 15 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 night): CITSM - the US500 last half-hour (M5 bars 22:30 open ->
22:55 close server; 21:30 -> 21:55 in DST-mismatch weeks) predicts DE40's first half-hour next trading day (10:00 open -> 10:25
close server = 09:00-09:30 Frankfurt). Cost = DE40's yearly median spread (server hours 10-17) + 0.0015% per side.
Usage: python research/scan/citsm.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
from scan2 import mismatch
from last_half import m5
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"

if __name__ == "__main__":
    span = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    us, de = m5("US500Cash"), m5("DE40Cash")
    xd = de[(de.index.hour >= 10) & (de.index.hour <= 17)]
    cost = (xd.spread * 0.1 / xd.close).groupby(xd.index.year).median() + 0.000015
    sig = {}
    for d, x in us.groupby(us.index.normalize()):
        k = 1 if mismatch(d) else 0; a, b = d + pd.Timedelta(hours=22 - k, minutes=30), d + pd.Timedelta(hours=22 - k, minutes=55)
        if a in x.index and b in x.index: sig[d] = np.sign(x.loc[b, "close"] / x.loc[a, "open"] - 1)
    sig = pd.Series(sig)
    out, gross = {}, {}
    for d, x in de.groupby(de.index.normalize()):
        if d.dayofweek >= 5: continue
        prev = sig[sig.index < d]
        if not len(prev) or (d - prev.index[-1]).days > 4: continue
        a, b = d + pd.Timedelta(hours=10), d + pd.Timedelta(hours=10, minutes=25)
        if a not in x.index or b not in x.index: continue
        q = prev.iloc[-1]; g = q * (x.loc[b, "close"] / x.loc[a, "open"] - 1)
        gross[d] = g; out[d] = g - 2 * cost.get(d.year, cost.iloc[-1]) * (q != 0)
    raw, g = pd.Series(out), pd.Series(gross)
    x = scale(raw); x.to_csv("data/derived/scan/R15_citsm_daily.csv", header=["ret"])
    print(f"===== round 15 CITSM US500 last half -> DE40 first half {PER} {span}; DE40 cost/side bp {(cost * 1e4).round(2).to_dict()}")
    rep(x.loc[span[0]:span[1]], "CITSM")
    y, gy = raw.loc[span[0]:span[1]], g.loc[span[0]:span[1]]
    print(f"    days {len(y)}, mean net {y.mean() * 1e4:.2f} bp, gross {gy.mean() * 1e4:.2f} bp, hit {(y > 0).mean() * 100:.0f}%, gross by year {gy.groupby(gy.index.year).mean().mul(1e4).round(1).to_dict()}")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([x, i2, c1], axis=1, keys=["CI", "I2", "C1"]).loc[span[0]:span[1]].dropna(subset=["CI"]).fillna(0)
    print("corr:", j.corr().round(2).loc["CI"].to_dict())
