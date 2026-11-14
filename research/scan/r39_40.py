"""Scan rounds 39-40 of docs/SCAN_PLAN.md (pre-registered 12.11.2026): C1 Donchian ensemble (long-short) on the ratio A/B.
Usage: python research/scan/r39_40.py [dev|test]"""
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, "research/scan")
from scan import load, tcost, scale, donch, E
import r28_30
from r28_30 import corr_rep
warnings.filterwarnings("ignore")
PER = sys.argv[1] if len(sys.argv) > 1 else "dev"; r28_30.PER = PER
r28_30.SPAN = ("2018-01-01", "2022-12-31") if PER == "dev" else ("2023-01-01", "2030")
key = lambda s: s if s in E.index else "." + s

def pair(A, B, tag, name):
    ha, hb = load(A), load(B)
    c = pd.concat([ha.close.resample("6h").last(), hb.close.resample("6h").last()], axis=1, keys=["a", "b"]).dropna()
    w = donch(c.a / c.b, False).shift(2).fillna(0)
    ra, rb = c.a.pct_change().fillna(0), c.b.pct_change().fillna(0)
    dt = c.index.to_series().diff().dt.total_seconds().fillna(0) / 86400 / 365
    la, sa, lb, sb = (E.loc[key(A), "swap_long"], E.loc[key(A), "swap_short"], E.loc[key(B), "swap_long"], E.loc[key(B), "swap_short"])
    fin = np.where(w > 0, w * 0.5 * (la + sb), -w * 0.5 * (sa + lb)) * dt / 100
    net = w * 0.5 * (ra - rb) - w.diff().abs().fillna(0) * 0.5 * (tcost(A, ha) + tcost(B, hb)) + fin
    x = (1 + net).groupby(net.index.normalize()).prod() - 1
    corr_rep(scale(x), tag, name)

if __name__ == "__main__":
    pair("ETHUSD", "BTCUSD", "R39_ethbtc", "round 39 trend on ETH/BTC")
    pair("USTECHCash", "US30Cash", "R40_ndxdow", "round 40 trend on USTECH/US30")
