"""Indicator gate for BD crash days (docs/BD_TA_GATE_PLAN.md, pre-registered 26.10.2026).
Every M15 bar gets ~50 past-only features (channels, Bollinger, momentum, moving averages, support/resistance, volume,
volatility, time, scheduled news) on H1/H4/D1 scales, computed as rolling windows of 4/16/96 M15 bars, so only closed data is used.
Label: within the next 24 h the price reaches +-2% of the bar's close (bar highs/lows).
Walk-forward HistGradientBoosting (fixed params); test periods 2023, 2024, 2025, 12/25-10/26 out of time, 2022 out of year.
Writes the block files for the tester (NewsFile with NewsBeforeMin=0, NewsAfterMin=15): blocked bars as broker unix times of the
NEXT bar (the decision is made at the bar close), and the same merged with the top-news windows (30 before, 60 after) in 15-min slots.
Usage: python research/hybrid/ta_gate.py"""
import glob, sys
import numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
sys.path.insert(0, "research/bd1"); from news_files import us_dst

PERIODS = ["rf2022", "rf2023", "rf2024", "rf2025", "eg2526"]
TF = {"h1": 4, "h4": 16, "d1": 96}
CF = "C:/Users/Benza/AppData/Roaming/MetaQuotes/Terminal/Common/Files/"

def rsi(c, n):
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1 / n).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n).mean()
    return 100 - 100 / (1 + up / dn)

def linreg(c, n):
    x = np.arange(n) - (n - 1) / 2
    def f(w):
        b = (x * (w - w.mean())).sum() / (x ** 2).sum()
        res = w - (w.mean() + b * x); ss = ((w - w.mean()) ** 2).sum()
        return b, 1 - (res ** 2).sum() / ss if ss > 0 else 0, res[-1] / (res.std() + 1e-12)
    v = np.array([f(c.values[i - n + 1:i + 1]) if i >= n - 1 else (np.nan,) * 3 for i in range(len(c))])
    return v[:, 0], v[:, 1], v[:, 2]

def features(p):
    b = pd.read_csv(glob.glob(f"data/derived/crash_signs/bars_{p}_*_PERIOD_M15.csv")[0])
    ts = pd.to_datetime(b.time, unit="s")
    utc = ts - pd.to_timedelta(np.where([p.startswith("rf") and us_dst(t) for t in ts], 3, 2), unit="h")
    c, h, l, v = b.close, b.high, b.low, b.tick_volume
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    atr_d = tr.rolling(96 * 20, min_periods=96 * 5).mean() * 96 ** 0.5   # ~ daily range scale
    F = pd.DataFrame(index=b.index)
    for k, m in TF.items():
        atr = tr.rolling(14 * m, min_periods=4 * m).mean() * m ** 0.5
        mid = c.rolling(20 * m).mean(); sd = c.rolling(20 * m).std()
        F[f"bb_pb_{k}"] = (c - (mid - 2 * sd)) / (4 * sd)
        F[f"bb_w_{k}"] = 4 * sd / c
        F[f"rsi_{k}"] = rsi(c, 14 * m)
        for e in (20, 50, 200):
            F[f"ema{e}_{k}"] = (c - c.ewm(span=e * m).mean()) / atr
        F[f"align_{k}"] = np.sign(c.ewm(span=20 * m).mean() - c.ewm(span=50 * m).mean()) + np.sign(c.ewm(span=50 * m).mean() - c.ewm(span=200 * m).mean())
        n = 20 * m if k != "d1" else 480   # D1 channel over 5 days (20 days = 1,920 bars is too slow here)
        s, r2, pos = linreg(c, n)
        F[f"ch_slope_{k}"] = s * n / atr; F[f"ch_r2_{k}"] = r2; F[f"ch_pos_{k}"] = pos
    for n in (4, 16, 96, 480, 1920):
        F[f"roc_{n}"] = np.log(c / c.shift(n)) / (atr_d / c)
    for n, nm in ((96, "1d"), (480, "1w"), (1920, "20d")):
        hi = h.rolling(n).max().shift(1); lo = l.rolling(n).min().shift(1)
        F[f"d_hi_{nm}"] = (hi - c) / atr_d; F[f"d_lo_{nm}"] = (c - lo) / atr_d
    F["vol_h1"] = v.rolling(4).sum() / v.rolling(96 * 20, min_periods=96 * 5).mean() / 4
    F["vol_h4"] = v.rolling(16).sum() / v.rolling(96 * 20, min_periods=96 * 5).mean() / 16
    F["atr_h1_d"] = tr.rolling(4).mean() * 96 ** 0.5 / atr_d
    r = np.log(c).diff()
    F["rv_24h_20d"] = r.rolling(96).std() / r.rolling(1920, min_periods=480).std()
    F["atr_d_pct"] = atr_d / c
    F["hour"] = utc.dt.hour; F["wd"] = utc.dt.dayofweek
    ev = np.array([int(x) for x in open(f"data/derived/news/news_top_{p[:2]}.txt")])
    t_close = b.time.values + 900
    j = np.searchsorted(ev, t_close)
    F["min_to_news"] = np.where(j < len(ev), (ev[np.minimum(j, len(ev) - 1)] - t_close) / 60, 1e4).clip(max=1e4)
    F["news_24h"] = np.searchsorted(ev, t_close + 86400) - j
    # label: +-2% within the next 96 bars
    fh = h[::-1].rolling(96, min_periods=1).max()[::-1].shift(-1); fl = l[::-1].rolling(96, min_periods=1).min()[::-1].shift(-1)
    y = ((fh / c - 1 >= 0.02) | (1 - fl / c >= 0.02)).astype(float); y[b.index[-96:]] = np.nan
    F["y"] = y; F["time"] = b.time; F["period"] = p
    return F

