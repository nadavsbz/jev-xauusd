"""t353 (docs/prereg/research_t353.md): insider cluster buys from SEC Form 345 data sets.
Usage: py -3.12 research/stable/t353.py parse|events|audit|density|dev|holdout"""
import glob, io, json, os, sys, zipfile
import numpy as np, pandas as pd
OUT = "data/derived/t353"; os.makedirs(OUT, exist_ok=True)
HOLD, COST = 60, {"base": 0.0010, "stress": 0.0025}


def parse():
    P = []
    for f in sorted(glob.glob("data/raw/edgar/form345/*_form345.zip")):
        z = zipfile.ZipFile(f); names = {os.path.basename(n).upper(): n for n in z.namelist()}
        rd = lambda k, cols: pd.read_csv(z.open(names[k]), sep="\t", usecols=cols, dtype=str, low_memory=False)
        S = rd("SUBMISSION.TSV", ["ACCESSION_NUMBER", "FILING_DATE", "DOCUMENT_TYPE", "ISSUERCIK", "ISSUERTRADINGSYMBOL"])
        O = rd("REPORTINGOWNER.TSV", ["ACCESSION_NUMBER", "RPTOWNERCIK", "RPTOWNER_RELATIONSHIP"])
        T = rd("NONDERIV_TRANS.TSV", ["ACCESSION_NUMBER", "TRANS_CODE", "TRANS_ACQUIRED_DISP_CD", "TRANS_SHARES", "TRANS_PRICEPERSHARE"])
        T = T[(T.TRANS_CODE == "P") & (T.TRANS_ACQUIRED_DISP_CD == "A")].copy()
        T["val"] = pd.to_numeric(T.TRANS_SHARES, errors="coerce") * pd.to_numeric(T.TRANS_PRICEPERSHARE, errors="coerce")
        T = T.groupby("ACCESSION_NUMBER", as_index=False).val.sum()
        O = O[O.RPTOWNER_RELATIONSHIP.fillna("").str.contains("Director|Officer", case=False)]
        O = O.drop_duplicates("ACCESSION_NUMBER")             # one reporting owner per filing (joint filings: first owner)
        X = T.merge(S[S.DOCUMENT_TYPE == "4"], on="ACCESSION_NUMBER").merge(O, on="ACCESSION_NUMBER")
        P.append(X); print(os.path.basename(f), len(X), flush=True)
    P = pd.concat(P).drop_duplicates("ACCESSION_NUMBER")
    P["FILING_DATE"] = pd.to_datetime(P.FILING_DATE, format="mixed", dayfirst=False)
    P.to_csv(f"{OUT}/purchases.csv.gz", index=False); print("purchases", len(P))


def events():
    P = pd.read_csv(f"{OUT}/purchases.csv.gz", parse_dates=["FILING_DATE"], dtype={"ISSUERCIK": str, "RPTOWNERCIK": str})
    P = P[P.val >= 10_000].dropna(subset=["ISSUERTRADINGSYMBOL"])
    P = P.groupby(["ISSUERCIK", "RPTOWNERCIK", "FILING_DATE"], as_index=False).agg(val=("val", "sum"), sym=("ISSUERTRADINGSYMBOL", "last"))
    E = []
    for cik, g in P.sort_values("FILING_DATE").groupby("ISSUERCIK"):
        last = None
        for d in g.FILING_DATE.unique():
            w = g[(g.FILING_DATE > d - pd.Timedelta(days=30)) & (g.FILING_DATE <= d)]
            if w.RPTOWNERCIK.nunique() >= 2 and w.val.sum() >= 100_000 and (last is None or (d - last).days >= 90):
                E.append(dict(cik=cik, sym=str(w.sym.iloc[-1]).strip().upper(), d=d, n_ins=w.RPTOWNERCIK.nunique(), val=w.val.sum())); last = d
    E = pd.DataFrame(E); E.to_csv(f"{OUT}/events.csv", index=False)
    print("events", len(E), E.groupby(E.d.dt.year).size().to_dict())


def load_px(syms):
    O, C, RC, V = [], [], [], []
    for f in sorted(glob.glob("data/raw/alpaca/daily_adj/*.csv.gz") + glob.glob("data/raw/alpaca/daily_adj_extra/*.csv.gz")):
        a = pd.read_csv(f); a = a[a.s.isin(syms)]
        if len(a): a["d"] = pd.to_datetime(a.t); O.append(a.pivot_table(index="d", columns="s", values="o")); C.append(a.pivot_table(index="d", columns="s", values="c"))
    for f in sorted(glob.glob("data/raw/alpaca/daily/*.csv.gz") + glob.glob("data/raw/alpaca/daily_extra/*.csv.gz")):
        a = pd.read_csv(f, usecols=["s", "t", "c", "v"]).dropna(); a = a[a.s.isin(syms)]
        if len(a): a["d"] = pd.to_datetime(a.t.str[:10]); RC.append(a.pivot_table(index="d", columns="s", values="c")); V.append(a.pivot_table(index="d", columns="s", values="v"))
    f = lambda L: pd.concat(L, axis=1).sort_index(); O, C, RC, V = f(O), f(C), f(RC), f(V)
    O, C, RC, V = [x.T.groupby(level=0).first().T for x in (O, C, RC, V)]
    idx = C["SPY"].dropna().index
    return O.reindex(idx), C.reindex(idx), RC.reindex(idx), V.reindex(idx)


