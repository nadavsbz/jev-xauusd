"""t355 (docs/prereg/research_t355.md): SPY 30-min direction from 30 mega-cap constituents, rolling ridge.
Usage: py -3.12 research/stable/t355.py density|dev|holdout"""
import glob, json, os, sys
import numpy as np, pandas as pd
D = "data/raw/alpaca/m5_t355"
ALPHA, THR, WIN, COST = 10.0, 0.0010, 252, {"base": 0.0002, "stress": 0.0004}
DEC = list(range(5, 66, 6))                        # bar indices 09:55, 10:25, ..., 14:55


def load():
    O, C = {}, {}
    for f in sorted(glob.glob(f"{D}/*.csv.gz")):
        s = os.path.basename(f)[:-7]; a = pd.read_csv(f); a["t"] = pd.to_datetime(a.t, utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
        a = a.drop_duplicates("t").set_index("t"); O[s] = a.o; C[s] = a.c
    O, C = pd.DataFrame(O), pd.DataFrame(C)
    days = sorted(set(C.index.normalize()))
    grid = pd.DatetimeIndex([d + pd.Timedelta(minutes=570 + 5 * i) for d in days for i in range(78)])
    O, C = O.reindex(grid), C.reindex(grid)
    return O, C, pd.DatetimeIndex(days)


def build(O, C, days):
    syms = [s for s in C.columns if s != "SPY"]; n = len(days)
    c = C.values.reshape(n, 78, -1); o = O.values.reshape(n, 78, -1)
    cf = pd.DataFrame(c.reshape(n * 78, -1)).groupby(np.repeat(np.arange(n), 78)).ffill().values.reshape(n, 78, -1)
    o0 = o[:, :1, :]
    prev = np.concatenate([o0, cf[:, :-1, :]], axis=1); r5 = cf / prev - 1
    lag6 = np.concatenate([np.repeat(o0, 6, axis=1), cf[:, :-6, :]], axis=1); r30 = cf / lag6 - 1
    k = list(C.columns).index("SPY"); ks = [list(C.columns).index(s) for s in syms]
    st5, st30 = r5[:, :, ks], r30[:, :, ks]
    X = np.concatenate([st5, st30, (st5 > 0).mean(2, keepdims=True), st5.mean(2, keepdims=True), st5.std(2, keepdims=True),
                        r5[:, :, k:k + 1], r30[:, :, k:k + 1]], axis=2)
    y = np.full((n, 78), np.nan)
    y[:, :72] = cf[:, 6:78, k] / o[:, 1:73, k] - 1      # open of t+1 .. close of t+6
    miss = np.isnan(c[:, :, :]).any(2)                   # any symbol missing a bar
    return X, y, miss


def run(X, y, days, lo, hi):
    n = len(days); trades = []
    months = pd.period_range(pd.Timestamp(lo), pd.Timestamp(hi), freq="M")
    for m in months:
        di = np.where((days.to_period("M") == m))[0]
        if not len(di): continue
        tr = np.arange(max(0, di[0] - WIN), di[0])
        if len(tr) < WIN: continue
        Xt = X[tr][:, 5:72, :].reshape(-1, X.shape[2]); yt = y[tr][:, 5:72].reshape(-1)
        ok = np.isfinite(Xt).all(1) & np.isfinite(yt); Xt, yt = Xt[ok], yt[ok]
        mu, sd = Xt.mean(0), Xt.std(0) + 1e-12; Z = (Xt - mu) / sd; ym = yt.mean()
        w = np.linalg.solve(Z.T @ Z + ALPHA * np.eye(Z.shape[1]), Z.T @ (yt - ym))
        for d in di:
            for t in DEC:
                x = X[d, t]
                if not np.isfinite(x).all() or not np.isfinite(y[d, t]): continue
                p = float(((x - mu) / sd) @ w + ym)
                trades.append(dict(day=days[d], bar=t, pred=p, y=float(y[d, t])))
    return pd.DataFrame(trades)


if __name__ == "__main__":
    st = sys.argv[1]
    O, C, days = load(); X, y, miss = build(O, C, days)
    lo, hi = ("2020-01-01", "2021-12-31") if st in ("density", "dev") else ("2022-01-01", "2026-11-20")
    sel = (days >= lo) & (days <= hi)
    if st == "density":
        full = ~miss[sel][:, DEC].any(1)
        print("days", int(sel.sum()), "days with all symbols at all decision bars", round(float(full.mean()), 3), "symbols", C.shape[1]); sys.exit()
    T = run(X, y, days, lo, hi)
    T["dir"] = np.where(T.pred > THR, 1, np.where(T.pred < -THR, -1, 0))
    A = T[T.dir != 0].copy(); out = {"decisions": len(T), "trades": len(A), "dir_hit_all": round(float((np.sign(T.pred) == np.sign(T.y)).mean()), 3)}
    for k, c in COST.items():
        A["pnl"] = A.dir * A.y - 2 * c
        dly = A.groupby("day").pnl.sum().reindex(sorted(set(T.day)), fill_value=0)
        out[k] = dict(mean_bp=round(float(A.pnl.mean() * 1e4), 2), t=round(float(A.pnl.mean() / A.pnl.std() * np.sqrt(len(A))), 2),
                      sharpe=round(float(dly.mean() / dly.std() * np.sqrt(252)), 2), by_year_pct={int(y_): round(float(v * 100), 2) for y_, v in dly.groupby(dly.index.year).sum().items()})
        if k == "base": base_daily = dly
    A["pnl"] = A.dir * A.y - 2 * COST["base"]
    out["win_rate"] = round(float((A.pnl > 0).mean()), 3); out["long_share"] = round(float((A.dir > 0).mean()), 2)
    try:
        sys.path.insert(0, "research/stable"); from book_tester import i2_daily
        i2 = i2_daily(); c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.resample("D").last().pct_change()
        out["corr_I2"] = round(float(base_daily.corr(i2.reindex(base_daily.index).fillna(0))), 2); out["corr_C1"] = round(float(base_daily.corr(c1.reindex(base_daily.index))), 2)
    except Exception as ex: out["corr_err"] = str(ex)[:80]
    print(json.dumps(out, indent=1, default=str))
