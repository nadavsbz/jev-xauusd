"""t326 (docs/prereg/research_t326.md): BTC/ETH hour-of-day seasonality, rolling monthly selection (top-3 long, bottom-3 short
UTC hours by trailing 365-day mean), H1 RF ECN bars. Usage: py -3.12 research/stable/t326.py density|dev|holdout"""
import json, sys
sys.path.insert(0, "research/bd1")
import numpy as np, pandas as pd
from news_files import us_dst

CF = "C:/Users/Benza/AppData/Roaming/MetaQuotes/Terminal/Common/Files/"
SIDE = {"BTCUSD": 1.0e-4, "ETHUSD": 1.5e-4}


def load(s):
    d = pd.read_csv(CF + f"t326_{s}_PERIOD_H1.csv")
    t = pd.to_datetime(d.time, unit="s")
    off = np.where([us_dst(x) for x in t], 3, 2)
    utc = t - pd.to_timedelta(off, unit="h")
    x = pd.DataFrame({"r": d.close.values / d.open.values - 1}, index=utc).sort_index()
    return x[~x.index.duplicated()]


def density(x):
    n = x.groupby(x.index.year).size()
    return {int(y): round(float(v / (24 * (366 if y % 4 == 0 else 365))), 3) for y, v in n.items()}


def hourly_pnl(x, s, rng=None):
    """returns hourly net P&L series (index = bar time), long-short, per the selection rule (or random hours with rng)"""
    x = x.copy(); x["h"] = x.index.hour; x["m"] = x.index.to_period("M")
    out = []
    for m in sorted(x.m.unique()):
        start = m.to_timestamp()
        hist = x[(x.index >= start - pd.Timedelta(days=365)) & (x.index < start)]
        if len(hist) < 0.9 * 24 * 365: continue
        if rng is None:
            mu = hist.groupby("h").r.mean().reindex(range(24))
            if mu.isna().any(): continue
            order = mu.sort_values().index.tolist(); longs, shorts = order[-3:], order[:3]
        else:
            p = rng.permutation(24); longs, shorts = p[:3].tolist(), p[3:6].tolist()
        cur = x[x.m == m]
        sig = np.where(cur.h.isin(longs), 1, np.where(cur.h.isin(shorts), -1, 0))
        sig = pd.Series(sig, index=cur.index)
        # costs: a side is paid whenever the position changes (consecutive same-direction hours merge); contiguity by real time
        prev = sig.shift(1).fillna(0); gap = cur.index.to_series().diff() != pd.Timedelta(hours=1)
        prev[gap.values] = 0
        nxt = sig.shift(-1).fillna(0); gap2 = (cur.index.to_series().shift(-1) - cur.index.to_series()) != pd.Timedelta(hours=1)
        nxt[gap2.values] = 0
        sides = (sig != prev).astype(int) * (sig != 0) + (sig != nxt).astype(int) * (sig != 0)
        out.append(pd.DataFrame({"g": sig * cur.r, "c": sides * SIDE[s], "sig": sig}))
    return pd.concat(out)


def stats(d):
    d = d.dropna(); eq = 1 + d.cumsum()
    return dict(ann=round(float(d.mean() * 365), 4), sharpe=round(float(d.mean() / d.std() * np.sqrt(365)), 2) if d.std() > 0 else 0,
                mdd=round(float((eq / eq.cummax() - 1).min()), 4), days=len(d))


def book(parts, lo, hi, dbl=False):
    days = {}
    for s, p in parts.items():
        p = p[lo:hi]; net = p.g - p.c * (2 if dbl else 1)
        days[s] = net.groupby(net.index.normalize()).sum()
    return pd.DataFrame(days).fillna(0).mean(axis=1)


if __name__ == "__main__":
    part = sys.argv[1]
    X = {s: load(s) for s in SIDE}
    if part == "density":
        print(json.dumps({s: density(x) for s, x in X.items()})); sys.exit()
    lo, hi = ("2019-01-01", "2022-12-31") if part == "dev" else ("2023-01-01", "2026-11-20")
    P = {s: hourly_pnl(x, s) for s, x in X.items()}
    port = book(P, lo, hi)
    out = {"portfolio": stats(port), "portfolio_2x_cost (info)": stats(book(P, lo, hi, True)),
           "months": int(sum(len(set(P[s][lo:hi].index.to_period("M"))) for s in P) / len(P))}
    for s, p in P.items():
        p = p[lo:hi]
        for nm, k in (("all", None), ("long", 1), ("short", -1)):
            q = p if k is None else p[p.sig == k]
            n = (q.g - q.c); out[f"{s}_{nm}"] = stats(n.groupby(n.index.normalize()).sum())
    rs = []
    for k in range(1, 101):
        R = {s: hourly_pnl(x, s, np.random.default_rng(k)) for s, x in X.items()}
        rs.append(stats(book(R, lo, hi))["sharpe"])
    out["random_sharpe_p50_p95"] = [round(float(np.percentile(rs, 50)), 2), round(float(np.percentile(rs, 95)), 2)]
    out["rule_pct_vs_random"] = round(float((np.array(rs) < out["portfolio"]["sharpe"]).mean() * 100), 1)
    c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity.pct_change()
    out["corr_C1 (info)"] = round(float(port.corr(c1.reindex(port.index))), 2)
    print(json.dumps(out, indent=1))
