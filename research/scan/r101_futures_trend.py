"""Round 101 (prereg docs/prereg/r101_futures_trend.md): the C1 rule on 18 futures proxies (ETF adjclose minus T-bill), daily, no swap.
Usage: py -3.12 research/scan/r101_futures_trend.py dev|hold"""
import sys, json, contextlib, io
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/btc"); sys.path.insert(0, "research/stable")
from scan import scale
PART = sys.argv[1]
GROUPS = {"eq": "SPY QQQ IWM DIA", "rates": "IEF TLT IEI", "metals": "GLD SLV CPER", "energy": "USO UNG", "fx": "FXE FXY FXB FXA", "ags": "CORN SOYB"}
TC = 0.0002

def comps(c, long_only):                       # identical to r94 (C1)
    out = []; cv = c.values
    for n in (10, 20, 30, 60, 90, 150, 250):
        hv, lv = c.rolling(n).max().values, c.rolling(n).min().values
        k = n // 2; xl, xh = c.rolling(k).min().values, c.rolling(k).max().values
        p = np.zeros(len(c))
        for i in range(1, len(c)):
            q = p[i - 1]
            if q == 0: q = 1 if cv[i] >= hv[i] else (-1 if (not long_only and cv[i] <= lv[i]) else 0)
            elif (q > 0 and cv[i] <= xl[i]) or (q < 0 and cv[i] >= xh[i]): q = 0
            p[i] = q
        out.append(p)
    return np.array(out)

tb = pd.read_csv("data/raw/fred/DTB3.csv"); tb.index = pd.to_datetime(tb.iloc[:, 0]); tb = pd.to_numeric(tb.iloc[:, 1], errors="coerce").ffill() / 100
def load(s):
    r = json.load(open(f"data/raw/etf/{s}.json"))["chart"]["result"][0]
    c = pd.Series(r["indicators"]["adjclose"][0]["adjclose"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
    c = c[~c.index.duplicated()]
    ex = c.pct_change() - tb.reindex(c.index).ffill().fillna(0) / 252           # excess (futures-like) daily return
    return (1 + ex.fillna(0)).cumprod()
def market(s, which="both"):
    c = load(s); r = c.pct_change().fillna(0)
    P = comps(c, True) if which == "lo" else (comps(c, False) if which == "ls" else np.vstack([comps(c, True), comps(c, False)]))
    vol = r.rolling(60).std().shift(0) * np.sqrt(252)
    sz = (0.10 / vol).clip(upper=3).fillna(0)
    w = (pd.Series(P.mean(0), index=c.index) * sz).shift(2).fillna(0)
    return w * r - w.diff().abs().fillna(0) * TC
def basket(names, which="both"):
    R = pd.concat({s: market(s, which) for s in names}, axis=1)
    live = R.notna() & (R.index.to_series().values[:, None] >= R.apply(lambda x: x.first_valid_index()).values + pd.Timedelta(days=400))  # 250d warm-up + vol
    return R.where(live).mean(1).fillna(0)
def st(r):
    r = r[r.index.dayofweek < 5]; eq = (1 + r).cumprod()
    return r.mean() / r.std() * np.sqrt(252), (eq / eq.cummax() - 1).min() * 100, {y: round(g.sum() * 100, 1) for y, g in r.groupby(r.index.year)}

ALL = " ".join(GROUPS.values()).split()
a, b = ("2007", "2018") if PART == "dev" else ("2019", "2026")
F = scale(basket(ALL))[a:b]
sh, mdd, yrs = st(F); pos = np.mean([v > 0 for v in yrs.values()])
print(f"{PART} {a}-{b}: BASKET Sh {sh:.2f} MDD {mdd:.1f}% positive years {pos:.0%}\n  {yrs}")
for g, n in GROUPS.items():
    s_, m_, _ = st(scale(basket(n.split()))[a:b]); print(f"  [desc] {g:7s} Sh {s_:.2f} MDD {m_:.1f}")
for w in ("lo", "ls"):
    s_, m_, _ = st(scale(basket(ALL, w))[a:b]); print(f"  [desc] {'long-only' if w == 'lo' else 'long-short'} Sh {s_:.2f} MDD {m_:.1f}")
if PART == "dev":
    ok = sh >= 0.7 and pos >= 0.6 and mdd >= -20
else:
    with contextlib.redirect_stdout(io.StringIO()):
        sys.argv = ["x", "hold"]; import r94_c1_stablecoin as c1m
        C1 = c1m.run(False)
        from x2_check import deals
    rows = []
    for y in range(2019, 2027):
        x = deals(f"C:/MT5_JEV_TEST/in2dst_t_{y}.htm"); x = x[x.symbol == ".USTECHCash"]
        p = (x.profit + x.swap + x.commission).groupby(pd.to_datetime(x.t, unit="s").dt.normalize()).sum()
        rows.append(p / (120000 + p.cumsum()).shift(1).fillna(120000))
    I2 = scale(pd.concat(rows))
    J = pd.concat({"F": F, "C1": C1[a:b], "I2": I2[a:b]}, axis=1).fillna(0); J = J[J.index.dayofweek < 5]
    cc, ci = J.F.corr(J.C1), J.F.corr(J.I2)
    s3, m3, _ = st(J.mean(1)); s2, m2, _ = st(J[["C1", "I2"]].mean(1))
    print(f"  corr F-C1 {cc:.2f}  F-I2 {ci:.2f} | [desc] C1+I2 Sh {s2:.2f} MDD {m2:.1f} -> C1+I2+F Sh {s3:.2f} MDD {m3:.1f}")
    ok = sh >= 0.5 and mdd >= -20 and cc <= 0.3 and ci <= 0.3
print("  ->", "PASS" if ok else "FAIL")
