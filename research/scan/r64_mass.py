"""Round 64 mass scan (prereg docs/prereg/r64_mass_scan.md, commit d84c027). 21 rules x all RF ECN symbols + class baskets + 4 cross-sectional.
dev: writes data/derived/scan/r64_dev.csv and r64_survivors.csv. test: holdout for survivors only (run once).
Usage: py -3.12 research/scan/r64_mass.py dev|test"""
import os, sys, glob
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/stable")
from scan import tcost, scale
MODE = sys.argv[1] if len(sys.argv) > 1 else "dev"
DEV_END, HO = "2022-12-31", "2023-01-01"
E = pd.read_csv("data/derived/ecn_costs_20261030.csv").set_index("symbol")
OUT = "data/derived/scan"

def loadh(s):
    for f in (f"{OUT}/h1/{s.lstrip('.')}.csv", f"data/derived/intraday/{s}_H1.csv"):
        if os.path.exists(f):
            h = pd.read_csv(f); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()].sort_index()
            return h[(h.close > 0) & (h.open > 0)]
    return None

def cls(s):
    if s.startswith("."): return "index"
    if s in ("BRENT", "WTI"): return "energy"
    if s.startswith(("XAU", "XAG")): return "metal"
    if s in ("BTCUSD", "ETHUSD", "XRPUSD", "SOLUSD"): return "crypto"
    if len(s) == 6 and s.isupper() and s.isalpha(): return "fx"
    return "stock"

def swaps(s, px):
    k = s if s in E.index else ("BTCUSD" if cls(s) == "crypto" else None)
    if k is None: return 0.0, 0.0
    e = E.loc[k]
    if e.swap_mode == 1: return e.swap_long * e.point / px * 365, e.swap_short * e.point / px * 365
    return e.swap_long / 100, e.swap_short / 100

def pnl(pos, r, tc, sl, ss, days):
    """pos decided at close t, earns r[t+1]; cost on change; swap per calendar day held."""
    p = pos.shift(1).fillna(0)
    return p * r - (p - p.shift(1).fillna(0)).abs() * tc + np.where(p > 0, p * sl, -p * ss) * days / 365

def hold_state(enter_long, enter_short, exit_long, exit_short):
    el, es, xl, xs = (np.asarray(a, bool) for a in (enter_long, enter_short, exit_long, exit_short)); out = np.zeros(len(el)); q = 0
    for i in range(len(el)):
        if q == 0: q = 1 if el[i] else (-1 if es[i] else 0)
        elif q > 0 and (xl[i] or es[i]): q = -1 if es[i] else 0
        elif q < 0 and (xs[i] or el[i]): q = 1 if el[i] else 0
        out[i] = q
    return out

def hold_n(sig, n):
    s = np.asarray(sig, float); out = np.zeros(len(s)); left = 0; q = 0
    for i in range(len(s)):
        if left > 0: left -= 1
        else: q = 0
        if left == 0 and s[i] != 0: q, left = s[i], n
        out[i] = q
    return out

def rsi(c, n=2):
    d = c.diff(); u = d.clip(lower=0).ewm(alpha=1 / n).mean(); v = (-d.clip(upper=0)).ewm(alpha=1 / n).mean()
    return 100 - 100 / (1 + u / v.replace(0, np.nan))

