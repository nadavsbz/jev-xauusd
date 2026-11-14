"""Scan round 23 of docs/SCAN_PLAN.md (pre-registered 12.11.2026 night): sharp-move momentum mini-bot as a hedge for BD clone cut days.
Usage: python research/scan/bd_minihedge.py"""
import sys; sys.path.insert(0, "research/scan/gr")
import numpy as np, pandas as pd
from gr_common import m1
from engine import run
COST, K = 0.0002, 3.0
m = m1(); idx = m.index; o, h, l, c = (m[k].values for k in ("open", "high", "low", "close"))
r60 = np.log(m.open / m.close.shift(60))                       # move of the last 60 min, known at bar open
sd = r60.rolling(20 * 1380, min_periods=10 * 1380).std().shift(1)
span = (idx.to_series().diff(60).dt.total_seconds() / 60).values
sig = ((r60.abs() > K * sd) & (span <= 75)).values; qv = np.sign(r60.values)
tr = []; busy = {1: -1, -1: -1}
for i in np.where(sig)[0]:
    q = int(qv[i])
    if q == 0 or i <= busy[q] or i >= len(idx) - 2: continue
    ret, n = run(o, h, l, c, i, q, cap=24 * 60); busy[q] = i + n
    tr.append((idx[i], idx[min(i + n, len(idx) - 1)], q, ret - COST))
T = pd.DataFrame(tr, columns=["t0", "t1", "q", "net"])
T["day"] = T.t1.dt.normalize()
B = pd.read_csv("data/derived/crash_signs/baskets.csv"); B = B[B.report.str.startswith("rf")]
cut = B[B.kind == "cut"].copy(); cut["day"] = pd.to_datetime(cut.t1, unit="s").dt.normalize()
cut = cut[(cut.day >= "2022-01-01") & (cut.day <= "2025-12-31")]
cd = cut.groupby("day").agg(net_pct=("net_pct", "sum"), side=("side", "first"))
daily = T.groupby("day").net.sum()
cd["mini_bp"] = daily.reindex(cd.index).fillna(0) * 1e4
# same-day plus previous day (crash builds up)
prev = daily.copy(); prev.index = prev.index + pd.Timedelta(days=1)
cd["mini_2d_bp"] = cd.mini_bp + prev.reindex(cd.index).fillna(0) * 1e4
print(f"trades total {len(T)}; cut days 2022-2025: {len(cd)}")
print(cd.round(1).to_string())
print(f"\nGATE1 sum on cut days: {cd.mini_bp.sum():.1f} bp (2-day window {cd.mini_2d_bp.sum():.1f})")
print(f"GATE2 non-negative cut days: {(cd.mini_bp >= 0).mean()*100:.0f}% (2-day {(cd.mini_2d_bp >= 0).mean()*100:.0f}%)")
for nm, a, z in (("GATE3 2022-2025", "2022", "2025"), ("GATE4 2018-2021", "2018", "2021"), ("info 2026", "2026", "2026")):
    x = T[(T.t0 >= a) & (T.t0 < str(int(z) + 1))].net
    print(f"{nm}: trades {len(x)}, mean net {x.mean()*1e4:.2f} bp, t {x.mean()/x.std()*np.sqrt(len(x)):.2f}, by year {x.groupby(T.t0.dt.year).mean().mul(1e4).round(1).to_dict()}")
