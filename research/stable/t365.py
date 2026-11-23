"""t365 (docs/prereg/research_t365.md): long after crypto forced-liquidation cascades (Binance USD-M, BTC/ETH).
Usage: py -3.12 research/stable/t365.py density|audit|dev|holdout"""
import glob, io, json, sys, zipfile
import numpy as np, pandas as pd
R = "data/raw/binance"; COST = {"base": 0.0005, "stress": 0.0015}; H = 12; HOLD = 288; W = 30 * 288


def kl(s):
    L = []
    for f in sorted(glob.glob(f"{R}/klines5m/{s}/*.zip")):
        z = zipfile.ZipFile(f); b = z.read(z.namelist()[0]).decode()
        hdr = 0 if b.startswith("open_time") else None
        a = pd.read_csv(io.StringIO(b), header=hdr, usecols=range(6)); a.columns = ["ot", "o", "h", "l", "c", "v"]; L.append(a)
    k = pd.concat(L); k["ot"] = pd.to_datetime(k.ot.astype("int64"), unit="ms"); return k.drop_duplicates("ot").set_index("ot").sort_index()


def oi(s):
    L = []
    for f in sorted(glob.glob(f"{R}/metrics/{s}/*.zip")):
        z = zipfile.ZipFile(f); L.append(pd.read_csv(z.open(z.namelist()[0]), usecols=["create_time", "sum_open_interest"]))
    m = pd.concat(L); m["t"] = pd.to_datetime(m.create_time); return m.drop_duplicates("t").set_index("t").sum_open_interest.sort_index()


def build(s):
    k = kl(s); full = pd.date_range(k.index[0], k.index[-1], freq="5min"); k = k.reindex(full)
    m = oi(s).reindex(full + pd.Timedelta("5min"))            # snapshot at bar close
    m.index = full
    r1 = k.c / k.c.shift(H) - 1
    sd = r1.rolling(W, min_periods=W // 2).std().shift(1)
    hv = k.v.rolling(H).sum(); medv = hv.rolling(W, min_periods=W // 2).median().shift(1)
    doi = m / m.shift(H) - 1
    sig = (r1 < -3 * sd) & (doi <= -0.03) & (hv > 3 * medv)
    return k, m, sig, r1, doi, hv / medv


def events(s, lo, hi):
    k, m, sig, r1, doi, vx = build(s); idx = k.index; E = []; last = None
    for t in idx[sig.fillna(False).values]:
        if not (pd.Timestamp(lo) <= t <= pd.Timestamp(hi)): continue
        if last is not None and t - last < pd.Timedelta("24h"): continue
        i = idx.get_loc(t); ie, ix = i + 1, i + HOLD
        if ix >= len(idx): continue
        po, pc = k.o.iloc[ie], k.c.iloc[ix]
        if not (po > 0 and pc > 0): continue
        f = lambda n: k.c.iloc[min(i + n, len(idx) - 1)] / po - 1
        E.append(dict(s=s, t=t, r1h=r1.iloc[i], doi=doi.iloc[i], vx=vx.iloc[i], ret=pc / po - 1, r4=f(48), r72=f(864), missed=po / k.c.iloc[i] - 1)); last = t
    win = k.c.loc[lo:hi]; unc = (win.shift(-HOLD) / win - 1).mean()
    cov = pd.DataFrame(dict(px=k.c.notna(), oi=m.notna())).loc[lo:hi].groupby(pd.Grouper(freq="ME")).mean()
    return pd.DataFrame(E), unc, cov


if __name__ == "__main__":
    st = sys.argv[1]; lo, hi = ("2022-01-01", "2023-12-31 23:55") if st in ("density", "audit", "dev") else ("2024-01-01", "2026-10-30 23:55")
    T, U, C = [], {}, {}
    for s in ("BTCUSDT", "ETHUSDT"):
        e, u, c = events(s, lo, hi); T.append(e); U[s] = u; C[s] = c
    T = pd.concat(T, ignore_index=True)
    if st == "density":
        print("events", len(T), T.groupby([T.s, T.t.dt.year]).size().to_dict())
        for s, c in C.items(): print(s, "min monthly coverage px", round(c.px.min(), 3), "oi", round(c.oi.min(), 3), "months<0.95:", int(((c.px < 0.95) | (c.oi < 0.95)).sum()))
        sys.exit()
    if st == "audit":
        print(T[["s", "t", "r1h", "doi", "vx"]].to_string()); sys.exit()
    out = dict(n=len(T), uncond_24h_pct={s: round(float(u * 100), 3) for s, u in U.items()}, missed_median_pct=round(float(T.missed.median() * 100), 2))
    for kk, c in COST.items():
        x = T.ret - 2 * c
        out[kk] = dict(mean_pct=round(float(x.mean() * 100), 2), median_pct=round(float(x.median() * 100), 2), t=round(float(x.mean() / x.std() * np.sqrt(len(x))), 2),
                       by_year_pct={int(y): round(float(v * 100), 2) for y, v in x.groupby(T.t.dt.year).mean().items()})
    xb = T.ret - 2 * COST["base"]
    out["excess_vs_uncond_pct"] = round(float((xb - T.s.map(U)).mean() * 100), 2)
    out["win_rate"] = round(float((xb > 0).mean()), 3)
    out["top5_share"] = round(float(xb.nlargest(5).sum() / xb.sum()), 2) if xb.sum() > 0 else None
    out["descr_hold4h_pct"] = round(float((T.r4 - 2 * COST["base"]).mean() * 100), 2); out["descr_hold72h_pct"] = round(float((T.r72 - 2 * COST["base"]).mean() * 100), 2)
    T.to_csv(f"data/derived/t365_trades_{st}.csv", index=False); print(json.dumps(out, indent=1, default=str))
