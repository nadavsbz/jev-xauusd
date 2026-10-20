"""Gold trend following, docs/TREND_GOLD_PLAN.md (registered before running).
Usage: python research/trend/gold_trend.py DATA_DIR [--test]"""
import glob, os, sys
import numpy as np, pandas as pd

SEL_END, TEST_START = pd.Timestamp("2022-01-01"), pd.Timestamp("2022-01-01")
LS, TARGET, CAP, SPREAD, SWAP = (50, 100, 200), 0.10, 2.0, 0.30, 0.04


def daily(data):
    fs = sorted(glob.glob(os.path.join(data, "xauusd_h1_*.csv")))
    d = pd.concat([pd.read_csv(f) for f in fs]).drop_duplicates("timestamp")
    d["t"] = pd.to_datetime(d.timestamp, unit="ms")
    return d.set_index("t").sort_index().close.resample("1D").last().dropna()


def run(c, L):
    r = c.pct_change()
    # observations per year from the data itself (review: the daily series also has Sundays)
    ppy = len(c) / ((c.index[-1] - c.index[0]).days / 365.25)
    sig = np.sign(c - c.rolling(L).mean()).shift(1)                      # decided at yesterday's close
    vol = r.rolling(20).std().shift(1) * np.sqrt(ppy)
    expo = (TARGET / vol).clip(upper=CAP) * sig                           # share of capital, signed
    turn = expo.diff().abs()
    days = pd.Series(c.index, index=c.index).diff().dt.days               # swap accrues by calendar time held
    cost = turn * SPREAD / c.shift(1) + expo.abs() * SWAP * days / 365
    ret = (expo * r - cost).dropna()
    return ret


def stats(ret):
    eq = (1 + ret).cumprod(); dd = (eq / eq.cummax() - 1).min()
    yrs = (ret.index[-1] - ret.index[0]).days / 365.25
    ann = eq.iloc[-1] ** (1 / yrs) - 1
    ppy = len(ret) / yrs
    sh = ret.mean() / ret.std() * np.sqrt(ppy) if ret.std() > 0 else 0
    return {"annual_pct": round(ann * 100, 1), "max_dd_pct": round(dd * 100, 1), "sharpe": round(sh, 2),
            "worst_year_pct": round(ret.groupby(ret.index.year).apply(lambda x: (1 + x).prod() - 1).min() * 100, 1)}


def main():
    c = daily(sys.argv[1])
    sel = {L: stats(run(c, L)[lambda s: s.index < SEL_END]) for L in LS}
    for L, s in sel.items():
        print("selection 2015-2021 L =", L, s)
    best = max(sel, key=lambda L: sel[L]["sharpe"])
    print("chosen L:", best)
    if "--test" in sys.argv:
        ret = run(c, best)
        t = ret[ret.index >= TEST_START]
        print("TEST 2022-2026 L =", best, stats(t))
        t.to_csv("docs/evidence/trend_gold_test_daily.csv")


if __name__ == "__main__":
    main()
