"""Chart analysis inside a deep basket: cut at -10% or hold? (docs/BD_TA_EXIT_PLAN.md, registered 21.10.2026)
Sample: tester run bd_robo_orig_bigdep (BD3 XAUUSD, original set, fixed 0.01 lot, no guard), 4.2024-10.2025,
with the same server's M1 bars. Depth in % of a balance of 6,000 per 0.01 lot (lot ratio 1:600k).
Check: account 1's real baskets that reached -10% (paths_strict.npz)."""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "crash"))
from guardian_sim import deals, pair
from stage1b import adx, rsi

K, CAP, T, G, SLIP = 100.0, 6000.0, 10.0, 15.0, 1.3
REP = "C:/MT5_JEV_TEST/bd_robo_orig_bigdep.htm"
BARS = "data/raw/black_dragon_3/rates_XAUUSD_M1_20261016T160347Z/bars.csv"
SPLIT = pd.Timestamp("2025-01-01").timestamp()
FEATS = ["F1", "F2", "F3", "F4", "F5", "F6"]


def hourly_feats(b):
    m = b.set_index(pd.to_datetime(b.time, unit="s"))
    g = m.resample("1h").agg({"open": "first", "high": "max", "low": "min", "close": "last"}).dropna()
    mid = g.close.rolling(20).mean(); sd = g.close.rolling(20).std()
    adr = (g.high.rolling("24h").max() - g.low.rolling("24h").min()).rolling("20D").mean()
    f = pd.DataFrame(index=g.index)
    f["z"] = (g.close - mid) / sd
    f["bw"] = (4 * sd / mid).rolling(720, min_periods=200).rank(pct=True)
    f["to_lo"] = (g.close - g.low.rolling("28D").min()) / adr
    f["to_hi"] = (g.high.rolling("28D").max() - g.close) / adr
    f["adx"] = adx(g); f["rsi"] = rsi(g.close); f["mom4"] = (g.close - g.close.shift(4)) / adr
    f["tclose"] = (g.index.astype("int64") // 10**9) + 3600          # known at the bar's close
    return f.dropna()


def feats_at(f, tm, sgn):
    i = np.searchsorted(f.tclose.values, tm, side="right") - 1
    r = f.iloc[i]
    return dict(F1=-sgn * r.z, F2=r.bw, F3=-(r.to_lo if sgn > 0 else r.to_hi), F4=r.adx, F5=-sgn * (r.rsi - 50),
                F6=-sgn * r.mom4)


def tester_events():
    b = pd.read_csv(BARS); bt = b.time.values; lo = b.low.values; hi = b.high.values; sp = b.spread.values * 0.01
    pos = pair(deals(REP))[0].sort_values("t0").reset_index(drop=True)
    cid = np.zeros(len(pos), int); end = -1; c = -1
    for i, r in enumerate(pos.itertuples()):
        if r.t0 >= end:
            c += 1
        end = max(end, r.t1); cid[i] = c
    pos["cid"] = cid; ev = []
    for c, g in pos.groupby("cid"):
        t0, t1 = g.t0.min(), g.t1.max()
        a = np.searchsorted(bt, t0 - t0 % 60); z = np.searchsorted(bt, t1 - t1 % 60, side="right")
        if z - a < 2:
            continue
        tt = bt[a:z]; fl = np.zeros(z - a)
        for p in g.itertuples():
            on = (tt + 60 > p.t0) & (tt < p.t1 - p.t1 % 60)
            s = 1 if p.side == "buy" else -1
            v = np.where(s > 0, lo[a:z] - p.p0, p.p0 - hi[a:z] - sp[a:z]) * p.vol * K + p.cost_in
            fl += np.where(on, v, 0.0) + np.where(tt >= p.t1 - p.t1 % 60, p.net, 0.0)
        fl = fl / CAP * 100
        k = np.where(fl <= -T)[0]
        if not len(k):
            continue
        first = g.iloc[0]; sgn = 1 if first.side == "buy" else -1
        bad = bool((fl[k[0]:] <= -G).any())
        ev.append(dict(t=int(tt[k[0]]), sgn=sgn, bad=bad, final=float(g.net.sum() / CAP * 100), worst=float(fl.min()),
                       lot0=float(first.vol)))
    return pd.DataFrame(ev), b


def acc1_events():
    o = pd.read_csv("data/derived/bd1_rescue/clusters_strict.csv")
    P = dict(np.load("data/derived/bd1_rescue/paths_strict.npz")); ev = []
    for r in o.itertuples():
        a = P.get(str(r.cid))
        if a is None:
            continue
        a = a[a[:, 0] + 60 <= r.t1]
        k = np.where(a[:, 1] <= -T)[0]
        if not len(k):
            continue
        bad = bool((a[k[0]:, 1] <= -G).any()) or bool(r.guard)
        ev.append(dict(t=int(a[k[0], 0]), sgn=1 if r.side == "B" else -1, bad=bad, final=float(r.pnl_pct)))
    return pd.DataFrame(ev)


def saving(d, flag):
    cut = d[flag]
    return float((np.where(cut.bad, SLIP * G - T, -(T + cut.final))).sum()), (float(cut.bad.mean()) if len(cut) else None), int(len(cut))


def main():
    ev, b = tester_events()
    f = hourly_feats(b)
    X = pd.DataFrame([feats_at(f, r.t, r.sgn) for r in ev.itertuples()]); ev = pd.concat([ev, X], axis=1)
    tr, te = ev[ev.t < SPLIT], ev[ev.t >= SPLIT]
    from sklearn.linear_model import LogisticRegression
    mu, sd = tr[FEATS].mean(), tr[FEATS].std()
    lr = LogisticRegression(max_iter=1000).fit((tr[FEATS] - mu) / sd, tr.bad)
    ev["F7"] = lr.predict_proba((ev[FEATS] - mu) / sd)[:, 1]
    tr, te = ev[ev.t < SPLIT], ev[ev.t >= SPLIT]
    res = {"events": len(ev), "train": dict(n=len(tr), bad=int(tr.bad.sum())), "test": dict(n=len(te), bad=int(te.bad.sum())),
           "signals": {}}
    for s in FEATS + ["F7"]:
        th = float(tr[s].quantile(2 / 3))
        res["signals"][s] = dict(threshold=round(th, 3), train=saving(tr, tr[s] > th))
    best = max(res["signals"], key=lambda s: res["signals"][s]["train"][0])
    th = res["signals"][best]["threshold"]
    res["chosen"] = best; res["test"]["chosen"] = saving(te, te[best] > th)
    sv, prec, n = res["test"]["chosen"]
    res["pass"] = bool(sv > 0 and prec is not None and prec >= 0.55)
    # check on account 1 (descriptive), features from account 1's own bars
    from inputs import load
    _, ab = load()
    fa = hourly_feats(ab[["time", "open", "high", "low", "close"]].assign(time=ab.time))
    ae = acc1_events()
    if best != "F7":
        ae[best] = [feats_at(fa, r.t, r.sgn)[best] for r in ae.itertuples()]
    else:
        XA = pd.DataFrame([feats_at(fa, r.t, r.sgn) for r in ae.itertuples()])
        ae[best] = lr.predict_proba((XA[FEATS] - mu) / sd)[:, 1]
    res["acc1"] = dict(n=len(ae), bad=int(ae.bad.sum()), chosen=saving(ae, ae[best] > th))
    print(json.dumps(res, indent=1))
    json.dump(res, open("docs/evidence/bd_ta_exit.json", "w"), indent=1)
    ev.to_csv("data/derived/bd_ta_exit_events.csv", index=False)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
