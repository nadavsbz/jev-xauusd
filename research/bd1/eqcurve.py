"""Equity-curve filter for Black Dragon (docs/BD_EQCURVE_PLAN.md, registered 23.10.2026).
Shadow curve = cumulative net of all baskets by close time; a new basket is blocked if the curve before its
open is below the mean of the last N curve points. N in {20, 50, 100} is chosen on train only.
Usage: python research/bd1/eqcurve.py"""
import os, sys, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sszone as sz  # noqa: E402  (main() is guarded; reuses the basket net / worst definition)

SRC = {"train": "ss_obj_robo.csv", "test1": "ss_obj_robo.csv", "test2": "ss_obj_eg.csv"}


def table(k):
    hb = sz.hourly(SRC[k]); ct = hb.index.to_numpy(); lo, hi = hb.low.to_numpy(), hb.high.to_numpy()
    pos, _ = sz.g.pair(sz.g.deals(sz.T + sz.RUNS[k] + ".htm")); pos = sz.baskets(pos)
    rows = []
    for b, x in pos.groupby("basket"):
        sgn = 1 if x.side.iloc[0] == "buy" else -1
        net, worst = sz.net_worst(x, sgn, ct, lo, hi)
        rows.append(dict(t0=x.t0.min(), t1=x.t1.max(), net=net, worst=worst))
    return pd.DataFrame(rows).sort_values("t0").reset_index(drop=True)


def blocked(b, n):
    c = b.sort_values("t1"); t1 = c.t1.to_numpy(); curve = np.cumsum(c.net.to_numpy())
    blk = np.zeros(len(b), bool)
    for i, t0 in enumerate(b.t0.to_numpy()):
        j = np.searchsorted(t1, t0)               # baskets closed strictly before t0... (t1 < t0)
        if j >= n:
            blk[i] = curve[j - 1] < curve[j - n:j].mean()
    return blk


def main():
    tabs = {k: table(k) for k in sz.RUNS}
    tr = tabs["train"]
    score = {n: float(tr[~blocked(tr, n)].net.sum()) for n in (20, 50, 100)}
    best = max(score, key=score.get)
    res = {"selection": dict(net_kept_by_n=score, net_all=float(tr.net.sum()), chosen_n=best)}
    for k, b in tabs.items():
        blk = blocked(b, best); kept = b[~blk]
        res[k] = dict(baskets=int(len(b)), blocked=int(blk.sum()), net_all=round(float(b.net.sum())), net_kept=round(float(kept.net.sum())),
                      worst_all=round(float(b.worst.min())), worst_kept=round(float(kept.worst.min())),
                      deep_all=int((b.worst < -5000).sum()), deep_kept=int((kept.worst < -5000).sum()))
        if k != "train":
            r = res[k]; r["pass"] = bool(r["net_kept"] >= r["net_all"] and r["worst_kept"] >= 0.7 * r["worst_all"])
    res["candidate"] = bool(res["test1"]["pass"] and res["test2"]["pass"])
    print(json.dumps(res, indent=1))
    json.dump(res, open("docs/evidence/bd_eqcurve.json", "w"), indent=1)


if __name__ == "__main__":
    main()
