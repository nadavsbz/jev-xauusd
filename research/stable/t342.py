"""t342 (docs/prereg/research_t342.md): 6 popular TradingView community indicators (default settings), always-in flip, BTC/ETH H1+H4.
Usage: py -3.12 research/stable/t342.py density|dev|holdout"""
import json, sys
import numpy as np, pandas as pd
CF = "C:/Users/Benza/AppData/Roaming/MetaQuotes/Terminal/Common/Files/"
SWAP, SIDE = 0.0475, 1.5e-4


def load(sym, tf):
    d = pd.read_csv(CF + f"t326_{sym}_PERIOD_H1.csv")
    x = pd.DataFrame({"o": d.open.values, "h": d.high.values, "l": d.low.values, "c": d.close.values, "v": d.tick_volume.values},
                     index=pd.to_datetime(d.time, unit="s")).sort_index()
    x = x[~x.index.duplicated()]
    if tf == "H4":
        x = x.resample("4h").agg({"o": "first", "h": "max", "l": "min", "c": "last", "v": "sum"}).dropna()
    return x


def rma(s, n):
    return s.ewm(alpha=1 / n, adjust=False).mean()


def tr(x):
    pc = x.c.shift(1)
    return pd.concat([x.h - x.l, (x.h - pc).abs(), (x.l - pc).abs()], axis=1).max(axis=1)


def supertrend(x, n=10, m=3.0):
    atr = rma(tr(x), n).values; src = ((x.h + x.l) / 2).values; c = x.c.values
    up = src - m * atr; dn = src + m * atr; tr_ = np.ones(len(x)); u = up.copy(); d = dn.copy()
    for i in range(1, len(x)):
        u[i] = max(up[i], u[i - 1]) if c[i - 1] > u[i - 1] else up[i]
        d[i] = min(dn[i], d[i - 1]) if c[i - 1] < d[i - 1] else dn[i]
        tr_[i] = 1 if (tr_[i - 1] == -1 and c[i] > d[i - 1]) else (-1 if (tr_[i - 1] == 1 and c[i] < u[i - 1]) else tr_[i - 1])
    return pd.Series(tr_, index=x.index)


def utbot(x, a=1.0, n=10):
    atr = rma(tr(x), n).values; s = x.c.values; st = np.zeros(len(x)); pos = np.zeros(len(x))
    st[0] = s[0]
    for i in range(1, len(x)):
        p = st[i - 1]; nl = a * atr[i]
        if s[i] > p and s[i - 1] > p: st[i] = max(p, s[i] - nl)
        elif s[i] < p and s[i - 1] < p: st[i] = min(p, s[i] + nl)
        elif s[i] > p: st[i] = s[i] - nl
        else: st[i] = s[i] + nl
        if s[i] > st[i] and s[i - 1] <= st[i - 1]: pos[i] = 1
        elif s[i] < st[i] and s[i - 1] >= st[i - 1]: pos[i] = -1
        else: pos[i] = pos[i - 1]
    return pd.Series(pos, index=x.index)


def mfi(x, n=14):
    tp = (x.h + x.l + x.c) / 3; mf = tp * x.v
    pos = mf.where(tp > tp.shift(1), 0.0).rolling(n).sum(); neg = mf.where(tp < tp.shift(1), 0.0).rolling(n).sum()
    return 100 - 100 / (1 + pos / neg.replace(0, np.nan))


def alphatrend(x, coeff=1.0, ap=14):
    atr = tr(x).rolling(ap).mean().values; m = mfi(x, ap).values
    upT = x.l.values - atr * coeff; dnT = x.h.values + atr * coeff
    at = np.zeros(len(x)); pos = np.zeros(len(x))
    for i in range(1, len(x)):
        if np.isnan(atr[i]) or np.isnan(m[i]): at[i] = at[i - 1]; continue
        at[i] = (at[i - 1] if upT[i] < at[i - 1] else upT[i]) if m[i] >= 50 else (at[i - 1] if dnT[i] > at[i - 1] else dnT[i])
        if i >= 3:
            if at[i] > at[i - 2] and at[i - 1] <= at[i - 3]: pos[i] = 1
            elif at[i] < at[i - 2] and at[i - 1] >= at[i - 3]: pos[i] = -1
            else: pos[i] = pos[i - 1]
    return pd.Series(pos, index=x.index)


def chandelier(x, n=22, m=3.0):
    atr = (m * rma(tr(x), n)).values; c = x.c.values
    hh = x.c.rolling(n).max().values; ll = x.c.rolling(n).min().values
    ls = hh - atr; ss = ll + atr; L = ls.copy(); S = ss.copy(); d = np.ones(len(x))
    for i in range(1, len(x)):
        if np.isnan(ls[i]): d[i] = d[i - 1]; continue
        L[i] = max(ls[i], L[i - 1]) if (not np.isnan(L[i - 1]) and c[i - 1] > L[i - 1]) else ls[i]
        S[i] = min(ss[i], S[i - 1]) if (not np.isnan(S[i - 1]) and c[i - 1] < S[i - 1]) else ss[i]
        d[i] = 1 if (not np.isnan(S[i - 1]) and c[i] > S[i - 1]) else (-1 if (not np.isnan(L[i - 1]) and c[i] < L[i - 1]) else d[i - 1])
    return pd.Series(d, index=x.index)


