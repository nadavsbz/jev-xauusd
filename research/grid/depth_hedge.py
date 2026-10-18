"""Depth-triggered convex hedge, added after the fact to the robot's exact positions (docs/DEPTH_HEDGE_PLAN.md).
The hedge does not change the robot (other magic), so the tester's positions stay valid:
- per side, net open lots from the paired positions, minute by minute;
- when a side's open lots exceed L (at a bar close), an opposite position of h x those lots opens at the NEXT
  bar's open (spread paid), with a trailing stop STOP $ from its best price; it closes on the stop or when that
  side's chain is flat again (spread paid).
Equity = robot equity (exact, guardian_sim.equity_path) + hedge P&L. K = 100 per lot per $.
Usage: python research/grid/depth_hedge.py REPORT.htm BARS_CSV DEPOSIT OUT_JSON [SCALE]"""
import itertools, json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
import guardian_sim as g  # noqa: E402

K, SPREAD = 100.0, 0.30
GRID = list(itertools.product((0.3, 0.6), (0.5, 1.0), (3.0, 6.0)))


def side_lots(pos, tt):
    """Open lots per side per minute (entry bar included, as in equity_path)."""
    out = {1: np.zeros(len(tt)), -1: np.zeros(len(tt))}
    for r in pos.itertuples():
        s = 1 if r.side == "buy" else -1
        i = max(np.searchsorted(tt, r.t0, "right") - 1, 0); j = np.searchsorted(tt, r.t1, "left")
        out[s][i:j] += r.vol
    return out


def hedge_pnl(lots, tt, op, lo, hi, cl, L, h, stop, scale):
    pnl = np.zeros(len(tt)); real = 0.0; n_open = 0
    for s in (1, -1):                                   # hedge AGAINST side s: direction -s
        d = -s; state = None                            # [entry, size, best]
        for m in range(1, len(tt)):
            if state is None:
                if lots[s][m - 1] * scale > L and lots[s][m] > 0:
                    px = op[m] + (SPREAD if d == 1 else 0.0)
                    state = [px, h * lots[s][m - 1], px]; n_open += 1
            if state is not None:
                px0, size, best = state
                best = max(best, hi[m]) if d == 1 else min(best, lo[m])
                state[2] = best
                stop_px = best - stop if d == 1 else best + stop
                hit = (lo[m] <= stop_px) if d == 1 else (hi[m] >= stop_px)
                flat = lots[s][m] == 0
                if hit or flat:
                    ex = stop_px if hit else cl[m]
                    ex = ex if d == 1 else ex + SPREAD
                    real += d * (ex - px0) * size * K; state = None
                    pnl[m] += 0
                else:
                    pnl[m] += d * ((cl[m] if d == 1 else cl[m] + SPREAD) - px0) * size * K
            pnl[m] += 0
        # realised hedge P&L accumulates over time: rebuild as a running sum below
    return pnl, real, n_open


def run(rep, bars_csv, dep, scale=1.0):
    bars = pd.read_csv(bars_csv)
    pos, left = g.pair(g.deals(rep))
    if left:
        sys.exit(f"{left} unpaired positions")
    bt = bars.time.values
    tt, eq_lo, _ = g.equity_path(pos, bt, bars.low.values, bars.high.values, 0.0)
    a0 = np.searchsorted(bt, tt[0]); sl = slice(a0, a0 + len(tt))
    op, lo, hi, cl = (bars[c].values[sl] for c in ("open", "low", "high", "close"))
    lots = side_lots(pos, tt)
    base = dep + eq_lo * scale
    res = {"no_hedge": dict(summary(base, dep, tt), max_margin_use_pct=margin_use(lots, None, cl, base, scale))}
    for L, h, stop in GRID:
        # rebuild the hedge path with realised P&L carried forward
        path = np.zeros(len(tt)); cum = 0.0; opened = 0
        for s in (1, -1):
            d = -s; state = None
            for m in range(1, len(tt)):
                if state is None and lots[s][m - 1] * scale > L and lots[s][m] > 0:
                    px = op[m] + (SPREAD if d == 1 else 0.0); state = [px, h * lots[s][m - 1], px]; opened += 1
                if state is not None:
                    px0, size, best = state
                    # conservative intrabar order (review PR #26): the stop from the PREVIOUS best is checked
                    # first; only a bar that does not hit it can raise the best for the next bars
                    stop_px = best - stop if d == 1 else best + stop
                    hit = (lo[m] <= stop_px) if d == 1 else (hi[m] >= stop_px)
                    if not hit:
                        best = max(best, hi[m]) if d == 1 else min(best, lo[m]); state[2] = best
                    worst = lo[m] if d == 1 else hi[m] + SPREAD
                    if hit or lots[s][m] == 0:
                        ex = (stop_px if hit else cl[m]) + (0.0 if d == 1 else SPREAD)
                        val = d * (ex - px0) * size * K
                        path[m:] += val; state = None
                    else:
                        path[m] += d * (worst - px0) * size * K      # the hedge's worse side inside the bar
        eq = base + path * scale
        res[f"L={L} h={h} stop={stop}"] = dict(summary(eq, dep, tt), hedges=opened,
                                              max_margin_use_pct=margin_use(lots, hedge_lots(lots, L, h, scale), cl, eq, scale))
    return res


def summary(eq, dep, tt):
    pk = np.maximum.accumulate(np.maximum(eq, dep))
    dd = (eq - pk) / pk
    daily = pd.Series(eq, index=pd.to_datetime(tt, unit="s")).resample("1D").last().dropna()
    r = daily.pct_change().dropna()
    es = float(r[r <= r.quantile(0.05)].mean() * 100) if len(r) > 20 else float("nan")   # Expected Shortfall 5%
    return {"final": round(float(eq[-1]), 2), "mult": round(float(eq[-1] / dep), 3),
            "max_dd_pct": round(float(dd.min() * 100), 1), "wiped": bool(eq.min() <= dep * 0.1),
            "es5_daily_pct": round(es, 2)}


def hedge_lots(lots, L, h, scale):
    """Upper bound of the hedge's open lots per minute: h x the side's lots while that side is above L."""
    out = np.zeros(len(lots[1]))
    for s in (1, -1):
        out += np.where(lots[s] * scale > L, h * lots[s], 0.0)
    return out


def margin_use(lots, hl, cl, eq, scale, lev=1000.0):
    """Peak margin use, % of equity: gross open lots x 100 oz x price / leverage (ASSUMED: no hedge netting)."""
    gross = (lots[1] + lots[-1] + (hl if hl is not None else 0.0)) * scale
    m = gross * 100 * cl / lev
    with np.errstate(divide="ignore", invalid="ignore"):
        u = np.where(eq > 0, m / eq * 100, np.inf)
    return round(float(np.nanmax(u)), 1)


if __name__ == "__main__":
    rep, bars_csv, dep, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
    sc = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    r = run(rep, bars_csv, dep, sc)
    json.dump(r, open(out, "w"), indent=1)
    for k, v in r.items():
        print(k, v)
