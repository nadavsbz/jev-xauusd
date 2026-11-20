"""t310 (docs/prereg/research_t310.md): A = front-running rebalancers SPY/IEF, B = turn-of-the-month SPY. Daily adj closes.
Usage: py -3.12 research/stable/t310.py dev|holdout"""
import json, sys
import numpy as np, pandas as pd


def load(s):
    r = json.load(open(f"data/raw/etf/{s}.json"))["chart"]["result"][0]
    return pd.Series(r["indicators"]["adjclose"][0]["adjclose"],
                     index=pd.to_datetime(r["timestamp"], unit="s").normalize(), name=s).dropna()


def stats(r):
    r = r.dropna()
    eq = (1 + r).cumprod(); mdd = float((eq / eq.cummax() - 1).min())
    yrs = len(r) / 252
    return dict(ann=round(float(eq.iloc[-1] ** (1 / yrs) - 1), 4), sharpe=round(float(r.mean() / r.std() * np.sqrt(252)), 2),
                mdd=round(mdd, 4), days=len(r), pos_months=round(float(((1 + r).resample("ME").prod() - 1 > 0).mean()), 2))


def rebal(px):
    ret = px.pct_change().fillna(0)
    d = px.index; ym = d.to_period("M")
    last = pd.Series(ym, index=d) != pd.Series(ym, index=d).shift(-1)      # last trading day of month
    first = pd.Series(ym, index=d) != pd.Series(ym, index=d).shift(1)
    wt, wc = 0.6, 0.6; T, C = [], []
    for i in range(len(d)):
        if i > 0:
            rs, rb = ret.SPY.iloc[i], ret.IEF.iloc[i]
            wt = wt * (1 + rs) / (wt * (1 + rs) + (1 - wt) * (1 + rb))
            wc = wc * (1 + rs) / (wc * (1 + rs) + (1 - wc) * (1 + rb))
        T.append(wt - 0.6); C.append(wc - 0.6)
        if abs(wt - 0.6) >= 0.02: wt = 0.6
        if last.iloc[i]: wc = 0.6
    T, C = pd.Series(T, index=d), pd.Series(C, index=d)
    thr = (-T / 0.015).clip(-1, 1)
    # trading-day position inside the month
    k_from_end = pd.Series(range(len(d)), index=d).groupby(ym).transform(lambda s: s.max() - s)   # 0 = last day
    cal = pd.Series(0.0, index=d)
    cal[k_from_end <= 4] = np.sign(-C[k_from_end <= 4])
    c4 = C.shift(4)
    cal[first.values] = np.sign(c4[first.values])
    w = ((thr + cal) / 2).fillna(0)
    gross = w.shift(1) * (ret.SPY - ret.IEF)
    cost = 4e-4 * w.diff().abs().fillna(0)
    return gross - cost.shift(0).fillna(0)


def tom(px):
    ret = px.SPY.pct_change().fillna(0); d = px.index; ym = d.to_period("M")
    pos_in = pd.Series(range(len(d)), index=d).groupby(ym)
    k_from_end = pos_in.transform(lambda s: s.max() - s); k_from_start = pos_in.transform(lambda s: s - s.min())
    hold = (k_from_end == 0) | (k_from_start <= 2)          # return days: last day + first 3 days
    w = hold.astype(float).shift(-1).fillna(0)               # position held from the previous close
    r = w.shift(1) * ret
    cost = 2e-4 * w.diff().abs().fillna(0)
    return r - cost


if __name__ == "__main__":
    part = sys.argv[1]
    px = pd.concat([load("SPY"), load("IEF")], axis=1).dropna()
    a, b = rebal(px), tom(px)
    lo, hi = ("2003-01-02", "2014-12-31") if part == "dev" else ("2015-01-01", "2100-01-01")
    out = {"A_rebal": stats(a[lo:hi]), "B_tom": stats(b[lo:hi])}
    if part == "holdout": out["A_post_2023-04 (info)"] = stats(a["2023-04-01":])
    out["data_end"] = str(px.index[-1].date())
    print(json.dumps(out, indent=1))
