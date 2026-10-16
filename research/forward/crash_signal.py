"""Forward test of the crash filter (docs/CRASH_DETECT_PLAN.md, stage 1 result): signal S5 =
percentile of the previous day's GVZ close within the trailing 250 trading days; a day is flagged
when S5 >= 0.90 (the threshold fixed on the training period). Downloads GVZCLS from FRED and writes
one row per day from 2026-10-17: date, gvz_prev, s5, flagged. Outcomes (gold 1%/4h events, account 1
deep baskets) are joined later by the monthly report; nothing here is chosen on forward data.
Usage: python research/forward/crash_signal.py OUT_CSV"""
import io, sys, urllib.request
import pandas as pd

THRESHOLD, START = 0.90, pd.Timestamp("2026-10-17")
raw = urllib.request.urlopen("https://fred.stlouisfed.org/graph/fredgraph.csv?id=GVZCLS", timeout=60).read()
g = pd.read_csv(io.BytesIO(raw), parse_dates=["observation_date"], na_values=".").set_index("observation_date").GVZCLS.dropna()
pct = g.rolling(250, min_periods=125).rank(pct=True)
days = pd.bdate_range(START, pd.Timestamp.today().normalize())
prev = pct.shift(1).reindex(days, method="ffill")          # the previous published close only
gv = g.shift(1).reindex(days, method="ffill")
out = pd.DataFrame({"gvz_prev": gv.round(2), "s5": prev.round(3), "flagged": prev >= THRESHOLD}, index=days)
out.index.name = "date"
out.to_csv(sys.argv[1])
print(out.tail(5).to_string())
