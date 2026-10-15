import glob, numpy as np, pandas as pd
RAW = "data/raw/black_dragon_1/"
deals = pd.read_csv(glob.glob(RAW + "2026*/deals.csv")[0])
bars = pd.read_csv(glob.glob(RAW + "rates_*/bars.csv")[0])
o = pd.read_csv("data/derived/bd1/clusters_strict.csv")
K = 97.5
x = deals[deals.symbol == "XAUUSDc"]
ins = x[x.entry == 0].set_index("position_id"); outs = x[x.entry == 1].groupby("position_id").agg(t1=("time","max"), magic_close=("magic","last"))
p = ins[["time","type","volume","price"]].join(outs, how="inner")
bt, lo, hi, cl = bars.time.values, bars.low.values, bars.high.values, bars.close.values
for _, c in o[o.guard & (o.pnl_pct < -5)].iterrows():
    g = p[(p.time >= c.t0) & (p.time <= c.t1) & (p.magic_close == 0)]
    sgn = np.where(g.type == 0, 1, -1); vol = g.volume.values; px = g.price.values
    net = (sgn * vol).sum(); be = (sgn * vol * px).sum() / net  # breakeven price of what the guard closed
    tg = g.t1.max(); i0 = np.searchsorted(bt, tg); i1 = np.searchsorted(bt, tg + 10 * 86400)
    worst_px = lo[i0:i1] if net > 0 else hi[i0:i1]
    fl = net * (worst_px - be) * K
    loss_at_guard = c.pnl
    rec = np.where((cl[i0:i1] - be) * np.sign(net) >= 0)[0]
    stop = rec[0] + 1 if len(rec) else len(fl)   # only until price first returns to breakeven
    fl = fl[:stop]; j = fl.argmin()
    print(f"{pd.to_datetime(c.t0,unit='s'):%Y-%m-%d} side={'BUY' if net>0 else 'SELL'} lots={abs(net):5.2f} "
          f"guard loss={c.pnl_pct:6.1f}%  further worst before breakeven={fl[j]/c.bal0*100:7.1f}% "
          f"(after {(bt[i0+j]-tg)/3600:5.1f}h)  back to breakeven: "
          + (f"after {(bt[i0+rec[0]]-tg)/3600:.1f}h" if len(rec) else "no, not within 10 days"))
