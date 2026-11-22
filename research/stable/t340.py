"""t340 (docs/prereg/research_t340.md): broad 13F cloning vs SPY.
Stages: parse -> data/derived/t340/holdings.csv.gz (13F-HR long shares, filed <=45 days, loose fund prefilter)
        figi   -> data/derived/t340/cusip_map.csv (OpenFIGI, no key)
        coverage | dev | holdout
Usage: py -3.12 research/stable/t340.py <stage>"""
import glob, io, json, os, sys, time, urllib.request, zipfile
import numpy as np, pandas as pd
RAW = "data/raw/sec13f"; OUT = "data/derived/t340"; os.makedirs(OUT, exist_ok=True)


def parse_zip(f):
    z = zipfile.ZipFile(f)
    names = {n.split("/")[-1]: n for n in z.namelist()}
    zo = lambda n: z.open(names[n])
    S = pd.read_csv(zo("SUBMISSION.tsv"), sep="\t", dtype=str)
    C = pd.read_csv(zo("COVERPAGE.tsv"), sep="\t", dtype=str, usecols=["ACCESSION_NUMBER", "ISAMENDMENT", "FILINGMANAGER_NAME"])
    S = S[S.SUBMISSIONTYPE == "13F-HR"].merge(C, on="ACCESSION_NUMBER")
    S = S[S.ISAMENDMENT.fillna("N").str.upper().str[0] != "Y"]
    S["fd"] = pd.to_datetime(S.FILING_DATE, format="%d-%b-%Y"); S["per"] = pd.to_datetime(S.PERIODOFREPORT, format="%d-%b-%Y")
    S = S[(S.fd - S.per).dt.days <= 45]
    I = pd.read_csv(zo("INFOTABLE.tsv"), sep="\t", dtype=str, usecols=["ACCESSION_NUMBER", "CUSIP", "VALUE", "SSHPRNAMTTYPE", "PUTCALL"],
                    on_bad_lines="skip")
    I = I[I.ACCESSION_NUMBER.isin(S.ACCESSION_NUMBER) & I.PUTCALL.isna() & (I.SSHPRNAMTTYPE == "SH")]
    I["v"] = pd.to_numeric(I.VALUE, errors="coerce")
    I = I.merge(S[["ACCESSION_NUMBER", "CIK", "FILINGMANAGER_NAME", "fd", "per"]], on="ACCESSION_NUMBER")
    I.loc[I.fd < "2023-01-03", "v"] *= 1000                      # values were in $1000s before the 2023 rule change
    I["CUSIP"] = I.CUSIP.str.upper().str.strip()
    H = I.groupby(["ACCESSION_NUMBER", "CIK", "FILINGMANAGER_NAME", "fd", "per", "CUSIP"], as_index=False).v.sum()
    g = H.groupby("ACCESSION_NUMBER").v
    H = H[(g.transform("size").between(10, 100)) & (g.transform("sum").between(1e8, 2.5e10))]   # loose superset of the prereg filter
    return H


if __name__ == "__main__":
    st = sys.argv[1]
    if st == "parse":
        parts = []
        for f in sorted(glob.glob(f"{RAW}/*.zip")):
            h = parse_zip(f); parts.append(h); print(os.path.basename(f), len(h), h.ACCESSION_NUMBER.nunique(), flush=True)
        H = pd.concat(parts).drop_duplicates(["ACCESSION_NUMBER", "CUSIP"])
        H.to_csv(f"{OUT}/holdings.csv.gz", index=False)
        print("rows", len(H), "filings", H.ACCESSION_NUMBER.nunique(), "cusips", H.CUSIP.nunique())
        print("filings per period:", H.groupby(H.per.astype(str).str[:7]).ACCESSION_NUMBER.nunique().to_dict())

