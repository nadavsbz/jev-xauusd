"""Builds DragonClone_v18.mq5 = v17 + NewsCloseAll (t309, the user's news rule, approved 20.11.2026 via Grok).
With NewsCloseAll = false (default) it trades exactly like v17.
  NewsCloseAll  inside the NewsFile window (NewsBeforeMin before an event .. NewsAfterMin after it) close every position of this
                EA and open nothing. With NewsBeforeMin=60, NewsAfterMin=60 and a FOMC+NFP file this is the rule:
                "exit before FOMC and NFP; no new baskets from an hour before to an hour after".
Also writes the event files (RoboForex clock, as research/bd1/news_files.py):
  news_fn_rf.txt          Fed Interest Rate Decision + Nonfarm Payrolls
  news_fnrand_rf_<k>.txt  k = 1..K random controls: the same number of events per calendar year, each at a random weekday
                          13:00-21:59 server time (US session, where FOMC/NFP fall), seed k; no look at returns.
Usage: py -3.12 research/bd1/make_v18.py [K]   (then compile v18 in C:\\MT5_JEV_TEST)"""
import shutil, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/bd1")
from news_files import us_dst, check_utc, D, CF

src = open("mql5/DragonClone_v17.mq5", encoding="utf-8").read()
def rep(a, b):
    global src
    assert src.count(a) == 1, a[:70]; src = src.replace(a, b)

rep("input int    NewsAfterMin = 60;", """input int    NewsAfterMin = 60;
input bool   NewsCloseAll = false;    // v18 (t309, 20.11.2026): inside the news window close all positions and open nothing""")
rep("   bool crash = G_Crash && now < crashUntil;\n", """   bool crash = G_Crash && now < crashUntil;
   if(NewsCloseAll && NewsFile != "" && InNewsPause()) { CloseSide(0); CloseSide(1); return; }   // v18
""")
open("mql5/DragonClone_v18.mq5", "w", encoding="utf-8").write(src.replace("DragonClone_v17", "DragonClone_v18"))

s = open("research/bd1/sets/dcv17_2d.set", "rb").read().decode("utf-16")
nl = "\r\n" if "\r\n" in s else "\n"
i = s.index("NewsAfterMin=")
j = s.index(nl, i) + len(nl)
s = s[:j] + "NewsCloseAll=false" + nl + s[j:]
open("research/bd1/sets/dcv18_2d.set", "wb").write(s.encode("utf-16"))

cal = pd.read_csv(D + "mt5_calendar_usd.csv", encoding="latin1")
check_utc(cal)
fn = cal[(cal.importance == 3) & cal.event.isin(["Fed Interest Rate Decision", "Nonfarm Payrolls"])]
rf = lambda x: int(x + (2 + (1 if us_dst(pd.Timestamp(x, unit="s")) else 0)) * 3600)
ev = sorted(set(rf(x) for x in fn.time))
def write(name, v):
    txt = "\n".join(str(x) for x in sorted(v)) + "\n"
    open(D + name, "w").write(txt); shutil.copy(D + name, CF + name)
write("news_fn_rf.txt", ev)
per_year = pd.Series([pd.Timestamp(x, unit="s").year for x in ev]).value_counts().to_dict()
K = int(sys.argv[1]) if len(sys.argv) > 1 else 40
for k in range(1, K + 1):
    rng = np.random.default_rng(k); out = []
    for y, n in sorted(per_year.items()):
        days = pd.bdate_range(f"{y}-01-01", f"{y}-12-31")
        for d in rng.choice(days, size=n, replace=False):
            out.append(int(pd.Timestamp(d).timestamp()) + int(rng.integers(13 * 60, 22 * 60)) * 60)
    write(f"news_fnrand_rf_{k}.txt", out)
print("v18;", len(ev), "FOMC+NFP events;", K, "random controls; per year", dict(sorted(per_year.items())))
