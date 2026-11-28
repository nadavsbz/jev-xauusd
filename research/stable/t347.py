"""t347 (docs/prereg/research_t347.md): cross-sectional overnight bias, Alpaca daily.
Usage: py -3.12 research/stable/t347.py density|dev|holdout"""
import glob, json, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/stable")
from t338 import universe

N, WIN, MINOBS, TMIN, PXMIN, DVMIN = 50, 252, 220, 1.96, 10.0, 20e6
COST = {"base": 0.0002, "stress": 0.0005}


def load(U):
    O, C, RC, V = [], [], [], []
    for f in sorted(glob.glob("data/raw/alpaca/daily_adj/*.csv.gz")):
        a = pd.read_csv(f)
        a = a[a.s.isin(U)]
        if len(a):
            a["d"] = pd.to_datetime(a.t); O.append(a.pivot_table(index="d", columns="s", values="o")); C.append(a.pivot_table(index="d", columns="s", values="c"))
    for f in sorted(glob.glob("data/raw/alpaca/daily/*.csv.gz")):
        a = pd.read_csv(f, usecols=["s", "t", "c", "v"]).dropna()
        a = a[a.s.isin(U)]
        if len(a):
            a["d"] = pd.to_datetime(a.t.str[:10]); RC.append(a.pivot_table(index="d", columns="s", values="c")); V.append(a.pivot_table(index="d", columns="s", values="v"))
    f = lambda L: pd.concat(L, axis=1).sort_index()
    O, C, RC, V = f(O), f(C), f(RC), f(V)
    idx = C["SPY"].dropna().index
    return O.reindex(idx), C.reindex(idx), RC.reindex(idx), V.reindex(idx)


def select(ON, RC, DV, idx, y):
    d = idx[idx.year == y][-1]; k = idx.get_loc(d)
    W = ON.iloc[k - WIN + 1:k + 1]
    n = W.notna().sum(); m = W.mean(); sd = W.std()
    t = m / (sd / np.sqrt(n))
    cum = (1 + W.fillna(0)).prod() - 1
    px = RC.iloc[k]; dv = DV.iloc[k - 59:k + 1].median()
    ok = (n >= MINOBS) & (m > 0) & (t >= TMIN) & (px >= PXMIN) & (dv >= DVMIN)
    ok = ok.drop("SPY", errors="ignore")
    elig = cum[ok[ok].index].sort_values(ascending=False)
    return list(elig.index[:N]), int(ok.sum())


def run(ON, RC, DV, idx, years, hi):
    port, info = [], {}
    for y in years:
        pick, ne = select(ON, RC, DV, idx, y - 1)
        days = idx[(idx.year == y) & (idx <= pd.Timestamp(hi))]
        X = ON.loc[days, pick]
        info[y] = dict(eligible=ne, picked=len(pick), valid_slots=round(float(X.notna().values.mean()), 3), sample=pick[:8])
        port.append(X.fillna(0).sum(axis=1) / N)
    return pd.concat(port), info


def stt(r):
    e = (1 + r).cumprod(); yrs = len(r) / 252
    yr = (1 + r).groupby(r.index.year).prod() - 1
    return dict(cagr=round(float(e.iloc[-1] ** (1 / yrs) - 1), 4), sharpe=round(float(r.mean() / r.std() * np.sqrt(252)), 2),
                mdd=round(float((e / e.cummax() - 1).min()), 4), by_year_pct={int(k): round(float(v * 100), 1) for k, v in yr.items()})


if __name__ == "__main__":
    st = sys.argv[1]
    U = universe() | {"SPY"}
    O, C, RC, V = load(U); idx = C.index
    ON = O / C.shift(1) - 1; DV = RC * V
    years, hi = ([2019, 2020, 2021], "2021-12-31") if st in ("density", "dev") else ([2022, 2023, 2024, 2025, 2026], "2026-11-20")
    g, info = run(ON, RC, DV, idx, years, hi)
    if st == "density":
        print(json.dumps(info, indent=1)); sys.exit()
    out = {"info": info}
    for k, c in COST.items(): out[k] = stt(g - 2 * c)
    spy = C["SPY"].loc[g.index[0] - pd.Timedelta(days=7):g.index[-1]]
    out["SPY_bh"] = stt(spy.pct_change().dropna().loc[g.index[0]:])
    out["SPY_nights"] = stt(ON["SPY"].loc[g.index].fillna(0))
    gb = g - 2 * COST["base"]; top = gb.sort_values(ascending=False).head(10)
    out["top10_nights_share_of_sum"] = round(float(top.sum() / gb.sum()), 2)
    try:
        from book_tester import i2_daily
        i2 = i2_daily()
        c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.resample("D").last().pct_change()
        out["corr_C1"] = round(float(gb.corr(c1.reindex(gb.index))), 2); out["corr_I2"] = round(float(gb.corr(i2.reindex(gb.index).fillna(0))), 2)
    except Exception as ex: out["corr_err"] = str(ex)[:80]
    print(json.dumps(out, indent=1, default=str))
