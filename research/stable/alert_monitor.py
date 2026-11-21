"""Early-warning monitor, PROTOCOL v1 (docs/agents/grok_data/t320/PROTOCOL_v1.md), for the C1+I2 demo.
Read-only: works on the exported deal file (research/stable/demo_export.py) and on daily equity snapshots, never on the terminal.
Usage: py -3.12 research/stable/alert_monitor.py data/derived/demo_c1i2/deals_YYYYMMDD.csv

Conventions (from the protocol, t320, 20.11.2026):
- t=0 = 2026-11-23. Demo risk = 1.5x tester, so demo returns and DD are divided by 1.5 before the thresholds.
- I2: daily return = realised P&L of the day (magic 7302, server date) / account balance at the start of the day; only days with
  an I2 exit count (same as the n=803 reference). Side = exit deal type (exit sell closes a long).
- C1: needs mark-to-market daily equity, which deals alone cannot give (positions are held for days). Until daily snapshots exist
  (data/derived/demo_c1i2/c1_snapshots.csv: date,c1_mtm_pnl) C1 CUSUM/DD is reported as NOT ACTIVE - not computed from realised P&L.
- RED = combined CUSUM >= h or DD >= bootstrap p99 (v1.1). YELLOW = DD >= p95, side CUSUM >= h (I2), or demo/tester ratio < 0.7 for 4 weeks
  (ratio comes from docs/evidence/demo_tracker.md, entered by hand). RED/YELLOW are recommendations only; every live action is Nadav's.
"""
import os, sys
import numpy as np, pandas as pd

T0, DEPOSIT, RISK = pd.Timestamp("2026-11-23"), 40000.0, 1.5
REF = {  # mu0, sigma0 (fraction/day), k, h  - PROTOCOL v1, sha 40efaf90...
    "I2": (17.7e-4, 155e-4, 0.0571, 16.7), "I2_long": (25.2e-4, 144e-4, 0.0875, 14.1),
    "I2_short": (9.7e-4, 172e-4, 0.0282, 20.3), "C1": (6.9e-4, 117e-4, 0.0295, 20.0)}
# v1.1 (21.11, before t0, GPT t321 P1): block-bootstrap MDD of 12-month reference paths (research/stable/t321_mdd_boot.py)
# RED = p99, YELLOW = p95, from the tester reference only (no demo data used)
MDD_RED = {"I2": 0.26, "C1": 0.37}
MDD_YEL = {"I2": 0.21, "C1": 0.31}


def cusum(r, name):
    mu, sd, k, h = REF[name]; s, peak = 0.0, 0.0
    for x in r:
        s = max(0.0, s + (mu - x) / sd - k); peak = max(peak, s)
    return s, h, peak


def main(path):
    d = pd.read_csv(path); d["day"] = pd.to_datetime(d.time, unit="s").dt.normalize()
    d["pnl"] = d.profit + d.swap + d.commission + d.get("fee", 0)
    bal = d.sort_values("time").pnl.cumsum()          # the deposit is itself a balance deal (type 2) in the export
    d["bal_before"] = bal - d.pnl
    i2 = d[(d.magic == 7302) & (d.entry == 1) & (d.day >= T0)]
    rep = [f"alert monitor, PROTOCOL v1, data to {d.day.max().date()}, t0 {T0.date()}"]
    if i2.empty:
        rep.append("I2: no exits since t0 - GREEN (nothing to measure)")
    else:
        g = i2.groupby("day").agg(pnl=("pnl", "sum"), base=("bal_before", "first"))
        r = g.pnl / g.base / RISK
        s, h, _ = cusum(r, "I2"); eq = (1 + r).cumprod(); dd = -(eq / eq.cummax() - 1).min()
        sides = {}
        for nm, typ in (("I2_long", 1), ("I2_short", 0)):   # deal type 1 = sell exit closes a long
            x = i2[i2.type == typ].groupby("day").pnl.sum()
            sides[nm] = cusum(x / g.base.reindex(x.index) / RISK, nm)[:2] if len(x) else (0.0, REF[nm][3])
        lvl = "RED" if s >= h or dd >= MDD_RED["I2"] else ("YELLOW" if dd >= MDD_YEL["I2"] or any(a >= b for a, b in sides.values()) else "GREEN")
        rep.append(f"I2: {lvl}  days {len(r)}  cum {r.sum() * 100:+.2f}% (tester units)  CUSUM {s:.2f}/{h}  DD {dd * 100:.1f}%/"
                   f"{MDD_RED['I2'] * 100:.1f}%  " + "  ".join(f"{k} {a:.2f}/{b}" for k, (a, b) in sides.items()))
    snap = "data/derived/demo_c1i2/c1_snapshots_raw.csv"   # demo_export.py appends "server time,C1 realised+floating"
    if os.path.exists(snap):
        c = pd.read_csv(snap, names=["ts", "v"], parse_dates=["ts"])
        c = c[c.ts.dt.hour < 2]                                   # day-start snapshots only (server date = C1 day cut)
        c = c.groupby(c.ts.dt.normalize()).v.first(); c.index.name = "date"
        c = c.reindex(pd.date_range(c.index.min(), c.index.max())) if len(c) else c   # missing days stay NaN, not 0
        c = c.dropna()   # a gap merges two days into one step (documented, conservative for CUSUM count)
        c = c[c.index >= T0]; r = c.diff().dropna() / (DEPOSIT + c.shift(1).dropna()) / RISK
        s, h, _ = cusum(r, "C1"); eq = (1 + r).cumprod(); dd = -(eq / eq.cummax() - 1).min() if len(r) else 0.0
        lvl = "RED" if s >= h or dd >= MDD_RED["C1"] else ("YELLOW" if dd >= MDD_YEL["C1"] else "GREEN")
        rep.append(f"C1: {lvl}  days {len(r)}  CUSUM {s:.2f}/{h}  DD {dd * 100:.1f}%/{MDD_RED['C1'] * 100:.1f}%")
    else:
        rep.append("C1: CUSUM/DD NOT ACTIVE (no daily mark-to-market snapshots yet); weekly demo/tester ratio only")
    rep.append("YELLOW by demo/tester ratio: see docs/evidence/demo_tracker.md (4 weeks < 0.7). Recommendation only.")
    print("\n".join(rep))


if __name__ == "__main__":
    main(sys.argv[1])
