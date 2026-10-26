"""Gold return by hour of day (UTC) and weekday, per period: is there a drift that repeats every year? (docs/HYBRID_PLAN.md, step 0)
Broker clock -> UTC: RoboForex UTC+2 / +3 in US daylight saving, EGlobal UTC+2 (research/bd1/news_files.py).
Usage: python research/hybrid/hour_drift.py"""
import glob, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/bd1"); from news_files import us_dst

out = {}
for f in sorted(glob.glob("data/derived/crash_signs/bars_*_PERIOD_M15.csv")):
    p = f.split("bars_")[1].split("_")[0]
    b = pd.read_csv(f); ts = pd.to_datetime(b.time, unit="s")
    off = np.where([p.startswith("rf") and us_dst(t) for t in ts], 3, 2)
    utc = ts - pd.to_timedelta(off, unit="h")
    r = np.log(b.close).diff().values; r[np.abs(r) > 0.03] = np.nan
    d = pd.DataFrame({"h": utc.dt.hour, "wd": utc.dt.dayofweek, "r": r * 1e4})   # basis points
    out[p] = d
def table(key, label):
    rows = {}
    for p, d in out.items():
        g = d.groupby(key).r; s = g.sum() / (d.groupby(d.index // 96).ngroups) * 1  # unused
        m = g.mean(); se = g.std() / np.sqrt(g.count())
        rows[p] = (g.sum() / len(set((d.index // 96)))).round(2)   # avg bp per day contributed by that bucket ~ sum/days
        rows[p + "_t"] = (m / se).round(1)
    t = pd.DataFrame(rows); t["same_sign"] = (np.sign(t[[p for p in out]]).sum(axis=1)).astype(int)
    print(label); print(t.to_string()); print()
table("h", "bp per day from each UTC hour (sum of returns / days) and t-stat")
table("wd", "weekday (0=Mon)")
