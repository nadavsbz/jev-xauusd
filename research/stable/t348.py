"""t348 (docs/prereg/research_t348.md): PEAD long-only from EDGAR 10-Q EPS.
Usage: py -3.12 research/stable/t348.py facts|audit|events|dev|holdout"""
import glob, json, os, sys, zipfile
import numpy as np, pandas as pd
sys.path.insert(0, "research/stable")
OUT = "data/derived/t348"; os.makedirs(OUT, exist_ok=True)
TAGS = ["EarningsPerShareDiluted", "EarningsPerShareBasicAndDiluted", "EarningsPerShareBasic"]
HOLD, MAXPOS, COST = 20, 50, {"base": 0.0005, "stress": 0.0010}


def extract():
    z = zipfile.ZipFile("data/raw/edgar/companyfacts.zip"); rows = []
    for k, name in enumerate(z.namelist()):
        try: j = json.load(z.open(name))
        except Exception: continue
        cik = j.get("cik"); g = j.get("facts", {}).get("us-gaap", {})
        for tag in TAGS:
            for x in g.get(tag, {}).get("units", {}).get("USD/shares", []):
                rows.append((cik, tag, x.get("start"), x.get("end"), x.get("val"), x.get("filed"), x.get("form")))
        if k % 4000 == 0: print(k, len(rows), flush=True)
    F = pd.DataFrame(rows, columns=["cik", "tag", "start", "end", "val", "filed", "form"])
    F.to_csv(f"{OUT}/eps.csv.gz", index=False); print("facts", len(F), "ciks", F.cik.nunique())


def quarters():
    """first-reported 3-month EPS per (cik,end), tag waterfall chosen per cik (first tag in TAGS with quarterly data)."""
    F = pd.read_csv(f"{OUT}/eps.csv.gz", parse_dates=["start", "end", "filed"]).dropna(subset=["start", "val"])
    F = F[F.form.isin(["10-Q", "10-Q/A"]) & ((F.end - F.start).dt.days.between(70, 110))]
    F["pri"] = F.tag.map({t: i for i, t in enumerate(TAGS)})
    best = F.groupby("cik").pri.min(); F = F[F.pri.values == best.reindex(F.cik).values]
    F = F.sort_values("filed").drop_duplicates(["cik", "end"], keep="first")   # first report of each quarter
    return F[["cik", "end", "val", "filed"]].sort_values(["cik", "end"]).reset_index(drop=True)


def sue_events(Q):
    ev = []
    for cik, g in Q.groupby("cik"):
        g = g.reset_index(drop=True)
        d = []                                                     # (end, filed, dEPS) seasonal differences
        for i, r in g.iterrows():
            p = g[((r.end - g.end).dt.days.between(350, 380))]
            if len(p): d.append((r.end, r.filed, r.val - p.val.iloc[-1], r.val))
        for i, (end, filed, de, v) in enumerate(d):
            prior = [x[2] for x in d[:i] if x[1] < filed][-8:]
            if len(prior) < 6: continue
            sd = np.std(prior, ddof=1)
            if not sd > 0: continue
            ev.append((cik, end, filed, de / sd, v))
    return pd.DataFrame(ev, columns=["cik", "end", "filed", "sue", "eps"]).sort_values("filed").reset_index(drop=True)


def top_decile(E):
    f = E.filed.values; s = E.sue.values; keep = np.zeros(len(E), bool); nwin = np.zeros(len(E), int)
    for i in range(len(E)):
        lo = f[i] - np.timedelta64(90, "D")
        m = (f >= lo) & (f < f[i]); nwin[i] = m.sum()
        if nwin[i] >= 100: keep[i] = s[i] >= np.quantile(s[m], 0.9)
    E = E.copy(); E["top"] = keep; E["nwin"] = nwin; return E


def load_px(U):
    O, C, RC, V = [], [], [], []
    for f in sorted(glob.glob("data/raw/alpaca/daily_adj/*.csv.gz")):
        a = pd.read_csv(f); a = a[a.s.isin(U)]
        if len(a): a["d"] = pd.to_datetime(a.t); O.append(a.pivot_table(index="d", columns="s", values="o")); C.append(a.pivot_table(index="d", columns="s", values="c"))
    for f in sorted(glob.glob("data/raw/alpaca/daily/*.csv.gz")):
        a = pd.read_csv(f, usecols=["s", "t", "c", "v"]).dropna(); a = a[a.s.isin(U)]
        if len(a): a["d"] = pd.to_datetime(a.t.str[:10]); RC.append(a.pivot_table(index="d", columns="s", values="c")); V.append(a.pivot_table(index="d", columns="s", values="v"))
    f = lambda L: pd.concat(L, axis=1).sort_index()
    O, C, RC, V = f(O), f(C), f(RC), f(V); idx = C["SPY"].dropna().index
    return O.reindex(idx), C.reindex(idx), RC.reindex(idx), V.reindex(idx)


