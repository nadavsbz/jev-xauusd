"""Bull Scalper realised P&L per day against account 1's deep-basket days (MAE <= -10%), and the
correlation of daily results (docs/DAY_20261016_SUMMARY.md, section 2). Realised P&L only: a day
with an open floating loss and no close shows 0. Day = calendar date of each side's own server
clock (EGlobal and account 1: Central European; RoboForex: UTC+3) - ASSUMED close enough by day.
Usage: python research/bull/crash_overlap.py REPORT.htm DEPOSIT OUT_JSON"""
import hashlib, json, re, sys
import pandas as pd


def daily(report, deposit):
    raw = open(report, "rb").read(); text = raw.decode("utf-16")
    cells = [[re.sub("<.*?>", "", x).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
             for r in re.findall(r"<tr[^>]*>(.*?)</tr>", text, re.S)]
    d = pd.DataFrame([c for c in cells if len(c) == 13 and re.match(r"\d{4}\.\d\d\.\d\d", c[0])],
                     columns=["time", "deal", "symbol", "type", "dir", "volume", "price", "order",
                              "commission", "swap", "profit", "balance", "comment"])
    for c in ["commission", "swap", "profit"]:
        d[c] = pd.to_numeric(d[c].str.replace(" ", "").str.replace(",", ""), errors="coerce")
    d = d[d.type != "balance"]
    t = pd.to_datetime(d.time, format="%Y.%m.%d %H:%M:%S").dt.normalize()
    return (d.profit + d.commission + d.swap).groupby(t).sum() / deposit * 100, hashlib.sha256(raw).hexdigest()


def main():
    rep, dep, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    bull, sha = daily(rep, dep)
    o = pd.read_csv("data/derived/bd1/clusters_strict.csv")
    o["day"] = pd.to_datetime(o.t0, unit="s").dt.normalize()
    acc = o.groupby("day").pnl_pct.sum()
    deep = sorted(set(o.day[o.mae_pct <= -10]))
    on_deep = bull.reindex(deep).fillna(0.0)
    # every weekday where both series exist, a day without a closed trade counted as 0
    days = pd.bdate_range(max(acc.index.min(), bull.index.min()), min(acc.index.max(), bull.index.max()))
    both = pd.concat([acc.reindex(days).fillna(0), bull.reindex(days).fillna(0)], axis=1, keys=["acc", "bull"])
    res = {"report": rep.split("\\")[-1], "report_sha256": sha,
           "bull_daily_pct_on_account1_deep_days": {str(k.date()): round(float(v), 3) for k, v in on_deep.items()},
           "deep_days": len(deep), "bull_losing_deep_days": int((on_deep < 0).sum()),
           "common_days": len(both), "daily_correlation": round(float(both.corr().iloc[0, 1]), 3)}
    json.dump(res, open(out, "w"), indent=1)
    print({k: res[k] for k in ["deep_days", "bull_losing_deep_days", "common_days", "daily_correlation"]})


if __name__ == "__main__":
    main()
