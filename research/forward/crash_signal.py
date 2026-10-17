"""Forward test of the crash filter (docs/CRASH_DETECT_PLAN.md, stage 1 result): signal S5 exactly as
tested in stage1.py - percentile of the GVZ close within the trailing 250 observations, shifted by one
observation, then carried forward to calendar days (so Sundays and holidays get the value of the
last observation's previous close, as in training, validation and test). Flag when S5 >= 0.90.
Timing: FRED publishes a GVZ close only the next day (around 17:00 Central European time), so the
close a weekday needs is often not yet in FRED when the day starts. Each row therefore records
which observation it used (source_obs) and from when it is valid (valid_from = the run time):
- a run writes rows for today (if not yet written) and for the next trading day;
- a row is eligible only if source_obs is the observation the stage-1 definition requires;
- the forward evaluation counts only hours at or after valid_from (no look-back use).
Days missed entirely are written with eligible=False. Append-only: an ineligible row for a day that
is not over may be followed by a newer row once the required close is published. Days: every day except Saturday.
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
# a date is closed once it has an eligible row; a date with only ineligible rows may get a new row
# (with a later valid_from) while it is not over yet - nothing earlier is rewritten
done = set(pd.to_datetime(old.date[old.eligible.astype(str) == "True"])) if len(old) and "eligible" in old else set()
seen = set(pd.to_datetime(old.date)) if len(old) else set()
days = pd.date_range(START, nxt, freq="D")
today = now.normalize()
rows = []
for d in days[days.weekday != 5]:
    if d in done or (d in seen and d < today):
        continue
    v = pct[pct.index < d].dropna()
    if len(v) < 2:
        continue
    k = -2 if d.weekday() == 6 else -1
    val, src = float(v.iloc[k]), v.index[k]
    # the observation the definition requires: the last weekday before d (Sunday: the Thursday)
    req = d - pd.Timedelta(days=1)
    while req.weekday() >= 5:
        req -= pd.Timedelta(days=1)
    if d.weekday() == 6:
        req -= pd.Timedelta(days=1)
    timely = d >= today                       # made before or during the day, never after it
    rows.append({"date": d.date(), "s5": round(val, 3), "flagged": bool(val >= THRESHOLD),
                 "source_obs": src.date(), "required_obs": req.date(),
                 "eligible": bool(timely and src.normalize() >= req.normalize()),
                 "valid_from": now.isoformat(timespec="seconds") + " Europe/Berlin"})
new = pd.DataFrame(rows)
pd.concat([old, new], ignore_index=True).to_csv(out_path, index=False)
print(f"{len(new)} new rows")
if len(new):
    print(new.to_string(index=False))
