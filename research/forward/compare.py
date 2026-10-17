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
    ru = np.where(hit, rb, ru)          # a cut basket has no run-up after the cut (as in guard_sim.py)
    return r, tr, rb, ru


def mix_chosen(r, tr, days, rb=None, ru=None):
    """Account 1 at the exposure of the chosen mix (docs/PORTFOLIO_PLAN.md): 90% of capital at f=0.2 with
    the 15% floor (an intraday breach stops it for good) and 10% CASH. Bull Scalper is not traded
    forward, so this is NOT scenario A's mix: it tracks only its account-1 part. Daily multiple and
    drawdown of the whole capital, booked on basket close days."""
    out = []; eq, peak, alive, tot_peak, worst = 0.9, 0.9, True, 1.0, 0.0
    rb = np.zeros(len(r)) if rb is None else rb; ru = np.zeros(len(r)) if ru is None else ru
    by_day = pd.DataFrame({"r": r * 0.2, "tr": tr * 0.2, "rb": rb * 0.2, "ru": ru * 0.2, "d": days}).groupby("d")
    for d, g in by_day:
        for rr, tt, bb, uu in zip(g.r, g.tr, g.rb, g.ru):
            if not alive:
                break
            # a floating peak before the trough raises the peak first (as in optimize.py, review)
            peak = max(peak, eq * (1 + max(bb, 0)))
            low = eq * (1 + min(tt, 0)); close = eq * (1 + rr); line = peak * 0.85
            if min(low, close) <= line:       # trough against the peak that existed before it:
                eq = line; alive = False   # closed AT the floor, nothing after the crossing (review)
                low = line                 # the path ends at the floor too (review: consistent with eq)
            # the drop is measured against the peak up to the trough (bb), BEFORE a later peak (uu) counts
            tot_peak = max(tot_peak, peak + 0.1)
            worst = min(worst, (low + 0.1) / tot_peak - 1)
            if alive:
                peak = max(peak, eq * (1 + max(uu, 0)), close)      # the basket's later floating peak, for what follows
                eq = close
            peak = max(peak, eq)
            tot_peak = max(tot_peak, peak + 0.1)
        tot = eq + 0.1; worst = min(worst, tot / tot_peak - 1); tot_peak = max(tot_peak, tot)
        out.append({"day": str(pd.Timestamp(d).date()), "mult": round(float(tot), 4), "dd": round(float(worst * 100), 2)})
    return out


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
    # results are booked on the day each basket CLOSED (t1), so a later close never rewrites an earlier day
    days = pd.to_datetime(o.t1[sel], unit="s").dt.normalize().values
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
                        "half_floor_dir": daily(*floor_half(*d), pd.DatetimeIndex(days)),
                        "mix_chosen": mix_chosen(base[0], base[1], days, base[2], base[3])}}
    json.dump(res, open(sys.argv[1], "w"), indent=1)
    # long rows for the dashboard: one row per day and variant
    names = {"actual": "בפועל", "half_floor": "חצי לוט + רצפה 15%", "half_floor_dir": "חצי לוט + רצפה + חסימת כיוון", "mix_chosen": "חשבון 1 בחשיפת השילוב (90% בלוט 0.2, רצפה) + 10% מזומן"}
    rows = [{"day": r["day"], "variant": names[k], "mult": r["mult"], "dd": r["dd"]}
            for k, v in res["variants"].items() for r in v]
    json.dump(rows, open(sys.argv[1].replace(".json", "_rows.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v[-1] if v else None for k, v in res["variants"].items()}), res["baskets"], "baskets")


if __name__ == "__main__":
    main()
