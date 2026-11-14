"""Stages 2-3 of docs/THIRD_COMPONENT_PLAN.md: correlation of a candidate with the C1+Nasdaq portfolio (2020-10.2026) and the
portfolio gain at equal max drawdown. Base = portfolio_x15.py's x1.5 portfolio (C1 ECN AssetVol 0.15 + IndexNoise TargetVol 0.15,
half each, daily rebalance). Candidate daily returns from data/derived/third/<name>_daily.csv (unlevered).
Method (pre-registered): scale the candidate to the base portfolio's volatility, try weights w in 0..0.5 for it (1-w for the base),
then lever the mix so its MDD equals the base MDD; report CAGR. Gain = best CAGR - base CAGR.
Usage: python research/third/port3.py rsi2"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/stable"); sys.path.insert(0, "research/btc")
from portfolio_x15 import i2_daily

def mdd(x): eq = (1 + x).cumprod(); return (eq / eq.cummax() - 1).min()
def cagr(x): eq = (1 + x).cumprod(); return eq.iloc[-1] ** (365.25 / (x.index[-1] - x.index[0]).days) - 1

def lever_to(x, target):
    lo, hi = 0.05, 10.0
    for _ in range(60):
        k = (lo + hi) / 2
        if mdd(k * x) < target: hi = k
        else: lo = k
    return lo

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "rsi2"
    c = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change().dropna()
    c.index = c.index.normalize(); c = c.groupby(c.index).apply(lambda z: (1 + z).prod() - 1)
    i2 = i2_daily("in2_tv15"); i2.index = i2.index.normalize(); i2 = i2.groupby(i2.index).sum()
    base = (0.5 * c + 0.5 * i2.reindex(c.index).fillna(0)).loc["2020":"2026-10-30"]
    cand = pd.read_csv(f"data/derived/third/{name}_daily.csv", index_col=0, parse_dates=True).ret
    cand = cand.reindex(base.index).fillna(0)
    bus = base.index.dayofweek < 5
    print(f"corr daily (weekdays) {np.corrcoef(base[bus], cand[bus])[0, 1]:+.3f} | weekly {base.resample('W').sum().corr(cand.resample('W').sum()):+.3f}")
    print(f"base: CAGR {cagr(base) * 100:.1f}% MDD {mdd(base) * 100:.1f}% | cand unlevered: CAGR {cagr(cand) * 100:.1f}% MDD {mdd(cand) * 100:.1f}%")
    cs = cand * base.std() / cand.std()
    tgt = mdd(base)
    for w in (0, 0.1, 0.2, 0.3, 0.4, 0.5):
        mix = (1 - w) * base + w * cs; k = lever_to(mix, tgt); m = k * mix
        y = m.groupby(m.index.year).apply(lambda z: (1 + z).prod() - 1) * 100
        print(f"w {w:.1f} lever x{k:.2f} CAGR {cagr(m) * 100:5.1f}% MDD {mdd(m) * 100:5.1f}% |", " ".join(f"{int(a) % 100:02d}:{v:+.0f}" for a, v in y.items()))
