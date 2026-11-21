"""Nasdaq bot (I2, second4.py) on EGlobal's cent symbol $US100c vs RoboForex .USTECHCash over the same months (EGlobal H1 bars start
3/2025). EGlobal's server clock is RoboForex's minus 1h (the NY-open volatility peak is at server 15:00 there, 16:00 at RF), so
the EGlobal hours are OpenHour 15, checks 15..20, exit at the 21:00 close. Costs: each broker's 2026 median bar spread per change
(+0.005% commission at RF only, ASSUMED; EGlobal cent symbols carry no commission, ASSUMED). Unscaled returns per 1x notional and
the same 10% vol scaling. Usage: python research/stable/eg_nasdaq.py"""
import numpy as np, pandas as pd

def strat(s, oh, tc, lb=14):
    h = pd.read_csv(f"data/derived/intraday/{s}_H1.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
    chk = list(range(oh, oh + 6)); ex = oh + 6
    m = (h.index.hour >= oh) & (h.index.hour <= ex)
    Cl = h.close[m].to_frame("c").assign(d=h.index[m].normalize(), k=h.index[m].hour).pivot_table(index="d", columns="k", values="c").dropna()
    O = h.open[h.index.hour == oh]; O.index = O.index.normalize(); Cl = Cl[Cl.index.isin(O.index)]; o = O.reindex(Cl.index)
    prev = Cl[ex].shift(1); sig = Cl[chk].div(o, axis=0).sub(1).abs().rolling(lb).mean().shift(1)
    up = pd.concat([o, prev], axis=1).max(1); lo = pd.concat([o, prev], axis=1).min(1); out = pd.Series(0.0, index=Cl.index)
    for d in Cl.index[lb + 2:]:
        if np.isnan(prev[d]) or sig.loc[d].isna().any(): continue
        q = 0; r = 0.0; last = None
        for k in chk + [ex]:
            c = Cl.at[d, k]
            if last is not None and q != 0: r += q * (c / last - 1)
            last = c
            nq = 0 if k == ex else (1 if c > up[d] * (1 + sig.at[d, k]) else (-1 if c < lo[d] * (1 - sig.at[d, k]) else 0))
            r -= abs(nq - q) * tc; q = nq
        out[d] = r
    return out

def tc_of(s, point, extra):
    d = pd.read_csv(f"data/derived/intraday/{s}_H1.csv"); d = d[d.time >= 1767225600]
    return float((d.spread * point / d.close).median()) + extra

R = {"RoboForex .USTECHCash": strat(".USTECHCash", 16, max(tc_of(".USTECHCash", 0.1, 0), 0.0001) + 0.00005),
     "EGlobal $US100c": strat("$US100c", 15, tc_of("$US100c", 0.1, 0))}
for nm, r in R.items():
    x = r.loc["2025-06-01":"2026-10-30"]; v = x.std() * np.sqrt(260); y = x * 0.10 / v; eq = (1 + y).cumprod()
    print(f"{nm:24s} days {len(x)} raw Sharpe {x.mean() / x.std() * np.sqrt(260):5.2f} | at 10% vol: return {(eq.iloc[-1] - 1) * 100:+.1f}% MDD {(eq / eq.cummax() - 1).min() * 100:.1f}%")
a = pd.concat(R, axis=1).loc["2025-06-01":].dropna(); print("daily corr between brokers:", round(a.corr().iloc[0, 1], 2))
print("cost per change: RF", round(max(tc_of(".USTECHCash", 0.1, 0), 0.0001) * 100 + 0.005, 4), "% | EG", round(tc_of("$US100c", 0.1, 0) * 100, 4), "%")
