import sys, numpy as np, pandas as pd
from inputs import max_drawdown, peak_before_cut, FORWARD_START, FORWARD_END, forward_coverage
o = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else "data/derived/bd1/clusters_strict.csv")
o["d"] = pd.to_datetime(o.t0, unit="s")
LOWS = dict(np.load(sys.argv[1].replace("clusters", "record_lows").replace(".csv", ".npz") if len(sys.argv) > 1
                    else "data/derived/bd1/record_lows_strict.npz"))
# the real guard closes: crash baskets in the history; in the forward window every guard
# close, whatever its loss (not selected by outcome)
real = o.guard & ((o.pnl_pct < -5) | (o.d >= FORWARD_START))
SLIP = 0.5                                  # extra % lost past the level (gap/slippage), ASSUMED
# paper continuation of each real guard cut (after_guard.py): worst floating % before breakeven.
# Lower bound on the loss: the EA would have kept adding levels.
CONT = pd.read_csv("data/derived/bd1/after_guard.csv").set_index("cid")
def run(sub, X, unknown):
    n_unres = 0
    r = sub.pnl_pct.values.copy() / 100
    tr = sub.mae_pct.values / 100
    hit = sub.mae_pct.values <= -X
    r[hit] = -(X + SLIP) / 100
    # real guard closed first, before reaching X: continuation unknown
    unk = real.loc[sub.index].values & ~hit
    if unknown == "worst": r[unk] = -(X + SLIP) / 100
    elif unknown == "cont":   # cut at X only if the paper continuation reached X
        w = CONT.reindex(sub.cid.values[unk])
        idx = np.where(unk)[0]
        lo_, up_ = w.worst_lower.values, w.worst_upper.values  # NaN (no continuation) -> False below
        back = w.recovered.fillna(False).values.astype(bool)
        crossed = lo_ <= -X                                    # crossed X before the touching bar
        # unresolved: neither crossed nor back to breakeven (window cut short / no continuation),
        # or X is crossed only inside the touching bar (order unknown).
        # Scored as a cut (conservative) and counted separately.
        unres = (~crossed & ~back) | (~crossed & back & (up_ <= -X))
        deep = crossed | unres
        r[idx[deep]] = -(X + SLIP) / 100; r[idx[~deep]] = 0.0
        tr = tr.copy(); tr[idx[~deep]] = np.minimum(tr[idx[~deep]], up_[~deep] / 100)   # keep the low seen before the guard
        unk = unk.copy(); unk[idx[~deep]] = False                 # recovered: not a cut
        n_unres = int(unres.sum())
    else: r[unk] = sub.loc[unk, "pnl_pct"].clip(lower=None).values * 0 + 0.02  # recovers with +2%
    cut = hit | (unk & (unknown != "best"))
    tr = np.where(cut, np.minimum(r, 0), tr)   # a cut basket bottoms at the cut
    rb = sub.runup_before_pct.values / 100      # floating peak before the trough
    rb = np.where(hit, [peak_before_cut(LOWS, c, -X) / 100 if h else 0 for c, h in zip(sub.cid.values, hit)], rb)
    ru = np.where(cut, rb, sub.runup_pct.values / 100)   # a cut basket has no later run-up
    eq, dd = max_drawdown(r, tr, rb, ru)       # drawdown from floating peaks to floating lows
    return eq[-1], dd, hit.sum(), unk.sum(), n_unres
periods = [("all 2025-11..2026-10", o[o.d < FORWARD_START]), ("Nov-May", o[o.d < "2026-06-01"]),
           ("Jun-Oct", o[(o.d >= "2026-06-01") & (o.d < FORWARD_START)])]
fw = o[(o.d >= FORWARD_START) & (o.d < FORWARD_END)]
if len(fw):
    periods.append((f"FORWARD {FORWARD_START}..2027-04-15", fw))
    # the verdict is due only when every forward guard cut has its full 10-day continuation
    fc = CONT.reindex(fw.cid[real.loc[fw.index]].values)
    covered, still_open = forward_coverage()   # snapshot coverage, not the date of the last basket
    print("forward verdict ready:", bool(covered and fc.window_complete.fillna(False).all()),
          f"(snapshots cover the window: {covered}, positions still open: {still_open}, "
          f"{fc.window_complete.fillna(False).sum()}/{len(fc)} guard continuations complete)")
for name, sub in periods:
    eq, dd = max_drawdown(sub.pnl_pct.values / 100, sub.mae_pct.values / 100,
                          sub.runup_before_pct.values / 100, sub.runup_pct.values / 100)
    print(f"\n== {name}: actual x{eq[-1]:.2f}, maxDD incl. floating {dd:.1f}%")
    print(" X%   x_end(worst)  maxDD   x_end(best)  maxDD   x_end(cont)  maxDD  cuts unknown unresolved")
    for X in [5, 8, 10, 12, 15, 18, 20, 22, 25, 30, 40, 50, 60, 70]:
        a = run(sub, X, "worst"); b = run(sub, X, "best"); c = run(sub, X, "cont")
        print(f"{X:3d}  {a[0]:9.2f}  {a[1]:7.1f}  {b[0]:9.2f}  {b[1]:6.1f}  {c[0]:9.2f}  {c[1]:6.1f}  {a[2]:4d} {a[3]:4d} {c[4]:4d}")
