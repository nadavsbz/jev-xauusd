"""Rebuild magic-5555 baskets of account 1 and their minute-level floating loss.

A basket is a run of overlapping positions (the account is hedging: one
position per grid order). Exposure is tracked per exit event, so partial
closes and OUT_BY closes reduce the open volume at the time they happen.
--strict counts only whole minutes a volume was open (understates MAE);
the default also counts the partial minutes of entry and exit (overstates)."""
import os, sys, numpy as np, pandas as pd
from inputs import load, START, MAGIC

STRICT = "--strict" in sys.argv
deals, bars = load()
deals["cash"] = deals.profit + deals.commission + deals.swap + deals.fee
# robot-only balance: actual balance minus the running P&L of every excluded
# position (manual trades, other magics), so manual losses do not shrink the
# denominator of robot returns. Deposits/withdrawals stay in.
deals["bal_after"] = deals.cash.cumsum()
x = deals[deals.symbol == "XAUUSDc"]
ENTRY_IN, EXITS = 0, (1, 3)                     # 1 = OUT, 3 = OUT_BY
if set(x.entry) - {ENTRY_IN, *EXITS}:
    sys.exit(f"unexpected entry types {set(x.entry)}")       # e.g. INOUT reversals
ins = x[x.entry == ENTRY_IN]
if ins.position_id.duplicated().any():
    sys.exit("a position has more than one entry deal")
ins = ins.set_index("position_id")
exits = x[x.entry.isin(EXITS)]

# K: cents per 1.0 price move per lot, from positions closed by one OUT deal
one = exits[exits.entry == 1].groupby("position_id").filter(lambda g: len(g) == 1).set_index("position_id")
one = one[one.index.isin(ins.index) & ~one.index.isin(exits[exits.entry == 3].position_id)]
j = ins.loc[one.index]
mv = (one.price - j.price) * np.where(j.type == 0, 1, -1) * j.volume
ok = mv.abs() > 0.01 * 100
k = one.profit[ok] / mv[ok]
print(f"K median {k.median():.2f}  IQR {k.quantile(.25):.2f}-{k.quantile(.75):.2f}  n={ok.sum()}")
K = k.median()

ins = ins[(ins.magic == MAGIC) & (ins.time >= START)]
ev = exits[exits.position_id.isin(ins.index)]
# a newer snapshot can hold positions that were still open at pull time: their basket is not
# finished, so every position opened from the first such entry on is left out (forward runs)
still_open = ins.volume - ev.groupby("position_id").volume.sum().reindex(ins.index).fillna(0) > 1e-9
if still_open.any():
    cut = ins.time[still_open].min()
    print(f"{int(still_open.sum())} positions still open; leaving out everything opened from {pd.to_datetime(cut, unit='s')}")
    ins = ins[ins.time < cut]; ev = exits[exits.position_id.isin(ins.index)]
if not np.allclose(ev.groupby("position_id").volume.sum().reindex(ins.index).fillna(0), ins.volume):
    sys.exit("exit volume does not match entry volume for some position")
g_ex = ev.groupby("position_id")
p = ins[["time", "time_msc", "type", "volume", "price"]].rename(columns={"time": "t0", "time_msc": "t0_msc", "price": "open_px"})
p["t1"] = g_ex.time.max()
p["pnl"] = g_ex.cash.sum() + ins.cash
p["cost"] = ins.commission + ins.swap + ins.fee + g_ex.commission.sum() + g_ex.swap.sum() + g_ex.fee.sum()
# the guard is an automatic program: magic 0 AND reason 3 (expert), comment
# "n_<price>_v". Manual closes (magic 0, reason 0 desktop / 1 mobile) are not guard.
ev = ev.assign(is_guard=(ev.magic == 0) & (ev.reason == 3))
p["guard"] = ev.groupby("position_id").is_guard.any()
p["sgn"] = np.where(p.type == 0, 1, -1)
p = p.sort_values("t0").reset_index()
print(f"{len(p)} positions of magic {MAGIC}; {ev.groupby('position_id').size().gt(1).sum()} with more than one exit deal")

# deal times and bar times must be on the same clock: each entry price has to
# lie inside the M1 bar of its own minute (spread-tolerant), and clearly less
# so when the clock is shifted by whole hours
bt_all = bars.time.values
def inside(shift):
    t = p.t0.values - shift * 3600
    i = np.clip(np.searchsorted(bt_all, t, side="right") - 1, 0, None)
    ok = bt_all[i] > t - 60
    return (ok & (p.open_px.values >= bars.low.values[i] - 0.5)
               & (p.open_px.values <= bars.high.values[i] + bars.spread.values[i] * 0.01 + 0.5)).mean()
