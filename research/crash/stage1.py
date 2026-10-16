"""Stage 1 of docs/CRASH_DETECT_PLAN.md: can a 1% gold move within the next 4 hours
be flagged in advance? Price, dollar, volatility-index and news signals only, each
computed from data known at the close of hour h.

Usage:
  python research/crash/stage1.py DATA_DIR            # train + validation only
  python research/crash/stage1.py DATA_DIR --test S2  # the ONE chosen signal on the test period

DATA_DIR holds: xauusd_h1_YYYY.csv, dollaridxusd_h1_YYYY.csv (Dukascopy, UTC, ms timestamps),
GVZCLS.csv (FRED), gdelt/timelinevolraw_YYYYMM.csv + gdelt/timelinetone_YYYYMM.csv,
events.csv (column utc: scheduled release times)."""
import glob, os, sys
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression

TRAIN_END, VALID_END = pd.Timestamp("2023-01-01"), pd.Timestamp("2025-01-01")
TEST_END = pd.Timestamp("2025-11-01")   # Nov 2025 on calibrated the target (account 1 baskets): not a test
LATE_START = pd.Timestamp("2018-01-01")  # dollar index (Dukascopy) from Dec 2017, GDELT from 2017
FLAG_BUDGET = 0.10           # share of training hours each signal may flag
EVENT_PCT, HORIZON = 1.0, 4  # target: high-low >= 1.0% of the close within the next 4 hours
DAYS = 250


def hourly(data, inst):
    fs = sorted(glob.glob(os.path.join(data, f"{inst}_h1_*.csv")))
    d = pd.concat([pd.read_csv(f) for f in fs]).drop_duplicates("timestamp")
    d["t"] = pd.to_datetime(d.timestamp, unit="ms")
    return d.set_index("t").sort_index()[["open", "high", "low", "close"]]


