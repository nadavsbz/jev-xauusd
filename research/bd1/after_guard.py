"""Hold, on paper, the magic-5555 positions the guard closed in each crash
basket, from the guard close until price returns to their breakeven (max
10 days). Lower bound: the EA would have kept adding levels."""
import numpy as np, pandas as pd
from inputs import load, MAGIC, FORWARD_START, covered_until

K = 100.0   # cents per 1.0 price move per lot, calibrated in clusters.py
deals, bars = load()
o = pd.read_csv("data/derived/bd1/clusters_strict.csv")
x = deals[deals.symbol == "XAUUSDc"]
ins = x[(x.entry == 0) & (x.magic == MAGIC)].set_index("position_id")
ex = x[x.entry.isin((1, 3))].assign(is_guard=lambda e: (e.magic == 0) & (e.reason == 3))  # guard = automatic close
ex = ex.groupby("position_id").agg(t1=("time", "max"), guard=("is_guard", "any"))
p = ins[["time", "type", "volume", "price"]].join(ex, how="inner")
# commission + swap + fee of each position (entry and exit deals): part of its loss
p["cost"] = x.assign(c=x.commission + x.swap + x.fee).groupby("position_id").c.sum().reindex(p.index).fillna(0)
bt, lo, hi, cl = bars.time.values, bars.low.values, bars.high.values, bars.close.values
out = []
COVERED = covered_until()
# history: the crash baskets (guard close with a loss over 5%); forward: every guard close,
# not selected by its outcome
o["d"] = pd.to_datetime(o.t0, unit="s")
for _, c in o[o.guard & ((o.pnl_pct < -5) | (o.d >= FORWARD_START))].iterrows():
    g = p[(p.time >= c.t0) & (p.time <= c.t1) & p.guard]
    sgn = np.where(g.type == 0, 1, -1); vol = g.volume.values; px = g.price.values
    net = (sgn * vol).sum(); be = (sgn * vol * px).sum() / net
    tg = g.t1.max(); i0 = np.searchsorted(bt, tg); i1 = np.searchsorted(bt, tg + 10 * 86400)
    cost = g.cost.sum()                               # <= 0; swap after the cut is not added
    fl = net * ((lo if net > 0 else hi)[i0:i1] - be) * K + cost
    # recovery = the favourable extreme TOUCHES breakeven after costs (high for a buy, low for a sell)
    fav = net * ((hi if net > 0 else lo)[i0:i1] - be) * K + cost
    rec = np.where(fav >= 0)[0]
    k = rec[0] if len(rec) else len(fl)
    # inside the touching bar the order of touch and low is unknown: report both bounds
    lower = fl[:k].min() if k > 0 else 0.0          # bars strictly before the touch
    upper = fl[:k + 1].min() if len(rec) else lower  # including the touching bar
    print(f"{pd.to_datetime(c.t0, unit='s'):%Y-%m-%d} side={'BUY' if net > 0 else 'SELL'} lots={abs(net):5.2f} "
          f"guard loss={c.pnl_pct:6.1f}%  further worst before breakeven: {lower / c.bal0 * 100:7.1f}% "
          f"(up to {upper / c.bal0 * 100:7.1f}% if the touching bar's low came first)  back to breakeven: "
          + (f"after {(bt[i0 + k] - tg) / 3600:.1f}h" if len(rec) else "no, not within 10 days"))
    # window_complete: all 10 days lie inside the calendar-checked range of the bars
    # (load() verifies completeness up to the day before the pull), so 'not recovered' is final
    # worst_lower: bars before the touch; worst_upper: including the touching bar
    # (order of touch and low inside that bar is unknown)
    out.append(dict(cid=c.cid, worst_lower=lower / c.bal0 * 100, worst_upper=upper / c.bal0 * 100,
                    recovered=bool(len(rec)), t_guard=int(tg),
                    window_complete=bool(tg + 10 * 86400 <= COVERED)))
# used by guard_sim.py to score guard levels beyond the real cut
pd.DataFrame(out).to_csv("data/derived/bd1/after_guard.csv", index=False)