def trades(E, O, C, RC, DV, cik2s, lo, hi):
    idx = C.index; T = []; open_until = {}; active = []
    hi_ts = pd.Timestamp(hi)
    for r in E[(E.filed >= pd.Timestamp(lo)) & (E.filed <= hi_ts) & E.top].itertuples():
        s = cik2s.get(r.cik)
        if s is None or s not in C.columns: continue
        k = idx.searchsorted(r.filed)                      # filing day (or next trading day if non-trading)
        if k >= len(idx) or k < 61: continue
        k0 = k                                             # reaction day = filing day, or next session if filed on a non-trading day
        if not (RC[s].iloc[k0] >= 10 and DV[s].iloc[k0 - 59:k0 + 1].median() >= 20e6): continue
        if not (C[s].iloc[k0] / C[s].iloc[k0 - 1] - 1 > 0): continue
        ke, kx = k0 + 1, k0 + HOLD
        if kx >= len(idx) or idx[kx] > hi_ts: continue
        if open_until.get(s, -1) >= ke: continue
        active = [a for a in active if a >= ke]
        if len(active) >= MAXPOS: continue
        po, pc = O[s].iloc[ke], C[s].iloc[kx]
        if not (po > 0 and pc > 0): continue
        so, sc = O["SPY"].iloc[ke], C["SPY"].iloc[kx]
        T.append(dict(s=s, filed=r.filed, entry=idx[ke], exit=idx[kx], sue=r.sue, ret=pc / po - 1, spy=sc / so - 1, ke=ke, kx=kx))
        open_until[s] = kx; active.append(kx)
    return pd.DataFrame(T)


def tstat(x): return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x))))


def portfolio(T, O, C, cost):
    idx = C.index; r = pd.Series(0.0, index=idx)
    for t in T.itertuples():
        path = C[t.s].iloc[t.ke:t.kx + 1].ffill().values
        v = np.r_[path[0] * 0 + O[t.s].iloc[t.ke], path]   # entry at open, then closes
        dr = v[1:] / v[:-1] - 1
        dr[0] -= cost; dr[-1] -= cost
        r.iloc[t.ke:t.kx + 1] += dr / MAXPOS
    return r


if __name__ == "__main__":
    st = sys.argv[1]
    if st == "facts": extract(); sys.exit()
    Q = quarters()
    if st == "audit":
        T = json.load(open("data/raw/edgar/company_tickers.json")); m = {v["ticker"]: v["cik_str"] for v in T.values()}
        for s in ["AAPL", "MSFT", "JPM", "KO", "INTC"]:
            g = Q[(Q.cik == m[s]) & (Q.end.dt.year == 2019)]
            print(s, [(str(x.end.date()), x.val, str(x.filed.date())) for x in g.itertuples()])
        sys.exit()
    E = sue_events(Q); E = top_decile(E); E.to_csv(f"{OUT}/events.csv.gz", index=False)
    if st == "events":
        print("events", len(E), "top", int(E.top.sum())); print(E[E.top].groupby(E.filed.dt.year).size()); sys.exit()
    from t338 import universe
    tk = json.load(open("data/raw/edgar/company_tickers.json")); U = universe()
    cik2s = {}
    for v in tk.values():
        if v["ticker"] in U and v["cik_str"] not in cik2s: cik2s[v["cik_str"]] = v["ticker"]
    O, C, RC, V = load_px(set(cik2s.values()) | {"SPY"}); DV = RC * V
    lo, hi = ("2019-01-01", "2021-12-31") if st in ("dev", "density") else ("2022-01-01", "2026-11-20")
    T = trades(E, O, C, RC, DV, cik2s, lo, hi)
    if st == "density": print("trades", len(T), T.groupby(T.filed.dt.year).size().to_dict()); sys.exit()
    out = {"n": len(T), "per_year": T.groupby(T.filed.dt.year).size().to_dict()}
    for k, c in COST.items():
        ex = T.ret - 2 * c - T.spy
        out[k] = dict(mean_excess_pct=round(float(ex.mean() * 100), 3), t=round(tstat(ex), 2),
                      by_year_pct={int(y): round(float(v * 100), 3) for y, v in ex.groupby(T.filed.dt.year).mean().items()})
    exb = T.ret - 2 * COST["base"] - T.spy
    out["win_rate_excess"] = round(float((exb > 0).mean()), 3)
    out["top10_share"] = round(float(exb.sort_values(ascending=False).head(10).sum() / exb.sum()), 2) if exb.sum() > 0 else None
    pr = portfolio(T, O, C, COST["base"]).loc[T.entry.min():T.exit.max()]
    e = (1 + pr).cumprod(); yrs = len(pr) / 252
    out["portfolio"] = dict(cagr=round(float(e.iloc[-1] ** (1 / yrs) - 1), 4), sharpe=round(float(pr.mean() / pr.std() * np.sqrt(252)), 2),
                            mdd=round(float((e / e.cummax() - 1).min()), 4),
                            by_year_pct={int(y): round(float(v * 100), 1) for y, v in ((1 + pr).groupby(pr.index.year).prod() - 1).items()})
    sp = C["SPY"].loc[pr.index].pct_change().fillna(0); es = (1 + sp).cumprod()
    out["SPY"] = dict(cagr=round(float(es.iloc[-1] ** (1 / yrs) - 1), 4), sharpe=round(float(sp.mean() / sp.std() * np.sqrt(252)), 2))
    try:
        from book_tester import i2_daily
        i2 = i2_daily()
        c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.resample("D").last().pct_change()
        out["corr_C1"] = round(float(pr.corr(c1.reindex(pr.index))), 2); out["corr_I2"] = round(float(pr.corr(i2.reindex(pr.index).fillna(0))), 2)
    except Exception as ex: out["corr_err"] = str(ex)[:80]
    T.drop(columns=["ke", "kx"]).to_csv(f"{OUT}/trades_{st}.csv", index=False)
    print(json.dumps(out, indent=1, default=str))
