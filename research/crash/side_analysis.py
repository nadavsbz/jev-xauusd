"""Directional blocking, step A (descriptive, account 1, all of Nov 2025 - Oct 2026):
in each deep basket (MAE <= -10%), which side carried the loss, and was the gold move already
visible before the losing side's entries? No rule is chosen here."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bd1"))
from inputs import load, START, MAGIC  # noqa: E402

K = 100      # cents per 1.0 price unit per lot (clusters.py: K median 100)
LOOK_H = 2   # hours of gold move seen before an entry
deals, bars = load()
ins = deals[(deals.entry == 0) & (deals.magic == MAGIC) & (deals.time >= START)]
outs = deals[deals.entry.isin((1, 3))]
cash = (outs.profit + outs.commission + outs.swap + outs.fee).groupby(outs.position_id).sum()
p = ins.set_index("position_id")[["time", "type", "volume", "price", "commission"]]
p["net"] = cash.reindex(p.index).fillna(0) + p.commission
p["t1"] = outs.groupby("position_id").time.max().reindex(p.index)
p["sgn"] = np.where(p.type == 0, 1, -1)
o = pd.read_csv("data/derived/bd1/clusters_strict.csv")
bt = bars.time.values; cl = bars.close.values
i = np.searchsorted(o.t0.values, p.time.values, side="right") - 1
p["cid"] = np.where((i >= 0) & (p.time.values <= o.t1.values[np.maximum(i, 0)]), o.cid.values[np.maximum(i, 0)], -1)
# gold move over the LOOK_H hours that ended just before the entry, in % ; "against" = position opposite to it
# the last minute bar CLOSED before the entry (review PR #28)
k0 = np.searchsorted(bt, p.time.values // 60 * 60, side="left") - 1
kh = np.searchsorted(bt, (p.time.values - LOOK_H * 3600) // 60 * 60, side="left") - 1
p["move_pct"] = (cl[k0] - cl[np.maximum(kh, 0)]) / cl[np.maximum(kh, 0)] * 100
p["against"] = p.move_pct * p.sgn < 0
deep = o[o.mae_pct <= -10]
rows = []
for r in deep.itertuples():
    g = p[p.cid == r.cid]
    km = np.searchsorted(bt, r.mae_t, side="right") - 1
    openm = g[(g.time <= r.mae_t) & (g.t1 > r.mae_t)]
    fl = (openm.sgn * openm.volume * (cl[km] - openm.price) * K).groupby(openm.type).sum()
    real = g[g.t1 <= r.mae_t].groupby("type").net.sum()
    side_pnl = fl.add(real, fill_value=0)
    lose = int(side_pnl.idxmin()) if len(side_pnl) else -1
    lg = g[g.type == lose]
    rows.append(dict(t0=pd.to_datetime(r.t0, unit="s"), mae=round(r.mae_pct, 1),
                     buy_pnl=round(side_pnl.get(0, 0) / r.bal0 * 100, 1), sell_pnl=round(side_pnl.get(1, 0) / r.bal0 * 100, 1),
                     losing="BUY" if lose == 0 else "SELL", n_lose=len(lg),
                     lose_against=round(lg.against.mean() * 100), lose_move_med=round(lg.move_pct.abs().median(), 2)))
t = pd.DataFrame(rows)
print(t.to_string(index=False))
print("\nloss share of the losing side (median):",
      round((t[["buy_pnl", "sell_pnl"]].min(axis=1) / t.mae).median(), 2))
other = p[~p.cid.isin(deep.cid)]
lose_all = pd.concat([p[(p.cid == c) & (p.type == (0 if s == "BUY" else 1))] for c, s in zip(deep.cid, t.losing)])
print(f"entries against the prior {LOOK_H}h move: losing side of deep baskets {lose_all.against.mean():.0%}, all other entries {other.against.mean():.0%}")
print(f"|prior {LOOK_H}h move| median: losing side {lose_all.move_pct.abs().median():.2f}%, other entries {other.move_pct.abs().median():.2f}%")
for x in [0.3, 0.5, 0.75, 1.0]:
    a = lose_all[(lose_all.move_pct.abs() >= x) & lose_all.against]; b = other[(other.move_pct.abs() >= x) & other.against]
    print(f"against a move >= {x}%: losing-side entries {len(a)} of {len(lose_all)}, other entries {len(b)} of {len(other)}")

# fair baseline: a grid adds levels after an adverse move by design, so compare the losing side
# with LATER levels (2nd entry on) of ordinary baskets, not with all other entries
p = p.sort_values("time"); p["lvl"] = p.groupby("cid").cumcount() + 1
later = p[(~p.cid.isin(deep.cid)) & (p.lvl >= 2) & (p.cid >= 0)]
print(f"\nordinary baskets, levels 2+: {len(later)} entries, against the prior {LOOK_H}h move {later.against.mean():.0%}")
for x in [0.3, 0.5, 0.75, 1.0]:
    print(f"  against a move >= {x}%: {int((later.against & (later.move_pct.abs() >= x)).sum())} of {len(later)}")
