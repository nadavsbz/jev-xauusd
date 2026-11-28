"""t328 (docs/prereg/research_t328.md): HalfTrend flips on XAUUSD M15, SL at channel edge, TP 1R/2R/3R thirds, BE after TP1.
Usage: py -3.12 research/stable/t328.py dev|holdout"""
import json, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "research/bd1")
import numpy as np, pandas as pd
from news_files import us_dst

CF = "C:/Users/Benza/AppData/Roaming/MetaQuotes/Terminal/Common/Files/"
SIDE, RISK = 0.8e-4, 0.0025


def load():
    d = pd.read_csv(CF + "t323_XAUUSD_PERIOD_M15.csv")
    t = pd.to_datetime(d.time, unit="s")
    off = np.where([us_dst(x) for x in t], 3, 2)
    d.index = t - pd.to_timedelta(off, unit="h")   # UTC
    return d[~d.index.duplicated()].sort_index()


def halftrend(d, amp=2, chdev=2):
    h, l, c = d.high.values, d.low.values, d.close.values; n = len(d)
    tr = np.maximum(h - l, np.maximum(abs(h - np.r_[c[0], c[:-1]]), abs(l - np.r_[c[0], c[:-1]])))
    atr2 = pd.Series(tr).rolling(100).mean().values / 2; dev = chdev * atr2
    hp = pd.Series(h).rolling(amp).max().values; lp = pd.Series(l).rolling(amp).min().values
    hma = pd.Series(h).rolling(amp).mean().values; lma = pd.Series(l).rolling(amp).mean().values
    trend = np.zeros(n, int); line = np.full(n, np.nan)
    tr_, nxt, maxlow, minhigh, up, dn = 0, 0, l[0], h[0], np.nan, np.nan
    for i in range(amp, n):
        if nxt == 1:
            maxlow = max(lp[i], maxlow)
            if hma[i] < maxlow and c[i] < l[i - 1]: tr_, nxt, minhigh = 1, 0, hp[i]
        else:
            minhigh = min(hp[i], minhigh)
            if lma[i] > minhigh and c[i] > h[i - 1]: tr_, nxt, maxlow = 0, 1, lp[i]
        if tr_ == 0:
            up = (dn if not np.isnan(dn) else maxlow) if trend[i - 1] != 0 else (maxlow if np.isnan(up) else max(maxlow, up))
            line[i] = up
        else:
            dn = (up if not np.isnan(up) else minhigh) if trend[i - 1] != 1 else (minhigh if np.isnan(dn) else min(minhigh, dn))
            line[i] = dn
        trend[i] = tr_
    return trend, line, dev


def run(d):
    trend, line, dev = halftrend(d)
    o, h, l = d.open.values, d.high.values, d.low.values; idx = d.index; n = len(d); hr = idx.hour
    out, tp1hits, i = [], 0, 101
    while i < n - 1:
        flip = trend[i] != trend[i - 1]
        if not flip or np.isnan(dev[i]) or not (7 <= hr[i + 1] < 20): i += 1; continue
        sg = 1 if trend[i] == 0 else -1
        e = o[i + 1]; sl = line[i] - sg * dev[i]; R = sg * (e - sl)
        if R <= 0: i += 1; continue
        tps = [e + sg * k * R for k in (1, 2, 3)]; left, pnl, cost, hit1, j = 3, 0.0, SIDE, False, i + 1
        while j < n and left > 0:
            if j > i + 1 and trend[j - 1] != trend[j - 2]:          # opposite flip on the previous closed bar -> exit at open
                pnl += left / 3 * sg * (o[j] - e) / R; cost += SIDE * left / 3; left = 0; break
            stop_hit = (sg > 0 and l[j] <= sl) or (sg < 0 and h[j] >= sl)
            if stop_hit:
                pnl += left / 3 * sg * (sl - e) / R; cost += SIDE * left / 3; left = 0; break
            for k in range(3 - left, 3):
                if (sg > 0 and h[j] >= tps[k]) or (sg < 0 and l[j] <= tps[k]):
                    pnl += (k + 1) / 3; cost += SIDE / 3; left -= 1
                    if k == 0: hit1 = True; sl = e
                else: break
            j += 1
        if left > 0: break
        risk_frac = R / e
        out.append((idx[i + 1], RISK * pnl - RISK * cost / risk_frac, RISK * cost / risk_frac, hit1))
        tp1hits += hit1; i = max(j - 1, i + 1)
    return pd.DataFrame(out, columns=["t", "r", "c", "tp1"]).set_index("t")


def stats(x):
    eq = 1 + x.cumsum()
    return dict(ann=round(float(x.mean() * 252), 4), sharpe=round(float(x.mean() / x.std() * np.sqrt(252)), 2),
                mdd=round(float((eq / eq.cummax() - 1).min()), 4))


if __name__ == "__main__":
    part = sys.argv[1]
    lo, hi = ("2016-01-01", "2020-12-31") if part == "dev" else ("2021-01-01", "2026-11-15")
    d = load()
    T = run(d["2015-01-01":hi])[lo:hi]
    days = pd.bdate_range(lo, min(pd.Timestamp(hi), T.index[-1]))
    daily = T.r.groupby(T.index.normalize()).sum().reindex(days, fill_value=0)
    dbl = (T.r - T.c).groupby(T.index.normalize()).sum().reindex(days, fill_value=0)
    print(json.dumps({"trades": len(T), "tp1_rate": round(float(T.tp1.mean()), 3), "portfolio": stats(daily),
                      "2x_cost (info)": stats(dbl), "by_year_%": (T.r.groupby(T.index.year).sum() * 100).round(1).to_dict()}, indent=1))
