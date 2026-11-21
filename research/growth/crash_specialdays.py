"""Crash days: Lars' rule from the Telegram group (data/raw/telegram/toptarget/lars, 2025-08-19 / 08-22 / 08-28):
do not start Black Dragon on special days (NFP, FOMC, CPI, US election, Jackson Hole, last Friday of the month).
Screen on the clone's baskets (not a tester run): baskets opened on such a day (server date) vs all other baskets -
cuts per 1000 baskets and the net P&L the day type carries per period. If the day type's net is < 0 in most periods,
dropping it would have helped [static: later baskets would change too]. Usage: python research/growth/crash_specialdays.py DIR_WITH_oos_b.csv"""
import sys, pandas as pd, numpy as np
from zoneinfo import ZoneInfo
S = sys.argv[1]
B = pd.concat([pd.read_csv("data/derived/crash_signs/baskets.csv"), pd.read_csv(S + "/oos_b.csv")]).drop_duplicates(["report", "side", "t0"])
B["day"] = pd.to_datetime(B.t0, unit="s").dt.normalize()
c = pd.read_csv("data/derived/news/mt5_calendar_usd.csv")
c["day"] = pd.to_datetime(c.time, unit="s", utc=True).dt.tz_convert(ZoneInfo("Europe/Athens")).dt.tz_localize(None).dt.normalize()
def days(*names): return set(c[c.event.isin(names)].day)
D = {"NFP": days("Nonfarm Payrolls"), "FOMC": days("Fed Interest Rate Decision"), "CPI": days("CPI m/m", "CPI y/y", "Core CPI m/m"),
     "PCE": days("Core PCE Price Index m/m"), "GDP": days("GDP q/q"),
     "Powell": days("Fed Chair Powell Speech", "Fed Chair Powell Testimony"),
     "election": {pd.Timestamp(d) for d in ("2020-11-03", "2020-11-04", "2024-11-05", "2024-11-06")}}
D["JacksonHole"] = {d for d in D["Powell"] if d.month == 8 and d.day >= 20}
allday = pd.date_range("2018-01-01", "2026-12-31", freq="D")
D["lastFri"] = {d for d in allday if d.weekday() == 4 and (d + pd.Timedelta(days=7)).month != d.month}
D["Lars_all"] = set().union(D["NFP"], D["FOMC"], D["election"], D["JacksonHole"], D["lastFri"])
D["all_top"] = set().union(*[D[k] for k in ("NFP", "FOMC", "CPI", "PCE", "GDP", "Powell", "election", "lastFri")])
B["cut"] = B.kind == "cut"
B["per"] = np.where(B.report.str.startswith("d6t"), B.report.str[4:10], B.report.str[:6])
print("net $ of baskets opened on the day type, per period (cuts / baskets); last col: all-days net")
for k, ds in D.items():
    m = B.day.isin(ds); out = []
    for p, G in B.groupby("per"):
        g = G[m[G.index] if False else G.day.isin(ds)]
        out.append(f"{p[-4:] if p!='yearf_' else 'EG'}:{g.net.sum()/1000:+.0f}k({g.cut.sum()}/{len(g)})")
    neg = sum(B[B.day.isin(ds)].groupby('per').net.sum() < 0)
    print(f"{k:12s} days {len(ds):4d}  cut/1000 {B[m].cut.mean()*1000:4.1f} vs {B[~m].cut.mean()*1000:4.1f}  neg {neg}/8  " + " ".join(out))
print("totals:", " ".join(f"{p}:{G.net.sum()/1000:+.0f}k" for p, G in B.groupby("per")))

# placebo: removing ANY share of baskets helps in a losing period. Compare the day type's net with the period total times its
# share of the period's baskets (what a random set of baskets of the same size would carry); < 0 = worse than random = drop helps.
print("\nexcess vs random (k$): day-type net - share x period net; + = dropping it beats random")
for k in ("NFP", "FOMC", "CPI", "PCE", "GDP", "Powell", "lastFri", "Lars_all", "all_top"):
    ds = D[k]; ex = []
    for p, G in B.groupby("per"):
        g = G[G.day.isin(ds)]; ex.append(-(g.net.sum() - len(g) / len(G) * G.net.sum()) / 1000)
    print(f"{k:9s} better than random in {sum(e > 0 for e in ex)}/8: " + " ".join(f"{e:+.0f}" for e in ex))
