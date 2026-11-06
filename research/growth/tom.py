"""T1 turn of the month on the Nasdaq (pre-registered 3.11.2026 in docs/GROWTH_SEARCH_PLAN.md): long .USTECHCash from the close
(bar 22 server) of the day before the month's last trading day to the close of the new month's 3rd trading day. Costs: 0.015% in
and out, swap 8.6%/yr per calendar day held. 10% vol as I2. Usage: python research/growth/tom.py [hold]"""
import sys
import numpy as np, pandas as pd
HOLD = len(sys.argv) > 1 and sys.argv[1] == "hold"
sys.argv = sys.argv[:1]; sys.path.insert(0, "research/stable")
import second4 as S4
S2 = S4.S2

h = pd.read_csv("data/derived/intraday/.USTECHCash_H1.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()]
c = h.close[h.index.hour == 22]; c.index = c.index.normalize()
ym = c.index.to_period("M"); pos = pd.Series(0, index=c.index)
for m, g in c.groupby(ym):
    d = g.index
    if len(d) >= 2: pos[d[-2]] = 1                 # entered at this close (day before the last day)
    pos[d[-1]] = 1
    pos[d[:2]] = 1                                  # held into days 1..3: exposure decided at closes of last-1, last, day1, day2
ret = c.pct_change().fillna(0); held = pos.shift(1).fillna(0)
days = pd.Series(c.index, index=c.index).diff().dt.days.fillna(1)
r = held * ret - held * days * 0.086 / 365 - pos.diff().abs().fillna(0) * 0.00015
x = S4.scale_s(r).reindex(S4.C["C1"].index).fillna(0)

if __name__ == "__main__":
    a, b = ("2025-10-25", "2026-10-30") if HOLD else ("2018", "2025-10-24")
    base = S4.C["C1"] + S4.C["I2"]; sb = base.loc[a:b]; sh = lambda z: z.mean() / z.std() * np.sqrt(365)
    S2.rep(base, "C1+I2", a, b); S2.rep(x, "T1", a, b); S2.rep(base + 0.5 * x, "C1+I2+0.5T1", a, b)
    print(f"raw T1 mean per window {r[r != 0].groupby(r[r != 0].index.to_period('M')).sum().mean() * 100:+.2f}% | "
          f"lift {sh((base + 0.5 * x).loc[a:b]) - sh(sb):+.2f} | corr C1 {x.loc[a:b].corr(S4.C['C1'].loc[a:b]):+.2f} I2 {x.loc[a:b].corr(S4.C['I2'].loc[a:b]):+.2f}")
