"""One-off correction of H1 files written by pull_h1.py with the old 'New York + 7h' rule: the RoboForex
server clock follows EUROPEAN daylight time (Europe/Athens, UTC+2/+3): with it 604 of 627 weekly gold
opens fall at 18:00 New York, against 563 with the old rule (docs/CRASH_DETECT_PLAN.md).
Old UTC -> server wall time (NY wall + 7h) -> UTC by Europe/Athens. Hours that do not exist or repeat
in Athens time are dropped. Rewrites the files in place after keeping a .bak copy.
Usage: python research/crash/reclock_h1.py FILE.csv [FILE.csv ...]"""
import shutil, sys
import pandas as pd

for f in sys.argv[1:]:
    d = pd.read_csv(f)
    utc = pd.to_datetime(d.timestamp, unit="ms").dt.tz_localize("UTC")
    wall = utc.dt.tz_convert("America/New_York").dt.tz_localize(None) + pd.Timedelta(hours=7)
    new = wall.dt.tz_localize("Europe/Athens", ambiguous="NaT", nonexistent="NaT").dt.tz_convert("UTC")
    ok = new.notna()
    shutil.copy(f, f + ".bak")
    d = d[ok.values].copy(); d["timestamp"] = (new[ok].astype("int64") // 10**6).values
    d.sort_values("timestamp").drop_duplicates("timestamp").to_csv(f, index=False)
    print(f, "dropped", int((~ok).sum()))
