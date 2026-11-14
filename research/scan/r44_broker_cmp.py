"""Diagnostic (no parameter choice): the 44a straddle (as frozen) on the same release windows from two brokers' tick histories
(RoboForex-ECN news_ticks/ vs EGlobal-Classic news_ticks_eg/, 2025-03-26 on) and Happy's real book (Eightcap) on the same events.
Usage: py -3.12 research/scan/r44_broker_cmp.py"""
import sys, glob, os
import numpy as np, pandas as pd
sys.argv = sys.argv[:1] + ["test"]; sys.path.insert(0, "research/scan")
from r44_sim import sim
R = {}
for tag, d in (("RF", "news_ticks"), ("EG", "news_ticks_eg")):
    for f in glob.glob(f"data/derived/scan/{d}/*.csv"):
        s, T = os.path.basename(f)[:-4].split("_"); T = int(T)
        if T < pd.Timestamp("2025-03-26").timestamp(): continue
        try: r = sim(f, "a", 0.0); n = len(pd.read_csv(f, usecols=["time_msc"]))
        except Exception: continue
        if r is None: continue
        R.setdefault((s, T), {})[tag] = r[0] if r[1] in ("long", "short") else np.nan
        R[(s, T)][tag + "_dir"] = {"long": 1, "short": -1}.get(r[1], 0); R[(s, T)][tag + "_ticks"] = n
x = pd.DataFrame.from_dict(R, orient="index"); x.index.names = ["sym", "T"]
both = x.dropna(subset=["RF_dir", "EG_dir"])
print("events-symbols with both brokers:", len(both))
print("fill rate RF/EG:", (both.RF_dir != 0).mean().round(2), (both.EG_dir != 0).mean().round(2), "| same dir when both fill:",
      ((both.RF_dir == both.EG_dir) & (both.RF_dir != 0)).sum(), "/", ((both.RF_dir != 0) & (both.EG_dir != 0)).sum())
print("ticks in window median RF/EG:", both.RF_ticks.median(), both.EG_ticks.median())
for t in ("RF", "EG"):
    p = both[t].dropna(); print(f"{t}: trades {len(p)} mean {p.mean():.2f} median {p.median():.2f} hit {(p>0).mean()*100:.0f}% by sym {both.groupby('sym')[t].mean().round(2).to_dict()}")
bm = pd.read_csv("data/derived/scan/r44_book_match.csv", parse_dates=["ot", "T"]); bm = bm[bm.match]
# book T is RF server time; map to UTC epoch like the file key
bm["key"] = (bm["T"] - pd.Timedelta(hours=7)).dt.tz_localize("America/New_York", ambiguous="NaT", nonexistent="NaT").dt.tz_convert("UTC").dt.tz_localize(None)
bm["key"] = (bm.key - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1)
j = bm.dropna(subset=["key"]).merge(both.reset_index(), left_on=["sym", "key"], right_on=["sym", "T"], how="inner")
print("book trades on those events:", len(j), "| book mean", j.bpips.mean().round(2), "| RF sim", j.RF.mean().round(2), "| EG sim", j.EG.mean().round(2),
      "| same dir book-RF", (j.bq == j.RF_dir).mean().round(2), "book-EG", (j.bq == j.EG_dir).mean().round(2))
x.to_csv("data/derived/scan/r44_broker_cmp.csv")
