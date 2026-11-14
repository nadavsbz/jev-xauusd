"""What do BD's crash days have in common? (user 3.11.2026: 'there must be a link'; docs/CRASH_LINK_PLAN.md)
Crash days: the clone's guard cuts (data/derived/crash_signs/baskets.csv, kind == cut: RF 2022-2025, EG 12/2025-10/2026, close day
of the cut basket) plus the live days of account 1 and the fleet (CRASH_LIVE). Control: every other weekday of the same span.
Features in two groups:
  BEFORE  known at the previous close (could have been acted on): gold returns, range expansion, distance from highs, GVZ, VIX,
          US yields/real yields/dollar/S&P moves, COT managed-money positioning (as published), calendar, scheduled US events today
  SAME    what happened that day (explains, cannot predict): the same markets' moves on the day, the US data surprise
Per feature: AUC (0.5 = no link) and a Mann-Whitney p; Bonferroni over all features. FRED/CFTC CSVs in data/raw (git-ignored).
Usage: python research/growth/crash_link.py"""
import numpy as np, pandas as pd
from scipy.stats import mannwhitneyu

CRASH_LIVE = ["2024-06-07", "2025-10-28", "2025-11-11", "2026-04-30", "2026-05-14", "2026-05-26", "2026-06-02", "2026-06-05",
              "2026-07-01", "2026-07-30", "2026-08-10", "2026-08-27", "2026-09-14", "2026-10-12"]
HIGH = ["CPI", "Nonfarm Payrolls", "Fed Interest Rate Decision", "PPI m/m", "Retail Sales m/m", "Core PCE Price Index m/m",
        "GDP q/q", "ISM Manufacturing PMI", "ISM Non-Manufacturing PMI", "JOLTS Job Openings", "Fed Chair Powell Speech",
        "Fed Chair Powell Testimony", "Initial Jobless Claims", "ADP Nonfarm Employment Change"]

def fred(s):
    d = pd.read_csv(f"data/raw/fred/{s}.csv"); d.columns = ["d", s]; d.index = pd.to_datetime(d.d)
    return pd.to_numeric(d[s], errors="coerce").ffill()

