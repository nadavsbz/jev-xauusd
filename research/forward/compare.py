"""Daily paper comparison for account 1 from the forward start (docs/BD1_GUARD_FORWARD.md window),
asked for by the user on 2026-10-16. Variants, fixed before any forward data:
  actual        - what the account did (robot baskets only)
  half_floor    - half the lot size, and every basket cut at -15% of its starting balance
  half_floor_dir- the same, plus directional blocking (no entry against a gold move of 1% or
                  more over the previous hour; docs/DIRECTION_BLOCK_PLAN.md, a NO-GO candidate)
ASSUMED: returns scale linearly with the lot (half lot = half the basket P&L and floating);
the -15% cut adds 0.5% slippage, as in guard_sim.py; blocked entries are removed and the
rest of the basket stays as it was (direction_block.py).
Usage (snapshot and derived folder through JEV_DEALS_SNAPSHOT, JEV_RATES_SNAPSHOT, JEV_DERIVED):
  python research/forward/compare.py OUT_JSON"""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "crash"))
import direction_block as db  # noqa: E402

START = pd.Timestamp("2026-10-16")
FLOOR, SLIP, LOT = 0.15, 0.005, 0.5


def floor_half(r, tr, rb, ru):
    r, tr, rb, ru = r * LOT, tr * LOT, rb * LOT, ru * LOT
    hit = tr <= -FLOOR
    r = np.where(hit, -(FLOOR + SLIP), r); tr = np.where(hit, -(FLOOR + SLIP), tr)
    return r, tr, rb, ru


def daily(r, tr, rb, ru, days):
    """Cumulative multiple and max drawdown (floating included) at the end of each day."""
    out = []
    for d in sorted(set(days)):
        m = days <= d
        if not m.any():
            continue
        eq, dd = db.max_drawdown(r[m], tr[m], rb[m], ru[m])
        out.append({"day": str(d.date()), "mult": round(float(eq[-1]), 4), "dd": round(float(dd), 2)})
    return out


def main():
    o = db.o
    sel = pd.to_datetime(o.t0, unit="s") >= START
    days = pd.to_datetime(o.t0[sel], unit="s").dt.normalize().values
    base = [a[sel.values] / 100 for a in (o.pnl_pct.values, o.mae_pct.values, o.runup_before_pct.values, o.runup_pct.values)]
    blocked = (db.move_pct(1) * db.p.sgn.values <= -1.0)
    q = db.p.assign(blk=blocked); keep = q[~q.blk]
    d = [a.copy() for a in (o.pnl_pct.values / 100, o.mae_pct.values / 100, o.runup_before_pct.values / 100, o.runup_pct.values / 100)]
    for c in set(q.cid[q.blk]):
        k = int(np.where(o.cid.values == c)[0][0])
        if not sel.values[k]:
            continue
        g = keep[keep.cid == c]
        vals = (0.0, 0.0, 0.0, 0.0) if len(g) == 0 else db.reprice(g, o.bal0.values[k])
        for a, v in zip(d, vals):
            a[k] = v
    d = [a[sel.values] for a in d]
    res = {"generated_utc": pd.Timestamp.utcnow().isoformat(), "baskets": int(sel.sum()),
           "variants": {"actual": daily(*base, pd.DatetimeIndex(days)),
                        "half_floor": daily(*floor_half(*base), pd.DatetimeIndex(days)),
                        "half_floor_dir": daily(*floor_half(*d), pd.DatetimeIndex(days))}}
    json.dump(res, open(sys.argv[1], "w"), indent=1)
    # long rows for the dashboard: one row per day and variant
    names = {"actual": "בפועל", "half_floor": "חצי לוט + רצפה 15%", "half_floor_dir": "חצי לוט + רצפה + חסימת כיוון"}
    rows = [{"day": r["day"], "variant": names[k], "mult": r["mult"], "dd": r["dd"]}
            for k, v in res["variants"].items() for r in v]
    json.dump(rows, open(sys.argv[1].replace(".json", "_rows.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v[-1] if v else None for k, v in res["variants"].items()}), res["baskets"], "baskets")


if __name__ == "__main__":
    main()
