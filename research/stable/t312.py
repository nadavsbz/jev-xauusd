"""t312 (docs/prereg/research_t312.md): FX fix reversal, Europe version, EURUSD + GBPUSD, Dukascopy BID M1.
Usage: py -3.12 research/stable/t312.py dev|holdout"""
import glob, json, os, sys
sys.path.insert(0, "research/bd1")
import numpy as np, pandas as pd

COST = {"EURUSD": 1.0e-4, "GBPUSD": 1.5e-4}      # round trip per trade, in price (1 pip = 1e-4)
LEGS = [("preE", "07:00", "13:15", -1), ("postL", "16:00", "22:00", +1)]   # London clock; -1 = sell XXXUSD (buy USD)


def load(pair):
    """RF ECN M15 bars (BarExport, server clock = UTC+2, UTC+3 in US daylight saving) -> minute-open series in London time.
    Technical change 20.11 18:25 (Dukascopy blocked): docs/prereg/research_t312.md."""
    from news_files import us_dst
    d = pd.read_csv(f"C:/Users/Benza/AppData/Roaming/MetaQuotes/Terminal/Common/Files/t312_{pair}_PERIOD_M15.csv")
    t = pd.to_datetime(d.time, unit="s")
    off = np.where([us_dst(x) for x in t], 3, 2)
    utc = (t - pd.to_timedelta(off, unit="h")).dt.tz_localize("UTC")
    s = pd.Series(d.open.values, index=utc).sort_index(); s = s[~s.index.duplicated()]
    return s.tz_convert("Europe/London")


def legs(pair, s):
    out = []
    dates = sorted(set(s.index.date))
    for name, a, b, sg in LEGS:
        ta = pd.DatetimeIndex([pd.Timestamp(f"{d} {a}", tz="Europe/London") for d in dates if pd.Timestamp(d).weekday() < 5])
        tb = ta + (pd.Timedelta(b + ":00") - pd.Timedelta(a + ":00"))
        pa, pb = s.reindex(ta), s.reindex(tb)
        r = sg * (pb.values - pa.values) / pa.values - COST[pair] / pa.values
        out.append(pd.Series(r, index=ta.date, name=f"{pair}_{name}").dropna())
    return out


def stats(r):
    r = r.dropna(); eq = (1 + r).cumprod()
    return dict(ann=round(float(eq.iloc[-1] ** (252 / len(r)) - 1), 4), sharpe=round(float(r.mean() / r.std() * np.sqrt(252)), 2),
                mdd=round(float((eq / eq.cummax() - 1).min()), 4), days=len(r))


if __name__ == "__main__":
    part = sys.argv[1]
    allr = {}
    for pair in COST:
        for x in legs(pair, load(pair)): allr[x.name] = x
    df = pd.DataFrame(allr); df.index = pd.to_datetime(df.index)
    lo, hi = ("2015-01-01", "2019-12-31") if part == "dev" else ("2020-01-01", "2100-01-01")
    d = df[lo:hi]
    port = d.fillna(0).sum(axis=1) / 2           # equal weight, two pairs; each pair = two legs a day
    out = {"portfolio": stats(port), "data_end": str(df.index[-1].date())}
    for c in d: out[c] = stats(d[c])
    dbl = port - (d.notna() * pd.Series({c: COST[c[:6]] for c in d.columns}) / 1.1).sum(axis=1) / 2   # ~2x cost (price ~1.1-1.3)
    out["portfolio_2x_cost (info)"] = stats(dbl)
    print(json.dumps(out, indent=1))
