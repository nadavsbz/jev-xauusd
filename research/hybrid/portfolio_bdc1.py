"""Portfolio of two separate accounts: BD (DragonClone_v11, one tester run per year) and C1 (CryptoTrend_C1, one 2020-2025 run),
re-balanced to fixed weights at each year start (docs/BD_EVERYYEAR_PLAN.md, round 6 + portfolio, pre-registered 31.10.2026).
Daily MTM equity of the BD runs: balance + floating P&L of the open tickets, exact for a hedging account: per symbol keep
N = net lots and K = sum(side x lots x entry) of the open tickets; floating = CS x (N x price - K). A closing deal removes its
ticket's entry, inferred from the realized profit. Price = the day's last RoboForex H1 close (intraday dips inside a day are
not seen, so the MDD here is a floor on the real one). C1: the daily equity saved by tester_sharpe.py (SAVE=data/derived/c1_equity).
Usage: python research/hybrid/portfolio_bdc1.py [BD_TAG=dd5q] [ROUND=5]"""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/btc"); from guardian_sim import deals

TAG = sys.argv[1] if len(sys.argv) > 1 else "dd5q"
RND = sys.argv[2] if len(sys.argv) > 2 else "5"
CS = {"XAUUSD": 100.0}
d = pd.read_csv("data/derived/intraday/XAUUSD_H1.csv"); d.index = pd.to_datetime(d.time, unit="s")
PX = {"XAUUSD": d.close.resample("1D").last().ffill()}
YEARS = range(2020, 2026)
FIX = {("5", 2022, "dd5q"): "ev5_rf2022_dd5q_r"}   # the stuck run was re-run under this name (identical result)

def mtm(report, deposit=120000.0):
    x = deals(f"C:/MT5_JEV_TEST/{report}.htm")
    x = x[x.symbol.isin(CS.keys())].sort_values(["t", "deal"]).copy()
    x["day"] = pd.to_datetime(x.t, unit="s").dt.normalize()
    days = pd.date_range(x.day.min(), x.day.max()); N = {s: 0.0 for s in CS}; K = {s: 0.0 for s in CS}
    bal = deposit; eq = []; it = iter(x.itertuples()); row = next(it, None)
    for day in days:
        while row is not None and row.day == day:
            s, side = row.symbol, (1.0 if row.type == "buy" else -1.0)
            bal += row.profit + row.swap + row.commission
            if row.dir == "in": N[s] += side * row.volume; K[s] += side * row.volume * row.price
            else:   # closes a ticket of the opposite side: profit = (exit - entry) x lots x CS x ticket_side
                ts = -side; e = row.price - row.profit / (row.volume * CS[s] * ts)
                N[s] -= ts * row.volume; K[s] -= ts * row.volume * e
            row = next(it, None)
        eq.append(bal + sum(CS[s] * (N[s] * PX[s].asof(day + pd.Timedelta(hours=23)) - K[s]) for s in CS))
    return pd.Series(eq, index=days), bal

BD = {}
for y in YEARS:
    rep = FIX.get((RND, y, TAG), f"ev{RND}_rf{y}_{TAG}"); e, bal = mtm(rep)
    assert abs(e.iloc[-1] - bal) < 1, (rep, e.iloc[-1], bal)   # every run ends flat
    BD[y] = e / 120000.0
for av in ("av08", "av10"):
    c = pd.read_csv(f"data/derived/c1_equity/c1r3_{av}_d0_rf_2020_2025_equity.csv", index_col=0, parse_dates=True).equity
    print(f"\nBD {TAG} (round {RND}) + C1 {av}, yearly re-balance; yearly % and MDD inside the year (daily closes)")
    print("  BD alone : " + " ".join(f"{y}:{(BD[y].iloc[-1]-1)*100:+.0f}(dd{(BD[y]/BD[y].cummax()-1).min()*100:.0f})" for y in YEARS))
    for w in (0.0, 0.3, 0.4, 0.5):
        tot = 1.0; out = []; chain = []
        for y in YEARS:
            cy = c[str(y)]; prev = c[:f"{y - 1}-12-31"]
            cn = cy / (prev.iloc[-1] if len(prev) else 120000.0)
            idx = BD[y].index.union(cn.index)
            b = BD[y].reindex(idx).ffill().fillna(1.0); k = cn.reindex(idx).ffill().fillna(1.0)
            p = w * b + (1 - w) * k                 # value of 1 unit split at the year start, no re-balance inside the year
            out.append((y, p.iloc[-1] - 1, (p / p.cummax() - 1).min()))
            chain.append(tot * p); tot *= p.iloc[-1]
        ch = pd.concat(chain); ch = ch[~ch.index.duplicated(keep="last")]   # the chained daily path, for the overall MDD
        yrs = (ch.index[-1] - ch.index[0]).days / 365.25
        print(f"  BD {int(w*100):2d}%   : " + " ".join(f"{y}:{r*100:+.0f}(dd{dd*100:.0f})" for y, r, dd in out)
              + f" | CAGR {(tot ** (1 / yrs) - 1) * 100:.1f}% MDD {(ch / ch.cummax() - 1).min() * 100:.1f}% positive {sum(r > 0 for _, r, _ in out)}/6")
