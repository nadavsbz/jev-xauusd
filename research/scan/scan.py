"""Broad scan of docs/SCAN_PLAN.md (pre-registered 10.11.2026): families F1 (IndexNoise rule, intraday, no nights) and F2 (C1 Donchian
ensemble on H6, half long-only / half long-short, swap per night) on an equal-weight basket of all ECN US stocks; F3 = F1 on DE40/JP225
with their own sessions. Per-stock numbers are descriptive only. dev = start..2022, test = 2023..now (run once with 'test').
Usage: python research/scan/scan.py [dev|test]  -> writes data/derived/scan/<family>_daily.csv"""
import glob, os, sys
import numpy as np, pandas as pd

PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
E = pd.read_csv("data/derived/ecn_costs_20261030.csv").set_index("symbol")
H = "data/derived/scan/h1"
NONSTOCK = {"DE40Cash", "US500Cash", "US30Cash", "USTECHCash", "JP225Cash", "BRENT", "WTI", "BTCUSD", "ETHUSD"}
COMM_STOCK = 0.0002

def load(s):
    h = pd.read_csv(f"{H}/{s}.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
    return h[(h.close > 0) & (h.open > 0)]       # MMM has zero-price bars (found 10.11)

def tcost(s, h):
    key = s if s in E.index else "." + s
    sp = E.loc[key, "med_spread_2026"] if key in E.index else np.nan
    if not np.isfinite(sp):
        pt = E.loc[key, "point"] if key in E.index else 0.01
        x = h.loc["2026"]; sp = float((x.spread * pt / x.close).median()) if len(x) else 0.0003
    return max(sp, 0.0001) + (COMM_STOCK if s not in NONSTOCK else 0.00005)

def noise(h, tc, o_hr, chk, ex, lb=14):
    """IndexNoise rule (research/stable/second4.py) with session hours as parameters (server time)."""
    day = h.index.normalize(); m = (h.index.hour >= o_hr) & (h.index.hour <= ex)
    O = h.open[h.index.hour == o_hr]; O.index = O.index.normalize()
    Cl = h.close[m].to_frame("c").assign(d=day[m], k=h.index.hour[m]).pivot_table(index="d", columns="k", values="c")
    if ex not in Cl or any(k not in Cl for k in chk): return pd.Series(dtype=float)
    Cl = Cl[chk + [ex]].dropna(); Cl = Cl[Cl.index.isin(O.index)]; o = O.reindex(Cl.index)
    prev = Cl[ex].shift(1); sig = Cl[chk].div(o, axis=0).sub(1).abs().rolling(lb).mean().shift(1)
    up = pd.concat([o, prev], axis=1).max(1); lo = pd.concat([o, prev], axis=1).min(1)
    C = Cl.values; S = sig.values; U0 = up.values; L0 = lo.values; out = np.zeros(len(Cl))
    for i in range(lb + 2, len(Cl)):
        if np.isnan(prev.iloc[i]) or np.isnan(S[i]).any(): continue
        q = 0; r = 0.0; last = None
        for j in range(len(chk) + 1):
            c = C[i, j]
            if last is not None and q: r += q * (c / last - 1)
            last = c
            nq = 0 if j == len(chk) else (1 if c > U0[i] * (1 + S[i, j]) else (-1 if c < L0[i] * (1 - S[i, j]) else 0))
            r -= abs(nq - q) * tc; q = nq
        out[i] = r
    return pd.Series(out, index=Cl.index)

def donch(c, long_only):
    st = []
    for n in (10, 20, 30, 60, 90, 150, 250):
        hv, lv = c.rolling(n).max().values, c.rolling(n).min().values; xl, xh = c.rolling(n // 2).min().values, c.rolling(n // 2).max().values
        p = np.zeros(len(c)); cv = c.values
        for i in range(1, len(c)):
            q = p[i - 1]
            if q == 0: q = 1 if cv[i] >= hv[i] else (-1 if (not long_only and cv[i] <= lv[i]) else 0)
            elif q > 0 and cv[i] <= xl[i]: q = 0
            elif q < 0 and cv[i] >= xh[i]: q = 0
            p[i] = q
        st.append(p)
    return pd.Series(np.mean(st, axis=0), index=c.index)

def trend(h, tc, sw_l, sw_s):
    """C1 rule on H6 bars: 0.5 x long-only + 0.5 x long-short ensemble, decided at a bar close, held from the next bar (lag 2 as C1)."""
    c = h.close.resample("6h").last().dropna()
    r = c.pct_change().fillna(0)
    w = (0.5 * donch(c, True) + 0.5 * donch(c, False)).shift(2).fillna(0)
    dt = c.index.to_series().diff().dt.total_seconds().fillna(0) / 86400 / 365
    fin = np.where(w > 0, w * sw_l, -w * sw_s) * dt        # swap in % per year (negative numbers = cost)
    net = w * r - w.diff().abs().fillna(0) * tc + fin / 100
    return (1 + net).groupby(net.index.normalize()).prod() - 1

def scale(r, target=0.10):
    v = r.rolling(90, min_periods=60).std().shift(1) * np.sqrt(252)
    return r * (target / v).clip(upper=5).fillna(0)

def rep(x, nm):
    x = x[x.index.dayofweek < 5]
    if x.std() == 0 or len(x) < 50: print(f"{nm:14s} no data"); return
    y = x.groupby(x.index.year).sum() * 100; sh = x.mean() / x.std() * np.sqrt(252)
    eq = (1 + x).cumprod(); mdd = (eq / eq.cummax() - 1).min() * 100
    print(f"{nm:14s} Sh {sh:5.2f} ann {x.mean() * 252 * 100:5.1f}% MDD {mdd:6.1f}% pos {int((y > 0).sum())}/{len(y)} |", " ".join(f"{a % 100:02d}:{v:+.0f}" for a, v in y.items()))

if __name__ == "__main__":
    span = ("2000", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    stocks = sorted(os.path.basename(f)[:-4] for f in glob.glob(f"{H}/*.csv") if os.path.basename(f)[:-4] not in NONSTOCK)
    F1, F2 = {}, {}
    print(f"===== {PER} {span}  stocks: {len(stocks)}")
    for s in stocks:
        h = load(s); tc = tcost(s, h); key = s if s in E.index else "." + s
        F1[s] = scale(noise(h, tc, 16, list(range(16, 22)), 22))
        F2[s] = scale(trend(h, tc, E.loc[key, "swap_long"], E.loc[key, "swap_short"]))
    for nm, F in (("F1", F1), ("F2", F2)):
        df = pd.DataFrame(F).fillna(0); bask = scale(df.mean(axis=1))
        os.makedirs("data/derived/scan", exist_ok=True); bask.to_csv(f"data/derived/scan/{nm}_daily.csv", header=["ret"])
        print(f"--- {nm} basket"); rep(bask.loc[span[0]:span[1]], f"{nm} BASKET")
        print(f"    per stock ({nm}, descriptive only):")
        for s in stocks: rep(F[s].loc[span[0]:span[1]], f"  {s}")
    # F3: DE40 (Frankfurt 9:00-17:30 = server 10..18 in winter; checks at closes of bars 10..16, flat at bar 18) and JP225
    # (Tokyo 9:00-15:00 = server 2..8; checks at closes of bars 2..6, flat at bar 8). Server = NY + 7 => CET + 1, JST - 7.
    print("--- F3 indices")
    for s, o, chk, ex in (("DE40Cash", 10, list(range(10, 17)), 18), ("JP225Cash", 2, list(range(2, 7)), 8)):
        h = load(s); x = scale(noise(h, tcost(s, h), o, chk, ex)); x.to_csv(f"data/derived/scan/F3_{s}_daily.csv", header=["ret"])
        rep(x.loc[span[0]:span[1]], f"F3 {s}")