def rules(c, r):
    """returns dict name -> position series (decided at close)."""
    P, ix = {}, c.index
    for L in (20, 60, 120, 250): P[f"tsmom{L}"] = np.sign(c / c.shift(L) - 1)
    for a, b in ((10, 50), (50, 200)): P[f"ma{a}_{b}"] = np.sign(c.rolling(a).mean() - c.rolling(b).mean())
    for n, x in ((20, 10), (100, 50)):
        P[f"donch{n}"] = pd.Series(hold_state(c >= c.rolling(n).max(), c <= c.rolling(n).min(), c <= c.rolling(x).min(), c >= c.rolling(x).max()), ix)
    for L in (1, 3, 5): P[f"rev{L}"] = -np.sign(c / c.shift(L) - 1)
    R = rsi(c)
    P["rsi2"] = pd.Series(hold_state(R < 10, R > 90, R > 50, R < 50), ix)
    z = (c - c.rolling(20).mean()) / c.rolling(20).std()
    P["boll"] = pd.Series(hold_state(z < -2, z > 2, z > 0, z < 0), ix)
    P["rsi2_lo"] = pd.Series(hold_state(R < 10, np.zeros(len(c)), c > c.rolling(5).mean(), np.zeros(len(c))), ix)
    # seasonality: pfr = position for the return of that day; pos_t = pfr_{t+1}
    dow = pd.Series(ix.dayofweek, ix)
    m = r.groupby(dow).transform(lambda x: x.rolling(150, min_periods=100).mean().shift(1)); P["dow"] = np.sign(m).shift(-1)
    ym = pd.Series(ix.to_period("M"), ix); first = ym != ym.shift(1); last = ym != ym.shift(-1)
    k = first.astype(int).groupby(ym).cumsum(); kk = pd.Series(1, ix).groupby(ym).cumsum()
    tom = last | (kk <= 3); P["tom"] = tom.astype(float).shift(-1)
    mm = r.groupby([ix.year, ix.month]).mean(); mon = {}
    for (y, mo) in mm.index:
        prev = [mm.get((y - j, mo)) for j in range(1, 6)]
        mon[(y, mo)] = np.sign(np.mean(prev)) if all(v is not None and np.isfinite(v) for v in prev) else 0
    P["moy"] = pd.Series([mon.get((d.year, d.month), 0) for d in ix], ix).shift(-1)
    hi5, lo5 = c.shift(1).rolling(5).max(), c.shift(1).rolling(5).min()
    P["brk5_1d"] = pd.Series(np.where(c > hi5, 1, np.where(c < lo5, -1, 0)), ix).astype(float)
    hi20, lo20 = c.shift(1).rolling(20).max(), c.shift(1).rolling(20).min()
    P["brk20_5d"] = pd.Series(hold_n(np.where(c > hi20, 1, np.where(c < lo20, -1, 0)), 5), ix)
    v20 = r.rolling(20).std(); P["tsmom60_lowvol"] = P["tsmom60"] * (v20 < v20.rolling(250).median())
    return {k: v.fillna(0).astype(float) for k, v in P.items()}

def hour_season(h, tc, sl, ss):
    R = h.close.pct_change().fillna(0); hr = pd.Series(h.index.hour, h.index)
    m = R.groupby(hr).transform(lambda x: x.rolling(60, min_periods=40).mean().shift(1)); p = np.sign(m).fillna(0)
    days = h.index.to_series().diff().dt.total_seconds().fillna(0) / 86400
    sw = np.where(h.index.hour == 0, np.where(p > 0, p * sl, -p * ss) * days.clip(lower=1) / 365, 0)
    x = p * R - (p - p.shift(1).fillna(0)).abs() * tc + sw
    return x.groupby(x.index.normalize()).sum()

def stats(x, a, b):
    x = x[a:b]; x = x.loc[x.ne(0).idxmax():] if x.ne(0).any() else x
    if len(x) < 250 or x.std() == 0: return None
    yrs = (x.index[-1] - x.index[0]).days / 365.25; npy = len(x) / yrs
    sh = x.mean() / x.std() * np.sqrt(npy); y = x.groupby(x.index.year).agg(["sum", "count"]); y = y[y["count"] >= 100]
    eq = (1 + x).cumprod()
    return dict(sh=sh, t=sh * np.sqrt(yrs), yrs=yrs, pos=(y["sum"] > 0).mean() if len(y) else 0, ny=len(y), npos=int((y["sum"] > 0).sum()),
                mdd=(eq / eq.cummax() - 1).min(), ann=x.mean() * npy)