align = {h: inside(h) for h in (-3, -2, -1, 0, 1, 2, 3)}
print("entry price inside its bar, by clock shift (h):", {h: round(v * 100, 1) for h, v in align.items()})
if align[0] < 0.99 or max(v for h, v in align.items() if h) > 0.5:
    sys.exit("deal and bar clocks do not line up - fix time zones first")

cid, end, c = [], -1, -1
for t0, t1 in zip(p.t0, p.t1):
    if t0 >= end:
        c += 1
    end = max(end, t1) if t0 < end else t1
    cid.append(c)
p["cid"] = cid
exits_by_pid = {pid: list(zip(g.time, g.volume)) for pid, g in ev.groupby("position_id")}
# per exit deal: (time, volume, cash) - partial exits are realised when they happen
exit_cash_by_pid = {pid: sorted(zip(g.time, g.volume, g.cash, g.commission + g.swap + g.fee))
                    for pid, g in ev.groupby("position_id")}
entry_cash = ins.cash
bt = bars.time.values; lo = bars.low.values; hi = bars.high.values
robot_pids = set(p.position_id)
# only positions OPENED after the robot started; older positions closing
# later belong to the capital the robot started with
t_robot = p.t0.min()
opened_after = set(x[(x.entry == ENTRY_IN) & (x.time >= t_robot)].position_id) - robot_pids
excl = deals.position_id.isin(opened_after) & (deals.symbol == "XAUUSDc")
deals["bal_robot"] = deals.bal_after - deals.cash.where(excl, 0).cumsum()
print(f"excluded positions' P&L since start: {deals.cash[excl].sum():.2f}")
bal_t = deals.time.values; bal_v = deals.bal_robot.values

def span(tt, ta, tb):
    if STRICT:
        return np.searchsorted(tt, ta, side="right"), np.searchsorted(tt, tb - 59, side="left")
    return np.searchsorted(tt, ta - 59), np.searchsorted(tt, tb, side="right")

out, lows_by_cid, levels_by_cid, paths_by_cid = [], {}, {}, {}
for c, g in p.groupby("cid"):
    t0, t1 = g.t0.min(), g.t1.max()
    i0 = np.searchsorted(bt, t0 - 59); i1 = np.searchsorted(bt, t1, side="right")
    worst, worst_t, runup_before, runup = 0.0, t0, 0.0, 0.0
    if i1 > i0:
        tt = bt[i0:i1]; fl_lo = np.zeros(len(tt)); fl_hi = np.zeros(len(tt))
        for r in g.itertuples():
            ta, vol = r.t0, r.volume
            for te, v in sorted(exits_by_pid[r.position_id]):   # one segment per exit
                a, z = span(tt, ta, te)
                fl_lo[a:z] += r.sgn * vol * (lo[i0 + a:i0 + z] - r.open_px) * K
                fl_hi[a:z] += r.sgn * vol * (hi[i0 + a:i0 + z] - r.open_px) * K
                vol = round(vol - v, 2); ta = te
            # costs: commission is charged at entry; swap is only booked at exit,
            # so it is counted from entry too (conservative, total swap is tiny)
            a, z = span(tt, r.t0, r.t1)
            fl_lo[a:z] += r.cost; fl_hi[a:z] += r.cost
        # realised cash of positions already closed inside the basket stays in its path:
        # each exit's price profit at its own time, the costs once the position is fully
        # closed (while open, fl already carries them) - so a realised loss plus a later
        # floating loss on the remaining positions is one combined trough
        rc = np.zeros(len(tt))
        for r in g.itertuples():
            for te, v, cash, cost in exit_cash_by_pid[r.position_id]:
                rc[np.searchsorted(tt, te, side="left"):] += cash - cost
            rc[np.searchsorted(tt, r.t1, side="left"):] += r.cost
        fl = np.minimum(fl_lo, fl_hi) + rc
        jx = fl.argmin(); worst, worst_t = fl[jx], tt[jx]
        best_all = np.maximum(fl_lo, fl_hi) + rc         # optimistic side, for peaks
        runup_before, runup = best_all[:jx + 1].max(), best_all.max()
        # record lows with the peak seen before each one: a simulated guard at
        # level L cuts at the first record low <= L, and its peak is the run-up
        # up to that minute (not up to the final trough)
        run_min = np.minimum.accumulate(fl); new_low = np.r_[True, run_min[1:] < run_min[:-1]]
        idx = np.where(new_low & (fl < 0))[0]
        kb0 = np.searchsorted(bal_t, t0, side="left") - 1
        b0 = bal_v[kb0] if kb0 >= 0 else 0
        if len(idx) and b0 > 0:
            peaks = np.maximum.accumulate(best_all)[idx]
            lows_by_cid[c] = np.c_[fl[idx] / b0 * 100, peaks / b0 * 100]
        if b0 > 0 and worst / b0 <= -0.03:               # the full minute path of deep baskets (BD_RESCUE_PLAN.md)
            paths_by_cid[c] = np.c_[tt, fl / b0 * 100, best_all / b0 * 100]
        # state when the k-th position of the basket opens (k = 1..n), using only
        # what was known at that moment:
        # - cut value = P&L already realised by closed positions + the open positions
        #   (including the k-th) marked at the k-th deal's own price (a real quote at
        #   that second, no bar high/low), plus their costs;
        # - peak / low so far from the basket equity path (floating + realised so far)
        #   over minutes that ended before the k-th deal.
        # Partial exits are realised at their own time and reduce the marked volume.
        if b0 > 0:
            eq_lo, eq_hi = fl, best_all                  # fl and best_all already include rc
            # deal order by milliseconds (then ticket order), so several entries in
            # one second are taken one by one and each depth is recorded right after
            # the entry that reached it, priced at that entry
            gs = g.sort_values(["t0_msc", "position_id"]); rows = []
            t1s = gs.t1.values
            for j, (tk, pxk) in enumerate(zip(gs.t0.values, gs.open_px.values)):
                done = np.arange(len(gs)) <= j                      # entries up to this one
                op = done & (t1s > tk)
                kk = int(op.sum())
                if kk <= len(rows):
                    continue
                # realised: entry commission + every exit deal done by tk; mark: the volume
                # still open at this entry's price. Commission is charged at entry only
                # (exit deals carry swap only); swap accrued up to tk is not known in the
                # data and is left out (all swap of the robot: -261 cents).
                realised, mark = 0.0, 0.0
                for r in gs[done].itertuples():
                    realised += entry_cash[r.position_id]
                    left = r.volume
                    for te, v, cash, cost in exit_cash_by_pid[r.position_id]:
                        if te <= tk:
                            realised += cash; left = round(left - v, 2)
                    if left > 0:
                        mark += r.sgn * left * (pxk - r.open_px) * K
                b = np.searchsorted(tt, tk - 60, side="right")      # minutes finished before tk
                peak = max(eq_hi[:b].max(), 0) if b else 0.0
                low = min(eq_lo[:b].min(), 0) if b else 0.0
                # columns: k, time, realised %, open positions marked %, peak so far %, low so far %
                row = (kk, tk, realised / b0 * 100, mark / b0 * 100, peak / b0 * 100, low / b0 * 100)
                rows.append(row)
            levels_by_cid[c] = np.array(rows)
    kb = np.searchsorted(bal_t, t0, side="left") - 1
    bal0 = bal_v[kb] if kb >= 0 else 0
    out.append(dict(cid=c, t0=t0, t1=t1, n=len(g), maxlots=g.volume.sum(),
                    side=",".join(sorted(set(np.where(g.sgn > 0, "B", "S")))),
                    pnl=g.pnl.sum(), mae=worst, mae_t=worst_t, bal0=bal0, guard=g.guard.any(),
                    runup_before=runup_before, runup=runup))
