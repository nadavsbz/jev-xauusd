"""The 'Asia opens up' window: long gold from UTC hour H1 to H2 every day, with the real spread of the entry bar
(bars spread column, in points) paid once per trade. Per period: trades, gross and net bp per trade, net % per year at 1x notional,
hit rate. Usage: python research/hybrid/session_long.py H1 H2   (UTC hours; H2 may be < H1 = next day)"""
import glob, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/bd1"); from news_files import us_dst

H1, H2 = int(sys.argv[1]), int(sys.argv[2])
PT = {"rf": 0.01, "eg": 0.001}
for f in sorted(glob.glob("data/derived/crash_signs/bars_*_PERIOD_M15.csv")):
    p = f.split("bars_")[1].split("_")[0]
    b = pd.read_csv(f); ts = pd.to_datetime(b.time, unit="s")
    off = np.where([p.startswith("rf") and us_dst(t) for t in ts], 3, 2)
    b["utc"] = ts - pd.to_timedelta(off, unit="h")
    b["h"] = b.utc.dt.hour
    ent = b[(b.h == H1) & (b.utc.dt.minute == 0)]
    res = []
    for i, e in ent.iterrows():
        ex = b[(b.utc > e.utc) & (b.h == H2) & (b.utc.dt.minute == 0) & (b.utc - e.utc < pd.Timedelta(hours=26))]
        if ex.empty: continue
        x = ex.iloc[0]
        gross = (x.open - e.open) / e.open * 1e4
        cost = e.spread * PT[p[:2]] / e.open * 1e4
        res.append((gross, cost))
    r = pd.DataFrame(res, columns=["gross", "cost"]); r["net"] = r.gross - r.cost
    yrs = (b.utc.iloc[-1] - b.utc.iloc[0]).days / 365.25
    print(f"{p}: n={len(r)} gross {r.gross.mean():+.2f}bp cost {r.cost.mean():.2f}bp net {r.net.mean():+.2f}bp/trade "
          f"t={r.net.mean() / r.net.std() * np.sqrt(len(r)):+.1f} hit {(r.net > 0).mean():.0%} net/yr {r.net.sum() / 100 / yrs:+.1f}% (1x)")
