"""Diversifiers for C1 on the RoboForex-ECN server (docs/STABLE_SYSTEM_PLAN.md; user 30.10.2026: "can the average be improved?").
ECN has indices (.US500Cash .US30Cash .USTECHCash .DE40Cash .JP225Cash) and oil (BRENT WTI) that RoboForex-Pro lacks.
Components, all with the C1 machinery (Donchian ensemble {10..250} on BAR-hour bars, half long-only + half long-short,
10%/vol sizing, vol-targeted, LAG as in intraday_trend.py, costs on final weights):
  IDX  indices trend          OIL  oil trend          C1   BTC+ETH (RoboForex-Pro costs, as tested)
  DIP  RSI(2) dips on indices, daily bars: long when RSI2 < 10 and close > SMA200, out when close > SMA5 (Connors)
Costs: turnover = max(2026 median bar spread, 0.01%) + 0.005% commission (ASSUMED, ECN commission not measured);
financing per direction from the ECN swap (mode 5 = %/yr; charges only). EXPLORATION: everything here is seen data.
Usage: python research/stable/multi.py [BAR_HOURS=6]"""
import os, sys
import numpy as np, pandas as pd

BAR = int(sys.argv[1]) if len(sys.argv) > 1 else 6
PER_YEAR = 365 * 24 / BAR
LAG = int(os.environ.get("LAG", "2"))
TARGET = 0.20
E = pd.read_csv("data/derived/ecn_costs_20261030.csv").set_index("symbol")
P = pd.read_csv("data/derived/rf_costs_20261030.csv").set_index("symbol")
G = {"IDX": [".US500Cash", ".US30Cash", ".USTECHCash", ".DE40Cash", ".JP225Cash"], "OIL": ["BRENT", "WTI"], "C1": ["BTCUSD", "ETHUSD"]}

def load(s, rule):
    d = pd.read_csv(f"data/derived/intraday/{s}_H1.csv"); d.index = pd.to_datetime(d.time, unit="s")
    return d.close.resample(rule).last()

C = pd.DataFrame({s: load(s, f"{BAR}h") for g in G.values() for s in g}).loc["2017-07-01":]
C = C.ffill(limit=8)   # weekends / closed sessions: carry the last price (no return, no signal change)
R = C.pct_change(fill_method=None).fillna(0)
vol = R.rolling(60, min_periods=40).std() * np.sqrt(PER_YEAR)

def tc(s):
    if s in G["C1"]:
        d = pd.read_csv(f"data/derived/intraday/{s}_H1.csv"); d = d[d.time >= 1767225600]
        return float((d.spread * P.loc[s, "point"] / d.close).median())
    return max(float(E.loc[s, "med_spread_2026"]), 0.0001) + 0.00005

def fin(s, side):
    k = E.loc[s] if s in E.index else P.loc[s]; sw = k.swap_long if side > 0 else k.swap_short
    return max(0.0, -(sw / 100 if k.swap_mode == 5 else sw * k.point / k.price * 365))

def donch(c, long_only):
    st = []
    for n in (10, 20, 30, 60, 90, 150, 250):
        hi, lo = c.rolling(n).max().values, c.rolling(n).min().values
        xl, xh = c.rolling(n // 2).min().values, c.rolling(n // 2).max().values
        cv = c.values; p = np.zeros(len(c))
        for i in range(1, len(c)):
            q = p[i - 1]
            if np.isnan(cv[i]) or np.isnan(hi[i]): p[i] = q; continue
            if q == 0: q = 1 if cv[i] >= hi[i] else (-1 if (not long_only and cv[i] <= lo[i]) else 0)
            elif q > 0 and cv[i] <= xl[i]: q = 0
            elif q < 0 and cv[i] >= xh[i]: q = 0
            p[i] = q
        st.append(p)
    return pd.Series(np.mean(st, axis=0), index=c.index)

def target(W, cols):
    r0 = (W.shift(LAG) * R[cols]).sum(axis=1)
    v = r0.rolling(int(PER_YEAR / 4), min_periods=60).std() * np.sqrt(PER_YEAR)
    return W.mul((TARGET / v).clip(upper=3).fillna(0), axis=0)

def trend_w(cols, long_only):
    W = pd.DataFrame({s: donch(C[s], long_only) * (0.10 / vol[s]).clip(upper=3) / len(cols) for s in cols}).fillna(0)
    return target(W, cols)

def dip_w(cols):
    W = pd.DataFrame(0.0, index=C.index, columns=cols)
    for s in cols:
        c = load(s, "1D").dropna(); dl = c.diff(); up = dl.clip(lower=0).ewm(alpha=0.5).mean(); dn = (-dl.clip(upper=0)).ewm(alpha=0.5).mean()
        rsi = 100 - 100 / (1 + up / dn); s200 = c.rolling(200).mean(); s5 = c.rolling(5).mean(); p = np.zeros(len(c))
        for i in range(1, len(c)):
            q = p[i - 1]
            if q == 0 and rsi.iloc[i] < 10 and c.iloc[i] > s200.iloc[i]: q = 1
            elif q == 1 and c.iloc[i] > s5.iloc[i]: q = 0
            p[i] = q
        # a daily close is known at the end of that day: shift to the next day's bars
        W[s] = pd.Series(p, index=c.index + pd.Timedelta("1D")).reindex(C.index, method="ffill").fillna(0) * (0.10 / vol[s]).clip(upper=3) / len(cols)
    return target(W, cols)

def net(F):
    cols = list(F.columns); held = F.shift(LAG).fillna(0)
    t = pd.Series({s: tc(s) for s in cols}); fl = pd.Series({s: fin(s, 1) for s in cols}); fs = pd.Series({s: fin(s, -1) for s in cols})
    return (held * R[cols]).sum(axis=1) - (held.diff().abs() * t).sum(axis=1) - (held.clip(lower=0) * fl + (-held).clip(lower=0) * fs).sum(axis=1) / PER_YEAR

def rep(r, nm, a="2018", b="2025-10-24"):
    x = r.loc[a:b]; eq = (1 + x).cumprod(); y = x.groupby(x.index.year).apply(lambda z: (1 + z).prod() - 1) * 100
    yrs = (x.index[-1] - x.index[0]).days / 365.25
    print(f"{nm:10s} CAGR {(eq.iloc[-1] ** (1 / yrs) - 1) * 100:5.1f}% Sh {x.mean() / x.std() * PER_YEAR ** .5:4.2f} MDD {(eq / eq.cummax() - 1).min() * 100:5.1f}% |",
          " ".join(f"{int(k) % 100:02d}:{v:+.0f}" for k, v in y.items()))
    return x

if __name__ == "__main__":
    W = {g: 0.5 * trend_w(G[g], True) + 0.5 * trend_w(G[g], False) for g in G}
    W["DIP"] = dip_w(G["IDX"])
    S = {g: rep(net(W[g]), g) for g in W}
    print("corr\n", pd.DataFrame(S).corr().round(2).to_string())
    def combo(names, nm):
        F = pd.concat([W[g] for g in names], axis=1)
        F = F.T.groupby(level=0).sum().T   # same symbol in two components (IDX trend + DIP): net it
        return rep(net(F), nm), rep(net(F), nm + "_hold", "2025-10-25", "2030")
    combo(["C1", "IDX"], "C1+IDX"); combo(["C1", "OIL"], "C1+OIL"); combo(["C1", "DIP"], "C1+DIP")
    combo(["C1", "IDX", "OIL"], "C1+IDX+OIL"); combo(["C1", "IDX", "OIL", "DIP"], "ALL")
