"""t334 audit after GPT t335 review (PR #44): fixes the measurement, NOT the rule; verdict stays as registered.
Fixes: (1) server->UTC via candidate check (us_dst evaluated on the UTC candidate), (2) missing boundary bar: position is
carried to the next valid open instead of a free close, (3) buy&hold on the same 05:00 UTC boundaries.
Reports: missing-boundary counts, DST-shifted bars, top-20 day-leg days share, result without the best 10 days.
Usage: py -3.12 research/stable/t334_audit.py"""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/bd1"); sys.path.insert(0, "research/stable")
from news_files import us_dst
import t334

def load_fixed():
    d = pd.read_csv(t334.CF + "t326_ETHUSD_PERIOD_H1.csv")
    t = pd.to_datetime(d.time, unit="s")
    c3 = t - pd.Timedelta(hours=3)
    off = np.where([us_dst(x) for x in c3], 3, 2)
    utc = t - pd.to_timedelta(off, unit="h")
    old = t - pd.to_timedelta(np.where([us_dst(x) for x in t], 3, 2), unit="h")
    x = pd.DataFrame({"o": d.open.values, "c": d.close.values}, index=utc).sort_index()
    return x[~x.index.duplicated()], int((utc != old).sum())

def run_fixed(x, side):
    """same rule; a missing boundary keeps the position open until the next available bar open (no free close)."""
    o = x.o; days = sorted(set(x.index.normalize()))
    def px_at(t):
        i = o.index.searchsorted(t)
        return (o.index[i], o.iloc[i]) if i < len(o) else (None, None)
    rows, prev_pos, prev_rd, miss = [], 0, None, 0
    sched = []
    for d in days:
        t05, t17, t16 = d + pd.Timedelta(hours=5), d + pd.Timedelta(hours=17), d + pd.Timedelta(hours=16)
        pos = 0 if (prev_rd is None or prev_rd == 0) else (-1 if prev_rd > 0 else 1)
        sched.append((t05, "day", pos)); sched.append((t17, "night", 1))
        prev_rd = (x.c[t16] / o[t05] - 1) if (t05 in o.index and t16 in x.index) else None
    for i in range(len(sched) - 1):
        t0, leg, pos = sched[i]; t1 = sched[i + 1][0]
        if t0 not in o.index: miss += 1
        a_t, a = px_at(t0); b_t, b = px_at(t1)
        if a is None or b is None or a_t >= b_t: continue
        hrs = (b_t - a_t).total_seconds() / 3600
        rows.append((t0, leg, pos, pos * (b / a - 1), side * abs(pos - prev_pos), t334.SWAP * abs(pos) * hrs / 24 / 365))
        prev_pos = pos
    return pd.DataFrame(rows, columns=["t", "leg", "pos", "g", "cost", "swap"]).set_index("t"), miss

if __name__ == "__main__":
    x, shifted = load_fixed()
    out = {"bars_shifted_by_dst_fix": shifted}
    for part, lo, hi in (("dev", "2018-01-01", "2020-12-31"), ("holdout", "2021-01-01", "2026-11-19")):
        r = {}
        for name, side in (("base", 1.5e-4), ("2x_cost", 3.0e-4)):
            T, miss = run_fixed(x["2017-12-01":hi], side); T = T[lo:hi]
            T["net"] = T.g - T.cost - T.swap
            r[name] = t334.stats(t334.daily(T, lo, hi))
            if name == "base":
                r["missing_boundaries_whole_file"] = miss
                D = T[T.leg == "day"]; r["day_leg_net_pct"] = round(float(D.net.sum() * 100), 1)
                r["night_leg_net_pct"] = round(float(T[T.leg == "night"].net.sum() * 100), 1)
                top = D.net.sort_values(ascending=False)
                r["day_leg_top20_pct"] = round(float(top.head(20).sum() * 100), 1)
                r["day_leg_without_top10_pct"] = round(float((D.net.sum() - top.head(10).sum()) * 100), 1)
                r["y2026_pct"] = round(float(T.loc["2026"].net.sum() * 100), 1) if part == "holdout" else None
        p05 = x.o[x.index.hour == 5][lo:hi]
        bh = (p05.shift(-1) / p05 - 1).dropna() - t334.SWAP / 365
        bh.index = bh.index.normalize()
        r["buy_hold_05utc"] = t334.stats(bh)
        out[part] = r
    print(json.dumps(out, indent=1, ensure_ascii=False))
