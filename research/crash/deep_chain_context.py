"""What did the dollar index and scheduled news look like around the deepest Black Dragon chains?
(docs/BD1_CRASH_CAUSE.md; descriptive). Calibrated run chains (vol_lot_map.baskets); for each chain's first
day: gold one-way move (gold_trend_days.csv), synthetic USDX daily range and its percentile, and whether a
scheduled NFP/FOMC fell on that day. Deep chains (10+ levels) against all chain days.
Usage: python research/crash/deep_chain_context.py DATA_DIR REPORT.htm"""
import glob, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bd1"))
import guardian_sim as g  # noqa: E402
from vol_lot_map import baskets  # noqa: E402

data, rep = sys.argv[1], sys.argv[2]
fs = sorted(glob.glob(os.path.join(data, "dollaridxusd_h1_*.csv")))
dx = pd.concat([pd.read_csv(f) for f in fs]).drop_duplicates("timestamp")
dx["t"] = pd.to_datetime(dx.timestamp, unit="ms"); dx = dx.set_index("t").sort_index()
dd = dx.resample("1D").agg({"high": "max", "low": "min", "close": "last"}).dropna()
dd["rng"] = (dd.high - dd.low) / dd.close * 100
dd["rng_pct"] = dd.rng.rolling(250, min_periods=60).rank(pct=True).shift(1)    # yesterday's view, no look-ahead
dd["prev_rng_pct"] = dd.rng_pct.shift(1)
gold = pd.read_csv("docs/evidence/gold_trend_days.csv", parse_dates=["day"]).set_index("day")
ev = pd.read_csv("docs/evidence/events_actual_nfp.csv")
ev_day = set(pd.to_datetime(ev.utc).dt.normalize())
pos, _ = g.pair(g.deals(rep)); pos = baskets(pos)
ch = pos.groupby("basket").agg(t0=("t0", "min"), levels=("t0", "size"))
ch["day"] = pd.to_datetime(ch.t0, unit="s").dt.normalize()
ch = ch.join(gold.one_way, on="day").join(dd[["rng", "prev_rng_pct"]], on="day")
ch["event"] = ch.day.isin(ev_day)
for name, m in (("all chains", ch.levels >= 1), ("10+ levels", ch.levels >= 10)):
    s = ch[m]
    print(f"{name}: n={len(s)} | gold one-way median {s.one_way.median():.2f}% | USDX range median {s.rng.median():.2f}% "
          f"| previous-day USDX range percentile median {s.prev_rng_pct.median():.2f} | on event day {s.event.mean():.1%}")
deep = ch[ch.levels >= 10].sort_values("day")
print(deep[["day", "levels", "one_way", "rng", "prev_rng_pct", "event"]].round(2).to_string(index=False))
deep.round(3).to_csv("docs/evidence/deep_chain_context.csv")
