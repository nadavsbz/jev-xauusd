"""t369 (docs/prereg/research_t369.md): C1 RebalPct 0.30 (base) vs 0.45. Needs both *_equity.csv (tester_sharpe.py, SAVE=...).
Usage: py -3.12 research/stable/t369.py"""
import sys, json
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals
CS = {"BTCUSD": 1.0, "ETHUSD": 10.0}
RUNS = {"base": "c1_ecn_av075_full", "rb45": "c1_ecn_av075_rb45_full"}
PER = {"DEV": ("2020-01-01", "2023-12-31"), "HO_retro": ("2024-01-01", "2026-10-30")}


def load(rep):
    eq = pd.read_csv(f"data/derived/c1_equity/{rep}_equity.csv", index_col=0, parse_dates=True).equity
    d = deals(f"C:/MT5_JEV_TEST/{rep}.htm"); d = d[d.symbol.isin(CS)].copy()
    d["day"] = pd.to_datetime(d.t, unit="s").dt.normalize()
    d["notional"] = d.volume * d.price * d.symbol.map(CS)
    d["cost"] = d.commission + d.swap
    return eq, d


def stats(eq, d, lo, hi, cost_mult=1.0):
    e = eq[lo:hi]; dd = d[(d.day >= lo) & (d.day <= hi)]
    extra = ((cost_mult - 1) * dd.cost).groupby(dd.day).sum().reindex(e.index).fillna(0).cumsum()
    e2 = e + extra; r = e2.pct_change().dropna()
    return dict(turnover=float(dd.notional.sum()), sharpe=round(float(r.mean() / r.std() * np.sqrt(365)), 3),
                mdd_pct=round(float((e2 / e2.cummax() - 1).min() * 100), 2), ret_pct=round(float((e2.iloc[-1] / e2.iloc[0] - 1) * 100), 1))


if __name__ == "__main__":
    L = {k: load(v) for k, v in RUNS.items()}; out = {}
    for p, (lo, hi) in PER.items():
        b, v = stats(*L["base"], lo, hi), stats(*L["rb45"], lo, hi)
        b2, v2 = stats(*L["base"], lo, hi, 2.0), stats(*L["rb45"], lo, hi, 2.0)
        g = dict(turnover_cut=round(1 - v["turnover"] / b["turnover"], 3), d_sharpe=round(v["sharpe"] - b["sharpe"], 3),
                 mdd_ok=v["mdd_pct"] >= b["mdd_pct"] and v["mdd_pct"] >= -25, x2_ok=v2["ret_pct"] > 0 and v2["sharpe"] >= b2["sharpe"])
        g["pass"] = g["turnover_cut"] >= 0.15 and g["d_sharpe"] >= 0.10 and g["mdd_ok"] and g["x2_ok"]
        out[p] = dict(base=b, rb45=v, base_x2=b2, rb45_x2=v2, gate=g)
    out["VERDICT"] = "GO-candidate (retrospective)" if all(out[p]["gate"]["pass"] for p in PER) else "NO-GO"
    print(json.dumps(out, indent=1))
