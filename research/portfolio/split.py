"""Capital split, docs/SPLIT_PLAN.md (registered before running): BD-A on a share w of the capital, the rest
in Bull Scalper (account-1 period only) or cash; no rebalancing. BD-A's path is the exact floating equity
rebuilt from the tester report (guardian_sim.equity_path, validated against the tester), daily low used.
Usage: python research/portfolio/split.py PERIOD REPORT.htm BARS_CSV DEPOSIT
PERIOD: acc (11.11.2025-14.10.2026, with Bull) or y2024 (1.4.2024-31.10.2025, cash only)"""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
import guardian_sim as g  # noqa: E402

WEIGHTS = tuple(float(x) for x in os.environ.get("SPLIT_WEIGHTS", "0.1,0.2,0.3,0.4").split(","))


def bd_daily(rep, bars_csv, dep):
    bars = pd.read_csv(bars_csv)
    pos, left = g.pair(g.deals(rep))
    if left:            # partial (Overlap) exits would leave exposure unaccounted for (review PR #22)
        sys.exit(f"{left} positions could not be paired exactly - the curve would be incomplete")
    tt, lo, hi = g.equity_path(pos, bars.time.values, bars.low.values, bars.high.values, dep)
    # the close path is marked at each bar's CLOSE price (review PR #24), the low path at the worse extreme
    tc, cl, _ = g.equity_path(pos, bars.time.values, bars.close.values, bars.close.values, dep)
    s_lo = pd.Series(lo / dep, index=pd.to_datetime(tt, unit="s"))
    s_cl = pd.Series(cl / dep, index=pd.to_datetime(tc, unit="s"))
    s_hi = pd.Series(hi / dep, index=pd.to_datetime(tt, unit="s"))
    return s_lo, s_hi, s_cl.resample("1D").last().dropna()     # minute low, minute high, daily close (x deposit)


def main():
    period, rep, bars_csv, dep = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
    m_lo, m_hi, close = bd_daily(rep, bars_csv, dep)
    # optional (docs/SPLIT_PLAN.md, "risky part"): SPLIT_SCALE scales the fixed-lot P&L linearly (lot x k), a
    # component that reaches 0 is wiped and stays 0 (stop-out), and SPLIT_START/SPLIT_END fix the calendar
    k = float(os.environ.get("SPLIT_SCALE", "1"))
    if k != 1:
        m_lo, m_hi, close = (1 + k * (x - 1) for x in (m_lo, m_hi, close))
    dead = m_lo.index[m_lo <= 0]
    if len(dead):
        t0 = dead[0]
        m_lo = m_lo.where(m_lo.index < t0, 0.0).clip(lower=0); m_hi = m_hi.where(m_hi.index < t0, 0.0).clip(lower=0)
        close = close.where(close.index < t0.normalize(), 0.0).clip(lower=0)
    if os.environ.get("SPLIT_START"):
        cal = pd.date_range(os.environ["SPLIT_START"], os.environ["SPLIT_END"], freq="D")
        close = close.reindex(cal).ffill().fillna(1.0)
        if len(dead):
            close[close.index >= dead[0].normalize()] = 0.0
        extra = pd.Series(close.values, index=cal)
        m_lo = pd.concat([m_lo, extra[extra.index > m_lo.index[-1]]]); m_hi = pd.concat([m_hi, extra[extra.index > m_hi.index[-1]]])
    days = close.index
    mday = m_lo.index.normalize()
    if period == "acc":
        bull = pd.read_csv("data/derived/portfolio_curves.csv", index_col=0, parse_dates=True).bull
        bull_eq = (1 + bull.reindex(days).fillna(0).cumsum())          # fixed lot: additive on the starting deposit
    # DBMF (addendum, docs/SPLIT_PLAN.md): adjusted close, rebased to 1 on the first day, carried over non-US days
    r = json.load(open("data/raw/survey4/DBMF.json"))["chart"]["result"][0]
    dbmf = pd.Series(r["indicators"]["adjclose"][0]["adjclose"], index=pd.to_datetime(r["timestamp"], unit="s").normalize()).dropna()
    dbmf = dbmf[~dbmf.index.duplicated()].reindex(days, method="ffill")
    dbmf_eq = dbmf / dbmf.iloc[0]
    others = ("bull", "cash", "dbmf") if period == "acc" else ("cash", "dbmf")
    out = {}
    for w in WEIGHTS:
        for other in others:
            base = {"bull": bull_eq if period == "acc" else None, "cash": pd.Series(1.0, index=days), "dbmf": dbmf_eq}[other]
            rest = (1 - w) * base
            # Bull's intraday order is unknown (review PR #23): the low uses the worse of its balance
            # before and after the day, the close uses the close
            rest_low = np.minimum(rest, rest.shift(1).fillna(1 - w))
            tot_close = w * close + rest
            # drawdown in time order at minute level (review PR #24): the peak includes BD-A's floating highs
            # of EARLIER minutes (the good extreme), each minute's low is measured against it; the rest of the
            # portfolio enters with its conservative value of that day
            r_m = rest_low.reindex(mday).values
            t_lo = w * m_lo.values + r_m; t_hi = w * m_hi.values + r_m
            peak = np.maximum.accumulate(np.concatenate([[1.0], t_hi[:-1]]))
            # also every earlier day-close of the whole portfolio (review PR #24): the peak before each minute
            close_peak_prev = tot_close.cummax().shift(1).fillna(1.0).reindex(mday).values
            peak = np.maximum(peak, close_peak_prev)
            dd = float(min((t_lo / peak - 1).min(), (tot_close / tot_close.cummax().clip(lower=1.0) - 1).min()) * 100)
            yrs = (days[-1] - days[0]).days / 365.25
            ann = float(tot_close.iloc[-1] ** (1 / yrs) - 1) * 100
            out[f"w={w} rest={other}"] = {"annual_pct": round(ann, 1), "max_dd_pct": round(dd, 1), "final": round(float(tot_close.iloc[-1]), 3)}
            print(period, w, other, out[f"w={w} rest={other}"], flush=True)
    tag = os.environ.get("SPLIT_TAG", "")
    json.dump(out, open(f"docs/evidence/split_{period}{tag}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
