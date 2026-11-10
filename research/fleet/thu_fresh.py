"""Out-of-sample check of "no new BD baskets on Thursday" on deals AFTER the data used so far (export of 10.11.2026).
Baskets are rebuilt simply from deals.csv: positions of magic 5555 on gold; a basket = a run of time-overlapping positions
(as clusters_strict). Basket PnL = profit+commission+swap+fee of its positions; start weekday = first open (server time).
Sanity: the same builder on 15.4-21.10.2026 must reproduce the sign of thufri_replay.py (Thursday baskets negative).
Usage: python research/fleet/thu_fresh.py"""
import glob, os
import pandas as pd

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def baskets(acc):
    d = sorted(glob.glob(f"data/raw/black_dragon_{acc}/2026111*"))[-1]
    x = pd.read_csv(os.path.join(d, "deals.csv"))
    x["cash"] = x.profit + x.commission + x.swap + x.fee
    bal = x.sort_values("time").assign(b=lambda z: z.cash.cumsum())
    ids = x[(x.entry == 0) & (x.magic == 5555) & x.symbol.fillna("").str.startswith("XAU")].position_id
    g = x[x.position_id.isin(ids)]                  # all deals of the robot's positions (exit deals may carry another magic)
    p = g.groupby("position_id").agg(t0=("time", "min"), t1=("time", "max"), pnl=("cash", "sum")).sort_values("t0")
    cid, end, ids = -1, -1, []
    for t0, t1 in zip(p.t0, p.t1):
        if t0 > end: cid += 1
        end = max(end, t1); ids.append(cid)
    p["cid"] = ids
    b = p.groupby("cid").agg(t0=("t0", "min"), t1=("t1", "max"), pnl=("pnl", "sum"), n=("pnl", "size"))
    b["bal0"] = [bal.b[bal.time < t].iloc[-1] if (bal.time < t).any() else 0 for t in b.t0]
    b["t0"] = pd.to_datetime(b.t0, unit="s"); b["t1"] = pd.to_datetime(b.t1, unit="s"); b["acc"] = acc
    return b

B = pd.concat([baskets(a) for a in "123568"]); B["dow"] = B.t0.dt.dayofweek

def show(b, lab):
    cap = b.groupby("acc").bal0.first().sum()
    print(f"--- {lab}: {len(b)} baskets, accounts {sorted(b.acc.unique())}, {b.t0.min():%d.%m}-{b.t1.max():%d.%m.%Y}")
    by = (b.groupby("dow").pnl.sum() / cap * 100).round(1)
    print("net% by start day:", {DAYS[i]: v for i, v in by.items()}, f"| total {b.pnl.sum() / cap * 100:.1f}%")
    day = b.groupby(b.t1.dt.normalize()).pnl.sum() / cap * 100
    print("worst days (all):", {f"{k:%a %d.%m}": round(v, 1) for k, v in day.nsmallest(5).items()})
    k = b[b.dow != 3]; dk = k.groupby(k.t1.dt.normalize()).pnl.sum() / cap * 100
    print(f"skip Thu: total {k.pnl.sum() / cap * 100:.1f}%, worst day {dk.min():.1f}%, days<=-5%: {(day <= -5).sum()} -> {(dk <= -5).sum()}")
    big = b[b.pnl / b.bal0 < -0.05].sort_values("t1")
    print("baskets losing >5% of balance:", [f"{a} {t:%a %d.%m} {p / q * 100:.0f}%" for a, t, p, q in zip(big.acc, big.t0, big.pnl, big.bal0)])

show(B[(B.t0 >= "2026-04-15") & (B.t0 < "2026-10-22")], "sanity 15.4-21.10 (in sample)")
show(B[B.t0 >= "2026-10-22"], "NEW 22.10-10.11 (out of sample)")
