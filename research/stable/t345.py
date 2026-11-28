"""t345 (docs/prereg/research_t345.md): Conservative Formula with point-in-time EDGAR cash NPY + Alpaca prices.
Stages: facts -> data/derived/t345/facts.csv.gz ; coverage ; audit ; dev ; holdout
Usage: py -3.12 research/stable/t345.py <stage>"""
import glob, json, os, sys, zipfile
import numpy as np, pandas as pd
OUT = "data/derived/t345"; os.makedirs(OUT, exist_ok=True)
DIV = ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends", "PaymentsOfOrdinaryDividends"]
REP = ["PaymentsForRepurchaseOfCommonStock", "PaymentsForRepurchaseOfCommonAndPreferredStock"]
ISS = ["ProceedsFromIssuanceOfCommonStock", "ProceedsFromIssuanceOrSaleOfEquity"]
SHR = "EntityCommonStockSharesOutstanding"


def extract():
    z = zipfile.ZipFile("data/raw/edgar/companyfacts.zip"); rows = []
    for k, name in enumerate(z.namelist()):
        try: j = json.load(z.open(name))
        except Exception: continue
        cik = j.get("cik"); f = j.get("facts", {})
        for tax, tags in (("us-gaap", DIV + REP + ISS), ("dei", [SHR])):
            for tag in tags:
                u = f.get(tax, {}).get(tag, {}).get("units", {})
                for unit, L in u.items():
                    if unit not in ("USD", "shares"): continue
                    for x in L:
                        rows.append((cik, tag, x.get("start"), x.get("end"), x.get("val"), x.get("filed"), x.get("form")))
        if k % 2000 == 0: print(k, len(rows), flush=True)
    F = pd.DataFrame(rows, columns=["cik", "tag", "start", "end", "val", "filed", "form"])
    F.to_csv(f"{OUT}/facts.csv.gz", index=False); print("facts", len(F), "ciks", F.cik.nunique())


def load_facts():
    F = pd.read_csv(f"{OUT}/facts.csv.gz", parse_dates=["start", "end", "filed"])
    F["dur"] = (F.end - F.start).dt.days
    return F


def npy_asof(F, d):
    """cash net payout TTM ($) per cik, using facts filed before d, first-reported value per (tag,start,end)."""
    G = F[(F.filed < d) & F.start.notna()]
    G = G.sort_values("filed").drop_duplicates(["cik", "tag", "start", "end"], keep="first")
    G = G[G.filed >= d - pd.Timedelta(days=200 + 400)]                 # enough history for FY + YTD pairs
    out = {}
    for cik, g in G.groupby("cik"):
        last_filed = g.filed.max()
        if (d - last_filed).days > 200: continue
        comp, have = {}, False
        for name, tags in (("div", DIV), ("rep", REP), ("iss", ISS)):
            val = None
            for tag in tags:
                h = g[g.tag == tag]
                if not len(h): continue
                fy = h[h.dur.between(330, 400)].sort_values("end")
                ytd = h[h.dur.between(70, 310)].sort_values("end")
                if not len(fy): continue
                F0 = fy.iloc[-1]
                cur = ytd[ytd.end > F0.end]
                if len(cur):
                    c = cur.iloc[-1]
                    prev = ytd[((c.end - ytd.end).dt.days.between(350, 380)) & ((ytd.dur - c.dur).abs() <= 20)]
                    if not len(prev): continue
                    val = F0.val + c.val - prev.iloc[-1].val
                else:
                    val = F0.val
                break
            if val is not None: have = True
            comp[name] = val
        if not have: continue
        out[cik] = (comp["div"] or 0) + (comp["rep"] or 0) - (comp["iss"] or 0)
    return pd.Series(out)


def shares_asof(F, d):
    S = F[(F.tag == SHR) & (F.filed < d)].sort_values(["filed", "end"])
    return S.groupby("cik").val.last()


