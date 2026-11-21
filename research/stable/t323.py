"""t323 (docs/prereg/research_t323.md): intraday momentum outside the US - first half-hour (from previous C) -> last half-hour.
Input: Common\\Files\\t323_<symbol>_PERIOD_M15.csv (BarExport, server clock UTC+2 / UTC+3 in US DST).
Usage: py -3.12 research/stable/t323.py dev|holdout"""
import json, sys
sys.path.insert(0, "research/bd1")
import numpy as np, pandas as pd
from news_files import us_dst

CF = "C:/Users/Benza/AppData/Roaming/MetaQuotes/Terminal/Common/Files/"
SPEC = {  # tz, first-half-hour end, entry, exit(C), one-side cost (ASSUMED, as t315)
    ".DE40Cash": ("Europe/Berlin", "09:30", "17:00", "17:30", 0.6e-4),
    ".JP225Cash": ("Asia/Tokyo", "09:30", "14:30", "15:00", 1.0e-4),
    "XAUUSD": ("America/New_York", "09:00", "13:00", "13:30", 0.8e-4)}


def load(s, tz):
    d = pd.read_csv(CF + f"t323_{s}_PERIOD_M15.csv")
    t = pd.to_datetime(d.time, unit="s")
    off = np.where([us_dst(x) for x in t], 3, 2)
    utc = (t - pd.to_timedelta(off, unit="h")).dt.tz_localize("UTC")
    o = pd.Series(d.open.values, index=utc).sort_index(); o = o[~o.index.duplicated()]
    return o.tz_convert(tz)


def trades(s):
    tz, f, a, c, side = SPEC[s]; o = load(s, tz)
    days = sorted({x for x in o.index.date if pd.Timestamp(x).weekday() < 5})
    at = lambda dd, hm: o.get(pd.Timestamp(f"{dd} {hm}", tz=tz), np.nan)
    rows, prev_c = [], np.nan
    for dd in days:
        pf, pa, pc = at(dd, f), at(dd, a), at(dd, c)
        if not np.isnan(prev_c) and not np.isnan(pf) and not np.isnan(pa) and not np.isnan(pc):
            r1 = pf / prev_c - 1; sg = np.sign(r1)
            if sg != 0:
                rows.append((pd.Timestamp(dd), sg * (pc / pa - 1) - 2 * side, 2 * side))
        prev_c = pc if not np.isnan(pc) else np.nan
    return pd.DataFrame(rows, columns=["day", "r", "cost"]).set_index("day")


def stats(r):
    r = r.dropna(); eq = 1 + r.cumsum()
    return dict(ann=round(float(r.mean() * 252), 4), sharpe=round(float(r.mean() / r.std() * np.sqrt(252)), 2),
                mdd=round(float((eq / eq.cummax() - 1).min()), 4), days=len(r))


if __name__ == "__main__":
    part = sys.argv[1]
    lo, hi = ("2015-01-01", "2020-12-31") if part == "dev" else ("2021-01-01", "2026-11-15")
    T = {s: trades(s)[lo:hi] for s in SPEC}
    R = pd.DataFrame({s: T[s].r for s in T}); C = pd.DataFrame({s: T[s].cost for s in T})
    port = R.mean(axis=1); out = {"portfolio": stats(port), "trades": int(R.notna().sum().sum()),
                                  "portfolio_2x_cost (info)": stats(port - C.mean(axis=1))}
    for s in T: out[s] = stats(T[s].r)
    print(json.dumps(out, indent=1))
