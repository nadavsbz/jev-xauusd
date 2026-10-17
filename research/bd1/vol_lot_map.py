"""Volatility-scaled lot on the calibrated Black Dragon tester run (docs/BD_VOL_LOT.md). Descriptive map,
fixed before it was run: every basket (one side, from the first entry while that side is flat until the
side is flat again) is scaled by m = clip(REF / ATR, LO, HI), where ATR = mean daily high-low of gold
over the 14 full days before the basket's first entry (EGlobal M1 bars, server days) and REF = the median
of that ATR over the run. Scaling the whole basket is exact for the P&L of a grid whose distances do not
depend on the lot (ASSUMED: lot rounding, MaxLot and margin limits ignored).
Usage: python research/bd1/vol_lot_map.py REPORT.htm BARS_CSV DEPOSIT OUT_JSON"""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
import guardian_sim as g  # noqa: E402

LO, HI = 0.25, 1.5


def baskets(pos):
    pos = pos.sort_values("t0").reset_index(drop=True); bid = np.full(len(pos), -1); n = 0
    for side in ("buy", "sell"):
        idx = pos.index[pos.side == side]
        ev = sorted([(pos.t0[i], 1, i) for i in idx] + [(pos.t1[i], -1, i) for i in idx], key=lambda x: (x[0], -x[1]))
        open_n, cur = 0, None
        for t, k, i in ev:
            if k == 1:
                if open_n == 0:
                    cur = n; n += 1
                bid[i] = cur; open_n += 1
            else:
                open_n -= 1
    return pos.assign(basket=bid)


def main():
    rep, bars_csv, dep, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
    bars = pd.read_csv(bars_csv); bt, lo, hi = bars.time.values, bars.low.values, bars.high.values
    day = pd.to_datetime(bars.time, unit="s").dt.normalize()
    dr = bars.groupby(day).agg(h=("high", "max"), l=("low", "min"))
    atr = (dr.h - dr.l).rolling(14).mean().shift(1)           # 14 full days BEFORE each day
    pos, left = g.pair(g.deals(rep)); pos = baskets(pos)
    first = pos.groupby("basket").t0.min()
    a = atr.reindex(pd.to_datetime(first, unit="s").dt.normalize().values).values
    ref = np.nanmedian(a)
    m = pd.Series(np.clip(ref / a, LO, HI), index=first.index).fillna(1.0)
    res = {"positions": len(pos), "unmatched": left, "baskets": int(len(first)), "ref_atr": round(float(ref), 2),
           "m_quantiles": {q: round(float(m.quantile(q)), 3) for q in (0.05, 0.25, 0.5, 0.75, 0.95)}}
    for name, mult in (("fixed", pd.Series(1.0, index=first.index)), ("vol_scaled", m)):
        k = pos.basket.map(mult).values
        p = pos.assign(vol=pos.vol * k, net=pos.net * k)
        tt, eq_lo, _ = g.equity_path(p, bt, lo, hi, dep); pk = np.maximum.accumulate(eq_lo)
        res[name] = {"mult": round(float(eq_lo[-1] / dep), 3), "max_dd_pct": round(float(((pk - eq_lo) / pk).max() * 100), 1),
                     "min_equity": round(float(eq_lo.min()), 0)}
        print(name, res[name], flush=True)
    # the same drawdown budget: scale the fixed lot down until its drawdown equals the vol-scaled one
    json.dump(res, open(out, "w"), indent=1)


if __name__ == "__main__":
    main()
