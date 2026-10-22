"""In-grid tools (level cap, MaxLot freeze, PAUSE on loss) re-simulated on account 1's real baskets, position by
position (docs/BD_INGRID_PLAN.md, registered 21.10.2026). Needs clusters.py --strict output in JEV_DERIVED and the
same deals/rates snapshots in JEV_DEALS_SNAPSHOT / JEV_RATES_SNAPSHOT."""
import json, os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inputs import load, max_drawdown

K, G, SLIP, MAXD = 100.0, 15.0, 0.5, 30 * 1440
DER = os.environ.get("JEV_DERIVED", "data/derived/bd1_rescue")
_, bars = load()
bt = bars.time.values; lo = bars.low.values; hi = bars.high.values; cl = bars.close.values
spr = bars.spread.values * 0.01
o = pd.read_csv(os.path.join(DER, "clusters_strict.csv")).sort_values("t0").reset_index(drop=True)
pos = pd.read_csv(os.path.join(DER, "positions_strict.csv")).sort_values(["t0_msc", "position_id"])
byc = {c: g for c, g in pos.groupby("cid")}
TP_MED = o.loc[o.pnl > 0, "pnl_pct"].median()
HALF = pd.Timestamp("2026-05-01").timestamp()


def sim(g, b0, target, rule):
    t = g.t0.values; s = g.sgn.values.astype(float); v = g.volume.values.copy(); px = g.open_px.values
    kind, par = rule
    keep = np.ones(len(g), bool)
    if kind == "cap":
        keep[par:] = False
    elif kind == "maxlot":
        v = np.minimum(v, par * v[0])
    i0 = np.searchsorted(bt, t[0], side="right") - 1
    i1 = min(len(bt), i0 + MAXD)
    L, H, C, S = lo[i0:i1], hi[i0:i1], cl[i0:i1], spr[i0:i1]
    on = np.searchsorted(bt[i0:i1], t, side="right") - 1                 # minute each position opens in
    if kind == "pause":
        for j in range(1, len(g)):
            m = on[j] - 1
            if m < 0:
                continue
            k = keep[:j] & (on[:j] <= m)
            bad = np.where(s[k] > 0, L[m] - px[k], px[k] - H[m] - S[m]) * s[k] * s[k]   # adverse side, per lot
            if (bad * v[k] * K).sum() <= -par / 100 * b0:
                keep[j] = False
    s, v, px, on = s[keep], v[keep], px[keep], on[keep]
    n = len(L); bad = np.zeros(n); good = np.zeros(n); last = np.zeros(n)
    for sj, vj, pj, oj in zip(s, v, px, on):
        if sj > 0:
            b, gd, c = L[oj:] - pj, H[oj:] - pj, C[oj:] - pj
        else:
            b, gd, c = pj - H[oj:] - S[oj:], pj - L[oj:] - S[oj:], pj - C[oj:] - S[oj:]
        bad[oj:] += b * vj * K; good[oj:] += gd * vj * K; last[oj:] += c * vj * K
    last_entry = on.max()
    hit_g = np.where(bad <= -G / 100 * b0)[0]; hit_t = np.where((good >= target) & (np.arange(n) >= last_entry))[0]
    ig = hit_g[0] if len(hit_g) else n; it = hit_t[0] if len(hit_t) else n
    if ig < n and ig <= it:
        return -(G + SLIP) / 100 * b0, bad[:ig + 1].min(), True
    if it < n:
        return target, bad[:it + 1].min(), False
    return last[-1], bad.min(), False


def run(rule):
    r = np.zeros(len(o)); tr = np.zeros(len(o)); hits = 0
    for i, row in enumerate(o.itertuples()):
        g = byc[row.cid]; b0 = row.bal0
        target = row.pnl if row.pnl > 0 else TP_MED / 100 * b0
        p, w, h = sim(g, b0, target, rule)
        r[i], tr[i] = p / b0, min(w, p) / b0; hits += h
    out = {"guard_hits": int(hits)}
    for h, m in {"h1": o.t0.values < HALF, "h2": o.t0.values >= HALF, "all": np.ones(len(o), bool)}.items():
        eq, dd = max_drawdown(r[m], tr[m])
        out[h] = (round(float(eq[-1]), 3), round(float(dd), 2))
    return out


if __name__ == "__main__":
    res = {}
    rules = [("base", 0)] + [("cap", k) for k in (6, 8, 10, 12)] + [("maxlot", m) for m in (8, 16, 32)] + [("pause", x) for x in (5, 10)]
    for rule in rules:
        res[f"{rule[0]}_{rule[1]}"] = run(rule); print(rule, res[f"{rule[0]}_{rule[1]}"], flush=True)
    b = res["base_0"]
    for k, v in res.items():
        v["candidate"] = k != "base_0" and all(v[h][0] > b[h][0] and v[h][1] > b[h][1] for h in ("h1", "h2"))
    eq, dd = max_drawdown(o.pnl_pct.values / 100, o.mae_pct.values / 100)
    res["real"] = {"all": (round(float(eq[-1]), 3), round(float(dd), 2))}
    print("real", res["real"]); json.dump(res, open("docs/evidence/bd1_ingrid.json", "w"), indent=1)
