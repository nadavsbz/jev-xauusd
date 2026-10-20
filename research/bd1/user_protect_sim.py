"""The user's real management of account 1, applied to a tester run's exact baskets (docs/BD1_CRASH_CAUSE.md):
- lot: Lot_Init = round(equity / RATIO, 2) lots (equity in account units, RATIO = 600,000), set at each reset;
- protection: Equity Protect basic with a fixed amount = (1 - FLOOR) x equity at the reset; when the equity
  (bar's worse side) reaches it, everything is closed (spread paid) and trading stops;
- reset: every RESET_DAYS days (new lot + new amount from the current equity) and after each trigger;
- after a trigger, trading resumes WAIT_DAYS later at 00:00 (server); only baskets that START after the resume
  are taken (the robot starts fresh).
Baskets keep their shape and scale with the lot (ASSUMED: linear in the lot; lot rounding inside the grid ignored).
Usage: python research/bd1/user_protect_sim.py REPORT.htm BARS_CSV DEPOSIT [RESET_DAYS WAIT_DAYS FLOOR RATIO]"""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
import guardian_sim as g  # noqa: E402
from vol_lot_map import baskets  # noqa: E402

K, SPREAD, DAY = 100.0, 0.30, 86400


def run(pos, bars, dep, reset_days=7, wait_days=1, floor=0.15, ratio=600000.0, base_lot=0.01):
    bt, lo, hi = bars.time.values, bars.low.values, bars.high.values
    a0 = np.searchsorted(bt, pos.t0.min(), "left"); a1 = np.searchsorted(bt, pos.t1.max(), "right")
    tt = bt[a0:a1]; n = len(tt)
    # per basket: floating (worse side, 1x lot) per minute over its life, and its exit cash per minute
    B = []
    for b, c in pos.groupby("basket"):
        i0 = max(np.searchsorted(tt, c.t0.min(), "right") - 1, 0); i1 = np.searchsorted(tt, c.t1.max(), "left")
        fl = np.zeros(i1 - i0 + 1); cash = np.zeros(i1 - i0 + 1); vol = np.zeros(i1 - i0 + 1)
        for r in c.itertuples():
            s = 1 if r.side == "buy" else -1
            i = max(np.searchsorted(tt, r.t0, "right") - 1, 0) - i0; j = np.searchsorted(tt, r.t1, "left") - i0
            w = lo[a0 + i0 + i:a0 + i0 + j] if s == 1 else hi[a0 + i0 + i:a0 + i0 + j]
            fl[i:j] += s * r.vol * (w - r.p0) * K + r.cost_in
            vol[i:j] += r.vol
            cash[min(j, len(cash) - 1)] += r.net
        B.append((i0, i1, fl, cash, vol))
    B.sort(key=lambda x: x[0]); starts = {}
    for idx, x in enumerate(B):
        starts.setdefault(x[0], []).append(idx)
    bal = dep; lot = max(round(bal / ratio, 2), 0.01); fl_amt = (1 - floor) * bal
    next_reset = tt[0] + reset_days * DAY; resume = -1; active = {}; stops = []; eq = np.empty(n); lots = []
    for m in range(n):
        t = tt[m]
        if resume >= 0 and t < resume:
            eq[m] = bal; continue
        resume = -1
        for idx in starts.get(m, []):
            active[idx] = lot / base_lot                     # the basket runs at the lot set at its start
        f = 0.0; done = []
        for idx, k in active.items():
            i0, i1, fl, cash, vol = B[idx]; o = m - i0
            bal += cash[o] * k
            if m >= i1:
                done.append(idx)
            else:
                f += fl[o] * k
        for idx in done:
            active.pop(idx)
        e = bal + f
        if active and e <= fl_amt:                           # Equity Protect: close everything at the worse side
            cost = sum(B[i][4][m - B[i][0]] * k * K * SPREAD for i, k in active.items())
            bal = e - cost; active = {}; stops.append((str(pd.to_datetime(t, unit="s")), round(bal, 0)))
            resume = (t // DAY + wait_days) * DAY
            lot = max(round(bal / ratio, 2), 0.01); fl_amt = (1 - floor) * bal; next_reset = resume + reset_days * DAY
            eq[m] = bal; continue
        if t >= next_reset:                                  # the user's periodic update
            lot = max(round(e / ratio, 2), 0.01); fl_amt = (1 - floor) * e; next_reset = t + reset_days * DAY
            lots.append(lot)
        eq[m] = e
        if e <= 0:
            eq[m:] = e; break
    pk = np.maximum.accumulate(np.maximum(eq, dep))
    return {"final": round(float(eq[-1]), 0), "mult": round(float(eq[-1] / dep), 2),
            "max_dd_pct": round(float(((eq - pk) / pk).min() * 100), 1), "stops": len(stops),
            "wiped": bool(eq.min() <= 0), "first_stops": stops[:12], "max_lot": max(lots) if lots else lot}


if __name__ == "__main__":
    rep, bars_csv, dep = sys.argv[1], sys.argv[2], float(sys.argv[3])
    rd, wd, fl, ra = (float(x) for x in (sys.argv[4:8] if len(sys.argv) > 7 else (7, 1, 0.15, 600000)))
    pos, left = g.pair(g.deals(rep)); pos = baskets(pos)
    bars = pd.read_csv(bars_csv)
    print(json.dumps(run(pos, bars, dep, rd, wd, fl, ra), ensure_ascii=False))
