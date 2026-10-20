"""Does the developer's trend indicator separate account 1's crash baskets from its normal ones?

Rule tested (the developer's own, Telegram 2026-04-22 / 06-17 / 08-08): trade WITH the indicator's direction,
cut when it flips. Question 1 (this script): at the moment a real basket of account 1 opened, was it with or
against the indicator's direction, and how does that split the crash baskets from the rest?

Inputs:
  data/derived/bd1_forward/clusters_strict.csv  account 1's real baskets (magic 5555): t0, t1, n, side, pnl, mae, bal0
  data/derived/indicators/<tag>_acc1_m15.csv    the exported indicator buffers (IndicatorExport.mq5), EGlobal server time,
                                                one row per CLOSED M15 bar, values of that bar (known at its close)
Direction from the buffers, decided per buffer from the data itself (no hand-picking):
  * an arrow buffer (sparse): a value at/below the bar's low = up signal, at/above the high = down signal; the
    direction holds until the next opposite arrow;
  * a line buffer (dense): close above the line = up, below = down.
Only information up to the last CLOSED bar before the basket's first entry is used (no look-ahead).

Usage: python research/signals/basket_signals.py TAG    (e.g. tai, tcind)
Output: docs/evidence/basket_signals_<TAG>.json"""
import json, os, sys
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_export(path):
    rows = [l for l in open(path, encoding="ascii", errors="ignore") if not l.startswith("#")]
    from io import StringIO
    d = pd.read_csv(StringIO("".join(rows)))
    d["t"] = pd.to_datetime(d.time, format="%Y.%m.%d %H:%M").astype("int64") // 10**9
    return d.set_index("t").sort_index()


def directions(d):
    """-> {buffer: Series of +1/-1/NaN per bar} for every buffer that carries information."""
    out = {}
    for b in [c for c in d.columns if c.startswith("b")]:
        v = pd.to_numeric(d[b], errors="coerce")
        v = v.where((v.abs() < 1e7) & (v != 0))
        share = v.notna().mean()
        if share == 0:
            continue
        if share < 0.3:                                   # arrows
            sig = pd.Series(np.nan, index=d.index)
            sig[(v.notna()) & (v <= d.low + 1e-9)] = 1.0
            sig[(v.notna()) & (v >= d.high - 1e-9)] = -1.0
            if sig.notna().sum() < 10:
                continue
            out[f"{b}_arrow"] = sig.ffill()
        elif v.between(d.low.min() * 0.5, d.high.max() * 1.5).mean() > 0.9:   # a price line
            out[f"{b}_line"] = np.sign(d.close - v)
    return out


def main():
    tag = sys.argv[1]
    exp = load_export(os.path.join(ROOT, "data", "derived", "indicators", f"{tag}_acc1_m15.csv"))
    cl = pd.read_csv(os.path.join(ROOT, "data", "derived", "bd1_forward", "clusters_strict.csv"))
    cl = cl[(cl.t0 >= exp.index.min() + 3600) & (cl.t1 <= exp.index.max())].copy()
    cl["sgn"] = np.where(cl.side == "B", 1.0, -1.0)
    # crash baskets: the worst 5% by floating loss (MAE) in % of the balance; registered in docs/BD_SIGNALS_PLAN.md
    thr = cl.mae_pct.quantile(0.05)
    cl["crash"] = cl.mae_pct <= thr
    res = {"tag": tag, "baskets": int(len(cl)), "crash_threshold_mae_pct": round(float(thr), 3),
           "crash_baskets": int(cl.crash.sum()), "buffers": {}}
    for name, dirn in directions(exp).items():
        # direction at the last bar that CLOSED before the basket opened (bar time + 15 min <= t0)
        idx = np.searchsorted(dirn.index.values + 900, cl.t0.values, side="right") - 1
        st = np.where(idx >= 0, dirn.values[np.maximum(idx, 0)], np.nan)
        cl["with"] = st * cl.sgn
        ok = cl["with"].notna()
        c, n = cl[ok & cl.crash], cl[ok & ~cl.crash]
        res["buffers"][name] = dict(
            crash_against_share=round(float((c["with"] < 0).mean()), 3) if len(c) else None,
            normal_against_share=round(float((n["with"] < 0).mean()), 3) if len(n) else None,
            # what the rule "only open with the indicator" keeps and drops (in cents, the account's real pnl)
            pnl_with=round(float(cl.loc[ok & (cl["with"] > 0), "pnl"].sum()), 2),
            pnl_against=round(float(cl.loc[ok & (cl["with"] < 0), "pnl"].sum()), 2),
            crash_pnl_against=round(float(c.loc[c["with"] < 0, "pnl"].sum()), 2),
            covered=int(ok.sum()))
    out = os.path.join(ROOT, "docs", "evidence", f"basket_signals_{tag}.json")
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