def tickers():
    T = json.load(open("data/raw/edgar/company_tickers.json"))
    m = pd.DataFrame(T.values()); return m.drop_duplicates("ticker").set_index("ticker").cik_str


def prices(syms):
    O, C, R = [], [], []
    for f in sorted(glob.glob("data/raw/alpaca/daily_adj/*.csv.gz")):
        a = pd.read_csv(f)
        if not len(a): continue
        a = a[a.s.isin(syms)]
        if len(a): a["d"] = pd.to_datetime(a.t); O.append(a.pivot(index="d", columns="s", values="o")); C.append(a.pivot(index="d", columns="s", values="c"))
    for f in sorted(glob.glob("data/raw/alpaca/daily/*.csv.gz")):
        a = pd.read_csv(f, usecols=["s", "t", "c"]).dropna()
        a = a[a.s.isin(syms)]
        if len(a): a["d"] = pd.to_datetime(a.t.str[:10]); R.append(a.pivot_table(index="d", columns="s", values="c"))
    return (pd.concat(O, axis=1).sort_index(), pd.concat(C, axis=1).sort_index(), pd.concat(R, axis=1).sort_index())


def rebal_dates(idx, lo, hi):
    out = []
    for y in range(2018, 2027):
        for m in (1, 4, 7, 10):
            d = idx[idx >= pd.Timestamp(y, m, 1)]
            if len(d) and pd.Timestamp(lo) <= d[0] <= pd.Timestamp(hi): out.append(d[0])
    return out


def select(F, O, C, RAW, tk, d):
    prev = C.index[C.index < d][-1]
    npy_usd = npy_asof(F, d); sh = shares_asof(F, d)
    me = C.loc[:prev].resample("ME").last()
    rets = me.pct_change()
    vol = rets.iloc[-36:].std(); ok = rets.iloc[-37:].notna().sum() >= 37 - 1
    mom = me.iloc[-2] / me.iloc[-13] - 1
    rows = []
    for s in C.columns:
        cik = tk.get(s)
        if cik is None or cik not in sh.index: continue
        px = RAW[s].loc[:prev].dropna()
        if not len(px) or px.iloc[-1] <= 1: continue
        mcap = px.iloc[-1] * sh[cik]
        rows.append((s, cik, mcap, npy_usd.get(cik, np.nan), vol.get(s, np.nan), mom.get(s, np.nan), bool(ok.get(s, False))))
    U = pd.DataFrame(rows, columns=["s", "cik", "mcap", "npy_usd", "vol", "mom", "hok"]).dropna(subset=["mcap"])
    U = U[U.mcap > 0].sort_values("mcap", ascending=False)
    top_any = U.head(1000); coverage = float(top_any.npy_usd.notna().mean())
    E = U[U.hok.astype(bool) & U.npy_usd.notna() & U.vol.notna() & U.mom.notna()].head(1000).copy()
    E["npy"] = E.npy_usd / E.mcap
    E["score"] = ((-E.vol).rank(pct=True) + E.mom.rank(pct=True) + E.npy.rank(pct=True)) / 3
    return list(E.sort_values("score", ascending=False).s.head(100)), coverage, len(E)


