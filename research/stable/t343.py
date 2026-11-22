"""t343 (docs/prereg/research_t343.md): mechanical SMC (BOS + overlapping FVG/OB) on BTCUSDT M5, M1 fills. Rulebook = GPT t341 sec. 6.
Usage: py -3.12 research/stable/t343.py density|dev|validation|holdout"""
import glob, json, os, sys, zipfile
import numpy as np, pandas as pd
RAW = "data/raw/binance"; CACHE = "data/derived/t343_m1.pkl"
SPREAD_BP, COST_BP = 1.5, 2.5            # spread proxy; cost per side = 1.5bp RF + 1bp slippage


def load_m1():
    if os.path.exists(CACHE): return pd.read_pickle(CACHE)
    parts = []
    for f in sorted(glob.glob(f"{RAW}/*.zip")):
        z = zipfile.ZipFile(f)
        d = pd.read_csv(z.open(z.namelist()[0]), header=None, usecols=[0, 1, 2, 3, 4])
        if not str(d.iloc[0, 0]).isdigit(): d = d.iloc[1:].astype(float)
        parts.append(d)
    d = pd.concat(parts); d.columns = ["t", "o", "h", "l", "c"]
    t = d.t.astype("int64"); t = np.where(t > 1e14, t // 1000, t)            # 2025+ files are in microseconds
    d.index = pd.to_datetime(t, unit="ms"); d = d.drop(columns="t").astype(float)
    d = d[~d.index.duplicated()].sort_index(); d.to_pickle(CACHE); return d


def m5_from(m1):
    x = m1.resample("5min", label="left", closed="left").agg({"o": "first", "h": "max", "l": "min", "c": "last"}).dropna()
    et = x.index.tz_localize("UTC").tz_convert("America/New_York")
    x["etmin"] = et.hour * 60 + et.minute; x["etday"] = et.normalize().tz_localize(None)
    pc = x.c.shift(1)
    trr = pd.concat([x.h - x.l, (x.h - pc).abs(), (x.l - pc).abs()], axis=1).max(axis=1)
    x["atr"] = trr.ewm(alpha=1 / 14, adjust=False).mean().shift(1)            # ATR14 at t-1
    body = (x.c - x.o).abs(); x["body"] = body; x["medbody"] = body.rolling(20).median().shift(1)
    x["rng"] = x.h - x.l
    return x


def setups(x, mode):
    """yield dicts: i (index of bar whose close completes the setup), dir, entry, stop, kind ('limit'|'stop'), expiry (bars)"""
    o, h, l, c = x.o.values, x.h.values, x.l.values, x.c.values
    atr, body, med, rng = x.atr.values, x.body.values, x.medbody.values, x.rng.values
    n = len(x); sh = sl = None; last_bull = last_bear = -10 ** 9; out = []
    disp = lambda t: med[t] > 0 and body[t] >= 1.5 * med[t] and rng[t] > 0 and body[t] / rng[t] >= 0.6
    buf = lambda t: max(2 * SPREAD_BP * 1e-4 * c[t], 0.05 * atr[t])

    def fvg(k, d):                                    # FVG completed at bar k, direction d
        if k < 2: return None
        mn = max(2 * SPREAD_BP * 1e-4 * c[k], 0.10 * atr[k])
        mid_ok = rng[k - 1] > 0 and body[k - 1] / rng[k - 1] >= 0.6
        if d == 1 and l[k] - h[k - 2] >= mn and c[k - 1] > o[k - 1] and mid_ok: return (h[k - 2], l[k])
        if d == -1 and l[k - 2] - h[k] >= mn and c[k - 1] < o[k - 1] and mid_ok: return (h[k], l[k - 2])
        return None

    for t in range(25, n - 1):
        if np.isnan(atr[t]) or np.isnan(med[t]): continue
        i = t - 2                                     # swing confirmed at close of t (2 left / 2 right)
        if h[i] > h[i - 1] and h[i] > h[i - 2] and h[i] >= h[i + 1] and h[i] >= h[i + 2]: new_sh = h[i]
        else: new_sh = None
        if l[i] < l[i - 1] and l[i] < l[i - 2] and l[i] <= l[i + 1] and l[i] <= l[i + 2]: new_sl = l[i]
        else: new_sl = None
        b = buf(t)
        bull = sh is not None and c[t] > sh + b and disp(t)
        bear = sl is not None and c[t] < sl - b and disp(t)
        for d, hit in ((1, bull), (-1, bear)):
            if not hit: continue
            if mode == "bos":
                out.append(dict(i=t, dir=d, kind="stop", entry=(h[t] + SPREAD_BP * 1e-4 * c[t]) if d == 1 else (l[t] - SPREAD_BP * 1e-4 * c[t]),
                                stop=(l[t] - b) if d == 1 else (h[t] + b), expiry=3))
                continue
            prev_bos = last_bull if d == 1 else last_bear
            j = None
            for q in range(t - 1, max(t - 11, prev_bos), -1):
                if (d == 1 and c[q] < o[q]) or (d == -1 and c[q] > o[q]): j = q; break
            if j is None: continue
            ob = (l[j], h[j])
            if mode == "ob":
                out.append(dict(i=t, dir=d, kind="limit", entry=(ob[0] + ob[1]) / 2, stop=(ob[0] - b) if d == 1 else (ob[1] + b), expiry=24))
                continue
            # combined: newest FVG with k in [j+3, t]; else wait one bar (k = t+1)
            f, done_at = None, t
            for k in range(t, j + 2, -1):
                f = fvg(k, d)
                if f: break
            if not f and t + 1 < n:
                f = fvg(t + 1, d); done_at = t + 1
            if not f: continue
            lo_, hi_ = max(f[0], ob[0]), min(f[1], ob[1])
            if lo_ >= hi_: continue
            out.append(dict(i=done_at, dir=d, kind="limit", entry=(lo_ + hi_) / 2, stop=(ob[0] - b) if d == 1 else (ob[1] + b), expiry=12))
        if mode == "fvg":
            for d in (1, -1):
                f = fvg(t, d)
                if f: out.append(dict(i=t, dir=d, kind="limit", entry=(f[0] + f[1]) / 2, stop=(f[0] - b) if d == 1 else (f[1] + b), expiry=12))
        if bull: sh = None; last_bull = t
        if bear: sl = None; last_bear = t
        if sh is not None and c[t] > sh: sh = None
        if sl is not None and c[t] < sl: sl = None
        if new_sh is not None: sh = new_sh
        if new_sl is not None: sl = new_sl
    return out


def simulate(x, m1, S, cost_mul=1.0):
    ts = x.index; etmin = x.etmin.values; etday = x.etday.values
    m1et = m1.index.tz_localize("UTC").tz_convert("America/New_York")
    m1min = (m1et.hour * 60 + m1et.minute).values; m1day = m1et.normalize().tz_localize(None).values
    mo, mh, ml = m1.o.values, m1.h.values, m1.l.values; mi = m1.index
    trades, traded_days, busy_until = [], set(), None
    for s in S:
        t = s["i"]
        if not (570 <= etmin[t] <= 685): continue                    # setup bar starts 09:30..11:25 ET
        day = etday[t]
        if day in traded_days: continue
        place = ts[t] + pd.Timedelta(minutes=5)                     # after the setup bar closes
        if busy_until is not None and place < busy_until: continue
        d, e, st = s["dir"], s["entry"], s["stop"]
        R = (e - st) * d
        cs = COST_BP * 1e-4 * cost_mul
        if R <= 0 or R < 3 * 2 * COST_BP * 1e-4 * e: continue
        tgt = e + 2 * R * d
        exp_t = place + pd.Timedelta(minutes=5 * s["expiry"])
        a = mi.searchsorted(place); fill = None
        while a < len(mi) and mi[a] < exp_t:
            if m1day[a] != day or m1min[a] >= 720: break             # entries until 12:00 ET
            if s["kind"] == "limit":
                if (d == 1 and ml[a] <= e) or (d == -1 and mh[a] >= e): fill = a; break
                if (d == 1 and ml[a] < st) or (d == -1 and mh[a] > st): break     # invalidated before fill
            else:
                if (d == 1 and mh[a] >= e) or (d == -1 and ml[a] <= e): fill = a; break
            a += 1
        if fill is None: continue
        b = fill; ex = None
        while b < len(mi):
            if m1day[b] != day or m1min[b] >= 960: ex = mo[b] if m1day[b] == day else mo[b]; break
            stop_hit = (ml[b] <= st) if d == 1 else (mh[b] >= st)
            tgt_hit = ((mh[b] >= tgt) if d == 1 else (ml[b] <= tgt)) and b > fill
            if stop_hit: ex = st; break
            if tgt_hit: ex = tgt; break
            b += 1
        if ex is None: continue
        r = ((ex - e) * d - cs * (e + ex)) / R
        trades.append(dict(t=mi[fill], dir=d, R=r)); traded_days.add(day); busy_until = mi[min(b, len(mi) - 1)]
    return pd.DataFrame(trades)


def summ(T):
    if not len(T): return dict(n=0)
    r = T.R; yr = r.groupby(T.t.dt.year).sum(); top = r.sort_values(ascending=False).head(10).sum()
    pf = r[r > 0].sum() / -r[r < 0].sum() if (r < 0).any() else None
    return dict(n=int(len(r)), meanR=round(float(r.mean()), 3), t=round(float(r.mean() / r.std() * np.sqrt(len(r))), 2),
                PF=round(float(pf), 2) if pf else None, win=round(float((r > 0).mean()), 3),
                top10_share=round(float(top / r.sum()), 2) if r.sum() > 0 else None,
                by_year_R=yr.round(1).to_dict(), pos_years=f"{int((yr > 0).sum())}/{len(yr)}")


if __name__ == "__main__":
    part = sys.argv[1]
    m1 = load_m1()
    if part == "density":
        print({int(y): round(v / (365 * 1440), 3) for y, v in m1.groupby(m1.index.year).size().items()}); sys.exit()
    lo, hi = {"dev": ("2020-01-01", "2022-12-31"), "validation": ("2023-01-01", "2024-12-31"), "holdout": ("2025-01-01", "2026-11-20")}[part]
    m1p = m1[pd.Timestamp(lo) - pd.Timedelta(days=5):pd.Timestamp(hi) + pd.Timedelta(days=1)]
    x = m5_from(m1p)
    out = {}
    for mode in ("combined", "fvg", "bos", "ob"):
        S = setups(x, mode)
        T = simulate(x, m1p, S); T = T[(T.t >= lo) & (T.t <= pd.Timestamp(hi) + pd.Timedelta(days=1))] if len(T) else T
        T2 = simulate(x, m1p, S, 2.0); T2 = T2[(T2.t >= lo) & (T2.t <= pd.Timestamp(hi) + pd.Timedelta(days=1))] if len(T2) else T2
        out[mode] = summ(T); out[mode]["meanR_2x"] = round(float(T2.R.mean()), 3) if len(T2) else None
        print(mode, out[mode], flush=True)
    json.dump(out, open(f"data/derived/t343_{part}.json", "w"), indent=1, default=str)