if __name__ == "__main__" and sys.argv[1] == "figi":
    H = pd.read_csv(f"{OUT}/holdings.csv.gz", usecols=["CUSIP"])
    cus = sorted(H.CUSIP.dropna().unique())
    mf = f"{OUT}/cusip_map.csv"
    done = set(pd.read_csv(mf).cusip) if os.path.exists(mf) else set()
    todo = [c for c in cus if c not in done]
    print(len(cus), "cusips,", len(todo), "to map", flush=True)
    if not os.path.exists(mf): open(mf, "w").write("cusip,ticker,name,sectype\n")
    for i in range(0, len(todo), 10):
        b = todo[i:i + 10]
        body = json.dumps([{"idType": "ID_CUSIP", "idValue": c, "exchCode": "US"} for c in b]).encode()
        for k in range(6):
            try:
                r = json.load(urllib.request.urlopen(urllib.request.Request("https://api.openfigi.com/v3/mapping", data=body,
                              headers={"Content-Type": "application/json"}), timeout=60)); break
            except Exception as e:
                time.sleep(30 * (k + 1)); r = None
        if r is None: print("failed batch", i, flush=True); continue
        with open(mf, "a", encoding="utf-8") as fh:
            for c, x in zip(b, r):
                d = (x.get("data") or [{}])[0]
                fh.write(f'{c},{d.get("ticker", "")},"{(d.get("name") or "").replace(chr(34), "")}",{d.get("securityType", "")}\n')
        if (i // 10) % 200 == 0: print(i, "/", len(todo), flush=True)
        time.sleep(2.5)
    print("done")


def load_all():
    sys.path.insert(0, "research/stable")
    from t338 import universe
    U = universe()
    H = pd.read_csv(f"{OUT}/holdings.csv.gz", parse_dates=["fd", "per"])
    M = pd.read_csv(f"{OUT}/cusip_map.csv", dtype=str)
    H = H.merge(M[["cusip", "ticker"]], left_on="CUSIP", right_on="cusip", how="left")
    stats = dict(rows=len(H), mapped_rows=float(H.ticker.notna().mean()),
                 in_universe_value_share=float(H.v[H.ticker.isin(U)].sum() / H.v.sum()))
    H = H[H.ticker.isin(U)]
    H = H.groupby(["ACCESSION_NUMBER", "CIK", "FILINGMANAGER_NAME", "fd", "per", "ticker"], as_index=False).v.sum()
    last = H.groupby(["CIK", "per"]).fd.transform("max"); H = H[H.fd == last]          # latest original filing per fund-period
    g = H.groupby("ACCESSION_NUMBER").v
    H["n"] = g.transform("size"); H["tot"] = g.transform("sum")
    H["rk"] = g.rank(ascending=False, method="first")
    top10 = H[H.rk <= 10].groupby("ACCESSION_NUMBER").v.sum()
    H["top10"] = H.ACCESSION_NUMBER.map(top10) / H.tot
    H = H[H.n.between(10, 60) & H.tot.between(1e8, 2e10) & (H.top10 >= 0.4)]
    need = set(H.ticker) | {"SPY", "GURU"}
    O, C = [], []
    for f in sorted(glob.glob("data/raw/alpaca/daily_adj/*.csv.gz")):
        a = pd.read_csv(f)
        if not len(a): continue
        a = a[a.s.isin(need)]
        if len(a): a["d"] = pd.to_datetime(a.t); O.append(a.pivot(index="d", columns="s", values="o")); C.append(a.pivot(index="d", columns="s", values="c"))
    O = pd.concat(O, axis=1).sort_index(); C = pd.concat(C, axis=1).sort_index()
    return H, O, C, stats


def rebal_dates(idx):
    out = []
    for y in range(2016, 2027):
        for m, pm in ((2, (y - 1, 12, 31)), (5, (y, 3, 31)), (8, (y, 6, 30)), (11, (y, 9, 30))):
            d = idx[idx >= pd.Timestamp(y, m, 16)]
            if len(d) and d[0] <= idx[-1]: out.append((d[0], pd.Timestamp(*pm)))
    return out


def picks_A(Hp):
    t3 = Hp[Hp.rk <= 3]
    sc = t3.groupby("ticker").agg(cnt=("CIK", "nunique"), val=("v", "sum")).sort_values(["cnt", "val"], ascending=False)
    return list(sc.index[:30])


def run(H, O, C, variant, cost, lo, hi):
    R = rebal_dates(C.index)
    R = [(d, p) for d, p in R if d <= pd.Timestamp(hi)]
    # clone returns per fund-period (top-10 equal weight, open of rebalance -> close of the day before the next rebalance)
    clone = {}
    if variant == "B":
        for k in range(len(R) - 1):
            d0, p = R[k]; d1 = C.index[C.index < R[k + 1][0]][-1]
            Hp = H[H.per == p]; Hp = Hp[Hp.rk <= 10]
            px0 = O.loc[d0].reindex(Hp.ticker.values).values; px1 = C.loc[:d1].ffill().iloc[-1].reindex(Hp.ticker.values).values
            Hp = Hp.assign(r=px1 / px0 - 1).dropna(subset=["r"])
            for cik, r in Hp.groupby("CIK").r.mean().items(): clone[(cik, k)] = r
    eq, dates, w_prev, val, nfunds = [], [], {}, 1.0, []
    for k in range(len(R) - 1):
        d0, p = R[k]; d1 = R[k + 1][0]
        if d0 < pd.Timestamp(lo) or d0 > pd.Timestamp(hi): continue
        Hp = H[H.per == p]
        if variant == "A":
            tick = picks_A(Hp); nfunds.append(Hp.CIK.nunique())
        else:
            if k < 8: continue
            sc = {}
            for cik in Hp.CIK.unique():
                past = [clone.get((cik, j)) for j in range(k - 8, k)]
                if all(x is not None for x in past): sc[cik] = np.mean(past)
            top = sorted(sc, key=sc.get, reverse=True)[:20]; nfunds.append(len(sc))
            tick = sorted(set(Hp[Hp.CIK.isin(top) & (Hp.rk <= 5)].ticker))
        px0 = O.loc[d0].reindex(tick); tick = list(px0.dropna().index)
        if not tick: continue
        w = {t: 1 / len(tick) for t in tick}
        turn = sum(abs(w.get(t, 0) - w_prev.get(t, 0)) for t in set(w) | set(w_prev))
        val *= (1 - cost * turn)
        seg = C.loc[d0:d1].iloc[:-1][tick].ffill()
        rel = (seg / px0[tick]).fillna(1.0)
        v = val * (rel * pd.Series(w)).sum(axis=1)
        eq.append(v)
        end = (O.loc[d1].reindex(tick).fillna(seg.iloc[-1]) / px0[tick])
        drift = end * pd.Series(w); val = val * float(drift.sum()); w_prev = (drift / drift.sum()).to_dict()
    e = pd.concat(eq); e = e[~e.index.duplicated()]
    return e, nfunds


def stt(e):
    r = e.pct_change().dropna(); yrs = (e.index[-1] - e.index[0]).days / 365.25
    yr = e.resample("YE").last(); yr = pd.concat([pd.Series([e.iloc[0]], index=[e.index[0]]), yr]).pct_change().dropna()
    return dict(cagr=round(float((e.iloc[-1] / e.iloc[0]) ** (1 / yrs) - 1), 4), sharpe=round(float(r.mean() / r.std() * np.sqrt(252)), 2),
                mdd=round(float((e / e.cummax() - 1).min()), 4), by_year_pct={int(k.year): round(float(v * 100), 1) for k, v in yr.items()})


def bench(O, C, e, sym):
    s = C[sym].loc[e.index[0]:e.index[-1]].ffill(); return s / s.iloc[0]


if __name__ == "__main__" and sys.argv[1] in ("coverage", "dev", "holdout"):
    H, O, C, cov = load_all()
    if sys.argv[1] == "coverage":
        cm = pd.read_csv(f"{OUT}/cusip_map.csv", dtype=str)
        cov["cusips_unmapped_share"] = round(float(cm.ticker.isna().mean()), 3)
        cov["eligible_funds_per_period"] = H.groupby(H.per.dt.strftime("%Y-%m")).CIK.nunique().to_dict()
        print(json.dumps(cov, indent=1, default=str)); sys.exit()
    part = sys.argv[1]
    out = {}
    for var in ("A", "B"):
        lo, hi = (("2017-02-01" if var == "A" else "2017-11-01"), "2021-12-31") if part == "dev" else ("2022-02-01", "2026-11-20")
        e, nf = run(H, O, C, var, 0.0010, lo, hi); e2, _ = run(H, O, C, var, 0.0025, lo, hi)
        spy = bench(O, C, e, "SPY")
        out[var] = dict(base=stt(e), stress=stt(e2), SPY=stt(spy), funds_min_max=(min(nf), max(nf)),
                        tracking_err=round(float((e.pct_change() - spy.pct_change()).std() * np.sqrt(252)), 3))
        if "GURU" in C: out[var]["GURU"] = stt(bench(O, C, e, "GURU"))
        try:
            from book_tester import i2_daily
            r = e.pct_change().dropna(); i2 = i2_daily()
            c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.resample("D").last().pct_change()
            out[var]["corr_C1"] = round(float(r.corr(c1.reindex(r.index))), 2); out[var]["corr_I2"] = round(float(r.corr(i2.reindex(r.index).fillna(0))), 2)
        except Exception as ex:
            out[var]["corr_err"] = str(ex)[:80]
    print(json.dumps(out, indent=1, default=str))
