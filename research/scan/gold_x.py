"""Scan round 6 of docs/SCAN_PLAN.md (pre-registered 11.11.2026 evening): our two working rules moved to XAUUSD.
X1 = C1 trend ensemble on H6 (scan.trend) with gold swaps; X2 = I2 noise rule + DST fix (scan2.run, mode i2) at the NY open.
Usage: python research/scan/gold_x.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep, trend, E
from scan2 import run
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"
TC = 0.00005
NOTIONAL_PER_LOT = 100 * 3975.0
SW_L = -60 * 1.0 * 365 / NOTIONAL_PER_LOT * 100    # -60 points x $1 per point per lot, per night -> % per year
SW_S = +19 * 1.0 * 365 / NOTIONAL_PER_LOT * 100

if __name__ == "__main__":
    span = ("2015-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    h = pd.read_csv("data/derived/intraday/XAUUSD_H1.csv"); h.index = pd.to_datetime(h.time, unit="s")
    h = h[~h.index.duplicated()]; h = h[(h.close > 0) & (h.open > 0)]
    print(f"===== round 6 gold {PER} {span}  swap %/yr long {SW_L:.2f} short {SW_S:.2f}")
    x1 = scale(trend(h, TC, SW_L, SW_S)); x1.to_csv("data/derived/scan/R6_X1_daily.csv", header=["ret"])
    rep(x1.loc[span[0]:span[1]], "X1 gold trend")
    r2 = run(h, TC, "i2", True)
    x2 = scale(r2 if isinstance(r2, pd.Series) else r2[0]); x2.to_csv("data/derived/scan/R6_X2_daily.csv", header=["ret"])
    rep(x2.loc[span[0]:span[1]], "X2 gold noise")
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    c1 = sum(scale(trend(load(s), tcost(s, load(s)), E.loc[s, "swap_long"], E.loc[s, "swap_short"])) for s in ("BTCUSD", "ETHUSD"))
    j = pd.concat([x1, x2, i2, c1], axis=1, keys=["X1", "X2", "I2", "C1"]).loc[span[0]:span[1]]
    j = j[j.index.dayofweek < 5].dropna(subset=["X1", "X2"]).fillna(0)
    print("corr:\n", j.corr().round(2).loc[["X1", "X2"], ["I2", "C1", "X1", "X2"]])