def tstat(x): return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x))))


if __name__ == "__main__":
    st = sys.argv[1]
    if st == "parse": parse(); sys.exit()
    if st == "events": events(); sys.exit()
    E = pd.read_csv(f"{OUT}/events.csv", parse_dates=["d"], dtype={"cik": str})
    lo, hi = ("2019-01-01", "2021-12-31") if st in ("dev", "density", "audit") else ("2022-01-01", "2026-11-20")
    E = E[(E.d >= lo) & (E.d <= hi)]
    if st == "audit":
        print(E.sample(5, random_state=1).to_string()); sys.exit()
    O, C, RC, V = load_px(set(E.sym) | {"SPY"}); DV = RC * V; idx = C.index
    T, miss = [], 0
    for r in E.itertuples():
        if r.sym not in C.columns: miss += 1; continue
        k0 = idx.searchsorted(r.d)
        if k0 < 60 or k0 + 1 + HOLD >= len(idx) or idx[k0 + HOLD + 1] > pd.Timestamp(hi): continue
        if np.isnan(C[r.sym].iloc[k0:k0 + 2]).any(): miss += 1; continue
        if not (RC[r.sym].iloc[k0] >= 5 and DV[r.sym].iloc[k0 - 59:k0 + 1].median() >= 2e6): continue
        ke, kx = k0 + 1, k0 + 1 + HOLD
        po = O[r.sym].iloc[ke]; pc = C[r.sym].iloc[:kx + 1].ffill().iloc[-1]
        if not (po > 0 and pc > 0): continue
        T.append(dict(s=r.sym, d=r.d, ke=ke, kx=kx, ret=pc / po - 1, spy=C["SPY"].iloc[kx] / O["SPY"].iloc[ke] - 1))
    T = pd.DataFrame(T); cov = 1 - miss / len(E)
    if st == "density":
        print("events", len(E), "price coverage", round(cov, 3), "trades", len(T), T.groupby(T.d.dt.year).size().to_dict()); sys.exit()
    out = dict(n=len(T), coverage=round(cov, 3))
    for k, c in COST.items():
        ex = T.ret - 2 * c - T.spy
        out[k] = dict(mean_excess_pct=round(float(ex.mean() * 100), 2), median_excess_pct=round(float(ex.median() * 100), 2), t=round(tstat(ex), 2),
                      by_year_pct={int(y): round(float(v * 100), 2) for y, v in ex.groupby(T.d.dt.year).mean().items()})
    exb = T.ret - 2 * COST["base"] - T.spy
    out["win_rate_excess"] = round(float((exb > 0).mean()), 3)
    out["top10_share"] = round(float(exb.nlargest(10).sum() / exb.sum()), 2) if exb.sum() > 0 else None
    r = pd.Series(0.0, index=idx); act = []
    for t in T.sort_values("ke").itertuples():
        act = [a for a in act if a >= t.ke]
        if len(act) >= 50: continue
        act.append(t.kx)
        p = np.r_[O[t.s].iloc[t.ke], C[t.s].iloc[t.ke:t.kx + 1].ffill().values]; dr = p[1:] / p[:-1] - 1; dr[0] -= COST["base"]; dr[-1] -= COST["base"]
        r.iloc[t.ke:t.kx + 1] += np.nan_to_num(dr) / 50
    pr = r.loc[T.d.min():idx[T.kx.max()]]; e = (1 + pr).cumprod(); yrs = len(pr) / 252
    sp = C["SPY"].loc[pr.index]
    out["portfolio"] = dict(cagr=round(float(e.iloc[-1] ** (1 / yrs) - 1), 4), sharpe=round(float(pr.mean() / pr.std() * np.sqrt(252)), 2), mdd=round(float((e / e.cummax() - 1).min()), 4),
                            spy_cagr=round(float((sp.iloc[-1] / sp.iloc[0]) ** (1 / yrs) - 1), 4))
    try:
        sys.path.insert(0, "research/stable"); from book_tester import i2_daily
        i2 = i2_daily(); c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.resample("D").last().pct_change()
        out["corr_C1"] = round(float(pr.corr(c1.reindex(pr.index))), 2); out["corr_I2"] = round(float(pr.corr(i2.reindex(pr.index).fillna(0))), 2)
    except Exception as ex: out["corr_err"] = str(ex)[:80]
    T.to_csv(f"{OUT}/trades_{st}.csv", index=False); print(json.dumps(out, indent=1, default=str))
