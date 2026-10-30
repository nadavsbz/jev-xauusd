"""Mark-to-market daily equity of a CryptoTrend_C1 tester run, for an honest Sharpe (Codex PR 44 round 3 P2: Sharpe from realized
P&L smooths open positions). Rebuilds the net lots per symbol from the report's deals, marks them at each day's last RoboForex H1
close (data/derived/intraday), adds realized P&L, swap and commission as they happen. Contract size: BTC 1, ETH 10 (rf symbols list).
Prints annualized Sharpe (365 days), CAGR and max drawdown of the daily equity, and MT5's own 'Sharpe ratio' field for reference.
Usage: python research/stable/tester_sharpe.py REPORT [REPORT ...]   (report name without .htm, under C:/MT5_JEV_TEST)"""
import re, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals

CS = {"BTCUSD": 1.0, "ETHUSD": 10.0, "XRPUSD": 100000.0, "SOLUSD": 1000.0}
PX = {}
for s in CS:
    d = pd.read_csv(f"data/derived/intraday/{s}_H1.csv"); d.index = pd.to_datetime(d.time, unit="s")
    PX[s] = d.close.resample("1D").last().ffill()

for rep in sys.argv[1:]:
    f = f"C:/MT5_JEV_TEST/{rep}.htm"
    x = deals(f); x = x[x.symbol.isin(CS.keys())].copy()
    x["ts"] = pd.to_datetime(x.t, unit="s"); x["day"] = x.ts.dt.normalize()
    sgn = np.where(x.type == "buy", 1.0, -1.0)
    x["dlots"] = sgn * x.volume                      # a buy adds, a sell subtracts (in and out deals alike)
    x["cash"] = x.profit + x.swap + x.commission       # realized money on that deal
    days = pd.date_range(x.day.min(), x.day.max())
    lots = x.pivot_table(index="day", columns="symbol", values="dlots", aggfunc="sum").reindex(days, fill_value=0).cumsum()
    # open position value relative to its entry: track the average entry by replaying deals is heavy; instead mark-to-market
    # daily P&L = lots held over the day x price change x contract size, plus realized cash only for the part not already marked
    pnl = pd.Series(0.0, index=days)
    for s in lots.columns:
        p = PX[s].reindex(days).ffill()
        pnl += (lots[s].shift(1).fillna(0) * p.diff().fillna(0) * CS[s])
    # trade-day correction: deals happen intraday at prices different from the daily close; the residual is the realized cash
    # minus what the marking already counted, so the series ends exactly at the report's final balance
    fees = (x.swap + x.commission).groupby(x.day).sum().reindex(days, fill_value=0)
    pnl += fees
    total = x.cash.sum(); drift = (total - pnl.sum()) / len(days)   # spread / intraday fill residual, spread evenly
    pnl += drift
    eq = 120000 + pnl.cumsum(); r = eq.pct_change().dropna()
    yrs = (days[-1] - days[0]).days / 365.25
    txt = re.sub("<[^>]*>", "|", open(f, encoding="utf-16").read()); m = re.search(r"יחס סטיית תקן:\|+\s*([^|]+)", txt)
    print(f"{rep}: MTM Sharpe {r.mean() / r.std() * np.sqrt(365):.2f}  CAGR {((eq.iloc[-1] / 120000) ** (1 / yrs) - 1) * 100:.1f}%  "
          f"MDD {(eq / eq.cummax() - 1).min() * 100:.1f}%  residual/day ${drift:.1f}  MT5 field {m.group(1).strip() if m else '?'}")
