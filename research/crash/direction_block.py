"""Directional blocking, stage B (docs/DIRECTION_BLOCK_PLAN.md).
Usage:
  python research/crash/direction_block.py            # sanity check + choice on Nov-May (all 12 combos)
  python research/crash/direction_block.py --test H X # the chosen combo on Jun-Oct, once
A blocked entry is removed; the other entries stay as they were (main version). Version B also
removes every later entry of the same side in the same basket. Baskets are re-priced minute by
minute: floating of the remaining open positions (worse of bar low/high) plus entry commission,
and each position's realised net from its exit on."""
import sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bd1"))
from inputs import load, START, MAGIC, max_drawdown  # noqa: E402

K = 100
SPLIT = pd.Timestamp("2026-06-01").timestamp()
deals, bars = load()
ins = deals[(deals.entry == 0) & (deals.magic == MAGIC) & (deals.time >= START)]
outs = deals[deals.entry.isin((1, 3))]
p = ins.set_index("position_id")[["time", "type", "volume", "price", "commission"]].copy()
p["net"] = (outs.profit + outs.commission + outs.swap + outs.fee).groupby(outs.position_id).sum().reindex(p.index).fillna(0) + p.commission
p["t1"] = outs.groupby("position_id").time.max().reindex(p.index)
p["sgn"] = np.where(p.type == 0, 1, -1)
# one exposure segment per exit deal (review: partial exits reduce the marked volume when they happen)
_oc = outs.assign(cash=outs.profit + outs.commission + outs.swap + outs.fee)
EXITS = {pid: sorted(zip(g.time, g.volume, g.cash)) for pid, g in _oc[_oc.position_id.isin(p.index)].groupby("position_id")}
o = pd.read_csv(os.path.join(os.environ.get("JEV_DERIVED", "data/derived/bd1"), "clusters_strict.csv"))
i = np.searchsorted(o.t0.values, p.time.values, side="right") - 1
ok = (i >= 0) & (p.time.values <= o.t1.values[np.maximum(i, 0)])
p["cid"] = np.where(ok, o.cid.values[np.maximum(i, 0)], -1)
p = p[p.cid >= 0].sort_values("time")
bt = bars.time.values; lo = bars.low.values; hi = bars.high.values; cl = bars.close.values
# the last minute bar CLOSED before the entry (review PR #28): floor the entry to its minute, take the bar before
k0 = np.searchsorted(bt, p.time.values // 60 * 60, side="left") - 1


def move_pct(h):
    kh = np.searchsorted(bt, (p.time.values - h * 3600) // 60 * 60, side="left") - 1
    return (cl[k0] - cl[np.maximum(kh, 0)]) / cl[np.maximum(kh, 0)] * 100


def reprice(g, b0):
    """pnl, trough, run-up before trough and run-up (all as fractions of b0) of the remaining positions."""
    t0, t1 = g.time.min(), g.t1.max()
    a0 = np.searchsorted(bt, t0, side="right"); a1 = np.searchsorted(bt, t1 - 59, side="left")
    if a1 <= a0:
        return g.net.sum() / b0, min(g.net.sum(), 0) / b0, 0.0, max(g.net.sum(), 0) / b0
    tt = bt[a0:a1]; f_lo = np.zeros(len(tt)); f_hi = np.zeros(len(tt)); rc = np.zeros(len(tt))
    for r in g.itertuples():
        a = np.searchsorted(tt, r.time, side="right"); z = np.searchsorted(tt, r.t1 - 59, side="left")
        f_lo[a:z] += r.commission; f_hi[a:z] += r.commission          # entry commission until fully closed
        ex = EXITS.get(r.Index, [])
        if not ex:                                                    # no exit deal: as before
            f_lo[a:z] += r.sgn * r.volume * (lo[a0 + a:a0 + z] - r.price) * K
            f_hi[a:z] += r.sgn * r.volume * (hi[a0 + a:a0 + z] - r.price) * K
            rc[np.searchsorted(tt, r.t1, side="left"):] += r.net
            continue
        for te, v, cash in ex:                                        # each exit's volume is open until its own exit
            ze = np.searchsorted(tt, te - 59, side="left")
            f_lo[a:ze] += r.sgn * v * (lo[a0 + a:a0 + ze] - r.price) * K
            f_hi[a:ze] += r.sgn * v * (hi[a0 + a:a0 + ze] - r.price) * K
            rc[np.searchsorted(tt, te, side="left"):] += cash
        rc[np.searchsorted(tt, r.t1, side="left"):] += r.commission   # entry commission realised at the last exit
    worst = np.minimum(f_lo, f_hi) + rc; best = np.maximum(f_lo, f_hi) + rc
    j = worst.argmin()
    return g.net.sum() / b0, min(worst[j], 0) / b0, max(best[:j + 1].max(), 0) / b0, max(best.max(), 0) / b0


def run(h=None, x=None, version="main"):
    blocked = np.zeros(len(p), bool) if h is None else ((move_pct(h) * p.sgn.values <= -x))
    q = p.assign(blk=blocked)
    if version == "B" and h is not None:
        q["blk"] = q.groupby(["cid", "type"]).blk.cummax()
    hit = set(q.cid[q.blk])
    r, tr, rb, ru = o.pnl_pct.values / 100, o.mae_pct.values / 100, o.runup_before_pct.values / 100, o.runup_pct.values / 100
    r, tr, rb, ru = r.copy(), tr.copy(), rb.copy(), ru.copy()
    keep = q[~q.blk]
    for c in hit:
        g = keep[keep.cid == c]; k = int(np.where(o.cid.values == c)[0][0])
        if len(g) == 0:
            r[k] = tr[k] = rb[k] = ru[k] = 0.0
        else:
            r[k], tr[k], rb[k], ru[k] = reprice(g, o.bal0.values[k])
    res = {}
    for name, m in (("nov_may", o.t0.values < SPLIT), ("jun_oct", o.t0.values >= SPLIT)):
        eq, dd = max_drawdown(r[m], tr[m], rb[m], ru[m])
        res[name] = (round(float(eq[-1]), 2), round(dd, 1))
    return res, int(q.blk.sum()), len(hit)


if __name__ == "__main__":
    # sanity: re-pricing the actual baskets (nothing blocked) must reproduce clusters_strict closely
    smp = o.sample(300, random_state=1)
    d = [reprice(p[p.cid == c], b) for c, b in zip(smp.cid, smp.bal0) if (p.cid == c).any()]
    d = np.array(d) * 100
    print("sanity (300 baskets): max |pnl diff|", round(np.abs(d[:, 0] - smp.pnl_pct.values[:len(d)]).max(), 3),
          "max |mae diff|", round(np.abs(d[:, 1] - np.minimum(smp.mae_pct.values[:len(d)], 0)).max(), 3), "pp")
    print("actual:", run()[0])
    if "--test" in sys.argv:
        h, x = int(sys.argv[-2]), float(sys.argv[-1])
        for v in ("main", "B"):
            res, nb, nc = run(h, x, v)
            print(f"TEST H={h} X={x} {v}: jun_oct x{res['jun_oct'][0]} / {res['jun_oct'][1]}% | blocked {nb} entries in {nc} baskets")
        sys.exit()
    rows = []
    for h in (1, 2, 4):
        for x in (0.3, 0.5, 0.75, 1.0):
            res, nb, nc = run(h, x)
            rows.append(dict(H=h, X=x, mult=res["nov_may"][0], dd=res["nov_may"][1], blocked=nb, baskets=nc))
    t = pd.DataFrame(rows)
    print(t.to_string(index=False))
    base = run()[0]["nov_may"][0]
    el = t[t["mult"] >= 0.8 * base].copy()
    if len(el):
        best = el.dd.max()
        top = el[el.dd >= best - 0.5].sort_values("mult", ascending=False).iloc[0]
        print(f"chosen on Nov-May: H={int(top.H)} X={top.X} (x{top['mult']} / {top.dd}%)")
    else:
        print("no combination keeps 80% of the actual multiplier: NO-GO")
