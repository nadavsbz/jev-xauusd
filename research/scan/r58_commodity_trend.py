"""Round 58 (docs/prereg/r58_commodity_trend.md, 49b6135): C1 trend rule on XAU/XAG/WTI/BRENT basket.
Usage: py -3.12 research/scan/r58_commodity_trend.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import scale, rep, trend, tcost, load, E
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
A, B = ("2015-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2026-10-30")
SW = {"XAUUSD": (-5.5, 1.7), "XAGUSD": (-9.4, 1.2), "WTI": (-6, -3), "BRENT": (-6, -3)}
X = {}
for s, (l, sh) in SW.items():
    h = pd.read_csv(f"data/derived/intraday/{s}_H1.csv"); h.index = pd.to_datetime(h.time, unit="s"); h = h[~h.index.duplicated()].query("close > 0 and open > 0")
    X[s] = scale(trend(h, tcost(s, h), l, sh)); rep(X[s].loc[A:B], s)
b = scale(pd.DataFrame(X).loc["2015":].fillna(0).mean(1)); b.to_csv("data/derived/scan/r58_basket_daily.csv", header=["ret"])
print(f"===== BASKET {PER}"); y = b.loc[A:B]; rep(y, "basket")
top = y.nlargest(10).sum() / y.sum() if y.sum() > 0 else np.nan
c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
j = pd.concat([y, c1, i2], axis=1, keys=["X", "C1", "I2"]).loc[A:B].dropna(subset=["X"]).fillna(0)
print(f"top10 days share {top*100:.0f}% | corr", j.corr().round(2).loc["X"].to_dict())
