"""t433 (docs/prereg/research_t433.md): BTC-ETH network-value pair, weekly. Coin Metrics community CSVs (frozen by SHA-256).
Score = log(sum7 AdrActCnt / Cap(Sunday)) - median(prev 52 weeks). Tuesday 00:00 UTC rebalance (PriceUSD proxy):
0.5 long the higher score, 0.5 short the other. Gate A on 2018-2022, items 1-9 of t432. Usage: py -3.12 research/stable/t433.py"""
import os, json, hashlib, urllib.request
import numpy as np, pandas as pd

RAW = "data/raw/t433"; os.makedirs(RAW, exist_ok=True)


def load(a):
    f = f"{RAW}/{a}.csv"
    if not os.path.exists(f):
        b = urllib.request.urlopen(urllib.request.Request(f"https://raw.githubusercontent.com/coinmetrics/data/master/csv/{a}.csv",
                                                           headers={"User-Agent": "research-client"}), timeout=300).read()
        open(f, "wb").write(b)
    sha = hashlib.sha256(open(f, "rb").read()).hexdigest()
    d = pd.read_csv(f, usecols=lambda c: c in ("time", "AdrActCnt", "CapMrktCurUSD", "PriceUSD"), low_memory=False)
    d["time"] = pd.to_datetime(d.time).dt.tz_localize(None); return d.set_index("time"), sha


def weekly(d):
    d = d["2016-06-01":"2026-11-01"]
    wk = d.AdrActCnt.resample("W-SUN").agg(["sum", "count"])                 # Mon..Sun weeks, labelled Sunday
    cap = d.CapMrktCurUSD.reindex(wk.index)
    nv = np.log(wk["sum"] / cap).where(wk["count"] == 7)
    med = nv.rolling(52, min_periods=52).median().shift(1)                   # previous 52 full weeks, current excluded
    valid = nv.notna() & nv.shift(1).rolling(52).count().eq(52)
    return (nv - med).where(valid)


if __name__ == "__main__":
    (B, sb), (E, se) = load("btc"), load("eth")
    sB, sE = weekly(B), weekly(E)
    tue = sB.index + pd.Timedelta(days=2)                                     # decision Tuesday 00:00 after the Sunday week
    pB, pE = B.PriceUSD, E.PriceUSD
    rows = []
    for i, (wsun, t0) in enumerate(zip(sB.index, tue)):
        t1 = t0 + pd.Timedelta(days=7)
        if t1 not in pB.index or t0 not in pB.index or t1 not in pE.index or t0 not in pE.index: continue
        a, b = sB.iloc[i], sE.iloc[i]
        rb, re = pB[t1] / pB[t0] - 1, pE[t1] / pE[t0] - 1
        if pd.isna(a) or pd.isna(b): side, g = "none", 0.0
        elif a > b: side, g = "longBTC", 0.5 * rb - 0.5 * re
        elif b > a: side, g = "longETH", 0.5 * re - 0.5 * rb
        else: side, g = "flat", 0.0
        rows.append(dict(t0=t0, year=t0.year, side=side, gross_bp=g * 1e4))
    T = pd.DataFrame(rows); T.to_csv(f"{RAW}/t433_weeks.csv", index=False)
    A = T[T.year.between(2018, 2022)].copy(); P = A[A.side.isin(["longBTC", "longETH"])].copy()
    P["net"] = P.gross_bp - 15; P["str"] = P.gross_bp - 25
    yr = P.groupby("year").net.sum()                                          # yearly net in bp (non-compounded sum)
    tot = P.gross_bp.sum(); top10 = P.gross_bp.nlargest(10).sum(); y2021 = P[P.year.isin([2020, 2021])].gross_bp.sum()
    t_stat = P.net.mean() / (P.net.std(ddof=1) / np.sqrt(len(P)))
    side_net = P.groupby("side").net.sum(); side_share = P.side.value_counts(normalize=True)
    g = {"1_coverage>=98%": len(P) / len(A) >= 0.98,
         "2_n>=250_and_48/yr": len(P) >= 250 and P.groupby("year").size().min() >= 48,
         "3_gross_mean>=30bp": P.gross_bp.mean() >= 30,
         "4_net_mean>0_t>=2": P.net.mean() > 0 and t_stat >= 2.0,
         "5_years>=4/5_none<-5%": (yr > 0).sum() >= 4 and yr.min() > -500,
         "6_both_sides": bool((side_net > 0).all() and len(side_net) == 2 and side_share.min() >= 0.30),
         "7_top10<=25%": tot > 0 and top10 / tot <= 0.25,
         "8_2020-21<=50%": tot > 0 and y2021 / tot <= 0.50,
         "9_stress>0": P.str.sum() > 0}
    out = dict(sha256=dict(btc=sb, eth=se), tag="current-revised-history", weeks=len(A), weeks_pos=len(P),
               gross_mean_bp=round(P.gross_bp.mean(), 2), net_mean_bp=round(P.net.mean(), 2), t=round(t_stat, 2),
               net_by_year_bp={int(k): round(v, 1) for k, v in yr.items()}, side_net_bp={k: round(v, 1) for k, v in side_net.items()},
               side_share={k: round(v, 3) for k, v in side_share.items()}, top10_share=round(top10 / tot, 3) if tot else None,
               share_2020_21=round(y2021 / tot, 3) if tot else None, stress_sum_bp=round(P.str.sum(), 1),
               gate={k: bool(v) for k, v in g.items()}, item10_revisions="UNKNOWN (no vintages)", PASS_A=bool(all(g.values())))
    json.dump(out, open("docs/evidence/t433.json", "w"), indent=1); print(json.dumps(out, indent=1))
