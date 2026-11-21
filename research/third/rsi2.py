"""Candidate 1 of docs/THIRD_COMPONENT_PLAN.md: Connors RSI(2) long-only on NDX/SPX/DAX/N225, frozen rules, costs.
Entry at the close when RSI(2) < 10 and close > SMA(200); exit at the close when close > SMA(5). Equal-weight sleeves, no leverage.
Costs: 0.02% per round trip, swap per calendar night held (-8.6%/yr US, -7.2%/yr DAX/N225).
Usage: python research/third/rsi2.py  -> prints per-index and portfolio stats; writes data/derived/third/rsi2_daily.csv"""
import os
import numpy as np, pandas as pd

SWAP = {"NDX": 0.086, "SPX": 0.086, "DAX": 0.072, "N225": 0.072}
RT_COST = 0.0002

def rsi(c, n=2):
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)

def sleeve(name):
    d = pd.read_csv(f"data/raw/yahoo/{name}.csv", parse_dates=["date"]).set_index("date").close
    d = d[~d.index.duplicated()].dropna()
    r2, s200, s5 = rsi(d), d.rolling(200).mean(), d.rolling(5).mean()
    pos = pd.Series(0.0, index=d.index); inpos = False
    for i, t in enumerate(d.index):
        if not inpos and r2.iloc[i] < 10 and d.iloc[i] > s200.iloc[i]: inpos = True
        elif inpos and d.iloc[i] > s5.iloc[i]: inpos = False
        pos.iloc[i] = 1.0 if inpos else 0.0
    held = pos.shift(1).fillna(0)                       # position held over the day ending at t
    nights = d.index.to_series().diff().dt.days.fillna(1)
    ret = held * (d.pct_change().fillna(0) - SWAP[name] / 365 * nights)
    trades = pos.diff().abs().fillna(0)                 # 1 at each entry and exit
    ret -= trades * RT_COST / 2
    return ret, pos

def stats(x, nm):
    eq = (1 + x).cumprod(); yrs = (x.index[-1] - x.index[0]).days / 365.25
    y = x.groupby(x.index.year).apply(lambda z: (1 + z).prod() - 1) * 100
    sh = x.mean() / x.std() * np.sqrt(252)
    print(f"{nm:10s} CAGR {(eq.iloc[-1] ** (1 / yrs) - 1) * 100:5.1f}% Sh {sh:5.2f} MDD {(eq / eq.cummax() - 1).min() * 100:6.1f}% pos {int((y > 0).sum())}/{len(y)} |",
          " ".join(f"{int(k) % 100:02d}:{v:+.0f}" for k, v in y.items()))
    return sh, int((y > 0).sum()), len(y)

if __name__ == "__main__":
    R, P = {}, {}
    for n in SWAP: R[n], P[n] = sleeve(n)
    df = pd.DataFrame(R).fillna(0); port = df.mean(axis=1)
    for a, b, lab in (("2000", "2015", "2000-2015"), ("2016", "2026-10-31", "2016-2026")):
        print(f"--- {lab}")
        for n in SWAP: stats(df[n].loc[a:b], n)
        stats(port.loc[a:b], "PORT(1/4)")
    print("exposure (share of days in a position):", {n: round(P[n].loc["2016":].mean(), 2) for n in SWAP})
    os.makedirs("data/derived/third", exist_ok=True); port.to_csv("data/derived/third/rsi2_daily.csv", header=["ret"])