def table():
    g = pd.read_csv("data/derived/daily/XAUUSD_D1.csv"); g.index = pd.DatetimeIndex(pd.to_datetime(g.time, unit="s")).normalize(); g = g[~g.index.duplicated()]
    g = g[g.index.weekday < 5]; c = g.close; r = c.pct_change(); rng = (g.high - g.low) / c
    F = pd.DataFrame(index=g.index)
    sd = r.rolling(250).std()
    # BEFORE: everything shifted one day (known at the prior close)
    F["b_ret1"] = (r / sd).shift(1); F["b_ret5"] = (c.pct_change(5) / (sd * 5 ** .5)).shift(1)
    F["b_ret20"] = (c.pct_change(20) / (sd * 20 ** .5)).shift(1)
    F["b_absret5"] = F.b_ret5.abs(); F["b_absret20"] = F.b_ret20.abs()
    F["b_rng_ratio"] = (rng.rolling(5).mean() / rng.rolling(60).mean()).shift(1)
    F["b_rng1"] = (rng / rng.rolling(60).mean()).shift(1)
    F["b_from_hi60"] = (c / c.rolling(60).max() - 1).shift(1); F["b_from_hi250"] = (c / c.rolling(250).max() - 1).shift(1)
    F["b_above_ma50"] = (c / c.rolling(50).mean() - 1).shift(1)
    gvz = pd.read_csv("data/raw/gvz/GVZCLS.csv"); gvz.index = pd.to_datetime(gvz.iloc[:, 0]); gvz = pd.to_numeric(gvz.iloc[:, 1], errors="coerce").ffill()
    M = {"gvz": gvz, "vix": fred("VIXCLS"), "y10": fred("DGS10"), "ry10": fred("DFII10"), "y2": fred("DGS2"), "usd": fred("DTWEXBGS"),
         "spx": fred("SP500"), "bei": fred("T10YIE")}
    for k, s in M.items():
        s = s.reindex(F.index.union(s.index)).ffill().reindex(F.index)
        ch = s.pct_change() if k in ("usd", "spx") else s.diff()
        zz = ch / ch.rolling(250).std()
        F[f"b_{k}_chg"] = zz.shift(1); F[f"s_{k}_chg"] = zz; F[f"s_{k}_abs"] = zz.abs()
        if k in ("gvz", "vix"): F[f"b_{k}_lvl_pct"] = s.rolling(250).rank(pct=True).shift(1)
    cot = pd.read_csv("data/raw/cot/gold_cot.csv", parse_dates=["date"]); cot["net"] = (cot.mm_long - cot.mm_short) / cot.oi
    cot["pub"] = cot.date + pd.Timedelta(days=3)                                   # Tuesday positions, Friday release
    net = cot.set_index("pub").net; net = net.reindex(F.index.union(net.index)).ffill().reindex(F.index)
    F["b_cot_net"] = net; F["b_cot_pct"] = net.rolling(156 * 5 // 7 * 5, min_periods=250).rank(pct=True)
    F["b_cot_chg"] = net.diff(5)
    # calendar and scheduled events (known in advance)
    F["c_weekday"] = F.index.weekday
    ym = F.index.to_period("M"); last = pd.Series(F.index, index=F.index).groupby(ym).transform("max")
    F["c_month_end"] = (last - pd.Series(F.index, index=F.index)).dt.days.le(2).astype(int).values
    cal = pd.read_csv("data/derived/news/mt5_calendar_usd.csv"); cal["d"] = pd.to_datetime(cal.time, unit="s").dt.normalize()
    hi = cal[cal.event.isin(HIGH)]
    for nm, ev in (("ev_any", HIGH), ("ev_cpi", ["CPI"]), ("ev_nfp", ["Nonfarm Payrolls"]), ("ev_fomc", ["Fed Interest Rate Decision"]),
                   ("ev_powell", ["Fed Chair Powell Speech", "Fed Chair Powell Testimony"])):
        F[f"c_{nm}"] = F.index.isin(hi[hi.event.isin(ev)].d).astype(int)
    F["c_ev_count"] = hi.groupby("d").size().reindex(F.index).fillna(0)
    a = pd.to_numeric(cal.actual, errors="coerce"); f = pd.to_numeric(cal.forecast, errors="coerce")
    cal["sur"] = ((a - f).abs() / (f.abs() + 1e-9)).clip(upper=5)
    F["s_surprise_max"] = cal[cal.event.isin(HIGH)].groupby("d").sur.max().reindex(F.index)
    F["s_gold_rng"] = rng / rng.rolling(60).mean().shift(1); F["s_gold_ret"] = (r / sd.shift(1))
    return F

def crash_days():
    B = pd.read_csv("data/derived/crash_signs/baskets.csv"); cut = B[B.kind == "cut"]
    d = set(pd.to_datetime(cut.t1, unit="s").dt.normalize()) | set(pd.to_datetime(CRASH_LIVE))
    return pd.DatetimeIndex(sorted(d))

if __name__ == "__main__":
    F = table(); CD = crash_days(); span = F.loc["2022-01-01":"2026-10-31"]
    y = span.index.isin(CD); print(f"crash days {y.sum()} of {len(span)} weekdays (2022-01..2026-10)")
    rows = []
    for col in span.columns:
        x = span[col]; a = x[y].dropna(); b = x[~y].dropna()
        if len(a) < 10 or b.nunique() < 2: continue
        u, p = mannwhitneyu(a, b); auc = u / (len(a) * len(b))
        rows.append((col, len(a), round(a.median(), 3), round(b.median(), 3), round(auc, 3), p))
    R = pd.DataFrame(rows, columns=["feature", "n", "med_crash", "med_other", "auc", "p"]); m = len(R)
    R["bonf_sig"] = R.p < 0.05 / m; R = R.reindex(R.auc.sub(0.5).abs().sort_values(ascending=False).index)
    pd.set_option("display.width", 200); print(f"{m} features, Bonferroni p < {0.05 / m:.4f}"); print(R.to_string(index=False))
    for col in [c for c in span.columns if c.startswith("c_ev_") and c != "c_ev_count"] + ["c_month_end"]:
        print(f"{col}: P(crash | flag) {span.loc[span[col] == 1].index.isin(CD).mean():.1%} vs P(crash | no flag) {span.loc[span[col] == 0].index.isin(CD).mean():.1%}")
    print("crash by weekday:", pd.Series(span.index[y].weekday).value_counts().sort_index().to_dict(), "| all:", pd.Series(span.index.weekday).value_counts().sort_index().to_dict())
    F.to_csv("data/derived/growth/crash_features.csv")
