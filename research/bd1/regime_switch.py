"""Weekly market-regime switch for Black Dragon (docs/BD_REGIME_PLAN.md, registered 22.10.2026).
Baskets of three fixed-lot tester runs; a week is blocked (no new baskets) if a feature measured up to the
end of the previous week exceeds the 67th percentile of the training weeks (2022-24).
Usage: python research/bd1/regime_switch.py"""
import os, sys, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guardian_sim as g  # noqa: E402
from vol_lot_map import baskets  # noqa: E402

T = "C:/MT5_JEV_TEST/"
RUNS = {"train": "bdanti_2022_orig", "test1": "bd_robo_orig_bigdep", "test2": "bd_cal_full"}

h = pd.read_csv("data/derived/indicators/strong_support_xauusd_h1.csv", usecols=range(5), comment="#")
h["t"] = pd.to_datetime(h.time, format="%Y.%m.%d %H:%M").astype("int64") // 10**9
h = h[["t", "open", "high", "low", "close"]]
m = pd.read_csv("data/raw/black_dragon_1/rates_XAUUSDc_M1_20261016T211917Z/bars.csv")
m["h"] = m.time // 3600 * 3600
e = m.groupby("h").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last")).reset_index().rename(columns={"h": "t"})
H = {"ss": h, "eg": e}

def daily(hb):
    d = hb.assign(day=pd.to_datetime(hb.t, unit="s").dt.normalize()).groupby("day").agg(
        high=("high", "max"), low=("low", "min"), close=("close", "last"))
    pc = d.close.shift()
    tr = pd.concat([d.high - d.low, (d.high - pc).abs(), (d.low - pc).abs()], axis=1).max(axis=1)
    f = pd.DataFrame(index=d.index)
    f["vol"] = tr.rolling(10).mean() / d.close * 100
    f["expand"] = tr.rolling(5).mean() / tr.rolling(40).mean()
    f["trend"] = (d.close / d.close.shift(20) - 1).abs() / (tr.rolling(20).mean() / d.close * np.sqrt(20))
    return f

FEAT = {k: daily(v) for k, v in H.items()}

def week_feats(weeks, src):
    f = FEAT[src]
    rows = []
    for w in weeks:
        prev = f[f.index < w]
        rows.append(prev.iloc[-1] if len(prev) else pd.Series(dtype=float))
    return pd.DataFrame(rows, index=weeks)

def basket_table(run, src):
    pos, _ = g.pair(g.deals(T + run + ".htm")); pos = baskets(pos)
    hb = H[src]; bt = hb.t.to_numpy(); lo = hb.low.to_numpy(); hi = hb.high.to_numpy()
    rows = []
    for b, x in pos.groupby("basket"):
        sgn = 1 if x.side.iloc[0] == "buy" else -1
        t0, t1 = x.t0.min(), x.t1.max()
        i0, i1 = np.searchsorted(bt, t0 - 3599), np.searchsorted(bt, t1, side="right")
        worst = 0.0
        if i1 > i0:
            px = lo[i0:i1] if sgn == 1 else hi[i0:i1]
            fl = np.zeros(i1 - i0)
            for r in x.itertuples():
                act = (bt[i0:i1] + 3600 > r.t0) & (bt[i0:i1] < r.t1)
                fl += np.where(act, sgn * (px - r.p0) * g.K * r.vol, 0)
                fl += np.where(bt[i0:i1] >= r.t1, r.net, 0)          # realised cash stays in the basket (PR 37 review)
            worst = float(fl.min())
        d0 = pd.to_datetime(t0, unit="s").normalize()
        rows.append(dict(week=d0 - pd.Timedelta(days=d0.weekday()), net=x.net.sum(), worst=min(worst, x.net.sum())))
    return pd.DataFrame(rows)

res = {}
tabs = {k: basket_table(r, "eg" if k == "test2" else "ss") for k, r in RUNS.items()}
for k, b in tabs.items():
    wf = week_feats(sorted(b.week.unique()), "eg" if k == "test2" else "ss")
    tabs[k] = b.join(wf, on="week")
tr = tabs["train"]
# all calendar weeks of the training period, not only weeks with a basket (PR 37 review)
allw = pd.date_range("2022-01-03", "2024-03-25", freq="W-MON")
wtr = week_feats(list(allw), "ss")
thr = {f: float(wtr[f].quantile(0.67)) for f in ("vol", "expand", "trend")}
score = {f: float(tr[~(tr[f] > thr[f])].net.sum()) for f in thr}
best = max(score, key=score.get)
res["train"] = dict(thresholds=thr, net_kept_by_feature=score, net_all=float(tr.net.sum()), chosen=best)
for k in ("train", "test1", "test2"):
    b = tabs[k]; blk = b[best] > thr[best]; wk = b.drop_duplicates("week")
    res[k] = dict(res.get(k, {}), feature=best, weeks=int(len(wk)), weeks_blocked=int((wk[best] > thr[best]).sum()),
                  baskets=int(len(b)), net_all=round(float(b.net.sum()), 2), net_switch=round(float(b[~blk].net.sum()), 2),
                  worst_all=round(float(b.worst.min()), 2), worst_switch=round(float(b[~blk].worst.min()), 2),
                  deep_all=int((b.worst < -5000).sum()), deep_switch=int((b[~blk].worst < -5000).sum()),
                  per_feature={f: dict(net_switch=round(float(b[~(b[f] > thr[f])].net.sum()), 2),
                                        worst_switch=round(float(b[~(b[f] > thr[f])].worst.min()), 2)) for f in thr})
for k in ("test1", "test2"):
    r = res[k]
    r["pass_net"] = r["net_switch"] >= r["net_all"]
    r["pass_worst"] = r["worst_switch"] >= 0.7 * r["worst_all"]
res["verdict"] = all(res[k]["pass_net"] and res[k]["pass_worst"] for k in ("test1", "test2"))
print(json.dumps(res, indent=1, ensure_ascii=False, default=str))
json.dump(res, open("docs/evidence/bd_regime_switch.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
