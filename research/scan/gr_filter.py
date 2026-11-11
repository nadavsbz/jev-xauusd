"""Scan round 22 test 2 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 night): extract Gold Reaper's breakout filter with a
fixed logistic model fitted once on the GR period, then trade it unchanged on 2018-2023 (the honest test).
Usage: python research/scan/gr_filter.py"""
import sys, warnings
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
warnings.filterwarnings("ignore")
COST, COST2, HOLD = 0.0002, 0.0003, 30
FIT = ("2024-10-29", "2026-11-10"); TEST = ("2018-01-01", "2023-12-31")

def atr(b, n):
    pc = b.close.shift(1)
    tr = pd.concat([b.high - b.low, (b.high - pc).abs(), (b.low - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()

def bars(m1, rule):
    b = m1.resample(rule, label="left", closed="left").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    return b

def asof(series_by_end, times):        # value of the last completed higher-TF bar at each time
    return series_by_end.reindex(series_by_end.index.union(times)).ffill().reindex(times).values

if __name__ == "__main__":
    m = pd.read_csv("data/derived/scan/m1/XAUUSD.csv"); m.index = pd.to_datetime(m.time, unit="s")
    m = m[~m.index.duplicated()].query("close > 0")[["open", "high", "low", "close"]]
    P = m.open
    b5 = bars(m, "5min"); T = b5.index + pd.Timedelta(minutes=5)            # decision time = bar close
    b15, bh, bd = bars(m, "15min"), bars(m, "1h"), bars(m, "1D")
    end = lambda b, mins: b.index + pd.Timedelta(minutes=mins)
    a15 = pd.Series(atr(b15, 14).values, end(b15, 15)); e200 = pd.Series(b15.close.ewm(span=200).mean().values, end(b15, 15))
    d = b15.close.diff(); up = d.clip(lower=0).ewm(alpha=1/14).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1/14).mean()
    rsi = pd.Series((100 - 100 / (1 + up / dn)).values, end(b15, 15))
    ah = pd.Series(atr(bh, 14).values, end(bh, 60)); ad = pd.Series(atr(bd, 14).values, end(bd, 1440))
    dopen = b5.open.groupby(b5.index.normalize()).transform("first")
    hi, lo = b5.high.rolling(144).max().shift(1), b5.low.rolling(144).min().shift(1)
    a5 = atr(b5, 12); a5med = a5.rolling(1440, min_periods=500).median()
    F = pd.DataFrame(index=b5.index)
    F["A15"], F["E200"], F["RSI"] = asof(a15, T), asof(e200, T), asof(rsi, T)
    F["AH"], F["AD"] = asof(ah, T), asof(ad, T)
    F["c"], F["r60"], F["hi"], F["lo"] = b5.close, b5.close - b5.close.shift(12), hi, lo
    F["act"], F["dop"] = a5 / a5med, b5.close - dopen
    # events, at most one per direction per 60 min
    ev = []; last = {1: None, -1: None}
    longs, shorts = (F.c > F.hi).values, (F.c < F.lo).values
    for i, t in enumerate(F.index):
        for q, hit in ((1, longs[i]), (-1, shorts[i])):
            if hit and (last[q] is None or t - last[q] >= pd.Timedelta(minutes=60)):
                ev.append((t, q)); last[q] = t
    ev = pd.DataFrame(ev, columns=["bar", "q"]); x = F.loc[ev.bar].reset_index(drop=True); q = ev.q.values
    h = (ev.bar + pd.Timedelta(minutes=5)).dt.hour.values
    X = pd.DataFrame({"lon": (h >= 9) & (h <= 14), "ny": (h >= 15) & (h <= 19), "eve": h >= 20,
                      "brk": q * (x.c - np.where(q > 0, x.hi, x.lo)) / x.A15, "act": x.act, "r60": q * x.r60 / x.AH,
                      "trend": q * (x.c - x.E200) / x.A15, "rsi": q * (x.RSI - 50), "dop": q * x.dop / x.AD,
                      "width": (x.hi - x.lo) / x.A15}).astype(float)
    ev["T"] = ev.bar + pd.Timedelta(minutes=5)
    ok = X.notna().all(axis=1) & np.isfinite(X).all(axis=1); ev, X = ev[ok].reset_index(drop=True), X[ok].reset_index(drop=True)
    # labels from Gold Reaper baskets
    g = pd.read_csv("docs/agents/grok_data/myfxbook/goldreaper_history.csv"); g = g[g.Symbol == "XAUUSD"]
    g["o"] = pd.to_datetime(g["Open Date"], format="%m.%d.%Y %H:%M"); g["q"] = np.where(g.Action == "Buy", 1, -1)
    bk = g.groupby(["o", "q"]).size().reset_index()[["o", "q"]]
    lab = np.zeros(len(ev), bool)
    for qq in (1, -1):
        bo = np.sort(bk.o[bk.q == qq].values); idx = np.where(ev.q.values == qq)[0]; tt = ev["T"].values[idx]
        lo_ = np.searchsorted(bo, tt - np.timedelta64(5, "m")); hi_ = np.searchsorted(bo, tt + np.timedelta64(15, "m"), side="right")
        lab[idx] = hi_ > lo_
    covered = 0
    for _, r in bk.iterrows():
        s = ev[(ev.q == r.q) & (ev["T"] >= r.o - pd.Timedelta(minutes=15)) & (ev["T"] <= r.o + pd.Timedelta(minutes=5))]
        covered += len(s) > 0
    fit = (ev["T"] >= FIT[0]) & (ev["T"] <= FIT[1] + " 23:59")
    print(f"events {len(ev)}, in fit period {fit.sum()}, labelled {lab[fit].sum()} ({lab[fit].mean()*100:.1f}%); GR baskets {len(bk)}, covered by an event {covered/len(bk)*100:.1f}%")
    mu, sd = X[fit].mean(), X[fit].std()
    Z = (X - mu) / sd
    mdl = LogisticRegression(C=1.0, max_iter=2000).fit(Z[fit], lab[fit])
    print("  coefs:", dict(zip(X.columns, mdl.coef_[0].round(2))))
    sc = mdl.decision_function(Z); thr = np.sort(sc[fit.values])[::-1][len(bk) - 1]
    sel = ev[sc >= thr].copy()
    print(f"  threshold picks {len(sel[(sel['T'] >= FIT[0])])} events in fit period; precision there {lab[(sc >= thr) & fit.values].mean()*100:.1f}% vs base {lab[fit].mean()*100:.1f}%")
    # trade it
    idx = P.index
    tr = []; busy = {1: pd.Timestamp(0), -1: pd.Timestamp(0)}
    for _, r in sel.sort_values("T").iterrows():
        if r["T"] < busy[r.q]: continue
        i0 = idx.searchsorted(r["T"]); i1 = idx.searchsorted(r["T"] + pd.Timedelta(minutes=HOLD))
        if i0 >= len(idx) or i1 >= len(idx): continue
        t0, t1 = idx[i0], idx[i1]
        if t0 - r["T"] > pd.Timedelta(minutes=10) or t1 - t0 > pd.Timedelta(minutes=HOLD + 30): continue
        g_ = r.q * (P.iloc[i1] / P.iloc[i0] - 1); tr.append((t1.normalize(), r.q, g_)); busy[r.q] = t1
    Tr = pd.DataFrame(tr, columns=["day", "q", "gross"])
    for nm, (a, z) in (("FIT (sanity)", FIT), ("TEST 2018-2023", TEST)):
        y = Tr[(Tr.day >= a) & (Tr.day <= z)]
        for c_ in (COST, COST2):
            n = y.gross - c_
            print(f"  {nm:15s} cost {c_*1e4:.0f}bp: trades {len(y)}, mean {n.mean()*1e4:5.2f} bp (gross {y.gross.mean()*1e4:5.2f}), t {n.mean()/n.std()*np.sqrt(len(n)):5.2f}, hit {(n>0).mean()*100:.0f}%")
        yy = (y.gross - COST); print("    by year (sum %):", yy.groupby(y.day.dt.year).sum().mul(100).round(1).to_dict(),
                                       " long/short mean bp:", round((y[y.q > 0].gross - COST).mean() * 1e4, 2), round((y[y.q < 0].gross - COST).mean() * 1e4, 2))
    daily = (Tr.gross - COST).groupby(Tr.day).sum(); full = pd.Series(0.0, index=pd.bdate_range(daily.index[0], daily.index[-1])); full.loc[daily.index] = daily.values
    xs = scale(full); xs.to_csv("data/derived/scan/R22_grfilter_daily.csv", header=["ret"])
    rep(xs.loc[TEST[0]:TEST[1]], "GR filter TEST")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([xs, i2, c1], axis=1, keys=["G", "I2", "C1"]).loc[TEST[0]:TEST[1]].dropna(subset=["G"]).fillna(0)
    print("    corr:", j.corr().round(2).loc["G"].to_dict())
