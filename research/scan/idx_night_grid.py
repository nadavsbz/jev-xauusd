"""Scan round 8b of docs/SCAN_PLAN.md (pre-registered 11.11.2026 evening): a fixed 3x3 grid of 'night' windows on the
US index basket (USTECH, US500, US30). Entry at the open of bar {03, 08, 10}, exit at the close of bar {15, 16, 17}, all
one hour earlier in DST-mismatch weeks. Bar is Sharpe >= 1.0 in dev; only the best window that passes runs on test, once.
Usage: python research/scan/idx_night_grid.py dev  |  python research/scan/idx_night_grid.py test A B"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, rep
from idx_night import window
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"

def basket(H, a, b):
    return scale(pd.DataFrame({s: scale(window(h, tc, a, b)) for s, (h, tc) in H.items()}).fillna(0).mean(axis=1))

if __name__ == "__main__":
    span = ("2000", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
    H = {s: (load(s), None) for s in ("USTECHCash", "US500Cash", "US30Cash")}
    H = {s: (h, tcost(s, h)) for s, (h, _) in H.items()}
    i2 = pd.read_csv("data/derived/scan/R2_P1_daily.csv", index_col=0, parse_dates=True).iloc[:, 0]
    grid = [(a, b) for a in (3, 8, 10) for b in (15, 16, 17)] if PER == "dev" else [(int(sys.argv[2]), int(sys.argv[3]))]
    print(f"===== round 8b night-window grid {PER} {span}")
    for a, b in grid:
        x = basket(H, a, b); x.to_csv(f"data/derived/scan/R8b_{a:02d}_{b:02d}_daily.csv", header=["ret"])
        rep(x.loc[span[0]:span[1]], f"win {a:02d}-{b:02d}")
        j = pd.concat([x, i2], axis=1).loc[span[0]:span[1]].dropna(); print(f"      corr with I2 {j.corr().iloc[0, 1]:.2f}")
