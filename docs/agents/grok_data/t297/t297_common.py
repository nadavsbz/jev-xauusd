#!/usr/bin/env python3
"""t297 common (Grok): MTM daily equity of an MT5 tester report from XAUUSD_H1 bars (server time), reusing t295_common parsing."""
import sys, os, bisect, datetime, hashlib
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from t295_common import deals, pair, baskets, K, sha
IN = "/workspace/t297/in"
_H1 = None
def h1():
    global _H1
    if _H1 is None:
        d = pd.read_csv(f"{IN}/XAUUSD_H1.csv").drop_duplicates("time").sort_values("time")
        _H1 = (d.time.values.astype(np.int64), d.high.values, d.low.values, d.close.values)
    return _H1
def mtm_daily(path, dep_default=120000.0):
    """-> DataFrame index=server date: eq_close, eq_worst, bal ; plus positions, baskets, deposit."""
    d, dep = deals(path); dep = dep or dep_default
    pos = pair(d)
    bt, hi, lo, cl = h1()
    if not d: return None
    t_first, t_last = d[0]["t"], d[-1]["t"]
    a = np.searchsorted(bt, t_first, "right") - 1; b = np.searchsorted(bt, t_last, "right")
    a = max(a, 0); T = bt[a:b]; H = hi[a:b]; L = lo[a:b]; C = cl[a:b]; n = len(T)
    Vl = np.zeros(n + 1); Cl = np.zeros(n + 1); Vs = np.zeros(n + 1); Cs = np.zeros(n + 1)
    for p in pos:
        i0 = np.searchsorted(T, p["t0"], "right") - 1; j1 = np.searchsorted(T, p["t1"], "right") - 1
        s, e = i0 + 1, j1          # bars fully after entry and strictly before the exit bar
        if e <= s or s < 0: continue
        if p["side"] == "buy": Vl[s] += p["vol"]; Vl[e] -= p["vol"]; Cl[s] += p["vol"] * p["p0"]; Cl[e] -= p["vol"] * p["p0"]
        else: Vs[s] += p["vol"]; Vs[e] -= p["vol"]; Cs[s] += p["vol"] * p["p0"]; Cs[e] -= p["vol"] * p["p0"]
    Vl, Cl, Vs, Cs = [np.cumsum(x)[:n] for x in (Vl, Cl, Vs, Cs)]
    fl_c = K * (C * Vl - Cl) + K * (Cs - C * Vs)
    fl_w = K * (L * Vl - Cl) + K * (Cs - H * Vs)
    # balance at end of each bar (bar end = T+3600)
    dt = np.array([r["t"] for r in d]); db = np.array([r["bal"] for r in d])
    k = np.searchsorted(dt, T + 3600, "left") - 1
    bal = np.where(k >= 0, db[np.clip(k, 0, None)], dep)
    day = pd.to_datetime(T, unit="s").normalize()
    df = pd.DataFrame({"day": day, "eq_close": bal + fl_c, "eq_worst": bal + np.minimum(fl_w, fl_c), "bal": bal})
    g = df.groupby("day").agg(eq_close=("eq_close", "last"), eq_worst=("eq_worst", "min"), bal=("bal", "last"))
    return dict(daily=g, deposit=dep, pos=pos, baskets=baskets(pos, d), deals=d)
def daily_returns(paths):
    """chain yearly runs: returns daily r_close and r_worst (worst = intraday worst equity vs previous close)."""
    rc, rw = [], []
    for p in paths:
        m = mtm_daily(p)
        if m is None: continue
        g = m["daily"]; prev = g.eq_close.shift(1).fillna(m["deposit"])
        rc.append(g.eq_close / prev - 1); rw.append(g.eq_worst / prev - 1)
    return pd.concat(rc).sort_index(), pd.concat(rw).sort_index()
