"""t366 (docs/prereg/research_t366.md): S&P 500 deletion reversal. Usage: py -3.12 research/stable/t366.py ledger|density|dev|holdout"""
import glob, io, json, re, sys
import numpy as np, pandas as pd
HOLD, COST = 20, {"base": 0.0010, "stress": 0.0025}
EXCL = re.compile(r"acquired|acquisition|merger|merged|spin|spun|bankrupt", re.I)


def ledger():
    h = json.load(open("data/raw/wiki/sp500_hist.json", encoding="utf-8"))["parse"]["text"]
    t = max(pd.read_html(io.StringIO(h)), key=len); t.columns = ["date", "add", "add_name", "sym", "name", "reason", "refs"]
    t = t[t.sym.notna()].copy(); t["d"] = pd.to_datetime(t.date, format="mixed", errors="coerce")
    t["excl"] = t.reason.fillna("").str.contains(EXCL)
    t["sym"] = t.sym.astype(str).str.strip().str.upper().str.replace(".", "", regex=False)
    t[["d", "sym", "name", "reason", "excl"]].to_csv("data/derived/t366_ledger.csv", index=False)
    print("removals", len(t), "excluded", int(t.excl.sum()), "kept by year", t[~t.excl].groupby(t.d.dt.year).size().loc[2015:].to_dict())


def load(syms):
    C = []
    for f in sorted(glob.glob("data/raw/alpaca/daily_adj/*.csv.gz") + glob.glob("data/raw/alpaca/daily_adj_extra/*.csv.gz")):
        a = pd.read_csv(f, usecols=["s", "t", "c"]); a = a[a.s.isin(syms)]
        if len(a): a["d"] = pd.to_datetime(a.t.str[:10]); C.append(a.pivot_table(index="d", columns="s", values="c"))
    C = pd.concat(C, axis=1).sort_index().T.groupby(level=0).first().T
    return C.reindex(C["SPY"].dropna().index)


if __name__ == "__main__":
    st = sys.argv[1]
    if st == "ledger": ledger(); sys.exit()
    L = pd.read_csv("data/derived/t366_ledger.csv", parse_dates=["d"])
    lo, hi = ("2016-01-01", "2020-12-31") if st in ("density", "dev") else ("2021-01-01", "2026-10-31")
    L = L[(~L.excl) & (L.d >= lo) & (L.d <= hi)]
    C = load(set(L.sym) | {"SPY"}); idx = C.index; T, miss = [], 0
    for r in L.itertuples():
        if r.sym not in C.columns: miss += 1; continue
        k = idx.searchsorted(r.d) - 1                         # last trading day before the effective date
        if k < 0 or k + HOLD >= len(idx): continue
        pe = C[r.sym].iloc[k]
        if not pe > 0: miss += 1; continue
        px = C[r.sym].iloc[k:k + HOLD + 1].ffill(); p5 = C[r.sym].iloc[k:k + 6].ffill().iloc[-1]
        T.append(dict(s=r.sym, d=r.d, ret=px.iloc[-1] / pe - 1, spy=C.SPY.iloc[k + HOLD] / C.SPY.iloc[k] - 1,
                      ex5=p5 / pe - 1 - (C.SPY.iloc[k + 5] / C.SPY.iloc[k] - 1)))
    T = pd.DataFrame(T); cov = len(T) / len(L)
    if st == "density":
        print("ledger", len(L), "trades", len(T), "coverage", round(cov, 3), "missing", miss, T.groupby(T.d.dt.year).size().to_dict()); sys.exit()
    out = dict(n=len(T), coverage=round(cov, 3))
    for kk, c in COST.items():
        ex = T.ret - 2 * c - T.spy
        out[kk] = dict(mean_excess_pct=round(float(ex.mean() * 100), 2), median_pct=round(float(ex.median() * 100), 2), t=round(float(ex.mean() / ex.std() * np.sqrt(len(ex))), 2),
                       by_year_pct={int(y): round(float(v * 100), 2) for y, v in ex.groupby(T.d.dt.year).mean().items()})
    exb = T.ret - 2 * COST["base"] - T.spy; out["win_rate"] = round(float((exb > 0).mean()), 3)
    out["top5_share"] = round(float(exb.nlargest(5).sum() / exb.sum()), 2) if exb.sum() > 0 else None
    out["descr_ex5_pct"] = round(float(T.ex5.mean() * 100), 2)
    print(json.dumps(out, indent=1, default=str))
