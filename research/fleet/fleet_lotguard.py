"""Lot ratio x guard level for the whole fleet (docs/FLEET_LOTGUARD_PLAN.md, registered 21.10.2026).
Per account the model of research/bd1/lotguard.py; the fleet's week = equal-weight mean of the accounts that ran BD
that week; 4-week blocks of COMMON calendar weeks keep shared crash days together."""
import json, os
import numpy as np, pandas as pd

DIRS = {"1": "data/derived/bd1_rescue", "2": "data/derived/fleet/bd2", "3": "data/derived/fleet/bd3",
        "5": "data/derived/fleet/bd5", "6": "data/derived/fleet/bd6", "8": "data/derived/fleet/bd8"}
SLIP, WIPE = 1.3, -90.0
W0, W1 = pd.Timestamp("2026-03-02"), pd.Timestamp("2026-10-16")
rng = np.random.default_rng(21)


class Acc:
    def __init__(self, d):
        o = pd.read_csv(os.path.join(d, "clusters_strict.csv")).sort_values("t0").reset_index(drop=True)
        pos = pd.read_csv(os.path.join(d, "positions_strict.csv"))
        o["rho"] = o.bal0 / o.cid.map(pos.sort_values("t0_msc").groupby("cid").volume.first())
        P = dict(np.load(os.path.join(d, "paths_strict.npz")))
        self.pmin = np.full(len(o), np.nan)
        for i in range(len(o)):
            a = P.get(str(o.cid[i]))
            if a is not None:
                a = a[a[:, 0] + 60 <= o.t1[i]]
                if len(a):
                    self.pmin[i] = a[:, 1].min()
        p = os.path.join(d, "after_guard.csv")
        self.ag = pd.read_csv(p).set_index("cid") if os.path.exists(p) else pd.DataFrame()
        o["wk"] = pd.to_datetime(o.t0, unit="s").dt.to_period("W")
        self.o = o

    def run_week(self, R, G):
        """Guard as the user runs it: level = (1-G) x equity at the start of the week (the weekly update)."""
        o = self.o; s = (o.rho / R).values; pnl = o.pnl_pct.values; mae = o.mae_pct.values
        base = np.fmin(np.where(np.isnan(self.pmin), mae, self.pmin), mae)
        r = s * pnl; tr = s * mae; eq = 1.0; ew = 1.0; wk = None; wks = o.wk.values
        for i in range(len(o)):
            if wks[i] != wk:
                wk, ew = wks[i], eq
            thr = ((1 - G / 100) * ew / eq - 1) * 100          # floating % of the current balance that hits the level
            worst = s[i] * base[i]; cont = None
            if o.guard[i] and o.cid[i] in self.ag.index:
                cont = s[i] * self.ag.loc[o.cid[i]].worst_lower; worst_all = min(worst, cont)
            else:
                worst_all = worst
            if thr >= 0 or worst_all <= thr:
                r[i] = tr[i] = SLIP * min(thr, 0) if thr < 0 else 0.0
            elif cont is not None:
                r[i] = 0.0 if self.ag.loc[o.cid[i]].recovered else cont; tr[i] = worst_all
            elif worst_all <= WIPE:
                r[i] = tr[i] = -100.0
            eq *= 1 + r[i] / 100
        return self._weeks(r, tr)

    def _weeks(self, r, tr):
        o = self.o; out = {}
        for w, idx in o.groupby("wk").indices.items():
            c = np.cumprod(1 + r[idx] / 100); prev = np.r_[1.0, c[:-1]]
            out[w] = (c[-1] - 1, min((prev * (1 + np.minimum(tr[idx], r[idx]) / 100)).min(), c.min()) - 1)
        return out

    def run(self, R, G):
        o = self.o; s = (o.rho / R).values; r = s * o.pnl_pct.values; tr = s * o.mae_pct.values
        base = np.fmin(np.where(np.isnan(self.pmin), o.mae_pct.values, self.pmin), o.mae_pct.values)
        for i in np.where(s * base <= -G)[0].tolist() + [i for i in np.where(o.guard.values)[0]]:
            worst = s[i] * base[i]
            if o.guard[i] and o.cid[i] in self.ag.index:
                after = s[i] * self.ag.loc[o.cid[i]].worst_lower
                if after > -G and worst > -G:
                    r[i] = 0.0 if self.ag.loc[o.cid[i]].recovered else after; tr[i] = min(worst, after); continue
                worst = min(worst, after)
            if worst <= -G:
                r[i] = tr[i] = -SLIP * G
            elif worst <= WIPE:
                r[i] = tr[i] = -100.0
        out = {}
        for w, idx in o.groupby("wk").indices.items():
            c = np.cumprod(1 + r[idx] / 100); prev = np.r_[1.0, c[:-1]]
            out[w] = (c[-1] - 1, min((prev * (1 + np.minimum(tr[idx], r[idx]) / 100)).min(), c.min()) - 1)
        return out


def fleet(accs, R, G, weekly=True):
    weeks = pd.period_range(W0, W1, freq="W")
    per = [a.run_week(R, G) if weekly else a.run(R, G) for a in accs]
    W = []
    for w in weeks:
        xs = [p[w] for p in per if w in p]
        W.append((np.mean([x[0] for x in xs]), np.mean([x[1] for x in xs])) if xs else (0.0, 0.0))
    return np.array(W)


def boot(W, n=2000, blocks=13):
    st = rng.integers(0, len(W) - 4, size=(n, blocks)); idx = (st[:, :, None] + np.arange(4)).reshape(n, -1)
    wr, wt = np.maximum(W[idx, 0], -1), np.maximum(W[idx, 1], -1)
    eq = np.cumprod(1 + wr, axis=1); prev = np.c_[np.ones(n), eq[:, :-1]]
    peak = np.maximum.accumulate(np.c_[np.ones(n), eq], axis=1)[:, :-1]
    dd = np.minimum(prev * (1 + wt) / peak - 1, 0).min(axis=1)
    return dict(median_x=round(float(np.median(eq[:, -1])), 2), p10_x=round(float(np.percentile(eq[:, -1], 10)), 2),
                p_dd50=round(float((dd <= -0.5).mean()), 3), p_dd25=round(float((dd <= -0.25).mean()), 3),
                p_6pct_month=round(float((eq[:, -1] >= 1.06 ** 12).mean()), 3))


if __name__ == "__main__":
    accs = [Acc(d) for d in DIRS.values()]
    res = {"grid": []}
    for R in (400e3, 500e3, 600e3, 700e3, 800e3, 1e6, 1.2e6):
        for G in (10, 15, 20, 25, 30):
            W = fleet(accs, R, G, weekly=False)          # the registered model; weekly is a separate comparison
            x = {"R": int(R), "G": G, "in_sample_x": round(float(np.prod(1 + W[:, 0])), 2)}
            x.update(boot(W)); res["grid"].append(x); print(x, flush=True)
    el = [x for x in res["grid"] if x["p_dd50"] <= 0.05]
    res["chosen"] = max(el, key=lambda x: x["median_x"]) if el else None
    print("chosen", res["chosen"])
    json.dump(res, open("docs/evidence/fleet_lotguard.json", "w"), indent=1)