def ssl(x, n=10):
    sh = x.h.rolling(n).mean().values; sl = x.l.rolling(n).mean().values; c = x.c.values; h = np.zeros(len(x))
    for i in range(1, len(x)):
        h[i] = 1 if c[i] > sh[i] else (-1 if c[i] < sl[i] else h[i - 1])
    return pd.Series(h, index=x.index)


def rangefilter(x, per=100, mult=3.0):
    s = x.c
    avr = s.diff().abs().ewm(span=per, adjust=False).mean(); r = (avr.ewm(span=per * 2 - 1, adjust=False).mean() * mult).values
    v = s.values; f = np.zeros(len(x)); f[0] = v[0]; up = np.zeros(len(x)); dn = np.zeros(len(x)); pos = np.zeros(len(x))
    for i in range(1, len(x)):
        p = f[i - 1]
        f[i] = (p if v[i] - r[i] < p else v[i] - r[i]) if v[i] > p else (p if v[i] + r[i] > p else v[i] + r[i])
        up[i] = up[i - 1] + 1 if f[i] > f[i - 1] else (0 if f[i] < f[i - 1] else up[i - 1])
        dn[i] = dn[i - 1] + 1 if f[i] < f[i - 1] else (0 if f[i] > f[i - 1] else dn[i - 1])
        if v[i] > f[i] and up[i] > 0: pos[i] = 1
        elif v[i] < f[i] and dn[i] > 0: pos[i] = -1
        else: pos[i] = pos[i - 1]
    return pd.Series(pos, index=x.index)


IND = {"supertrend": supertrend, "utbot": utbot, "alphatrend": alphatrend, "chandelier": chandelier, "ssl": ssl, "rangefilter": rangefilter}


def backtest(x, sig, side):
    pos = sig.shift(1).fillna(0)                         # signal at bar close -> held from next bar open
    ret = x.o.shift(-1) / x.o - 1                       # open-to-open bar return
    hrs = x.index.to_series().diff().shift(-1).dt.total_seconds().fillna(3600) / 3600
    net = pos * ret - side * pos.diff().abs().fillna(pos.abs()) - SWAP * pos.abs() * hrs / 24 / 365
    return net.fillna(0), pos


def daily(net, lo, hi):
    d = net.groupby(net.index.normalize()).sum(); return d.reindex(pd.date_range(lo, hi), fill_value=0)


def st(d):
    yr = d.groupby(d.index.year).sum(); eq = 1 + d.cumsum()
    sh = d.mean() / d.std() * np.sqrt(365); yrs = len(d) / 365
    return dict(sharpe=round(float(sh), 2), t=round(float(sh * np.sqrt(yrs)), 2), ann_pct=round(float(d.mean() * 365 * 100), 1),
                mdd=round(float((eq / eq.cummax() - 1).min()), 3), by_year_pct=(yr * 100).round(1).to_dict(), pos_years=f"{int((yr > 0).sum())}/{len(yr)}")


if __name__ == "__main__":
    part = sys.argv[1]
    if part == "density":
        for s in ("BTCUSD", "ETHUSD"):
            x = load(s, "H1"); print(s, {int(y): round(v / (24 * 365), 3) for y, v in x.groupby(x.index.year).size().items()})
        sys.exit()
    lo, hi = ("2018-01-01", "2022-12-31") if part == "dev" else ("2023-01-01", "2026-11-19")
    only = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.resample("D").last().pct_change()
    out = {}
    for s in ("BTCUSD", "ETHUSD"):
        for tf in ("H1", "H4"):
            x = load(s, tf)
            bh = daily(x.o.shift(-1) / x.o - 1 - SWAP / 365 / (24 if tf == "H1" else 6), lo, hi)
            for name, fn in IND.items():
                key = f"{s}_{tf}_{name}"
                if only and key not in only: continue
                sig = fn(x)
                net, pos = backtest(x, sig, SIDE); net2, _ = backtest(x, sig, 2 * SIDE)
                d = daily(net[lo:hi], lo, hi); d2 = daily(net2[lo:hi], lo, hi)
                r = st(d); r["t_2x"] = st(d2)["t"]; r["flips_per_year"] = int(pos[lo:hi].diff().abs().gt(0).sum() / ((pd.Timestamp(hi) - pd.Timestamp(lo)).days / 365))
                r["corr_C1"] = round(float(d.corr(c1.reindex(d.index))), 2)
                r["buyhold_sharpe"] = st(bh)["sharpe"]
                yrs = int(r["pos_years"].split("/")[0])
                r["PASS_DEV"] = bool(r["t"] >= 2.9 and yrs >= 4 and r["t_2x"] >= 2.0) if part == "dev" else None
                out[key] = r
                print(key, r["sharpe"], r["t"], r["pos_years"], r["t_2x"], r["corr_C1"], r["PASS_DEV"], flush=True)
    json.dump(out, open(f"data/derived/t342_{part}.json", "w"), indent=1, default=str)
