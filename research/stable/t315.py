"""t315 (docs/prereg/research_t315.md): intraday H1 Donchian-20 breakout, SL 2ATR / TP 4ATR, flat at 22:00 server, 10 RF ECN symbols.
Input: Common\\Files\\t315_<symbol>_PERIOD_H1.csv from BarExport. Usage: py -3.12 research/stable/t315.py costs|dev|holdout"""
import json, os, sys
import numpy as np, pandas as pd

CF = "C:/Users/Benza/AppData/Roaming/MetaQuotes/Terminal/Common/Files/"
SYMS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD", "XAGUSD", ".US500Cash", ".DE40Cash", ".JP225Cash", "WTI"]
DIGITS = {"EURUSD": 5, "GBPUSD": 5, "USDJPY": 3, "AUDUSD": 5, "XAUUSD": 2, "XAGUSD": 3, ".US500Cash": 2, ".DE40Cash": 2, ".JP225Cash": 2, "WTI": 3}
COMM = 0.5e-4   # round trip, of notional
# technical fix 20.11 17:45 (before any result): the exported bar spread is mostly 0 in open-prices mode, so it cannot price costs.
# Fixed one-side costs (ASSUMED, typical RF ECN spread/2 + commission/2), in fraction of price:
SIDE = {"EURUSD": 0.5e-4, "GBPUSD": 0.6e-4, "USDJPY": 0.5e-4, "AUDUSD": 0.6e-4, "XAUUSD": 0.8e-4, "XAGUSD": 4.0e-4,
        ".US500Cash": 0.6e-4, ".DE40Cash": 0.6e-4, ".JP225Cash": 1.0e-4, "WTI": 2.6e-4}


def load(s):
    d = pd.read_csv(CF + f"t315_{s}_PERIOD_H1.csv")
    d["t"] = pd.to_datetime(d.time, unit="s"); d = d.set_index("t").sort_index()
    d["spr"] = d.spread * 10.0 ** -DIGITS[s]
    return d


def cost_ok(s, d):
    side = SIDE[s]
    return float(side), bool(side <= 2e-4)


def trades(d, s):
    h, l, c, o = d.high.values, d.low.values, d.close.values, d.open.values
    tr = np.maximum(h - l, np.maximum(abs(h - np.r_[c[0], c[:-1]]), abs(l - np.r_[c[0], c[:-1]])))
    atr = pd.Series(tr).rolling(20).mean().values
    hh = pd.Series(h).rolling(20).max().shift(1).values; ll = pd.Series(l).rolling(20).min().shift(1).values
    hr = d.index.hour.values; spr = d.spr.values; idx = d.index
    out = []; i = 21; n = len(d)
    while i < n - 1:
        sig = 1 if c[i] > hh[i] else (-1 if c[i] < ll[i] else 0)
        if sig == 0 or not (9 <= hr[i + 1] <= 20) or np.isnan(atr[i]) or idx[i + 1].date() != idx[i].date():
            i += 1; continue
        e = o[i + 1]; a = atr[i]; sl = e - sig * 2 * a; tp = e + sig * 4 * a; j = i + 1; x = None
        while j < n:
            if hr[j] >= 22 or idx[j].date() != idx[i + 1].date():
                x = o[j]; break
            if (sig > 0 and l[j] <= sl) or (sig < 0 and h[j] >= sl): x = sl; break
            if (sig > 0 and h[j] >= tp) or (sig < 0 and l[j] <= tp): x = tp; break
            j += 1
        if x is None: break
        units = 0.0025 / (2 * a / e)                          # 0.25% risk at the stop
        gross = sig * (x - e) / e * units
        cst = 2 * SIDE[s] * units
        out.append((idx[i + 1], sig, gross - cst, cst))
        i = j
    return pd.DataFrame(out, columns=["t", "side", "r", "cost"])


def stats(daily, ntr):
    r = daily.dropna(); eq = 1 + r.cumsum()
    return dict(ann=round(float(r.mean() * 252), 4), sharpe=round(float(r.mean() / r.std() * np.sqrt(252)), 2),
                mdd=round(float((eq / eq.cummax() - 1).min()), 4), trades=int(ntr))


if __name__ == "__main__":
    part = sys.argv[1]
    data = {s: load(s) for s in SYMS if os.path.exists(CF + f"t315_{s}_PERIOD_H1.csv")}
    costs = {s: cost_ok(s, d) for s, d in data.items()}
    if part == "costs":
        print(json.dumps({s: {"side_cost_bp": round(v[0] * 1e4, 2), "ok": v[1]} for s, v in costs.items()}, indent=1)); sys.exit()
    lo, hi = ("2015-01-01", "2020-12-31") if part == "dev" else ("2021-01-01", "2026-11-15")
    keep = [s for s in data if costs[s][1]]
    T = {s: trades(data[s][lo:hi], s) for s in keep}
    days = pd.bdate_range(lo, min(pd.Timestamp(hi), max(data[s].index[-1] for s in keep)))
    per = {s: T[s].groupby(T[s].t.dt.normalize()).r.sum().reindex(days, fill_value=0) for s in keep if len(T[s])}
    port = pd.DataFrame(per).sum(axis=1)
    dbl = port - pd.DataFrame({s: T[s].groupby(T[s].t.dt.normalize()).cost.sum().reindex(days, fill_value=0) for s in per}).sum(axis=1)
    out = {"kept": keep, "portfolio": stats(port, sum(len(T[s]) for s in keep)), "portfolio_2x_cost (info)": stats(dbl, 0)}
    for s in per:
        out[s] = stats(per[s], len(T[s]))
        for sd, nm in ((1, "long"), (-1, "short")):
            x = T[s][T[s].side == sd]; out[f"{s}_{nm}"] = round(float(x.r.sum()), 4)
    print(json.dumps(out, indent=1))
