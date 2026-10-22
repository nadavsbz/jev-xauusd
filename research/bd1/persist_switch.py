"""Daily persistence (variance-ratio) switch for Black Dragon (docs/BD_PERSIST_PLAN.md, registered 22.10.2026).
Same baskets, bars and criterion as regime_switch.py; a DAY is blocked (no new baskets) if the variance ratio
measured on the 120 H1 bars up to the end of the previous day exceeds the 67th percentile of all training days.
Usage: python research/bd1/persist_switch.py"""
import os, sys, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import regime_switch as rs  # noqa: E402  (re-uses its bars and basket tables; it also re-writes its own evidence)

def vr_daily(hb, q, n=120):
    r = np.log(hb.close).diff().to_numpy()
    out = np.full(len(r), np.nan)
    for i in range(n + q, len(r)):
        x = r[i - n + 1:i + 1]
        v1 = np.var(x, ddof=1)
        rq = np.convolve(x, np.ones(q), "valid")
        out[i] = np.var(rq, ddof=1) / (q * v1) if v1 > 0 else np.nan
    s = pd.Series(out, index=pd.to_datetime(hb.t, unit="s"))
    return s.groupby(s.index.normalize()).last()            # value at the last bar of each day

FEAT = {src: pd.DataFrame({"VR6": vr_daily(hb, 6), "VR24": vr_daily(hb, 24)}) for src, hb in rs.H.items()}

def day_table(run, src):
    pos, _ = rs.g.pair(rs.g.deals(rs.T + run + ".htm")); pos = rs.baskets(pos)
    b = rs.basket_table(run, src)
    d0 = pos.groupby("basket").t0.min().sort_index().to_numpy()
    b["day"] = pd.to_datetime(d0, unit="s").normalize()
    f = FEAT[src]
    prev = [f[f.index < d].iloc[-1] if (f.index < d).any() else pd.Series(dtype=float) for d in b.day]
    return pd.concat([b.reset_index(drop=True), pd.DataFrame(prev).reset_index(drop=True)], axis=1)

tabs = {k: day_table(r, "eg" if k == "test2" else "ss") for k, r in rs.RUNS.items()}
ftr = FEAT["ss"][(FEAT["ss"].index >= "2022-01-01") & (FEAT["ss"].index < "2024-04-01")]
thr = {f: float(ftr[f].quantile(0.67)) for f in ("VR6", "VR24")}
tr = tabs["train"]
score = {f: float(tr[~(tr[f] > thr[f])].net.sum()) for f in thr}
best = max(score, key=score.get)
res = {"train": dict(thresholds=thr, net_kept_by_feature=score, net_all=float(tr.net.sum()), chosen=best)}
for k in ("train", "test1", "test2"):
    b = tabs[k]; blk = b[best] > thr[best]
    res[k] = dict(res.get(k, {}), feature=best, baskets=int(len(b)), blocked=int(blk.sum()),
                  net_all=round(float(b.net.sum()), 2), net_switch=round(float(b[~blk].net.sum()), 2),
                  worst_all=round(float(b.worst.min()), 2), worst_switch=round(float(b[~blk].worst.min()), 2),
                  deep_all=int((b.worst < -5000).sum()), deep_switch=int((b[~blk].worst < -5000).sum()),
                  per_feature={f: dict(net_switch=round(float(b[~(b[f] > thr[f])].net.sum()), 2),
                                        worst_switch=round(float(b[~(b[f] > thr[f])].worst.min()), 2)) for f in thr})
for k in ("test1", "test2"):
    r = res[k]; r["pass_net"] = r["net_switch"] >= r["net_all"]; r["pass_worst"] = r["worst_switch"] >= 0.7 * r["worst_all"]
res["verdict"] = all(res[k]["pass_net"] and res[k]["pass_worst"] for k in ("test1", "test2"))
print(json.dumps(res, indent=1, ensure_ascii=False, default=str))
json.dump(res, open("docs/evidence/bd_persist_switch.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
