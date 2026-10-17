"""Forward log of the crash filter S5 (docs/CRASH_DETECT_PLAN.md), with the SAME timing as stage 1
and stage 2 (research/crash/gvz_pub.py): the GVZ close of day D counts as published at 16:00 UTC on the
next US-exchange business day. Each run appends ONE row (append-only):
- s5 = the value already published at the run time (as stage 1 gives the hour that ends now);
- source_obs = the observation it comes from; required_obs = the latest observation that the timing
  rule says must be published by now; eligible = FRED really had it (source_obs == required_obs);
- valid_from = the run time. The forward evaluation counts the hours from valid_from until the next
  row's valid_from, and only for eligible rows. Flag when S5 >= 0.90.
Usage: python research/forward/crash_signal.py OUT_CSV"""
import io, os, sys, urllib.request
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "crash"))
import gvz_pub  # noqa: E402

THRESHOLD = 0.90
out_path = sys.argv[1]
raw = urllib.request.urlopen("https://fred.stlouisfed.org/graph/fredgraph.csv?id=GVZCLS", timeout=60).read()
g = pd.read_csv(io.BytesIO(raw), parse_dates=["observation_date"], na_values=".").set_index("observation_date").GVZCLS.dropna()
pub = gvz_pub.published(gvz_pub.percentile(g))
now_utc = pd.Timestamp.now(tz="UTC").tz_localize(None)
v, p = gvz_pub.at([now_utc], pub)
src = (pd.Timestamp(p[0]) - pd.Timedelta(hours=16) - gvz_pub.BDAY).normalize() if pd.notna(p[0]) else None
# the latest observation day whose publication time (rule) is not after now
d = now_utc.normalize()
while d + gvz_pub.BDAY + pd.Timedelta(hours=16) > now_utc:
    d -= pd.Timedelta(days=1)
req = d if gvz_pub.BDAY.is_on_offset(d) else d - gvz_pub.BDAY
row = {"date": pd.Timestamp.now(tz="Europe/Berlin").date(), "s5": round(float(v[0]), 3),
       "flagged": bool(v[0] >= THRESHOLD), "source_obs": src.date() if src is not None else None,
       "required_obs": req.date(), "eligible": bool(src is not None and src.normalize() == req.normalize()),
       "valid_from": now_utc.isoformat(timespec="seconds") + " UTC"}
old = pd.read_csv(out_path) if os.path.exists(out_path) else pd.DataFrame()
pd.concat([old, pd.DataFrame([row])], ignore_index=True).to_csv(out_path, index=False)
print(pd.DataFrame([row]).to_string(index=False))