def backtest(F, O, C, RAW, tk, lo, hi, cost):
    R = rebal_dates(C.index, lo, hi) + [C.index[-1]]
    val, w_prev, eq, covs = 1.0, {}, [], []
    for k in range(len(R) - 1):
        d0, d1 = R[k], R[k + 1]
        tick, cov, ne = select(F, O, C, RAW, tk, d0); covs.append((str(d0.date()), round(cov, 3), ne))
        px0 = O.loc[d0].reindex(tick); tick = list(px0.dropna().index)
        if not tick:                                   # nobody eligible yet (history rule) -> cash for the quarter
            eq.append(pd.Series(val, index=C.loc[d0:d1].index[:-1])); w_prev = {}; continue
        w ={t: 1 / len(tick) for t in tick}
        turn = sum(abs(w.get(t, 0) - w_prev.get(t, 0)) for t in set(w) | set(w_prev)); val *= 1 - cost * turn
        seg = C.loc[d0:d1].iloc[:-1][tick].ffill()
        v = val * (seg / px0[tick]).fillna(1.0).mul(pd.Series(w)).sum(axis=1); eq.append(v)
        end = O.loc[d1].reindex(tick).fillna(seg.iloc[-1]) / px0[tick] if d1 in O.index else seg.iloc[-1] / px0[tick]
        dr = end * pd.Series(w); val *= float(dr.sum()); w_prev = (dr / dr.sum()).to_dict()
    e = pd.concat(eq); return e[~e.index.duplicated()], covs


def stt(e):
    r = e.pct_change().dropna(); yrs = (e.index[-1] - e.index[0]).days / 365.25
    yr = pd.concat([pd.Series([e.iloc[0]], index=[e.index[0]]), e.resample("YE").last()]).pct_change().dropna()
    return dict(cagr=round(float((e.iloc[-1] / e.iloc[0]) ** (1 / yrs) - 1), 4), sharpe=round(float(r.mean() / r.std() * np.sqrt(252)), 2),
                mdd=round(float((e / e.cummax() - 1).min()), 4), by_year_pct={int(k.year): round(float(v * 100), 1) for k, v in yr.items()})


if __name__ == "__main__":
    st = sys.argv[1]
    if st == "facts": extract(); sys.exit()
    sys.path.insert(0, "research/stable"); from t338 import universe
    F = load_facts(); tk = tickers(); U = universe()
    syms = sorted((set(tk.index) & U) | {"SPY"}); O, C, RAW = prices(syms)
    if st == "audit":
        for s in ["AAPL", "MSFT", "JPM", "XOM", "JNJ", "PG", "KO", "WMT", "INTC", "TSLA"]:
            cik = tk[s]; v = npy_asof(F, pd.Timestamp("2020-04-01")).get(cik); sh = shares_asof(F, pd.Timestamp("2020-04-01")).get(cik)
            print(s, "net payout TTM $bn:", None if v is None else round(v / 1e9, 1), " shares bn:", None if sh is None else round(sh / 1e9, 2))
        sys.exit()
    if st == "coverage":
        for d in rebal_dates(C.index, "2019-01-01", "2021-12-31"):
            _, cov, ne = select(F, O, C, RAW, tk, d); print(d.date(), "coverage top1000:", round(cov, 3), "eligible:", ne, flush=True)
        sys.exit()
    lo, hi = ("2019-01-01", "2021-12-31") if st == "dev" else ("2022-01-01", "2026-11-20")
    C2 = C.loc[:hi]; O2 = O.loc[:hi]; RAW2 = RAW.loc[:hi]
    out = {}
    e, covs = backtest(F, O2, C2, RAW2, tk, lo, hi, 0.0010); e2, _ = backtest(F, O2, C2, RAW2, tk, lo, hi, 0.0025)
    spy = C2["SPY"].loc[e.index[0]:e.index[-1]].ffill(); spy = spy / spy.iloc[0]
    out["base"] = stt(e); out["stress"] = stt(e2); out["SPY"] = stt(spy)
    out["tracking_err"] = round(float((e.pct_change() - spy.pct_change()).std() * np.sqrt(252)), 3); out["coverage"] = covs
    try:
        from book_tester import i2_daily
        r = e.pct_change().dropna(); i2 = i2_daily()
        c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.resample("D").last().pct_change()
        out["corr_C1"] = round(float(r.corr(c1.reindex(r.index))), 2); out["corr_I2"] = round(float(r.corr(i2.reindex(r.index).fillna(0))), 2)
    except Exception as ex: out["corr_err"] = str(ex)[:80]
    print(json.dumps(out, indent=1, default=str))
