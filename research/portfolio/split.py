"""Capital split, docs/SPLIT_PLAN.md (registered before running): BD-A on a share w of the capital, the rest
in Bull Scalper (account-1 period only) or cash; no rebalancing. BD-A's path is the exact floating equity
rebuilt from the tester report (guardian_sim.equity_path, validated against the tester), daily low used.
Usage: python research/portfolio/split.py PERIOD REPORT.htm BARS_CSV DEPOSIT
PERIOD: acc (11.11.2025-14.10.2026, with Bull) or y2024 (1.4.2024-31.10.2025, cash only)"""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
import guardian_sim as g  # noqa: E402

WEIGHTS = (0.1, 0.2, 0.3, 0.4)


def bd_daily(rep, bars_csv, dep):
    bars = pd.read_csv(bars_csv)
    pos, left = g.pair(g.deals(rep))
    if left:            # partial (Overlap) exits would leave exposure unaccounted for (review PR #22)
        sys.exit(f"{left} positions could not be paired exactly - the curve would be incomplete")
    tt, lo, _ = g.equity_path(pos, bars.time.values, bars.low.values, bars.high.values, dep)
    s = pd.Series(lo / dep, index=pd.to_datetime(tt, unit="s"))
    return s.resample("1D").min().dropna(), s.resample("1D").last().dropna()   # daily low, daily close (x deposit)


def main():
    period, rep, bars_csv, dep = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
    low, close = bd_daily(rep, bars_csv, dep)
    days = close.index
    if period == "acc":
        bull = pd.read_csv("data/derived/portfolio_curves.csv", index_col=0, parse_dates=True).bull
        bull_eq = (1 + bull.reindex(days).fillna(0).cumsum())          # fixed lot: additive on the starting deposit
    out = {}
    for w in WEIGHTS:
        for other in (("bull", "cash") if period == "acc" else ("cash",)):
            rest = (1 - w) * (bull_eq if other == "bull" else pd.Series(1.0, index=days))
            tot_low = w * low + rest; tot_close = w * close + rest
            # the day's low against the peak up to the PREVIOUS close (no same-day look-ahead, review PR #22),
            # and each close against the running peak of closes
            prev_peak = tot_close.cummax().shift(1).fillna(1.0).clip(lower=1.0)
            dd = float(min((tot_low / prev_peak - 1).min(), (tot_close / tot_close.cummax().clip(lower=1.0) - 1).min()) * 100)
            yrs = (days[-1] - days[0]).days / 365.25
            ann = float(tot_close.iloc[-1] ** (1 / yrs) - 1) * 100
            out[f"w={w} rest={other}"] = {"annual_pct": round(ann, 1), "max_dd_pct": round(dd, 1), "final": round(float(tot_close.iloc[-1]), 3)}
            print(period, w, other, out[f"w={w} rest={other}"], flush=True)
    json.dump(out, open(f"docs/evidence/split_{period}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
