"""Replay of "no new baskets on two weekdays" on the real baskets of the live BD accounts (static: the skipped basket's PnL is removed,
other baskets unchanged). Periods: before 15.4.2026 (outside Grok's window = out of sample) and 15.4.2026 onwards.
Control: all 10 pairs of weekdays, so Thu+Fri is compared with simply trading 3 days instead of 5.
Daily = realized PnL of baskets closing that day / the account balance at the start of the period; the book = sum over accounts.
Usage: python research/fleet/thufri_replay.py"""
import itertools
import pandas as pd, numpy as np

ACC = {"1": "data/derived/bd1/clusters_strict.csv"}
for a in "23568": ACC[a] = f"data/derived/fleet/bd{a}/clusters_strict.csv"
SPLIT = pd.Timestamp("2026-04-15")
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]

rows = []
for a, f in ACC.items():
    d = pd.read_csv(f); d["acc"] = a
    d["t0"] = pd.to_datetime(d.t0, unit="s"); d["t1"] = pd.to_datetime(d.t1, unit="s")
    rows.append(d)
B = pd.concat(rows)
B["dow"] = B.t0.dt.dayofweek

def stats(b, skip):
    k = b[~b.dow.isin(skip)]
    cap = b.groupby("acc").bal0.first().sum()           # capital of the accounts active in the period
    day = k.groupby(k.t1.dt.normalize()).pnl.sum() / cap
    eq = cap + k.sort_values("t1").pnl.cumsum()
    dd = (eq / eq.cummax().clip(lower=cap) - 1).min()
    return k.pnl.sum() / cap * 100, dd * 100, day.min() * 100, int((day <= -0.05).sum()), int(k.guard.sum())

for lab, b in (("before 15.4.2026 (out of sample)", B[B.t0 < SPLIT]), ("15.4.2026 on", B[B.t0 >= SPLIT])):
    print(f"--- {lab}: accounts {sorted(b.acc.unique())}, baskets {len(b)}, {b.t0.min():%d.%m.%Y}-{b.t1.max():%d.%m.%Y}")
    print(f"{'skip':10s} {'net%':>7s} {'maxDD%':>7s} {'worst%':>7s} {'d<=-5%':>6s} {'guard':>5s}")
    res = [("none", *stats(b, []))]
    for p in itertools.combinations(range(5), 2): res.append(("+".join(DAYS[i] for i in p), *stats(b, list(p))))
    for r in res: print(f"{r[0]:10s} {r[1]:7.1f} {r[2]:7.1f} {r[3]:7.1f} {r[4]:6d} {r[5]:5d}")
    pnl_by_dow = b.groupby("dow").pnl.sum() / b.groupby("acc").bal0.first().sum() * 100
    print("net% by basket start day:", {DAYS[i]: round(v, 1) for i, v in pnl_by_dow.items() if i < 5})
