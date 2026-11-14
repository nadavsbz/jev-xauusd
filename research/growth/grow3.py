"""Growth search round 3 (pre-registered 3.11.2026 in docs/GROWTH_SEARCH_PLAN.md), same bar as rounds 1-2. Server = NY + 7.
  H1  .USTECHCash M30: at the 22:30 close take the sign of (17:00 close / yesterday's 23:00 close - 1), out at the 23:00 close
  H2  as H1 only when the 22:00->22:30 half hour has the same sign
  W1  BTCUSD H1: Monday 02:00 server, sign of the prior 24h return, held 24h; 0.025% per change + one night of 4.75%/yr swap
Usage: python research/growth/grow3.py [hold]"""
import sys
import numpy as np, pandas as pd
HOLD = len(sys.argv) > 1 and sys.argv[1] == "hold"
sys.argv = sys.argv[:1]; sys.path.insert(0, "research/stable"); sys.path.insert(0, "research/growth")
import second4 as S4
import noise_more as N
S2 = S4.S2

def halfhour(agree):
    h = pd.read_csv("data/derived/intraday/.USTECHCash_M30.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
    m = h.index.hour * 60 + h.index.minute + 30; d = h.index.normalize()
    piv = pd.DataFrame({"c": h.close, "d": d, "k": m}).pivot_table(index="d", columns="k", values="c")
    need = [17 * 60, 22 * 60, 22 * 60 + 30, 23 * 60]; piv = piv[need].dropna()
    first = piv[17 * 60] / piv[23 * 60].shift(1) - 1; pen = piv[22 * 60 + 30] / piv[22 * 60] - 1
    sgn = np.sign(first)
    if agree: sgn = sgn.where(np.sign(pen) == sgn, 0)
    last = piv[23 * 60] / piv[22 * 60 + 30] - 1
    return (sgn * last - sgn.abs() * 2 * 0.00015).dropna()

def monday():
    h = N.bars("BTCUSD"); c = h.close
    out = {}
    for t in h.index[(h.index.weekday == 0) & (h.index.hour == 2)]:
        try: p0, pm, p1 = c[t - pd.Timedelta(hours=24)], c[t - pd.Timedelta(hours=1)], c[t + pd.Timedelta(hours=23)]
        except KeyError: continue
        s = np.sign(pm / p0 - 1)                       # entered at the open of the 02:00 bar = close of 01:00
        out[t.normalize()] = s * (p1 / pm - 1) - abs(s) * (2 * 0.00025 + 0.0475 / 365)
    return pd.Series(out)

COMP = {"H1": lambda: halfhour(False), "H2": lambda: halfhour(True), "W1": monday}

if __name__ == "__main__":
    base = S4.C["C1"] + S4.C["I2"]; idx = base.index; sh = N.sharpe
    a, b = ("2025-10-25", "2026-10-30") if HOLD else ("2018", "2025-10-24")
    print(f"--- {'HOLDOUT' if HOLD else 'EXPLORATION'} {a}..{b}"); S2.rep(base, "C1+I2", a, b)
    for nm, f in COMP.items():
        x = S4.scale_s(f()).reindex(idx).fillna(0); xs = x.loc[a:b]
        y = xs.groupby(xs.index.year).apply(lambda z: (1 + z).prod() - 1); lift = sh((base + 0.5 * x).loc[a:b]) - sh(base.loc[a:b])
        S2.rep(x, nm, a, b)
        print(f"     corr C1 {S4.C['C1'].loc[a:b].corr(xs):+.2f} I2 {S4.C['I2'].loc[a:b].corr(xs):+.2f} | lift {lift:+.2f} | "
              f"pass: Sh {sh(xs) >= 0.5} years {(y > 0).mean() >= 0.6} lift {lift >= 0.1}")
