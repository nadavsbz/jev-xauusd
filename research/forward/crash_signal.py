"""Forward test of the crash filter (docs/CRASH_DETECT_PLAN.md, stage 1 result): signal S5 =
percentile of the last published GVZ close before the day, within the trailing 250 observations;
a day is flagged when S5 >= 0.90 (threshold fixed on the training period).
Append-only: a day already in the file is never rewritten (FRED revisions or late values do not
change past forecasts); each new row records when it was made. Days: every calendar day except
Saturday (gold trades Sunday to Friday), from 2026-10-17 up to today.
Usage: python research/forward/crash_signal.py OUT_CSV"""
import io, os, sys, urllib.request
import numpy as np, pandas as pd

THRESHOLD, START = 0.90, pd.Timestamp("2026-10-17")
out_path = sys.argv[1]
raw = urllib.request.urlopen("https://fred.stlouisfed.org/graph/fredgraph.csv?id=GVZCLS", timeout=60).read()
g = pd.read_csv(io.BytesIO(raw), parse_dates=["observation_date"], na_values=".").set_index("observation_date").GVZCLS.dropna()
pct = g.rolling(250, min_periods=125).rank(pct=True)
old = pd.read_csv(out_path, parse_dates=["date"]) if os.path.exists(out_path) else pd.DataFrame(columns=["date"])
done = set(pd.to_datetime(old.date)) if len(old) else set()
days = pd.date_range(START, pd.Timestamp.today().normalize(), freq="D")
rows = []
for d in days[days.weekday != 5]:
    if d in done:
        continue
    k = np.searchsorted(g.index.values, d.to_datetime64(), side="left") - 1     # last close strictly before the day
    if k < 0:
        continue
    rows.append({"date": d.date(), "gvz_close_used": round(float(g.iloc[k]), 2), "close_date": g.index[k].date(),
                 "s5": round(float(pct.iloc[k]), 3), "flagged": bool(pct.iloc[k] >= THRESHOLD),
                 "made_utc": pd.Timestamp.now(tz="UTC").isoformat(timespec="seconds")})
new = pd.DataFrame(rows)
pd.concat([old, new], ignore_index=True).to_csv(out_path, index=False)
print(f"{len(new)} new rows")
if len(new):
    print(new.to_string(index=False))
