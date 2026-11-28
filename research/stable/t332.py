"""t332 (docs/prereg/research_t332.md): GAP currency sort by one-sided HP output gap, top2/bottom2 incl. USD.
Usage: py -3.12 research/stable/t332.py dev|holdout"""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/stable")
from t331 import load as load_fx, stats, C as C331

AREA = {"USD": "USA", "EUR": "EA20", "JPY": "JPN", "GBP": "GBR", "CAD": "CAN", "NOK": "NOR", "SEK": "SWE", "CHF": "CHE"}
C = [c for c in AREA if c != "USD"]
LAM = 129600


def hp_last(y):
    n = len(y); D = np.zeros((n - 2, n))
    for i in range(n - 2): D[i, i:i + 3] = (1, -2, 1)
    trend = np.linalg.solve(np.eye(n) + LAM * D.T @ D, y)
    return y[-1] - trend[-1]


def gaps():
    d = pd.read_csv("data/raw/oecd_ip.csv")
    d = d[d.ADJUSTMENT == "Y"]
    ip = d.pivot_table(index="TIME_PERIOD", columns="REF_AREA", values="OBS_VALUE")
    ip.index = pd.PeriodIndex(ip.index, freq="M")
    out = {}
    for m in pd.period_range("2000-01", "2025-12", freq="M"):
        row = {}
        for c, a in AREA.items():
            s = np.log(ip[a].loc[:m - 2].dropna()) if a in ip else pd.Series(dtype=float)
            if len(s) >= 60 and s.index[-1] == m - 2: row[c] = hp_last(s.values[-240:])
        out[m] = row
    return pd.DataFrame(out).T


def run(G, px, R, markup=1.4, spread=0.5e-4):
    px = px[C]["2000-01-01":].ffill(limit=5)
    days = px.index[px.notna().all(axis=1)]
    ret = px.loc[days].pct_change().fillna(0)
    me = days.to_series().groupby(days.to_period("M")).max()
    Rm = R.reindex(R.index.union(days)).ffill().reindex(days)
    w = pd.DataFrame(np.nan, index=days, columns=C)
    for p, t in me.items():
        if p not in G.index: continue
        g = G.loc[p].dropna().sort_values()
        row = pd.Series(0.0, index=C + ["USD"])
        if len(g) >= 5:
            row[g.index[-2:]] += 0.25; row[g.index[:2]] -= 0.25
        w.loc[t] = row[C].values
    w = w.ffill().shift(1).fillna(0)
    cal = days.to_series().diff().dt.days.fillna(1).values
    diff = Rm[C].sub(Rm["USD"], axis=0).fillna(0) / 100 / 365
    carry = (w * diff).sum(1) * cal
    fee = w.abs().sum(1) * markup / 100 / 365 * cal
    tc = w.diff().abs().sum(1).fillna(0) * spread
    return (w * ret).sum(1) + carry - fee - tc, w


if __name__ == "__main__":
    part = sys.argv[1]
    lo, hi = ("2001-01-01", "2016-12-31") if part == "dev" else ("2017-01-01", "2025-12-31")
    G = gaps(); px, R = load_fx()
    print("currencies per month (min/max in window):", int(G.loc[lo[:7]:hi[:7]].notna().sum(1).min()), int(G.loc[lo[:7]:hi[:7]].notna().sum(1).max()))
    out = {}
    for name, mk in (("base", 1.4), ("stress_2.4", 2.4)):
        net, w = run(G, px, R, markup=mk); out[name] = stats(net[lo:hi])
    import t331
    dc, _ = t331.run(px, R)
    out["corr_t331_monthly"] = round(float(net[lo:hi].resample("ME").sum().corr(dc[lo:hi].resample("ME").sum())), 2)
    print(json.dumps(out, indent=1, ensure_ascii=False))
