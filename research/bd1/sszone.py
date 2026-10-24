"""Strong_Support zones vs Black Dragon baskets (docs/BD_SSZONE_PLAN.md, registered 23.10.2026).
Two features at basket open, from the zone snapshot of the last H1 bar before the open:
room  = % distance to the nearest zone fully on the losing side (inf if none); block above the train 67th pct
broke = a close beyond a zone on the losing side in the last 24 H1 bars (zones from the snapshot 24h earlier)
The feature is chosen on train only (max kept net), then both test periods are scored.
Usage: python research/bd1/sszone.py"""
import os, sys, json
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guardian_sim as g  # noqa: E402
from vol_lot_map import baskets  # noqa: E402

T = "C:/MT5_JEV_TEST/"
RUNS = {"train": "bdanti_2022_orig", "test1": "bd_robo_orig_bigdep", "test2": "bd_cal_full"}
D = "data/derived/indicators/"
SRC = {"train": "ss_obj_robo.csv", "test1": "ss_obj_robo.csv", "test2": "ss_obj_eg.csv"}


def zones(csv):
    # the zone name can hold a comma ("Strength=Verified, Test Count=3"): bar_time first, six fields from the right
    rec = []
    with open(D + csv, encoding="utf-8", errors="replace") as f:
        next(f)
        for ln in f:
            a = ln.rstrip("\r\n").split(",")
            rec.append([a[0], ",".join(a[1:-6])] + a[-6:])
    z = pd.DataFrame(rec, columns=["bar_time", "name", "type", "time1", "price1", "time2", "price2", "color"])
    z[["price1", "price2"]] = z[["price1", "price2"]].astype(float)
    z = z[z.name.str.contains("Strength=") & (z.price2 > 0)].copy()
    z["t"] = pd.to_datetime(z.bar_time, format="%Y.%m.%d %H:%M").astype("int64") // 10**9
    z["lo"] = z[["price1", "price2"]].min(axis=1)
    z["hi"] = z[["price1", "price2"]].max(axis=1)
    return {t: (x.lo.to_numpy(), x.hi.to_numpy()) for t, x in z.groupby("t")}


def snap(Z, keys, t):
    i = np.searchsorted(keys, t) - 1          # last bar strictly before t
    return Z[keys[i]] if i >= 0 else (np.array([]), np.array([]))


def hourly(csv_src):
    """H1 bars indexed by bar open time (s): open/high/low/close, the same sources as regime_switch.py"""
    if csv_src == "ss_obj_eg.csv":
        m = pd.read_csv("data/raw/black_dragon_1/rates_XAUUSDc_M1_20261016T211917Z/bars.csv")
        m["h"] = m.time // 3600 * 3600
        return m.groupby("h").agg(high=("high", "max"), low=("low", "min"), close=("close", "last"))
    h = pd.read_csv(D + "strong_support_xauusd_h1.csv", usecols=range(5), comment="#")
    h.index = pd.to_datetime(h.time, format="%Y.%m.%d %H:%M").astype("int64") // 10**9
    return h[["high", "low", "close"]]


def net_worst(x, sgn, bt, lo, hi):
    """basket net and worst floating P/L in cents, copied from regime_switch.basket_table (not imported:
    importing that module re-runs it and rewrites its evidence)"""
    t0, t1 = x.t0.min(), x.t1.max()
    i0, i1 = np.searchsorted(bt, t0 - 3599), np.searchsorted(bt, t1, side="right")
    worst = 0.0
    if i1 > i0:
        px = lo[i0:i1] if sgn == 1 else hi[i0:i1]
        fl = np.zeros(i1 - i0)
        for r in x.itertuples():
            act = (bt[i0:i1] + 3600 > r.t0) & (bt[i0:i1] < r.t1)
            fl += np.where(act, sgn * (px - r.p0) * g.K * r.vol, 0)
            fl += np.where(bt[i0:i1] >= r.t1, r.net, 0)
        worst = float(fl.min())
    return x.net.sum(), min(worst, x.net.sum())