if __name__ == "__main__":
    D = pd.concat([features(p) for p in PERIODS], ignore_index=True)
    X = [x for x in D.columns if x not in ("y", "time", "period")]
    print(len(X), "features; label rate per period:", D.groupby("period").y.mean().round(3).to_dict())
    folds = {"rf2022": ["rf2023", "rf2024", "rf2025"], "rf2023": ["rf2022"], "rf2024": ["rf2022", "rf2023"],
             "rf2025": ["rf2022", "rf2023", "rf2024"], "eg2526": ["rf2022", "rf2023", "rf2024", "rf2025"]}
    block, imp = {}, []
    for test, train in folds.items():
        tr = D[D.period.isin(train) & D.y.notna()]
        te = D[(D.period == test)]
        res = {}
        for name, cols in (("all", X), ("atr_only", ["atr_d_pct", "atr_h1_d", "rv_24h_20d", "bb_w_h1", "bb_w_h4", "bb_w_d1"])):
            m = HistGradientBoostingClassifier(max_iter=200, max_depth=4, learning_rate=0.05, random_state=0).fit(tr[cols], tr.y)
            pt = m.predict_proba(te[cols])[:, 1]; ok = te.y.notna()
            res[name] = roc_auc_score(te.y[ok], pt[ok])
            if name == "all":
                thr = np.quantile(m.predict_proba(tr[cols])[:, 1], 0.75)
                blk = te.time.values[pt >= thr] + 900
                block[test] = blk
                yb = te.y[ok][pt[ok] >= thr].mean(); yn = te.y[ok][pt[ok] < thr].mean()
                res.update(blocked=f"{(pt >= thr).mean():.0%}", y_blocked=f"{yb:.2f}", y_open=f"{yn:.2f}")
        print(test, "<-", "+".join(train), {k: (round(v, 3) if isinstance(v, float) else v) for k, v in res.items()})
    for br in ("rf", "eg"):
        g = np.sort(np.concatenate([v for k, v in block.items() if k[:2] == br])).astype(np.int64)
        ev = np.array([int(x) for x in open(f"data/derived/news/news_top_{br}.txt")])
        nt = (ev[:, None] + np.arange(-30, 60, 15)[None, :] * 60).ravel()
        for name, arr in ((f"gate_{br}.txt", g), (f"gatent_{br}.txt", np.unique(np.concatenate([g, nt])))):
            txt = "\n".join(str(x) for x in arr) + "\n"
            open(f"data/derived/news/{name}", "w").write(txt); open(CF + name, "w").write(txt)
            print(name, len(arr))
