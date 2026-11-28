"""t351 (docs/prereg/research_t351.md): cash merger arbitrage, ledger from GPT t349.
Usage: py -3.12 research/stable/t351.py check|dev"""
import glob, json, sys
import numpy as np, pandas as pd

L = pd.read_csv("docs/prereg/research_t349.csv", parse_dates=["announcement_date", "next_trading_date", "outcome_date"])
syms = set(L.target_ticker) | {"SPY"}
R = []
for f in sorted(glob.glob("data/raw/alpaca/daily/*.csv.gz")):
    a = pd.read_csv(f, usecols=["s", "t", "c"]).dropna(); a = a[a.s.isin(syms)]
    if len(a): a["d"] = pd.to_datetime(a.t.str[:10]); R.append(a.pivot_table(index="d", columns="s", values="c"))
C = pd.concat(R, axis=1).sort_index(); C = C.T.groupby(level=0).first().T
idx = C["SPY"].dropna().index; C = C.reindex(idx)
COST, STRESS = 0.0005, 0.015

rows = []
for x in L.itertuples():
    s = x.target_ticker
    if s not in C.columns: rows.append(dict(s=s, ok=False, why="no symbol")); continue
    p = C[s]
    ke = idx.searchsorted(x.next_trading_date)
    if ke >= len(idx) or idx[ke] != x.next_trading_date or np.isnan(p.iloc[ke]): rows.append(dict(s=s, ok=False, why="no entry px")); continue
    pin = p.iloc[ke]
    if x.outcome == "completed":
        last = p.loc[:x.outcome_date].dropna()
        if not len(last) or last.index[-1] < idx[ke]: rows.append(dict(s=s, ok=False, why="no exit px")); continue
        kx = idx.searchsorted(x.outcome_date); kx = min(kx, len(idx) - 1)
        pout = x.offer_price_per_share; dev_last = last.iloc[-1] / pout - 1
        ret = pout / pin - 1 - COST
    else:
        kx = idx.searchsorted(x.outcome_date) + 1
        if kx >= len(idx) or np.isnan(p.iloc[kx]): rows.append(dict(s=s, ok=False, why="no break px")); continue
        pout = p.iloc[kx]; dev_last = np.nan; ret = pout / pin - 1 - 2 * COST
    rows.append(dict(s=s, ok=True, outcome=x.outcome, ke=ke, kx=kx, pin=pin, pout=pout, dev_last=dev_last, ret=ret, days=(idx[kx] - idx[ke]).days))
D = pd.DataFrame(rows)

if sys.argv[1] == "check":
    ok = D[D.ok]; comp = ok[ok.outcome == "completed"]
    print("price coverage", len(ok), "/", len(L), round(len(ok) / len(L), 3))
    print("missing:", D[~D.ok][["s", "why"]].values.tolist())
    print("completed within 2% of offer:", round(float((comp.dev_last.abs() <= 0.02).mean()), 3), "n", len(comp))
    print("worst:", comp.reindex(comp.dev_last.abs().sort_values(ascending=False).index)[["s", "pout", "dev_last"]].head(8).values.tolist())
    sys.exit()

ok = D[D.ok]
r = pd.Series(0.0, index=idx); n = pd.Series(0, index=idx)
for x in ok.astype({"ke": int, "kx": int}).itertuples():
    path = C[x.s].iloc[x.ke:x.kx + 1].ffill().values.copy()
    path[-1] = x.pout
    dr = path[1:] / path[:-1] - 1
    dr[0] -= COST if x.outcome == "completed" else 2 * COST
    r.iloc[x.ke + 1:x.kx + 1] += dr; n.iloc[x.ke + 1:x.kx + 1] += 1
pr = (r / n.replace(0, np.nan)).fillna(0).loc["2019-01-01":"2022-12-31"]
pr = pr.loc[:pr[n.loc[pr.index] > 0].index[-1]]
e = (1 + pr).cumprod(); yrs = len(pr) / 252
spy = C["SPY"].loc[pr.index]
out = dict(n=len(ok), mean_ret_pct=round(float(ok.ret.mean() * 100), 2), mean_ret_stress_pct=round(float((ok.ret.mean() - STRESS) * 100), 2),
           mean_days=round(float(ok.days.mean()), 1), ann_per_deal_pct=round(float((((1 + ok.ret) ** (365 / ok.days.clip(lower=1))) - 1).median() * 100), 1),
           breaks=ok[ok.outcome != "completed"][["s", "ret"]].values.tolist(),
           cagr=round(float(e.iloc[-1] ** (1 / yrs) - 1), 4), sharpe=round(float(pr.mean() / pr.std() * np.sqrt(252)), 2),
           mdd=round(float((e / e.cummax() - 1).min()), 4),
           by_year_pct={int(y): round(float(v * 100), 1) for y, v in ((1 + pr).groupby(pr.index.year).prod() - 1).items()},
           spy_cagr=round(float((spy.iloc[-1] / spy.iloc[0]) ** (1 / yrs) - 1), 4), worst5=ok.nsmallest(5, "ret")[["s", "ret"]].values.tolist())
try:
    sys.path.insert(0, "research/stable"); from book_tester import i2_daily
    i2 = i2_daily(); c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.resample("D").last().pct_change()
    out["corr_C1"] = round(float(pr.corr(c1.reindex(pr.index))), 2); out["corr_I2"] = round(float(pr.corr(i2.reindex(pr.index).fillna(0))), 2)
except Exception as ex: out["corr_err"] = str(ex)[:80]
print(json.dumps(out, indent=1, default=str))
