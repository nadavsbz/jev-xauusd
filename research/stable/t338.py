"""t338 (docs/prereg/research_t338.md): long-only all-time-high trend on US stocks, Alpaca daily.
Usage: py -3.12 research/stable/t338.py trades|coverage|dev|holdout"""
import glob, json, os, re, sys
import numpy as np, pandas as pd
RAW = "data/raw/alpaca"; TR = "data/derived/t338"; os.makedirs(TR, exist_ok=True)
BAD = re.compile(r"\bETF\b|\bETN\b|fund|trust|ishares|proshares|direxion|index|notes|\bright|warrant|\bunit|preferred|depositary|acquisition", re.I)

def universe():
    A = json.load(open(f"{RAW}/assets.json"))
    return {a["symbol"] for a in A if a["exchange"] in ("NYSE", "NASDAQ", "AMEX") and re.fullmatch(r"[A-Z]{1,5}", a["symbol"])
            and not BAD.search(a.get("name") or "")}

def batch_trades(fr, fa, U):
    R = pd.read_csv(fr, usecols=["s", "t", "c", "v"]); R = R.dropna(subset=["t"]); R["d"] = pd.to_datetime(R.t.str[:10])
    A = pd.read_csv(fa)
    if not len(A): return [], []
    A["d"] = pd.to_datetime(A.t)
    D = A.merge(R[["s", "d", "c", "v"]].rename(columns={"c": "rc"}), on=["s", "d"]).sort_values(["s", "d"])
    D = D[D.s.isin(U)]
    trades, paths = [], []
    for s, g in D.groupby("s", sort=False):
        seg = (g.d.diff().dt.days > 15).cumsum()
        for _, x in g.groupby(seg):
            if len(x) < 253: continue
            d = x.d.values; o = x.o.values; h = x.h.values; l = x.l.values; c = x.c.values
            pc = np.r_[np.nan, c[:-1]]
            tr = np.nanmax(np.c_[h - l, np.abs(h - pc), np.abs(l - pc)], axis=1)
            atr = pd.Series(tr).rolling(42).mean().values
            sig = pd.Series(np.log(c)).diff().rolling(42).std().values * np.sqrt(252)
            dv = pd.Series(x.rc.values * x.v.values).rolling(42).mean().values
            prevmax = np.r_[np.nan, np.maximum.accumulate(c)[:-1]]
            elig = (x.rc.values > 10) & (dv > 1e6) & (np.arange(len(x)) >= 251)
            entry_sig = elig & (c >= prevmax)
            i, n = 0, len(x)
            while i < n - 1:
                if entry_sig[i] and np.isfinite(atr[i]) and sig[i] > 0:
                    e = i + 1; ath = c[i]; stop = ath * (1 - 10 * atr[i] / c[i]); stop0 = stop
                    j = e; ex = None
                    while j < n:
                        ath = max(ath, c[j]); stop = max(stop, ath * (1 - 10 * atr[j] / c[j]))
                        if c[j] < stop and j + 1 < n: ex = j + 1; break
                        j += 1
                    if ex is None: ex_i, ex_px, ex_kind = n - 1, c[n - 1], "end"
                    else: ex_i, ex_px, ex_kind = ex, o[ex], "stop"
                    trades.append(dict(s=s, sig_d=d[i], ed=d[e], ep=o[e], xd=d[ex_i], xp=ex_px, kind=ex_kind, sigma=sig[i], stop0=stop0))
                    paths.append(pd.DataFrame({"tid": len(trades) - 1, "d": d[e:ex_i + 1], "c": c[e:ex_i + 1]}))
                    i = ex_i if ex_kind == "stop" else n
                    continue
                i += 1
    return trades, paths

if __name__ == "__main__":
    part = sys.argv[1]
    if part == "trades":
        U = universe(); T, P = [], []
        for fr in sorted(glob.glob(f"{RAW}/daily/*.csv.gz")):
            fa = f"{RAW}/daily_adj/{os.path.basename(fr)}"
            t, p = batch_trades(fr, fa, U)
            off = len(T)
            for q in p: q["tid"] += off
            T += t; P += p
        T = pd.DataFrame(T); T.index.name = "tid"; T.to_csv(f"{TR}/trades.csv.gz")
        pd.concat(P).to_csv(f"{TR}/paths.csv.gz", index=False)
        print(len(T), "trades", T.groupby(pd.to_datetime(T.ed).dt.year).size().to_dict()); sys.exit()
    if part == "coverage":
        U = universe(); first, last = {}, {}
        for fa in sorted(glob.glob(f"{RAW}/daily_adj/*.csv.gz")):
            A = pd.read_csv(fa, usecols=["s", "t"])
            if not len(A): continue
            A = A[A.s.isin(U)]; g = A.groupby("s").t
            first.update(g.min().to_dict()); last.update(g.max().to_dict())
        L = pd.Series(last); F = pd.Series(first)
        print("symbols with data:", len(L), " ended before 2020:", int((L < "2020-01-01").sum()), " ended before 2018:", int((L < "2018-01-01").sum()),
              " started by 2016-01-31:", int((F <= "2016-01-31").sum()))
        print("symbols alive per year-end:", {y: int(((F <= f"{y}-12-31") & (L >= f"{y}-12-01")).sum()) for y in range(2016, 2027)})
        sys.exit()

