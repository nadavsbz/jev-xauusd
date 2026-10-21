"""Fleet baskets only WITH the H4 trend (close vs SMA200 on H4), docs/SEMI_TREND_PLAN.md (registered 21.10.2026)."""
import json, os
import numpy as np, pandas as pd

DIRS = {"1": "data/derived/bd1_rescue", "2": "data/derived/fleet/bd2", "3": "data/derived/fleet/bd3",
        "5": "data/derived/fleet/bd5", "6": "data/derived/fleet/bd6", "8": "data/derived/fleet/bd8"}
T0, T1 = pd.Timestamp("2026-01-01").timestamp(), pd.Timestamp("2026-10-17").timestamp()
b = pd.read_csv("data/raw/black_dragon_8/rates_XAUUSDc_M1_20261021T162837Z/bars.csv")
g = b.set_index(pd.to_datetime(b.time, unit="s")).close.resample("4h").last().dropna()
reg = np.sign(g - g.rolling(200).mean()).dropna()
tclose = (reg.index.astype("int64") // 10**9).values + 4 * 3600          # known at the H4 bar's close
res = {"accounts": {}}; saved = lost = 0.0; ok = 0
for k, d in DIRS.items():
    o = pd.read_csv(os.path.join(d, "clusters_strict.csv")).sort_values("t0")
    o = o[(o.t0 >= T0) & (o.t1 <= T1)].reset_index(drop=True)
    i = np.searchsorted(tclose, o.t0.values, side="right") - 1
    r = np.where(i >= 0, reg.values[np.maximum(i, 0)], 0)
    pos = pd.read_csv(os.path.join(d, "positions_strict.csv"))
    sgn = o.cid.map(pos.sort_values("t0_msc").groupby("cid").sgn.first()).fillna(0).values   # side of the FIRST entry (review PR 36)
    blk = r * sgn < 0
    xa, xr = float(np.prod(1 + o.pnl_pct / 100)), float(np.prod(1 + o.pnl_pct[~blk] / 100))
    bb = o[blk]; s_, l_ = float(-bb.pnl_pct[bb.pnl_pct < 0].sum()), float(bb.pnl_pct[bb.pnl_pct > 0].sum())
    saved += s_; lost += l_; ok += xr >= xa
    deep = o.mae_pct <= -10
    res["accounts"][k] = dict(baskets=len(o), blocked=int(blk.sum()), deep=int(deep.sum()), deep_blocked=int((deep & blk).sum()),
                              x_actual=round(xa, 3), x_rule=round(xr, 3), saved=round(s_, 2), lost=round(l_, 2))
    print(k, res["accounts"][k])
res["fleet"] = dict(saved=round(saved, 2), lost=round(lost, 2), accounts_not_worse=ok, passes=bool(saved > lost and ok >= 4))
print(res["fleet"]); json.dump(res, open("docs/evidence/fleet_h4_gate.json", "w"), indent=1)
