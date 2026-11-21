"""BD crash-balancer groundwork (t271, 15.11.2026): daily realized P&L of the BD candidate ms20_h1119 (RoboForex, 120K per year,
2019-2025, tester reports ev12_*) and the gold move on its worst days. Descriptive only - no rule is chosen here.
Writes data/derived/bd/ms20_h1119_daily.csv. Usage: py -3.12 research/bd1/bd_daily_worst.py"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); sys.path.insert(0, "research/stable"); sys.path.insert(0, "research/scan")
from guardian_sim import deals
from r64_mass import loadh
out = []
for y in range(2019, 2026):
    x = deals(f"C:/MT5_JEV_TEST/ev12_rf{y}_ms20_h1119.htm")
    x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize()
    pnl = (x.profit + x.swap + x.commission).groupby(x.day).sum()
    eq = 120000 + pnl.cumsum(); out.append(pnl / eq.shift(1).fillna(120000))
r = pd.concat(out).rename("bd"); os.makedirs("data/derived/bd", exist_ok=True); r.to_csv("data/derived/bd/ms20_h1119_daily.csv")
h = loadh("XAUUSD"); d = h.close.resample("1D").last().dropna(); o = h.open.resample("1D").first().dropna()
g = pd.DataFrame({"bd": r, "gold_ret": d.pct_change(), "gold_oc": d / o - 1}).dropna()
rng = (h.high.resample("1D").max() / h.low.resample("1D").min() - 1).reindex(g.index); g["gold_rng"] = rng
q = g.bd.quantile(0.05); worst = g[g.bd <= q].sort_values("bd")
print(f"days {len(g)}  BD worst-5% threshold {q*100:.2f}%  worst-5% sum {worst.bd.sum()*100:.0f}% of equity  (all days sum {g.bd.sum()*100:.0f}%)")
print("worst 15 days:"); print((worst.head(15) * 100).round(2).to_string())
print(f"on worst-5% days: |gold close-to-close| median {worst.gold_ret.abs().median()*100:.2f}% vs all days {g.gold_ret.abs().median()*100:.2f}%;"
      f" gold range median {worst.gold_rng.median()*100:.2f}% vs {g.gold_rng.median()*100:.2f}%; gold up on {int((worst.gold_ret>0).sum())}/{len(worst)}")
print(f"corr(BD, |gold ret|) all days {g.bd.corr(g.gold_ret.abs()):.2f};  corr(BD, gold ret) {g.bd.corr(g.gold_ret):.2f}")