o = pd.DataFrame(out)
o["pnl_pct"] = o.pnl / o.bal0 * 100; o["mae_pct"] = o.mae / o.bal0 * 100
o["runup_before_pct"] = o.runup_before / o.bal0 * 100; o["runup_pct"] = o.runup / o.bal0 * 100
OUT = os.environ.get("JEV_DERIVED", "data/derived/bd1")   # forward runs write to their own folder
os.makedirs(OUT, exist_ok=True)
o.to_csv(f"{OUT}/clusters_strict.csv" if STRICT else f"{OUT}/clusters.csv", index=False)
np.savez_compressed(f"{OUT}/record_lows_strict.npz" if STRICT else f"{OUT}/record_lows.npz",
                    **{str(k): v for k, v in lows_by_cid.items()})
np.savez_compressed(f"{OUT}/levels_strict.npz" if STRICT else f"{OUT}/levels.npz",
                    **{str(k): v for k, v in levels_by_cid.items()})
p.to_csv(f"{OUT}/positions_strict.csv" if STRICT else f"{OUT}/positions.csv", index=False)   # per position, with its basket
np.savez_compressed(f"{OUT}/paths_strict.npz" if STRICT else f"{OUT}/paths.npz",
                    **{str(k): v for k, v in paths_by_cid.items()})
print(len(o), "baskets;", o.guard.sum(), "with a guard (magic 0) close")
for X in (5, 10, 15, 20):
    print(f"MAE <= -{X}%: {(o.mae_pct <= -X).sum()}")
show = lambda d: d.assign(t0=pd.to_datetime(d.t0, unit="s")).round(2).to_string()
print(show(o[o.guard & (o.pnl_pct < -5)][["t0", "n", "maxlots", "pnl_pct", "mae_pct", "bal0"]]))
print("worst non-guard baskets:"); print(show(o[~o.guard].nsmallest(10, "mae_pct")[["t0", "n", "maxlots", "pnl_pct", "mae_pct"]]))
