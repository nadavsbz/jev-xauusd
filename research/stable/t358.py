"""t358 (docs/prereg/research_t358.md): same-calendar-month seasonality (Heston-Sadka), survivorship-reduced universe.
Usage: py -3.12 research/stable/t358.py density|dev|holdout"""
import glob, json, re, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/stable")
from t338 import universe, BAD
R = "data/raw/alpaca"; COST = {"base": 0.0010, "stress": 0.0025}


def univ():
    A = json.load(open(f"{R}/assets_inactive.json"))
    ina = {a["symbol"] for a in A if a["exchange"] in ("NYSE", "NASDAQ", "AMEX") and re.fullmatch(r"[A-Z]{1,5}", a["symbol"]) and not BAD.search(a.get("name") or "")}
    return universe(), ina


def load(U):
    C, RC, V = [], [], []
    for f in sorted(glob.glob(f"{R}/daily_adj/*.csv.gz") + glob.glob(f"{R}/daily_adj_extra/*.csv.gz")):
        a = pd.read_csv(f, usecols=["s", "t", "c"]); a = a[a.s.isin(U)]
        if len(a): a["d"] = pd.to_datetime(a.t.str[:10]); C.append(a.pivot_table(index="d", columns="s", values="c"))
    for f in sorted(glob.glob(f"{R}/daily/*.csv.gz") + glob.glob(f"{R}/daily_extra/*.csv.gz")):
        a = pd.read_csv(f, usecols=["s", "t", "c", "v"]).dropna(); a = a[a.s.isin(U)]
        if len(a): a["d"] = pd.to_datetime(a.t.str[:10]); RC.append(a.pivot_table(index="d", columns="s", values="c")); V.append(a.pivot_table(index="d", columns="s", values="v"))
    f = lambda L: pd.concat(L, axis=1).sort_index().T.groupby(level=0).first().T
    C, RC, V = f(C), f(RC), f(V); idx = C["SPY"].dropna().index
    return C.reindex(idx), RC.reindex(idx), V.reindex(idx)


if __name__ == "__main__":
    st = sys.argv[1]
    act, ina = univ(); U = act | ina | {"SPY"}
    C, RC, V = load(U); DV = RC * V
    ME = C.resample("ME").last(); MR = ME.pct_change(fill_method=None)
    lastday = C.index.to_series().groupby(C.index.to_period("M")).last()
    months = pd.period_range("2021-01", "2022-12", freq="M") if st in ("density", "dev") else pd.period_range("2023-01", "2026-10", freq="M")
    rows, prev_w = [], {}
    for m in months:
        d0 = lastday[m - 1]; k0 = C.index.get_loc(d0)
        past = [MR.loc[(m - 12 * j).to_timestamp(how="end").normalize().replace(day=1) + pd.offsets.MonthEnd(0)] if (m - 12 * j).to_timestamp(how="end").normalize().replace(day=1) + pd.offsets.MonthEnd(0) in MR.index else None for j in range(1, 6)]
        if any(p is None for p in past): continue
        P = pd.concat(past, axis=1); sig = P.mean(axis=1)[P.notna().all(axis=1)]
        px = RC.iloc[k0]; dv = DV.iloc[k0 - 59:k0 + 1].median()
        elig = [s for s in sig.index if s != "SPY" and px.get(s, np.nan) >= 5 and dv.get(s, 0) >= 5e6]
        if not elig: continue
        sg = sig[elig].sort_values(ascending=False); top = list(sg.index[: max(1, len(sg) // 10)])
        mend = m.to_timestamp(how="end").normalize().replace(day=1) + pd.offsets.MonthEnd(0)
        r_all = MR.loc[mend, elig].fillna(0.0)               # delisted before month end: last close via ME ffill-less -> NaN -> cash 0
        # month return for a stock delisted mid-month: last available close vs previous month end
        for s in elig:
            if np.isnan(MR.loc[mend, s]):
                seg = C[s].loc[d0:lastday[m]].dropna()
                if len(seg) > 1: r_all[s] = seg.iloc[-1] / seg.iloc[0] - 1
        w = {s: 1 / len(top) for s in top}; turn = sum(abs(w.get(s, 0) - prev_w.get(s, 0)) for s in set(w) | set(prev_w)); prev_w = w
        rows.append(dict(m=str(m), n_elig=len(elig), n_top=len(top), inactive_share=round(sum(s in ina for s in elig) / len(elig), 3),
                         port=float(r_all[top].mean()), ew=float(r_all.mean()), turn=turn, spy=float(MR.loc[mend, "SPY"])))
    T = pd.DataFrame(rows)
    if st == "density":
        print(T[["m", "n_elig", "n_top", "inactive_share"]].to_string(index=False)); sys.exit()
    out = {"months": len(T)}
    for k, c in COST.items():
        ex = T.port - 2 * c * T.turn / 2 - T.ew          # turnover counts both sides: sum|dw| = buys+sells
        out[k] = dict(mean_excess_pct=round(float(ex.mean() * 100), 3), t=round(float(ex.mean() / ex.std() * np.sqrt(len(ex))), 2), pos_months=int((ex > 0).sum()),
                      by_year_pct={y: round(float(v * 100), 2) for y, v in ex.groupby(T.m.str[:4]).mean().items()})
    pr = T.port - COST["base"] * T.turn; e = (1 + pr).cumprod()
    out["portfolio"] = dict(cagr=round(float(e.iloc[-1] ** (12 / len(pr)) - 1), 4), sharpe=round(float(pr.mean() / pr.std() * np.sqrt(12)), 2), mdd=round(float((e / e.cummax() - 1).min()), 4),
                            spy_cagr=round(float((1 + T.spy).prod() ** (12 / len(T)) - 1), 4), ew_cagr=round(float((1 + T.ew).prod() ** (12 / len(T)) - 1), 4), mean_turn=round(float(T.turn.mean()), 2))
    print(json.dumps(out, indent=1, default=str))