def table(k):
    Z = zones(SRC[k]); keys = np.array(sorted(Z)); hb = hourly(SRC[k])
    ct = hb.index.to_numpy(); cv = hb.close.to_numpy(); lo_, hi_ = hb.low.to_numpy(), hb.high.to_numpy()
    pos, _ = g.pair(g.deals(T + RUNS[k] + ".htm")); pos = baskets(pos)
    rows = []
    for b, x in pos.groupby("basket"):
        sgn = 1 if x.side.iloc[0] == "buy" else -1
        t0 = x.t0.min(); p0 = x.sort_values("t0").p0.iloc[0]
        net, worst = net_worst(x, sgn, ct, lo_, hi_)
        lo, hi = snap(Z, keys, t0)
        side = hi < p0 if sgn == 1 else lo > p0
        dist = (p0 - hi[side]) if sgn == 1 else (lo[side] - p0)
        room = float(dist.min() / p0 * 100) if side.any() else np.inf
        # the last 24 H1 bars closed by t0 (open time <= t0 - 1h); PR 38 review: the window had only 23 bars
        i1 = np.searchsorted(ct, t0 - 3600, side="right"); i0 = max(0, i1 - 24)
        c = cv[i0:i1]
        # zones from the snapshot taken at or before the open of the first window bar, and the reference price
        # is the close of the bar BEFORE that snapshot (known when it was written); PR 38 review (P1): it was
        # the close of the bar after the snapshot, i.e. one hour in its future
        lo24, hi24, kz = np.array([]), np.array([]), None
        if i1 > i0:
            j = np.searchsorted(keys, ct[i0], side="right") - 1
            if j >= 0:
                kz = keys[j]; lo24, hi24 = Z[kz]
        jp = np.searchsorted(ct, kz - 3600) if kz is not None else -1
        p24 = cv[jp] if kz is not None and 0 <= jp < len(ct) and ct[jp] == kz - 3600 else np.nan
        broke = False
        if len(c) and len(lo24) and np.isfinite(p24):
            if sgn == 1:
                s = hi24 < p24; broke = bool(s.any() and (c.min() < lo24[s].max()))
            else:
                s = lo24 > p24; broke = bool(s.any() and (c.max() > hi24[s].min()))
        rows.append(dict(t0=t0, net=net, worst=worst, room=room, broke=broke))
    return pd.DataFrame(rows)


def main():
    tabs = {k: table(k) for k in RUNS}
    tr = tabs["train"]
    thr = float(tr.room.replace(np.inf, 1e9).quantile(0.67))   # if over a third has no zone, thr = 1e9 and only those are blocked
    rule = {"room": lambda b: b.room > thr, "broke": lambda b: b.broke}
    score = {f: float(tr[~rule[f](tr)].net.sum()) for f in rule}
    best = max(score, key=score.get)
    res = {"selection": dict(room_threshold_pct=thr, net_kept=score, net_all=float(tr.net.sum()), chosen=best,
                         share_inf_room=float(np.isinf(tr.room).mean()), share_broke=float(tr.broke.mean()))}
    for k, b in tabs.items():
        blk = rule[best](b); kept = b[~blk]
        res[k] = dict(baskets=int(len(b)), blocked=int(blk.sum()), net_all=round(float(b.net.sum())), net_kept=round(float(kept.net.sum())),
                      worst_all=round(float(b.worst.min())), worst_kept=round(float(kept.worst.min())),
                      deep_all=int((b.worst < -5000).sum()), deep_kept=int((kept.worst < -5000).sum()))
        if k != "train":
            r = res[k]; r["pass"] = bool(r["net_kept"] >= r["net_all"] and r["worst_kept"] >= 0.7 * r["worst_all"])
    res["candidate"] = bool(res["test1"]["pass"] and res["test2"]["pass"])
    print(json.dumps(res, indent=1))
    json.dump(res, open("docs/evidence/bd_sszone.json", "w"), indent=1)


if __name__ == "__main__":
    main()
