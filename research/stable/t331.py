"""t331 (docs/prereg/research_t331.md): dollar carry (Lustig-Roussanov-Verdelhan 2014), G10 basket vs USD.
Usage: py -3.12 research/stable/t331.py dev|holdout|coverage"""
import json, sys
import numpy as np, pandas as pd

D = "data/raw/fred/"
FX = {"EUR": ("DEXUSEU", 1), "JPY": ("DEXJPUS", -1), "GBP": ("DEXUSUK", 1), "CHF": ("DEXSZUS", -1), "AUD": ("DEXUSAL", 1),
      "NZD": ("DEXUSNZ", 1), "CAD": ("DEXCAUS", -1), "SEK": ("DEXSDUS", -1), "NOK": ("DEXNOUS", -1)}
IR = {"USD": "US", "EUR": "EZ", "JPY": "JP", "GBP": "GB", "CHF": "CH", "AUD": "AU", "NZD": "NZ", "CAD": "CA", "SEK": "SE", "NOK": "NO"}
C = list(FX)


def rd(s):
    x = pd.read_csv(D + s + ".csv", index_col=0, parse_dates=True).iloc[:, 0]
    return pd.to_numeric(x, errors="coerce")


def load():
    px = pd.DataFrame({c: rd(FX[c][0]) ** FX[c][1] for c in C})          # USD per 1 unit of foreign ccy
    R = pd.DataFrame({c: rd(f"IR3TIB01{IR[c]}M156N") for c in IR})       # monthly, % p.a., dated 1st of month
    R.index = R.index + pd.offsets.MonthEnd(0) + pd.offsets.MonthEnd(1)  # month m usable from end of m+1
    return px, R


def run(px, R, markup=1.4, spread=0.5e-4):
    px = px["1999-12-01":].ffill(limit=5)
    days = px.index[px.notna().all(axis=1)]
    ret = px.loc[days].pct_change().fillna(0)
    me = days.to_series().groupby(days.to_period("M")).max()
    Rm = R.reindex(R.index.union(days)).ffill().reindex(days)
    w = pd.DataFrame(np.nan, index=days, columns=C)
    for t in me:
        r = Rm.loc[t]
        if pd.isna(r["USD"]): continue
        avail = [c for c in C if not pd.isna(r[c])]
        s = r[avail].mean() - r["USD"]
        w.loc[t, avail] = (1 if s > 0 else -1) / len(avail)
        w.loc[t, [c for c in C if c not in avail]] = 0.0
    w = w.ffill().shift(1).fillna(0)                                     # decided at month-end close, held from next day
    cal = days.to_series().diff().dt.days.fillna(1).values
    diff = Rm[C].sub(Rm["USD"], axis=0).fillna(0) / 100 / 365
    carry = (w * diff).sum(1) * cal
    fee = w.abs().sum(1) * markup / 100 / 365 * cal
    tc = w.diff().abs().sum(1).fillna(0) * spread
    net = (w * ret).sum(1) + carry - fee - tc
    return net, w


def stats(x):
    eq = pd.concat([pd.Series([0.0]), x.cumsum()]) + 1
    yr = x.groupby(x.index.year).sum()
    return dict(ann=round(float(x.mean() * 252), 4), sharpe=round(float(x.mean() / x.std() * np.sqrt(252)), 2),
                mdd=round(float((eq / eq.cummax() - 1).min()), 4), pos_years=f"{(yr > 0).sum()}/{len(yr)}",
                by_year_pct=(yr * 100).round(1).to_dict())


if __name__ == "__main__":
    part = sys.argv[1]
    px, R = load()
    if part == "coverage":
        bd = pd.bdate_range("2000-01-01", "2025-12-31")
        cov = px.reindex(bd).notna().groupby(bd.year).mean().round(3)
        print(cov.min(axis=1).to_dict()); print(R["2000":"2025"].notna().groupby(R["2000":"2025"].index.year).mean().min().to_dict()); sys.exit()
    lo, hi = ("2000-01-01", "2013-12-31") if part == "dev" else ("2014-01-01", "2025-12-31")
    out = {}
    for name, mk in (("base", 1.4), ("stress_2.4", 2.4)):
        net, w = run(px, R, markup=mk)
        out[name] = stats(net[lo:hi])
    out["pct_months_long"] = round(float((w[lo:hi].sum(1) > 0).groupby(w[lo:hi].index.to_period("M")).last().mean()), 2)
    print(json.dumps(out, indent=1, ensure_ascii=False))
