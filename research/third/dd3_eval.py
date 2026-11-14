"""Evaluate candidate 4 of docs/THIRD_COMPONENT_PLAN.md (US500_3DD tester, pre-registered 12.11.2026).
Daily realised P&L from the tester deal tables (both legs hold 1-5 days), as % of running balance.
Usage: py -3.12 research/third/dd3_eval.py"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/portfolio")
from curves import report_deals

def daily(rep):
    d = report_deals(rf"C:\MT5_JEV_TEST\{rep}.htm")
    d["pnl"] = d.commission.fillna(0) + d.swap.fillna(0) + d.profit.fillna(0)
    bal = pd.to_numeric(d.balance.str.replace(" ", "").str.replace(",", ""), errors="coerce")
    d["bal0"] = bal - d.pnl                                   # balance before this deal
    g = d.groupby("day").agg(pnl=("pnl", "sum"), bal0=("bal0", "first"))
    r = g.pnl / g.bal0
    return r.reindex(pd.bdate_range("2018-01-01", "2026-10-31"), fill_value=0.0)

def stats(x, nm):
    sh = x.mean() / x.std() * np.sqrt(252) if x.std() else 0
    eq = (1 + x).cumprod(); dd = (eq / eq.cummax() - 1).min()
    yrs = x.groupby(x.index.year).apply(lambda y: (1 + y).prod() - 1)
    print(f"  {nm:14s} Sh {sh:5.2f}  CAGR {(eq.iloc[-1] ** (252 / len(x)) - 1) * 100:5.1f}%  maxDD {dd * 100:6.1f}%  years+ {(yrs > 0).sum()}/{len(yrs)}")
    return sh, dd, yrs

if __name__ == "__main__":
    D, R = daily("dd3_us500_2018_2026"), daily("imr_us500_2018_2026")
    C = 0.5 * D + 0.5 * R
    C = C * R.std() / C.std()                                 # amended before results: compare at RSI2's volatility
    print("corr 3DD vs RSI2 (daily):", round(D.corr(R), 2))
    out = {}
    for nm, a, z in (("2018-2023", "2018", "2023"), ("2024-2026", "2024", "2026"), ("2018-2026", "2018", "2026")):
        print(f"== {nm}")
        for k, x in (("3DD", D), ("RSI2", R), ("50/50 volm", C)):
            out[(k, nm)] = stats(x.loc[a:z], k)
    print("yearly % (3DD / RSI2 / 50-50):")
    print(pd.DataFrame({k: out[(k, "2018-2026")][2] * 100 for k in ("3DD", "RSI2", "50/50 volm")}).round(1).to_string())
    g1 = out[("3DD", "2018-2023")][0] >= 0.5; g2 = out[("3DD", "2024-2026")][0] >= 0.8
    g3 = out[("50/50 volm", "2018-2026")][0] > out[("RSI2", "2018-2026")][0] and out[("50/50 volm", "2018-2026")][1] >= out[("RSI2", "2018-2026")][1]
    print(f"gates: 3DD 2018-23>=0.5 {g1} | 3DD 2024-26>=0.8 {g2} | combo better Sh & DD {g3}  ->  {'PASS' if g1 and g2 and g3 else 'FAIL'}")
