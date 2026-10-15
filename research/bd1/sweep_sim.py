"""Split as "one trading account + one reserve": every week the trading account
is reset to a fixed size B - profit above B is swept to the reserve, a shortfall
is refilled from the reserve (while it lasts). Lots follow the trading balance,
so the robot always risks about B; total wealth = trading + reserve.

Method written together with its first results (2026-10-16), so the three
values of B are NOT a pre-registered choice; only the forward test in
docs/NIGHT1_SPLIT_SWEEP.md is registered ahead of its data.
- Basket returns are the real ones (real guard included), as fractions of the
  trading balance at basket start; floating lows/peaks as in the report.
- B is a fixed share of the starting capital (the rest starts in the reserve). Sweep/refill on the first basket
  of each ISO week (a basket is never split).
- Variants: weekly sweep with refill, weekly sweep without refill, and no
  sweep (the real compounding account) for reference; trading account size
  B = 100%, 50% or 33% of the starting capital (all reported, none chosen).
- Reported: end wealth multiple, max drawdown of TOTAL wealth (floating
  included), for Nov-May, Jun-Oct and all. B is not optimised.
"""
import numpy as np, pandas as pd

o = pd.read_csv("data/derived/bd1/clusters_strict.csv"); o["d"] = pd.to_datetime(o.t0, unit="s")


def sim(sub, mode, frac=1.0, lots="per_basket"):
    """lots="per_basket": lots follow the trading balance before every basket
    (auto-lot). lots="weekly": lots are fixed at the weekly reset and kept all
    week; a basket then earns the real basket P&L scaled by (trading balance at
    the reset / real robot balance at the reset), i.e. ASSUMED the real lots
    were proportional to the real balance."""
    r = sub.pnl_pct.values / 100; lo = np.minimum(sub.mae_pct.values / 100, r)
    hi = np.maximum(np.maximum(sub.runup_pct.values, 0) / 100, r)
    hb = np.maximum(sub.runup_before_pct.values, 0) / 100
    bal0 = sub.bal0.values
    wk = sub.d.dt.isocalendar().week.values + 100 * sub.d.dt.isocalendar().year.values
    B = frac; trade, res = B, 1.0 - frac    # trading account starts at frac of the capital
    w0 = trade + res; peak, worst = w0, 0.0
    expo = trade / bal0[0]                  # money per cent of real P&L (weekly mode)
    for i in range(len(r)):
        new_week = i == 0 or wk[i] != wk[i - 1]
        if mode != "none" and new_week:
            if trade > B:
                res += trade - B; trade = B
            elif mode == "refill" and trade < B:
                take = min(B - trade, res); res -= take; trade += take
        if new_week:
            expo = trade / bal0[i]
        size = trade if lots == "per_basket" else expo * bal0[i]   # money the basket's % applies to
        w_start = trade + res
        p_in = max(peak, w_start + size * hb[i])
        worst = min(worst, (w_start + size * lo[i]) / p_in - 1)
        peak = max(peak, w_start + size * hi[i])
        trade += size * r[i]
        if trade <= 0:
            trade = 0.0
        w = trade + res
        worst = min(worst, w / max(peak, w) - 1); peak = max(peak, w)
    return (trade + res) / w0, worst * 100


from inputs import FORWARD_START, FORWARD_END
periods = [("Nov-May", o[o.d < "2026-06-01"]), ("Jun-Oct", o[(o.d >= "2026-06-01") & (o.d < FORWARD_START)]),
           ("all", o[o.d < FORWARD_START])]
fw = o[(o.d >= FORWARD_START) & (o.d < FORWARD_END)]
if len(fw):   # forward test of the weekly-lot 33% variant, docs/NIGHT1_SPLIT_SWEEP.md
    periods.append(("FORWARD", fw))
for name, sub in periods:
    print(f"== {name}")
    for frac in [1.0, 0.5, 0.33]:
        for mode in ["none", "refill", "norefill"]:
            if mode == "none" and frac < 1:
                continue
            for lots in ["per_basket", "weekly"]:
                x, dd = sim(sub.reset_index(drop=True), mode, frac, lots)
                print(f"  trade {frac:4.2f} of capital  {mode:9s} lots {lots:10s} wealth x{x:6.2f}  max DD of total wealth {dd:6.1f}%")
