"""Crash-day signs (docs/BD_CRASH_SIGNS.md): every basket the user's guard cut, against deep baskets that recovered,
from clone runs on the same ticks (2022-2025 RoboForex, 12/2025-10/2026 EGlobal), with what the market did before.
Usage: python research/bd1/crash_signs.py OUT.csv REPORT:BARS [REPORT:BARS ...]
BARS = an M15 CSV from mql5/BarExport.mq5 (Common Files), or '-' to skip the market features."""
import os, sys
import numpy as np
import pandas as pd
sys.path[:0] = [os.path.join(os.path.dirname(__file__), "..", "btc"), os.path.dirname(__file__)]
import guardian_sim as g

def baskets(rep):
    d = g.deals(f"C:/MT5_JEV_TEST/{rep}.htm"); out = d[d.dir == "out"].copy()
    p = g.pair(d)[0].sort_values("t0").reset_index(drop=True)
    rows = []
    for side, s in p.groupby("side"):          # a basket = positions of one side whose lifetimes chain without a gap
        s = s.sort_values("t0"); start = None; end = -1; grp = []
        for _, r in s.iterrows():
            if start is not None and r.t0 > end:
                rows.append((side, grp)); grp = []; start = None
            if start is None: start = r.t0
            grp.append(r); end = max(end, r.t1)
        if grp: rows.append((side, grp))
    bal = out.set_index("t").balance.sort_index()
    res = []
    for side, grp in rows:
        x = pd.DataFrame(grp); t0, t1 = int(x.t0.min()), int(x.t1.max())
        b0 = bal[bal.index < t0].iloc[-1] if (bal.index < t0).any() else float(bal.iloc[0])
        res.append({"report": rep, "side": side, "t0": t0, "t1": t1, "levels": len(x), "lots": round(x.vol.sum(), 2),
                    "net": round(x.net.sum(), 2), "net_pct": round(x.net.sum() / b0 * 100, 2), "hours": round((t1 - t0) / 3600, 1)})
    return pd.DataFrame(res)

def market(bars, t0):
    """What the market did in the hours before the basket opened (t0), from M15 bars that closed before t0."""
    b = bars[bars.time < t0].tail(96 * 5)
    if len(b) < 96 * 2: return {}
    rng = (b.high - b.low); atr96 = rng.tail(96).mean(); atr_5d = rng.mean()
    c = b.close.to_numpy(); ema = pd.Series(c).ewm(span=99).mean().to_numpy()
    return {"atr_ratio": round(atr96 / atr_5d, 3),                         # last day's bar range vs the 5-day average
            "move_24h": round((c[-1] - c[-97]) / atr_5d, 2),               # 24 h drift in 5-day bar ranges
            "move_4h": round((c[-1] - c[-17]) / atr_5d, 2),
            "ema_dist": round((c[-1] - ema[-1]) / atr_5d, 2),               # distance from the EMA BD trades on
            "range_24h": round((b.high.tail(96).max() - b.low.tail(96).min()) / atr_5d, 1),
            "hour": pd.Timestamp(t0, unit="s").hour, "weekday": pd.Timestamp(t0, unit="s").weekday()}

if __name__ == "__main__":
    out = []
    for arg in sys.argv[2:]:
        rep, bars = arg.split(":", 1)
        B = baskets(rep)
        if bars != "-":
            bb = pd.read_csv(bars)
            B = pd.concat([B, pd.DataFrame([market(bb, t) for t in B.t0])], axis=1)
        out.append(B)
    A = pd.concat(out, ignore_index=True)
    A["kind"] = np.where(A.net_pct <= -8, "cut", np.where((A.levels >= 7) & (A.net > 0), "deep_recovered", "other"))
    A.to_csv(sys.argv[1], index=False)
    print(A.groupby(["report", "kind"]).size().unstack(fill_value=0))
