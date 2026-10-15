import glob, sys, numpy as np, pandas as pd
STRICT = "--strict" in sys.argv
RAW = "data/raw/black_dragon_1/"
deals = pd.read_csv(glob.glob(RAW + "2026*/deals.csv")[0]).sort_values(["time_msc", "ticket"])
bars = pd.read_csv(glob.glob(RAW + "rates_*/bars.csv")[0])
deals["cash"] = deals.profit + deals.commission + deals.swap + deals.fee
deals["bal_after"] = deals.cash.cumsum()
x = deals[deals.symbol == "XAUUSDc"]
ins = x[x.entry == 0].set_index("position_id")
outs = x[x.entry == 1].groupby("position_id").agg(t1=("time", "max"), close_px=("price", "last"),
        out_vol=("volume", "sum"), pnl=("cash", "sum"), magic_close=("magic", "last"), reason=("reason", "last"))
p = ins[["time", "type", "volume", "price", "magic", "cash"]].rename(columns={"time": "t0", "price": "open_px", "magic": "magic_open"}).join(outs, how="inner")
p["pnl"] += p.cash
p["sgn"] = np.where(p.type == 0, 1, -1)
# calibrate cents per (1.0 price move x 1 lot) from closes with a real move
m = (p.close_px - p.open_px).abs() > 1
k = (p.pnl[m] - 0) / (p.sgn[m] * p.volume[m] * (p.close_px[m] - p.open_px[m]))
print("K median", k.median(), "IQR", k.quantile([.25, .75]).tolist())
K = round(k.median())
p = p[p.t0 >= pd.Timestamp("2025-11-11").timestamp()].sort_values("t0").reset_index()
# clusters: continuous non-zero exposure
cid, end, c = [], -1, -1
for t0, t1 in zip(p.t0, p.t1):
    if t0 >= end:
        c += 1
    end = max(end, t1) if t0 < end else t1
    cid.append(c)
p["cid"] = cid
bt = bars.time.values; lo = bars.low.values; hi = bars.high.values
bal_t = deals.time.values; bal_v = deals.bal_after.values
out = []
for c, g in p.groupby("cid"):
    t0, t1 = g.t0.min(), g.t1.max()
    i0 = np.searchsorted(bt, t0 - 59); i1 = np.searchsorted(bt, t1, side="right")
    worst = 0.0; worst_t = t0
    if i1 > i0:
        tt = bt[i0:i1]
        fl_lo = np.zeros(len(tt)); fl_hi = np.zeros(len(tt))
        for r in g.itertuples():
            if STRICT:  # only whole minutes the position was open for
                a = np.searchsorted(tt, r.t0, side="right"); z = np.searchsorted(tt, r.t1 - 59, side="left")
            else:       # also the partial minutes of open and close (overstates MAE)
                a = np.searchsorted(tt, r.t0 - 59); z = np.searchsorted(tt, r.t1, side="right")
            fl_lo[a:z] += r.sgn * r.volume * (lo[i0 + a:i0 + z] - r.open_px) * K
            fl_hi[a:z] += r.sgn * r.volume * (hi[i0 + a:i0 + z] - r.open_px) * K
        fl = np.minimum(fl_lo, fl_hi)  # conservative: worst of the bar's extremes
        j = fl.argmin(); worst = fl[j]; worst_t = tt[j]
    kb = np.searchsorted(bal_t, t0, side="left") - 1
    bal0 = bal_v[kb] if kb >= 0 else 0
    out.append(dict(cid=c, t0=t0, t1=t1, n=len(g), maxlots=g.volume.sum(), side=",".join(sorted(set(np.where(g.sgn>0,"B","S")))),
                    pnl=g.pnl.sum(), mae=worst, mae_t=worst_t, bal0=bal0,
                    guard=(g.magic_close == 0).any()))
o = pd.DataFrame(out)
o["pnl_pct"] = o.pnl / o.bal0 * 100; o["mae_pct"] = o.mae / o.bal0 * 100
o.to_csv("data/derived/bd1/clusters_strict.csv" if STRICT else "data/derived/bd1/clusters.csv", index=False)
print(len(o), "baskets;", o.guard.sum(), "with guard close")
print(o.mae_pct.describe(percentiles=[.5, .9, .95, .99]))
print(o[o.guard][["t0", "n", "maxlots", "pnl", "pnl_pct", "mae_pct", "bal0"]].assign(t0=lambda d: pd.to_datetime(d.t0, unit="s")).to_string())
print("worst non-guard baskets:"); print(o[~o.guard].nsmallest(10, "mae_pct")[["t0","n","maxlots","pnl_pct","mae_pct"]].assign(t0=lambda d: pd.to_datetime(d.t0, unit="s")).to_string())