def trailing_pct(x, window):
    """Percentile of each value within the trailing window that ends at it
    (past values and the current one only, no look-ahead)."""
    return x.rolling(window, min_periods=window // 2).rank(pct=True)


def rng(h, n):
    return (h.high.rolling(n).max() - h.low.rolling(n).min()) / h.close


def build(data):
    g = hourly(data, "xauusd")
    bars_per_day = 23
    f = pd.DataFrame(index=g.index)
    # target: range of the NEXT 4 bars relative to this bar's close
    fut_hi = g.high[::-1].rolling(HORIZON).max()[::-1].shift(-1)
    fut_lo = g.low[::-1].rolling(HORIZON).min()[::-1].shift(-1)
    f["y"] = ((fut_hi - fut_lo) / g.close * 100 >= EVENT_PCT).astype(float)
    f.loc[fut_hi.isna() | fut_lo.isna(), "y"] = np.nan
    r24 = rng(g, 24)
    f["S1"] = trailing_pct(r24, DAYS * bars_per_day)
    one = (g.high - g.low) / g.close
    f["har1"], f["har24"], f["har120"] = np.log(one + 1e-6), np.log(one.rolling(24).mean()), np.log(one.rolling(120).mean())
    ret = np.log(g.close).diff()
    z = ret / ret.rolling(250).std().shift(1)
    sp = sm = 0.0; cs = []
    for v in z.fillna(0).values:
        sp = max(0.0, sp + v - 0.5); sm = max(0.0, sm - v - 0.5); cs.append(max(sp, sm))
    f["S3"] = cs
    day = g.index.normalize()
    night_hi = g.high.groupby(day).cummax(); night_lo = g.low.groupby(day).cummin()
    daily = g.groupby(day).agg(h=("high", "max"), l=("low", "min"), c=("close", "last"))
    adr = ((daily.h - daily.l) / daily.c).rolling(20).mean().shift(1)
    f["S4"] = ((night_hi - night_lo) / g.close).values / adr.reindex(day).values
    gvz = pd.read_csv(os.path.join(data, "GVZCLS.csv"), parse_dates=["observation_date"], na_values=".")
    gvz = gvz.set_index("observation_date").GVZCLS.dropna()
    gp = trailing_pct(gvz, DAYS).shift(1)                  # yesterday's close only
    f["S5"] = gp.reindex(day, method="ffill").values
    dx = hourly(data, "dollaridxusd")
    f["S6"] = trailing_pct(rng(dx, 24), DAYS * bars_per_day).reindex(g.index, method="ffill")
    vol = pd.concat([pd.read_csv(x) for x in glob.glob(os.path.join(data, "gdelt", "timelinevolraw_*.csv"))])
    vol.columns = [c.strip().lstrip("﻿") for c in vol.columns]
    vol = vol.pivot_table(index="Date", columns="Series", values="Value", aggfunc="sum")
    vol.index = pd.to_datetime(vol.index)
    share = (vol["Article Count"] / vol["Total Monitored Articles"]).sort_index()
    news = (share / share.rolling(30).mean().shift(1)).shift(1)       # yesterday vs the 30 days before it
    f["S7"] = news.reindex(day).values
    tone = pd.concat([pd.read_csv(x) for x in glob.glob(os.path.join(data, "gdelt", "timelinetone_*.csv"))])
    tone.columns = [c.strip().lstrip("﻿") for c in tone.columns]
    tone["Date"] = pd.to_datetime(tone.Date); tone = tone.groupby("Date").Value.mean().sort_index()
    f["S8"] = (tone - tone.rolling(7).mean().shift(1)).abs().shift(1).reindex(day).values
    ev = pd.to_datetime(pd.read_csv(os.path.join(data, "events.csv")).utc).values.astype("datetime64[ns]")
    ev.sort()
    tt = g.index.values
    nxt = np.searchsorted(ev, tt, side="right")          # first event strictly after hour h's close
    nxt_t = np.where(nxt < len(ev), ev[np.minimum(nxt, len(ev) - 1)], np.datetime64("NaT"))
    close_t = tt + np.timedelta64(1, "h")
    f["S9"] = ((nxt_t - close_t) <= np.timedelta64(HORIZON, "h")).astype(float)
    return f


def split(f):
    """A row belongs to a period only if its whole target window (h .. h+4) lies inside it."""
    end = f.index + pd.Timedelta(hours=HORIZON + 1)
    tr = f[end <= TRAIN_END]
    va = f[(f.index >= TRAIN_END) & (end <= VALID_END)]
    te = f[(f.index >= VALID_END) & (end <= TEST_END)]
    return tr, va, te


def fit_scores(tr, frames, cols, name):
    ok = tr[cols + ["y"]].dropna()
    m = LogisticRegression(max_iter=1000).fit(ok[cols], ok.y)
    return {k: pd.Series(m.predict_proba(v[cols].fillna(ok[cols].median()))[:, 1], index=v.index, name=name)
            for k, v in frames.items()}


def evaluate(score_tr, score_x, y_x):
    thr = np.nanquantile(score_tr, 1 - FLAG_BUDGET)
    ok = y_x.notna() & score_x.notna()
    flag = score_x[ok] >= thr
    hit = y_x[ok] == 1
    return float(flag.mean()), float((flag & hit).sum() / max(hit.sum(), 1)), float(hit.mean())


def main():
    data = sys.argv[1]
    f = build(data)
    tr, va, te = split(f)
    frames = {"train": tr, "valid": va, "test": te}
    scores = {}
    for s in ["S1", "S3", "S4", "S5", "S9"]:
        scores[s] = {k: v[s] for k, v in frames.items()}
    for s in ["S6", "S7", "S8"]:                       # trained (thresholded) only where their data exist
        scores[s] = {"train": tr.loc[tr.index >= LATE_START, s], "valid": va[s], "test": te[s]}
    scores["S2"] = fit_scores(tr, frames, ["har1", "har24", "har120"], "S2")
    news_tr = tr[tr.index >= LATE_START]
    scores["S10"] = fit_scores(news_tr, frames, ["S1", "har1", "har24", "har120", "S3", "S4", "S5", "S6", "S7", "S8", "S9"], "S10")
    if "--test" in sys.argv:
        s = sys.argv[sys.argv.index("--test") + 1]
        fr, rc, base = evaluate(scores[s]["train"], scores[s]["test"], te.y)
        print(f"TEST {s}: flagged {fr:.1%} of hours, recall {rc:.1%}, event base rate {base:.1%}")
        return
    rows = []
    for s, sc in scores.items():
        a = evaluate(sc["train"], sc["train"], tr.y.reindex(sc["train"].index)); b = evaluate(sc["train"], sc["valid"], va.y)
        rows.append((s, *a, *b))
    out = pd.DataFrame(rows, columns=["signal", "tr_flag", "tr_recall", "tr_base", "va_flag", "va_recall", "va_base"])
    out["va_lift"] = out.va_recall / out.va_flag
    # S9 is binary (a few % of hours): reported as lift, never chosen on its own
    eligible = out[(out.signal != "S9") & out.va_flag.between(0.08, 0.12)]
    print(out.round(3).to_string(index=False))
    print("chosen by validation recall:", eligible.sort_values("va_recall").signal.iloc[-1] if len(eligible) else "none eligible")
    print("hours:", len(tr), len(va), len(te), "| events train/valid:", int(tr.y.sum()), int(va.y.sum()))


if __name__ == "__main__":
    main()
