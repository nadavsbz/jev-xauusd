"""Round 102 (prereg docs/prereg/r102_ibs_etf.md): IBS<0.2 long / IBS>0.8 short, close->next close, 13 index/sector ETFs.
Usage: py -3.12 research/scan/r102_ibs.py dev|hold"""
import sys, json, contextlib, io
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan"); sys.path.insert(0, "research/btc"); sys.path.insert(0, "research/stable")
from scan import scale
PART = sys.argv[1]; TC = 0.0002
IDX, SEC = "SPY QQQ IWM DIA".split(), "XLB XLE XLF XLI XLK XLP XLU XLV XLY".split()

def load(s):
    r = json.load(open(f"data/raw/etf/{s}.json"))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    d = pd.DataFrame({"o": q["open"], "h": q["high"], "l": q["low"], "c": q["close"], "a": r["indicators"]["adjclose"][0]["adjclose"]},
                     index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
    return d[~d.index.duplicated()]
def one(s, side="both"):
    d = load(s); rng = d.h - d.l
    ibs = ((d.c - d.l) / rng).where(rng > 0)
    sig = pd.Series(np.where(ibs < 0.2, 1, np.where(ibs > 0.8, -1, 0)), d.index)
    if side == "long": sig = sig.clip(lower=0)
    if side == "short": sig = sig.clip(upper=0)
    r = d.a.pct_change().fillna(0)
    sz = (0.10 / (r.rolling(60).std().shift(1) * np.sqrt(252))).clip(upper=3).fillna(0)
    w = (sig * sz).shift(1).fillna(0)                                 # decided at close t, earns close t -> close t+1
    net = w * r - w.diff().abs().fillna(0) * TC
    ro = (d.c / d.o - 1)                                              # robustness: same signal, enter next open, exit that close
    op = (sig.shift(1).fillna(0) * ro)
    return net, w.diff().abs().fillna(0) * TC, op, (sig.shift(1).fillna(0) != 0)
def basket(names, side="both"):
    parts = [one(s, side) for s in names]
    N = pd.concat({s: p[0] for s, p in zip(names, parts)}, axis=1)
    C = pd.concat({s: p[1] for s, p in zip(names, parts)}, axis=1)
    O = pd.concat({s: p[2] for s, p in zip(names, parts)}, axis=1)
    A = pd.concat({s: p[3] for s, p in zip(names, parts)}, axis=1)
    return N.mean(1).fillna(0), C.mean(1).fillna(0), O.where(A).stack().mean()
def st(r):
    r = r[r.index.dayofweek < 5]; eq = (1 + r).cumprod()
    return r.mean() / r.std() * np.sqrt(252), (eq / eq.cummax() - 1).min() * 100, {y: round(g.sum() * 100, 1) for y, g in r.groupby(r.index.year)}

a, b = ("2006", "2018") if PART == "dev" else ("2019", "2026")
ALL = IDX + SEC
n, c, _ = basket(ALL); F = scale(n)[a:b]
k = (scale(n) / n.replace(0, np.nan)).fillna(0)                      # same scaling applied to the cost, for net/cost
nc = (n[a:b] * k[a:b]).sum() / (c[a:b] * k[a:b]).sum()
sh, mdd, yrs = st(F); pos = np.mean([v > 0 for v in yrs.values()])
# robustness on the period only
parts = [one(s) for s in ALL]
O = pd.concat({s: p[2] for s, p in zip(ALL, parts)}, axis=1)[a:b]; A = pd.concat({s: p[3] for s, p in zip(ALL, parts)}, axis=1)[a:b]
opn = O.where(A).stack().mean()
print(f"{PART} {a}-{b}: BASKET Sh {sh:.2f} MDD {mdd:.1f}% pos years {pos:.0%} net/cost {nc:.2f} | next-open robustness gross/trade {opn * 1e4:.1f}bp")
print("  ", yrs)
for nm, names, side in (("indices", IDX, "both"), ("sectors", SEC, "both"), ("long-only", ALL, "long"), ("short-only", ALL, "short")):
    s_, m_, _ = st(scale(basket(names, side)[0])[a:b]); print(f"  [desc] {nm:10s} Sh {s_:.2f} MDD {m_:.1f}")
if PART == "dev":
    ok = sh >= 0.8 and pos >= 0.6 and nc >= 2 and opn > 0
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
    cc, ci = J.F.corr(J.C1), J.F.corr(J.I2); s3, m3, _ = st(J.mean(1)); s2, m2, _ = st(J[["C1", "I2"]].mean(1))
    print(f"  corr F-C1 {cc:.2f}  F-I2 {ci:.2f} | [desc] C1+I2 Sh {s2:.2f} MDD {m2:.1f} -> C1+I2+F Sh {s3:.2f} MDD {m3:.1f}")
    ok = sh >= 0.5 and mdd >= -20 and cc <= 0.3 and ci <= 0.3
print("  ->", "PASS" if ok else "FAIL")
