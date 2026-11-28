"""t360 (docs/prereg/research_t360.md): activist SC 13D copy. Usage: py -3.12 research/stable/t360.py ledger|audit|density|dev|holdout"""
import glob, json, os, re, sys, time, urllib.request
import numpy as np, pandas as pd
sys.path.insert(0, "research/stable")
OUT = "data/derived/t360"; os.makedirs(OUT, exist_ok=True); IDX = "data/raw/edgar/fullindex"; os.makedirs(IDX, exist_ok=True)
UA = {"User-Agent": "research-client admin@example.com"}
ACT = ["elliott", "starboard", "icahn", "trian", "valueact", "jana partners", "jana master", "engaged capital", "land & buildings", "land and buildings", "ancora",
       "legion partners", "sachem head", "corvex", "third point", "pershing square", "politan", "blackwells", "barington", "cannell", "driver management",
       "irenic", "mantle ridge", "macellum", "scopia", "oculus", "saba capital", "bulldog investors"]
HOLD, COST = 60, {"base": 0.0010, "stress": 0.0025}


def fetch(url, f=None):
    for k in range(5):
        try:
            b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read(); time.sleep(0.15)
            if f: open(f, "wb").write(b)
            return b
        except Exception as e:
            time.sleep(3 * (k + 1)); err = e
    raise err


def ledger(years):
    rows = []
    for y in years:
        for q in range(1, 5):
            f = f"{IDX}/{y}Q{q}.idx"
            if not os.path.exists(f): fetch(f"https://www.sec.gov/Archives/edgar/full-index/{y}/QTR{q}/master.idx", f)
            for line in open(f, encoding="latin-1"):
                p = line.rstrip("\n").split("|")
                if len(p) == 5 and p[2] == "SC 13D": rows.append(dict(cik=p[0], name=p[1], date=p[3], fn=p[4]))
    M = pd.DataFrame(rows); out = []
    M["acc"] = M.fn.str.split("/").str[-1]
    for _, g in M.groupby("acc"):
        fn = g.fn.iloc[0]
        isact = g.name.str.lower().apply(lambda n: any(a in n for a in ACT))
        if not isact.any() or isact.all(): continue
        filer = g[isact].name.iloc[0]; subj = g[~isact].iloc[0]
        out.append(dict(fn=fn, date=g.date.iloc[0], subj_cik=int(subj.cik), subj=subj["name"], filer=filer))
    L = pd.DataFrame(out)
    acc = []
    for r in L.itertuples():
        a = os.path.basename(r.fn)[:-4]; u = f"https://www.sec.gov/Archives/edgar/data/{r.fn.split('/')[2]}/{a.replace('-', '')}/{a}.hdr.sgml"
        try: h = fetch(u).decode("latin-1"); m = re.search(r"<ACCEPTANCE-DATETIME>(\d{14})", h); acc.append(m.group(1) if m else None)
        except Exception: acc.append(None)
    L["acceptance"] = acc
    T = json.load(open("data/raw/edgar/company_tickers.json")); c2t = {}
    for v in T.values(): c2t.setdefault(v["cik_str"], v["ticker"])
    PIT = pd.read_csv("data/derived/pit/form345_symbols_by_quarter.csv.gz", dtype=str)
    pit = PIT.assign(c=PIT.ISSUERCIK.astype(int)).sort_values("q").groupby("c").sym.last().to_dict()   # last known symbol per issuer (covers delisted)
    L["sym"] = [c2t.get(c) or pit.get(c) for c in L.subj_cik]
    L["key"] = L.subj_cik.astype(str) + "|" + L.filer.str.lower().str[:20]
    L = L.sort_values("date").drop_duplicates("key")
    L.to_csv(f"{OUT}/ledger_{years[0]}_{years[-1]}.csv", index=False); print("ledger", len(L), "with symbol", int(L.sym.notna().sum()), "with acceptance", int(L.acceptance.notna().sum()))
    print(L.filer.str.lower().str[:25].value_counts().head(15).to_string())


def load_px(syms):
    O, C = [], []
    for f in sorted(glob.glob("data/raw/alpaca/daily_adj/*.csv.gz") + glob.glob("data/raw/alpaca/daily_adj_extra/*.csv.gz")):
        a = pd.read_csv(f); a = a[a.s.isin(syms)]
        if len(a): a["d"] = pd.to_datetime(a.t.str[:10]); O.append(a.pivot_table(index="d", columns="s", values="o")); C.append(a.pivot_table(index="d", columns="s", values="c"))
    f = lambda L: pd.concat(L, axis=1).sort_index().T.groupby(level=0).first().T
    O, C = f(O), f(C); idx = C["SPY"].dropna().index
    return O.reindex(idx), C.reindex(idx)


if __name__ == "__main__":
    st = sys.argv[1]
    if st == "ledger": ledger([2019, 2020, 2021]); sys.exit()
    L = pd.read_csv(f"{OUT}/ledger_2019_2021.csv", dtype={"acceptance": str})
    if st == "audit": print(L.sample(5, random_state=2)[["fn", "date", "subj", "filer", "acceptance", "sym"]].to_string()); sys.exit()
    O, C = load_px(set(L.sym.dropna()) | {"SPY"}); idx = C.index; T, miss = [], 0
    for r in L.itertuples():
        if not isinstance(r.sym, str) or r.sym not in C.columns or not isinstance(r.acceptance, str): miss += 1; continue
        ts = pd.Timestamp(r.acceptance[:8] + " " + r.acceptance[8:10] + ":" + r.acceptance[10:12])   # EDGAR acceptance is US Eastern
        d = ts.normalize(); k = idx.searchsorted(d)
        if k < len(idx) and idx[k] == d and ts.time() > pd.Timestamp("09:30").time(): k += 1
        kx = k + HOLD
        if kx >= len(idx) or k < 1: continue
        po, pc, prevc = O[r.sym].iloc[k], C[r.sym].iloc[:kx + 1].ffill().iloc[-1], C[r.sym].iloc[idx.searchsorted(d) - 1]
        if not (po > 0 and pc > 0): miss += 1; continue
        T.append(dict(s=r.sym, d=idx[k], ret=pc / po - 1, spy=C["SPY"].iloc[kx] / O["SPY"].iloc[k] - 1, missed=po / prevc - 1 if prevc > 0 else np.nan))
    T = pd.DataFrame(T); cov = len(T) / len(L)
    if st == "density": print("ledger", len(L), "trades", len(T), "coverage", round(cov, 3), T.groupby(T.d.dt.year).size().to_dict()); sys.exit()
    out = dict(n=len(T), coverage=round(cov, 3), missed_jump_median_pct=round(float(T.missed.median() * 100), 2))
    for k, c in COST.items():
        ex = T.ret - 2 * c - T.spy
        out[k] = dict(mean_excess_pct=round(float(ex.mean() * 100), 2), median_pct=round(float(ex.median() * 100), 2), t=round(float(ex.mean() / ex.std() * np.sqrt(len(ex))), 2),
                      by_year_pct={int(y): round(float(v * 100), 2) for y, v in ex.groupby(T.d.dt.year).mean().items()})
    exb = T.ret - 2 * COST["base"] - T.spy; out["win_rate"] = round(float((exb > 0).mean()), 3)
    out["top5_share"] = round(float(exb.nlargest(5).sum() / exb.sum()), 2) if exb.sum() > 0 else None
    print(json.dumps(out, indent=1, default=str))
