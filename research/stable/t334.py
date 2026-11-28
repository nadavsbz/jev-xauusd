"""t334 (docs/prereg/research_t334.md): ETH Long/Reversal, sessions 05-17 / 17-05 UTC, RF H1.
Usage: py -3.12 research/stable/t334.py dev|holdout"""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/bd1")
from news_files import us_dst

CF = "C:/Users/Benza/AppData/Roaming/MetaQuotes/Terminal/Common/Files/"
SWAP = 0.0475


def load():
    d = pd.read_csv(CF + "t326_ETHUSD_PERIOD_H1.csv")
    t = pd.to_datetime(d.time, unit="s")
    utc = t - pd.to_timedelta(np.where([us_dst(x) for x in t], 3, 2), unit="h")
    x = pd.DataFrame({"o": d.open.values, "c": d.close.values}, index=utc).sort_index()
    return x[~x.index.duplicated()]


def run(x, side):
    """returns per-session DataFrame: date, leg, pos, gross, cost, swap"""
    o = x.o; days = sorted(set(x.index.normalize()))
    rows, prev_pos, prev_rd = [], 0, None
    for d in days:
        t05, t17, t16 = d + pd.Timedelta(hours=5), d + pd.Timedelta(hours=17), d + pd.Timedelta(hours=16)
        t05n = t05 + pd.Timedelta(days=1)
        # day leg
        pos = 0 if (prev_rd is None or prev_rd == 0) else (-1 if prev_rd > 0 else 1)
        if t05 in o.index and t17 in o.index:
            g = pos * (o[t17] / o[t05] - 1)
            rows.append((t05, "day", pos, g, side * abs(pos - prev_pos), SWAP * abs(pos) * 12 / 24 / 365)); prev_pos = pos
        else:
            if prev_pos != 0: rows.append((t05, "day", 0, 0.0, side * abs(prev_pos), 0.0))
            prev_pos = 0
        rd_today = (x.c[t16] / o[t05] - 1) if (t05 in o.index and t16 in x.index) else None
        prev_rd = rd_today
        # night leg (always long)
        if t17 in o.index and t05n in o.index:
            g = o[t05n] / o[t17] - 1
            rows.append((t17, "night", 1, g, side * abs(1 - prev_pos), SWAP * 12 / 24 / 365)); prev_pos = 1
        else:
            if prev_pos != 0: rows.append((t17, "night", 0, 0.0, side * abs(prev_pos), 0.0))
            prev_pos = 0
    return pd.DataFrame(rows, columns=["t", "leg", "pos", "g", "cost", "swap"]).set_index("t")


def stats(r):
    eq = pd.concat([pd.Series([0.0]), r.cumsum()]) + 1
    yr = r.groupby(r.index.year).sum()
    return dict(ann=round(float(r.mean() * 365), 4), sharpe=round(float(r.mean() / r.std() * np.sqrt(365)), 2),
                mdd=round(float((eq / eq.cummax() - 1).min()), 4), by_year_pct=(yr * 100).round(1).to_dict())


def daily(T, lo, hi, col="net"):
    days = pd.date_range(lo, hi)
    return T[col].groupby(T.index.normalize()).sum().reindex(days, fill_value=0)


if __name__ == "__main__":
    part = sys.argv[1]
    lo, hi = ("2018-01-01", "2020-12-31") if part == "dev" else ("2021-01-01", "2026-11-19")
    x = load()
    n = x[lo:hi].groupby(x[lo:hi].index.year).size()
    print("bar density:", {int(y): round(v / (24 * 365), 3) for y, v in n.items()})
    out = {}
    for name, side in (("base", 1.5e-4), ("2x_cost", 3.0e-4)):
        T = run(x["2017-12-01":hi], side)[lo:hi]
        T["net"] = T.g - T.cost - T.swap
        out[name] = stats(daily(T, lo, hi))
        if name == "base":
            D = T[T.leg == "day"]; out["day_leg_net_sum_pct"] = round(float(D.net.sum() * 100), 1)
            out["night_leg_net_sum_pct"] = round(float(T[T.leg == "night"].net.sum() * 100), 1)
            base = daily(T, lo, hi)
    bh = x.o[lo:hi].resample("D").first().pct_change().fillna(0) - SWAP / 365
    out["buy_hold_same_swap"] = stats(bh)
    try:
        c1 = pd.read_csv("data/derived/c1_equity/c1_ecn_av15_full_equity.csv", index_col=0, parse_dates=True).equity
        c1 = c1.resample("D").last().pct_change()
        out["corr_C1_daily"] = round(float(base.corr(c1.reindex(base.index))), 2)
    except Exception as e:
        out["corr_C1_daily"] = str(e)[:80]
    print(json.dumps(out, indent=1, ensure_ascii=False))
