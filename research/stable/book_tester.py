"""Grok's C1+I2 book (grok_inbox 11.11 19:45: risk-parity weights from train vol, L = smallest leverage reaching 5%/month CAGR in
train, optional half-L layer while the book is >12% below its peak) rebuilt on OUR tester daily returns instead of the sim:
C1 = c1_ecn_av15_full (ECN, AssetVol 0.15, continuous), I2 = in2dst_t_YYYY (ECN real ticks, DstFix, TargetVol 0.15, one run a year).
Train 2020-2023 (C1 tester starts 2020), holdout 2024-01-01..2026-10-30. Same procedure, our numbers.
Usage: python research/stable/book_tester.py"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals

def i2_daily():
    out = []
    for y in range(2018, 2027):
        x = deals(f"C:/MT5_JEV_TEST/in2dst_t_{y}.htm"); x = x[x.symbol == ".USTECHCash"]
        x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize()
        pnl = (x.profit + x.swap + x.commission).groupby(x.day).sum()
        eq = 120000 + pnl.cumsum(); out.append(pnl / eq.shift(1).fillna(120000))
    return pd.concat(out)

def stats(x):
    eq = (1 + x).cumprod(); yrs = (x.index[-1] - x.index[0]).days / 365.25
    return (eq.iloc[-1] ** (1 / yrs) - 1), (eq / eq.cummax() - 1).min(), x.mean() / x.std() * np.sqrt(365)

def layer(u, L, X=0.12):
    eq, pk, out = 1.0, 1.0, []
    for r in u:
        lev = L / 2 if eq / pk - 1 < -X else L
        eq *= 1 + lev * r; pk = max(pk, eq); out.append(lev * r)
    return pd.Series(out, index=u.index)

def show(x, nm):
    c, d, s = stats(x); y = x.groupby(x.index.year).apply(lambda z: (1 + z).prod() - 1) * 100
    print(f"{nm:28s} CAGR {c * 100:6.1f}% ({((1 + c) ** (1 / 12) - 1) * 100:4.2f}%/mo) MDD {d * 100:6.1f}% Sh {s:4.2f} |",
          " ".join(f"{k % 100:02d}:{v:+.0f}" for k, v in y.items()))

if __name__ == "__main__":
    c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change().dropna()
    i2 = i2_daily().reindex(c1.index).fillna(0)
    tr, ho = slice("2020-01-01", "2023-12-31"), slice("2024-01-01", "2026-10-30")
    v1, v2 = c1[tr].std(), i2[tr].std(); w1 = (1 / v1) / (1 / v1 + 1 / v2); w2 = 1 - w1
    u = w1 * c1 + w2 * i2
    print(f"tester series: corr {c1.corr(i2):.2f}; RP weights C1 {w1:.4f} I2 {w2:.4f} (Grok: 0.3992 / 0.6008 on sim series)")
    target = 1.05 ** 12 - 1; L = None
    for l in np.arange(0.1, 10, 0.01):
        if stats(l * u[tr])[0] >= target: L = l; break
    print(f"L for 5%/month in train: {L:.2f} (Grok: 4.14 on the sim book)")
    show(u[tr], "unlevered train"); show(u[ho], "unlevered holdout")
    show(L * u[tr], f"L={L:.2f} train"); show(L * u[ho], f"L={L:.2f} holdout")
    show(layer(u[tr], L), "L + layer 12% train"); show(layer(u[ho], L), "L + layer 12% holdout")
    for l in (1.0, 1.5, 2.0):
        show(l * (0.5 * c1 + 0.5 * i2)["2020":"2026-10-30"], f"descr: 50/50 x{l} (x1 = live x1.5)")