def build():
    syms = [s for s in E.index] + ["XRPUSD", "SOLUSD"]
    S, CL, RET, TC, SW = {}, {}, {}, {}, {}
    for s in syms:
        h = loadh(s)
        if h is None: print("no data", s); continue
        tc = tcost(s.lstrip("."), h) if s.startswith(".") else tcost(s, h)
        c = h.close.resample("1D").last().dropna(); r = c.pct_change().fillna(0)
        days = c.index.to_series().diff().dt.days.fillna(1).values
        sl, ss = swaps(s, float(c.iloc[-1])); CL[s] = c; RET[s] = r; TC[s] = tc; SW[s] = (sl, ss)
        for k, p in rules(c, r).items(): S[(s, k)] = scale(pnl(p, r, tc, sl, ss, days))
        S[(s, "hour")] = scale(hour_season(h, tc, sl, ss))
    rl = sorted({k for _, k in S})
    for g in sorted({cls(s) for s in CL}):
        mem = [s for s in CL if cls(s) == g]
        for k in rl:
            parts = [S[(s, k)] for s in mem if (s, k) in S]
            if len(parts) >= 2: S[(f"BASKET_{g}", k)] = scale(pd.concat(parts, axis=1).fillna(0).mean(1))
    def xs(mem, look, skip, every, n, rev):
        C = pd.concat({s: CL[s] for s in mem}, axis=1).ffill(); Rt = pd.concat({s: RET[s] for s in mem}, axis=1).fillna(0)
        sc = (C.shift(skip) / C.shift(look) - 1) * (-1 if rev else 1)
        reb = np.arange(len(C)) % every == 0 if every != "M" else (C.index.to_period("M") != C.index.to_period("M").shift(1) if False else pd.Series(C.index.month, C.index).diff().ne(0).values)
        W = pd.DataFrame(0.0, C.index, C.columns); cur = pd.Series(0.0, C.columns)
        for i, d in enumerate(C.index):
            if reb[i] and sc.iloc[i].notna().sum() >= 2 * n:
                rk = sc.iloc[i].rank(); m = sc.iloc[i].notna().sum(); cur = pd.Series(0.0, C.columns)
                cur[rk > m - n] = 1 / n; cur[rk <= n] = -1 / n
            W.iloc[i] = cur
        Wp = W.shift(1).fillna(0); days = pd.Series(C.index, C.index).diff().dt.days.fillna(1)
        sw = sum(np.where(Wp[s] > 0, Wp[s] * SW[s][0], -Wp[s] * SW[s][1]) for s in mem) * days / 365
        cost = sum((Wp[s] - Wp[s].shift(1).fillna(0)).abs() * TC[s] for s in mem)
        return scale((Wp * Rt).sum(1) - cost + sw)
    fx = [s for s in CL if cls(s) == "fx"]; st = [s for s in CL if cls(s) == "stock"]
    S[("XS_fx", "mom60")] = xs(fx, 60, 0, 5, 5, False); S[("XS_fx", "rev5")] = xs(fx, 5, 0, 5, 5, True)
    S[("XS_stock", "mom12_1")] = xs(st, 250, 20, "M", 10, False); S[("XS_stock", "rev5")] = xs(st, 5, 0, 5, 10, True)
    return S

if __name__ == "__main__":
    S = build()
    C1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change()
    from book_tester import i2_daily
    I2 = i2_daily()
    if MODE == "dev":
        rows = []
        for (s, k), x in S.items():
            st = stats(x, "2000", DEV_END)
            if st is None: continue
            j = pd.concat([x[:DEV_END], C1, I2], axis=1).dropna(); j = j[j.iloc[:, 0] != 0]
            cc = j.corr().iloc[0, 1:].abs().max() if len(j) > 100 else np.nan
            rows.append(dict(sym=s, rule=k, cls=cls(s) if not s.startswith(("BASKET", "XS")) else s, **st, cc=cc))
        D = pd.DataFrame(rows); D.to_csv(f"{OUT}/r64_dev.csv", index=False)
        ok = D[(D.t >= 2.5) & (D.pos >= 0.6) & (D.ny >= 3) & ~(D.cc > 0.3)]
        print(f"trials {len(D)}  t>=2.5: {(D.t >= 2.5).sum()}  t<=-2.5: {(D.t <= -2.5).sum()}  survivors {len(ok)}  (null expectation ~{0.0062 * len(D):.0f} per tail)")
        print(D.groupby("rule").t.median().round(2).sort_values().to_string())
        print(ok.sort_values("t", ascending=False).round(2).to_string(index=False))
        ok.to_csv(f"{OUT}/r64_survivors.csv", index=False)
    else:
        ok = pd.read_csv(f"{OUT}/r64_survivors.csv"); res = []
        for _, o in ok.iterrows():
            x = S[(o.sym, o.rule)]; st = stats(x, HO, "2030")
            res.append(dict(sym=o.sym, rule=o.rule, dev_sh=o.sh, ho_sh=st["sh"], ho_pos=f"{st['npos']}/{st['ny']}", ho_mdd=st["mdd"],
                            ok=st["sh"] >= 0.5 and st["npos"] >= 3))
        R = pd.DataFrame(res); print(R.round(2).to_string(index=False)); R.to_csv(f"{OUT}/r64_holdout.csv", index=False)
        from scipy.stats import binom
        k, n = int(R.ok.sum()), len(R); print(f"holdout passes {k}/{n}; P(>= {k} | p=0.15 null) = {binom.sf(k - 1, n, 0.15):.3f}")
