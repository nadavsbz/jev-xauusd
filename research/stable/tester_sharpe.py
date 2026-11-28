"""Mark-to-market daily equity of a CryptoTrend_C1 tester run, for an honest Sharpe (Codex PR 44 round 3 P2: Sharpe from realized
P&L smooths open positions; round 4 2xP1: missing pivot cells and a residual spread over time). Equity at each day's end =
balance (realized profit + swap + commission of every deal up to that day, from the report) + floating P&L of the net position
per symbol, marked at that day's last RoboForex H1 close (data/derived/intraday) against its average entry price.
Average entry: replaying the deals in order - adding re-averages; reducing removes the closed tickets' entry, inferred from the
realized profit (round 5 P1); crossing zero restarts at the deal price (the EA keeps one direction per symbol).
Contract size: BTC 1, ETH 10, XRP 100000, SOL 1000 (rf symbols list). Prints annualized Sharpe (365 days), CAGR, max drawdown of
the daily equity, and the gap between the last equity and the report's final balance (0 when the run ends flat).
Usage: python research/stable/tester_sharpe.py REPORT [REPORT ...]   (report name without .htm, under C:/MT5_JEV_TEST)"""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals

CS = {"BTCUSD": 1.0, "ETHUSD": 10.0, "XRPUSD": 100000.0, "SOLUSD": 1000.0}
PX = {}
for s in CS:
    d = pd.read_csv(f"data/derived/intraday/{s}_H1.csv"); d.index = pd.to_datetime(d.time, unit="s")
    PX[s] = d.close.resample("1D").last().ffill()

for rep in sys.argv[1:]:
    x = deals(f"C:/MT5_JEV_TEST/{rep}.htm")
    x = x[x.symbol.isin(CS.keys())].sort_values(["t", "deal"]).copy()
    x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize()
    days = pd.date_range(x.day.min(), x.day.max())
    pos = {s: 0.0 for s in CS}; avg = {s: 0.0 for s in CS}
    bal = 120000.0; eq = []; it = iter(x.itertuples()); row = next(it, None)
    for day in days:
        while row is not None and row.day == day:
            s, q = row.symbol, (row.volume if row.type == "buy" else -row.volume)
            bal += row.profit + row.swap + row.commission
            p0 = pos[s]; p1 = p0 + q
            if abs(p1) < 1e-9: avg[s] = 0.0
            elif p0 == 0 or (p0 > 0) != (p1 > 0): avg[s] = row.price          # opened, or crossed zero
            elif abs(p1) > abs(p0): avg[s] = (avg[s] * abs(p0) + row.price * abs(q)) / abs(p1)   # added
            else:   # reduced (Codex PR 44 round 5 P1): the hedging EA closed particular tickets; their entry price follows from
                    # the realized profit, profit = (exit - entry) x lots x CS x side -> the rest keeps the remaining cost basis
                side = 1.0 if p0 > 0 else -1.0
                e_closed = row.price - row.profit / (abs(q) * CS[s] * side)
                avg[s] = (avg[s] * abs(p0) - e_closed * abs(q)) / abs(p1)
            pos[s] = 0.0 if abs(p1) < 1e-9 else p1
            row = next(it, None)
        fl = sum(pos[s] * (PX[s].asof(day + pd.Timedelta("23h")) - avg[s]) * CS[s] for s in CS if pos[s] != 0)
        eq.append(bal + fl)
    eq = pd.Series(eq, index=days); r = eq.pct_change().dropna()
    if os.environ.get("SAVE"): eq.rename("equity").to_csv(f"{os.environ['SAVE']}/{rep}_equity.csv")   # for c1_timemachine.py
    yrs = (days[-1] - days[0]).days / 365.25
    print(f"{rep}: MTM Sharpe {r.mean() / r.std() * np.sqrt(365):.2f}  CAGR {((eq.iloc[-1] / 120000) ** (1 / yrs) - 1) * 100:.1f}%  "
          f"MDD {(eq / eq.cummax() - 1).min() * 100:.1f}%  open at end {sum(abs(v) > 0 for v in pos.values())} symbols, "
          f"last equity - balance ${eq.iloc[-1] - bal:,.0f}")
