"""How often does gold move one way by X% within a day (the condition of the 7.6.2024 wipe,
docs/BD1_CRASH_CAUSE.md)? From the H1 history (UTC days): for each day, the largest drop from a running
high and the largest rise from a running low inside the day, in % of that high/low. Descriptive.
Usage: python research/crash/trend_days.py DATA_DIR"""
import glob, os, sys
import pandas as pd

fs = sorted(glob.glob(os.path.join(sys.argv[1], "xauusd_h1_*.csv")))
d = pd.concat([pd.read_csv(f) for f in fs]).drop_duplicates("timestamp")
d["t"] = pd.to_datetime(d.timestamp, unit="ms"); d = d.set_index("t").sort_index()
rows = []
for day, g in d.groupby(d.index.normalize()):
    run_hi = g.high.cummax(); run_lo = g.low.cummin()
    drop = ((run_hi - g.low) / run_hi).max() * 100       # deepest fall from the day's high so far
    rise = ((g.high - run_lo) / run_lo).max() * 100
    rows.append((day, drop, rise))
x = pd.DataFrame(rows, columns=["day", "drop", "rise"]).set_index("day")
x["one_way"] = x[["drop", "rise"]].max(axis=1)
print("days:", len(x), x.index.min().date(), "->", x.index.max().date())
for th in (2.0, 2.5, 3.0, 3.5, 4.0):
    y = x[x.one_way >= th]
    per_year = y.groupby(y.index.year).size().reindex(range(x.index.year.min(), x.index.year.max() + 1), fill_value=0)
    print(f">= {th}%: {len(y)} days, {len(y) / (len(x) / 252):.1f} per year | by year: {per_year.to_dict()}")
print("7.6.2024:", x.loc["2024-06-07"].round(2).to_dict() if pd.Timestamp("2024-06-07") in x.index else "missing")
print("largest 10:", x.one_way.sort_values().tail(10).round(2).to_dict())
x.round(3).to_csv("docs/evidence/gold_trend_days.csv")