def portfolio(T, P, cost, start="2016-11-01", end="2026-11-20"):
    T = T.copy(); T["ed"] = pd.to_datetime(T.ed); T["xd"] = pd.to_datetime(T.xd)
    P = P.copy(); P["d"] = pd.to_datetime(P.d)
    T = T[(T.ed >= start) & (T.ed <= end)]
    P = P[P.tid.isin(T.index)]
    C = P.pivot_table(index="d", columns="tid", values="c")
    days = C.index[(C.index >= start) & (C.index <= end)]
    ent = T.groupby("ed").groups; ext = T.groupby("xd").groups
    cash, E, sh, out, gross, npos, pnl = 1.0, 1.0, {}, [], [], [], {}
    lastpx = {}
    for d in days:
        row = C.loc[d]
        # exits at today's open (stop) or at the last close (end of series)
        for tid in ext.get(d, []):
            if tid in sh:
                px = T.at[tid, "xp"]; v = sh.pop(tid) * px; cash += v * (1 - cost); pnl[tid] = pnl.get(tid, 0) + v * (1 - cost)
        # entries at today's open
        new = [t for t in ent.get(d, []) if t not in sh]
        if new:
            N = len(sh) + len(new)
            w = {t: (0.30 / T.at[t, "sigma"]) / max(200, N) for t in new}
            held = sum(sh[t] * lastpx[t] for t in sh)
            room = max(0.0, 1.0 * E - held); room = min(room, cash / (1 + cost))
            tot = sum(w.values()) * E
            k = min(1.0, room / tot) if tot > 0 else 0
            for t in new:
                notional = w[t] * E * k
                if notional <= 0: continue
                sh[t] = notional / T.at[t, "ep"]; cash -= notional * (1 + cost); pnl[t] = -notional * (1 + cost)
        # mark to market
        for t in list(sh):
            px = row.get(t, np.nan)
            if np.isfinite(px): lastpx[t] = px
            elif t not in lastpx: lastpx[t] = T.at[t, "ep"]
        held = sum(sh[t] * lastpx[t] for t in sh)
        E = cash + held; out.append(E); gross.append(held / E); npos.append(len(sh))
    for t in sh: pnl[t] = pnl.get(t, 0) + sh[t] * lastpx[t]          # open positions at the end: marked at the last close
    eq = pd.Series(out, index=days)
    return eq, pd.Series(gross, index=days), pd.Series(npos, index=days), pnl

def st(eq, lo, hi):
    e = eq[lo:hi]; r = e.pct_change().dropna()
    yrs = (e.index[-1] - e.index[0]).days / 365.25
    yr = e.resample("YE").last().pct_change(); yr.iloc[0] = e.resample("YE").last().iloc[0] / e.iloc[0] - 1
    return dict(cagr=round(float((e.iloc[-1] / e.iloc[0]) ** (1 / yrs) - 1), 4), sharpe=round(float(r.mean() / r.std() * np.sqrt(252)), 2),
                mdd=round(float((e / e.cummax() - 1).min()), 4), by_year_pct={int(k.year): round(float(v * 100), 1) for k, v in yr.items()})

if __name__ == "__main__" and sys.argv[1] in ("dev", "holdout"):
    lo, hi = ("2017-01-01", "2021-12-31") if sys.argv[1] == "dev" else ("2022-01-01", "2026-11-20")
    T = pd.read_csv(f"{TR}/trades.csv.gz", index_col="tid"); P = pd.read_csv(f"{TR}/paths.csv.gz")
    out = {}
    for name, cost in (("base_25bp", 0.0025), ("stress_50bp", 0.005)):
        eq, g, n, pnl = portfolio(T, P, cost, end=hi)
        out[name] = st(eq, lo, hi)
        if name == "base_25bp":
            out["avg_gross"] = round(float(g[lo:hi].mean()), 2); out["avg_positions"] = int(n[lo:hi].mean())
            Tp = T.copy(); Tp["ed"] = pd.to_datetime(Tp.ed)
            W = Tp[(Tp.ed >= lo) & (Tp.ed <= hi)]
            Rm = ((W.xp * (1 - cost) - W.ep * (1 + cost)) / (W.ep - W.stop0).clip(lower=1e-9))
            out["trades"] = int(len(W)); out["win_rate"] = round(float((W.xp > W.ep).mean()), 3)
            out["expectancy_R"] = round(float(Rm.clip(-5, 50).mean()), 3)
            pp = pd.Series({k: v for k, v in pnl.items() if k in W.index})
            out["top10_share_of_profit"] = round(float(pp.sort_values(ascending=False).head(10).sum() / pp.sum()), 2) if pp.sum() > 0 else None
            base = eq[lo:hi].pct_change().dropna()
    for f in sorted(glob.glob(f"{RAW}/daily_adj/*.csv.gz")):
        a = pd.read_csv(f)
        if len(a) and (a.s == "SPY").any():
            spy = a[a.s == "SPY"].set_index(pd.to_datetime(a[a.s == "SPY"].t)).c; break
    out["SPY_buy_hold"] = st(spy, lo, hi)
    try:
        sys.path.insert(0, "research/stable"); from book_tester import i2_daily
        i2 = i2_daily(); c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.resample("D").last().pct_change()
        out["corr_C1_daily"] = round(float(base.corr(c1.reindex(base.index))), 2)
        out["corr_I2_daily"] = round(float(base.corr(i2.reindex(base.index).fillna(0))), 2)
    except Exception as e:
        out["corr_err"] = str(e)[:100]
    print(json.dumps(out, indent=1, ensure_ascii=False))
