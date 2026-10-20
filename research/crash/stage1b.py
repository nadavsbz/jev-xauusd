"""Stage 1b of docs/CRASH_DETECT_PLAN.md (registered 20.10.2026): technical-analysis signals the user proposed
(Bollinger bands, support/resistance, trend strength) on the SAME target, data and periods as stage 1, so the
results are comparable. Every feature of bar h uses bars up to and including h only.

  T1  Bollinger squeeze: bandwidth (20 H1 bars, 2 sigma) as a trailing percentile, LOW = flagged
  T2  Bollinger stretch: |close - mid| / sigma (20 bars), HIGH = flagged
  T3  support/resistance: distance of the close to the 20-trading-day high or low (whichever is nearer),
      in units of the average 24h range; NEAR (or through) = flagged
  T4  trend strength: ADX(14) on H1, HIGH = flagged
  T5  momentum extreme: |RSI(14) - 50| on H1, HIGH = flagged
  T6  logistic regression on T1..T5 (fitted on the training period only)
Benchmarks reported from stage 1 on the same rows: S2 (HAR) for comparison only.

Usage:
  python research/crash/stage1b.py DATA_DIR            # train + validation
  python research/crash/stage1b.py DATA_DIR --test T3  # the ONE chosen signal on the test period"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from stage1 import hourly, future_range, split, evaluate, fit_scores, trailing_pct, EVENT_PCT, HORIZON, DAYS


def adx(g, n=14):
    up = g.high.diff(); dn = -g.low.diff()
    pdm = np.where((up > dn) & (up > 0), up, 0.0); ndm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = pd.concat([g.high - g.low, (g.high - g.close.shift()).abs(), (g.low - g.close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / n, adjust=False).mean()
    pdi = 100 * pd.Series(pdm, index=g.index).ewm(alpha=1 / n, adjust=False).mean() / atr
    ndi = 100 * pd.Series(ndm, index=g.index).ewm(alpha=1 / n, adjust=False).mean() / atr
    dx = 100 * (pdi - ndi).abs() / (pdi + ndi).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False).mean()


def rsi(c, n=14):
    d = c.diff(); up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean(); dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def build(data):
    g = hourly(data, "xauusd")
    f = pd.DataFrame(index=g.index)
    fr = future_range(g, HORIZON)
    f["y"] = (fr / g.close * 100 >= EVENT_PCT).astype(float)
    f.loc[fr.isna(), "y"] = np.nan
    mid = g.close.rolling(20).mean(); sd = g.close.rolling(20).std()
    f["T1"] = -trailing_pct(4 * sd / mid, DAYS * 23)                  # negated: a squeeze scores high
    f["T2"] = ((g.close - mid) / sd).abs()
    hi20 = g.high.rolling("28D").max(); lo20 = g.low.rolling("28D").min()   # ~20 trading days, clock window
    adr = (g.high.rolling("24h").max() - g.low.rolling("24h").min()).rolling("20D").mean()
    dist = np.minimum((hi20 - g.close).clip(lower=0), (g.close - lo20).clip(lower=0)) / adr
    f["T3"] = -dist
    f["T4"] = adx(g)
    f["T5"] = (rsi(g.close) - 50).abs()
    one = (g.high - g.low) / g.close
    f["har1"], f["har24"], f["har120"] = (np.log(one + 1e-6), np.log(one.rolling("24h").mean() + 1e-6),
                                          np.log(one.rolling("120h").mean() + 1e-6))
    return f


def main():
    f = build(sys.argv[1])
    tr, va, te = split(f)
    frames = {"train": tr, "valid": va, "test": te}
    scores = {s: {k: v[s] for k, v in frames.items()} for s in ["T1", "T2", "T3", "T4", "T5"]}
    scores["T6"] = fit_scores(tr, frames, ["T1", "T2", "T3", "T4", "T5"], "T6")
    scores["S2_bench"] = fit_scores(tr, frames, ["har1", "har24", "har120"], "S2")
    if "--test" in sys.argv:
        s = sys.argv[sys.argv.index("--test") + 1]
        fr_, rc, base = evaluate(scores[s]["train"], scores[s]["test"], te.y)
        b = evaluate(scores["S2_bench"]["train"], scores["S2_bench"]["test"], te.y)
        print(f"TEST {s}: flagged {fr_:.1%} of hours, recall {rc:.1%}, base {base:.1%} | S2 bench: flagged {b[0]:.1%}, recall {b[1]:.1%}")
        return
    rows = []
    for s, sc in scores.items():
        a = evaluate(sc["train"], sc["train"], tr.y.reindex(sc["train"].index)); b = evaluate(sc["train"], sc["valid"], va.y)
        rows.append((s, *a, *b))
    out = pd.DataFrame(rows, columns=["signal", "tr_flag", "tr_recall", "tr_base", "va_flag", "va_recall", "va_base"])
    out["va_lift"] = out.va_recall / out.va_flag
    eligible = out[(out.signal != "S2_bench") & out.va_flag.between(0.08, 0.12)]
    print(out.round(3).to_string(index=False))
    print("chosen by validation recall:", eligible.sort_values("va_recall").signal.iloc[-1] if len(eligible) else "none eligible")


if __name__ == "__main__":
    main()
