"""Forward test of the crash filter (docs/CRASH_DETECT_PLAN.md, stage 1 result): signal S5 exactly as
tested in stage1.py - percentile of the GVZ close within the trailing 250 observations, shifted by one
observation, then carried forward to calendar days (so Sundays and holidays get the value of the
last observation's previous close, as in training, validation and test). Flag when S5 >= 0.90.
Append-only, no back-dated forecasts: a run writes the forecast for the NEXT trading day only
(eligible=True, made before that day starts); days missed by earlier runs get a row with
eligible=False and are excluded from the forward evaluation. Days: every day except Saturday.
Usage: python research/forward/crash_signal.py OUT_CSV"""
import io, os, sys, urllib.request
import pandas as pd

THRESHOLD, START = 0.90, pd.Timestamp("2026-10-17")
out_path = sys.argv[1]
raw = urllib.request.urlopen("https://fred.stlouisfed.org/graph/fredgraph.csv?id=GVZCLS", timeout=60).read()
g = pd.read_csv(io.BytesIO(raw), parse_dates=["observation_date"], na_values=".").set_index("observation_date").GVZCLS.dropna()
pct = g.rolling(250, min_periods=125).rank(pct=True)
# stage1.py: trailing_pct(...).shift(1) then ffill to days, so a Monday-Friday day d gets the
# percentile of the last observation BEFORE d, and a Sunday gets the one before that (Friday's row,
# which holds Thursday's percentile). Holidays inside the week follow the weekday rule (ASSUMED: rare).
now = pd.Timestamp.now(tz="Europe/Berlin").tz_localize(None)              # the account's server clock
nxt = now.normalize() + pd.Timedelta(days=1)
while nxt.weekday() == 5:
    nxt += pd.Timedelta(days=1)
old = pd.read_csv(out_path, parse_dates=["date"]) if os.path.exists(out_path) else pd.DataFrame(columns=["date"])
done = set(pd.to_datetime(old.date)) if len(old) else set()
days = pd.date_range(START, nxt, freq="D")
rows = []
for d in days[days.weekday != 5]:
    if d in done:
        continue
    v = pct[pct.index < d].dropna()
    if len(v) < 2:
        continue
    val = float(v.iloc[-2] if d.weekday() == 6 else v.iloc[-1])
    rows.append({"date": d.date(), "s5": round(val, 3), "flagged": bool(val >= THRESHOLD),
                 "eligible": bool(d == nxt), "made_server_time": now.isoformat(timespec="seconds") + " Europe/Berlin"})
new = pd.DataFrame(rows)
pd.concat([old, new], ignore_index=True).to_csv(out_path, index=False)
print(f"{len(new)} new rows")
if len(new):
    print(new.to_string(index=False))
