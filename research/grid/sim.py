"""Grid simulator that replicates Black Dragon from its known parameters (docs/GRID_REPLICA_PLAN.md, stage 1).
Minute bars (Bid). Each side runs its own chain:
- a chain opens with Lot_Init at an M15 bar open inside the trading hours when that side is flat;
- a new level opens at an M15 bar open (or any minute, see ADD_ANY_MINUTE) when price is DIST(n) against the
  last entry; lot = Lot_Init * Martin^n rounded to 0.01, capped at MaxLot; at most MaxOrders levels;
- exit: trailing on the basket's average price (start TS, step TD), as iTS/iTD;
- overlap: from OverlapOrderNumber levels, the first and the last position close together when their combined
  profit is positive.
All logic is ASSUMED from the parameters and checked against the tester (stage 1 criteria); nothing here is
the robot's source. K = 100 money units per lot per $ (cent account: cents).
Usage: python research/grid/sim.py BARS_CSV [--from YYYY-MM-DD --to YYYY-MM-DD] [--deposit 24895]"""
import argparse, json
import numpy as np, pandas as pd

P = dict(lot=0.01, martin=1.5, maxlot=5.0, maxorders=10, dist=3.0, dyn_from=6, dyn_dist=2.0, dyn_mult=1.2,
         ts=0.6, td=0.1, overlap_n=7, h0=2, h1=21, spread=0.25, K=100.0)


# v2 (from the tester's trades): the lot follows the chain's ENTRY counter k, which does not go back after an
# overlap; levels 0-15 use the tester's modal lot per k (OBSERVED, bd_cal_full), beyond that x Martin
LOT_K = [1, 2, 2, 3, 5, 8, 11, 15, 23, 15, 23, 23, 34, 38, 57, 61]


def lot_n(k, p):
    base = LOT_K[k] / 100 * (p["lot"] / 0.01) if k < len(LOT_K) else LOT_K[-1] / 100 * p["martin"] ** (k - len(LOT_K) + 1)
    return min(p["maxlot"], max(p["lot"], round(base, 2)))


def dist_n(n, p):
    # v2: from the dynamic level on, the distance is Dynamic_distance_start x multiplier^(n - level), measured
    # from the last OPEN position (OBSERVED: 2.0, 2.4 ... after overlaps)
    return p["dist"] if n < p["dyn_from"] else p["dyn_dist"] * p["dyn_mult"] ** (n - p["dyn_from"])


def run(bars, p, dep, rules=None):
    rules = rules or {}
    t = bars.time.values; lo = bars.low.values; hi = bars.high.values; op = bars.open.values; cl = bars.close.values
    # v3: a new chain opens only on the side of the M15 close vs its EMA(100), as of the previous closed M15 bar
    # (OBSERVED: 99.8% of 14,286 chains in bd_cal_full)
    tt = pd.to_datetime(t, unit="s")
    m15 = pd.Series(cl, index=tt).resample("15min").last().dropna()
    trend = np.sign(m15 - m15.ewm(span=p.get("ema", 100)).mean()).shift(1)
    trend_at = trend.reindex(tt.floor("15min")).values
    minute = (t // 60) % 60; hour = (t // 3600) % 24
    bal = dep; entries = []; closes = []; eq_lo = np.empty(len(t))
    book = {1: [], -1: []}                       # side -> list of [price, lot]
    kcount = {1: 0, -1: 0}                       # entries in the current chain (not reduced by overlaps)
    trail = {1: None, -1: None}
    for i in range(len(t)):
        m15 = minute[i] % 15 == 0
        for s in (1, -1):
            pos = book[s]
            # entry price: buy at Ask (bid + spread), sell at Bid; exits the other way
            if not pos:
                trail[s] = None
                if m15 and p["h0"] <= hour[i] < p["h1"] and trend_at[i] == s and not rules.get("block_new", lambda *a: False)(s, i):
                    px = op[i] + (p["spread"] if s == 1 else 0.0)
                    pos.append([px, p["lot"]]); entries.append((t[i], s, p["lot"], px)); kcount[s] = 1
                continue
            n = len(pos); last = pos[-1][0]
            adverse = (last - (lo[i] + p["spread"])) if s == 1 else ((hi[i] + p["spread"]) - last)   # move against
            if n < p["maxorders"] and adverse >= dist_n(n, p) and (m15 or rules.get("add_any_minute")):
                if not rules.get("block_add", lambda *a: False)(s, i, pos):
                    px = (last - dist_n(n, p)) if s == 1 else (last + dist_n(n, p))
                    l = lot_n(kcount[s], p); kcount[s] += 1; pos.append([px, l]); entries.append((t[i], s, l, px))
            # overlap: first + last close together when their combined profit is positive
            if len(pos) >= p["overlap_n"]:
                exitp = cl[i] if s == 1 else cl[i] + p["spread"]
                pf = sum(s * (exitp - q[0]) * q[1] * p["K"] for q in (pos[0], pos[-1]))
                if pf > 0:
                    bal += pf; closes.append((t[i], s, "overlap", pf)); del pos[-1]; del pos[0]
            if not pos:
                continue
            # basket trailing on the average price
            v = sum(q[1] for q in pos); avg = sum(q[0] * q[1] for q in pos) / v
            best = (hi[i] - avg) if s == 1 else (avg - (lo[i] + p["spread"]))
            if trail[s] is None and best >= p["ts"]:
                trail[s] = best
            if trail[s] is not None:
                trail[s] = max(trail[s], best)
                now = (cl[i] - avg) if s == 1 else (avg - (cl[i] + p["spread"]))
                if now <= trail[s] - p["td"]:
                    pf = now * v * p["K"]; bal += pf; closes.append((t[i], s, "trail", pf)); book[s] = []; trail[s] = None
        fl = 0.0
        for s in (1, -1):
            for q in book[s]:
                fl += s * ((lo[i] if s == 1 else hi[i] + p["spread"]) - q[0]) * q[1] * p["K"]
        eq_lo[i] = bal + fl
    pk = np.maximum.accumulate(np.maximum(eq_lo, dep))
    return {"final": round(float(bal), 2), "net": round(float(bal - dep), 2), "entries": len(entries),
            "max_dd_pct": round(float(((eq_lo - pk) / pk).min() * 100), 1), "wiped": bool(eq_lo.min() <= dep * 0.1)}, entries


def main():
    a = argparse.ArgumentParser(); a.add_argument("bars"); a.add_argument("--from", dest="frm"); a.add_argument("--to")
    a.add_argument("--deposit", type=float, default=24895); a = a.parse_args()
    b = pd.read_csv(a.bars)
    if a.frm:
        b = b[(b.time >= pd.Timestamp(a.frm).timestamp()) & (b.time < pd.Timestamp(a.to).timestamp())]
    res, ent = run(b.reset_index(drop=True), P, a.deposit)
    e = pd.DataFrame(ent, columns=["t", "side", "lot", "px"]); e["m"] = pd.to_datetime(e.t, unit="s").dt.to_period("M")
    res["entries_per_month"] = e.groupby("m").size().astype(int).to_dict()
    print(json.dumps({k: (str(v) if k == "entries_per_month" else v) for k, v in res.items()}, indent=1))


if __name__ == "__main__":
    main()
