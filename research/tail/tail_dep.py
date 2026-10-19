"""MASTER_PLAN step A5 (section 4.2): does an engine lose on Black Dragon's tail days?

Inputs are daily series, CSV with columns date,ret[,worst]: ret = close-to-close change of the engine's equity
(floating included) as a fraction of the previous close; worst = the change to the WORST minute of the day
(optional; ES uses it when present, ret otherwise). P(R<0) and the joint tail use ret. Two helpers build them:
  * from a tester report + the broker's M1 bars:  python research/tail/tail_dep.py daily REPORT.htm CONFIG.json OUT.csv
    (CONFIG gives symbol and bars like research/mgmt/*.json)
  * any other engine: its own CSV (e.g. docs/evidence/trend_gold_test_daily.csv after renaming the columns).

Measure:  python research/tail/tail_dep.py measure BD.csv ENGINE.csv [ENGINE2.csv ...] [--protect-days FILE]
  BD tail days = the worst 5% of BD days (+ the protection days if given), fixed on the BD series itself.
  Per engine, on those days: P(R<0 | BD-tail), mean conditional loss (ES, % of the engine's equity), and the
  joint-tail rate (share of BD tail days that are also in the engine's own worst 5%).
  90% intervals: block bootstrap over crash EPISODES (tail days at most 3 calendar days apart form one episode).
  Pass as a diversifier (registered): P <= 0.5, joint-tail <= 20%, upper 90% bound of the loss <= 1%."""
import json, os, sys
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def daily(report, cfg_path, out):
    sys.path.insert(0, os.path.join(ROOT, "research", "mgmt"))
    import chain                                     # noqa: E402
    cfg = json.load(open(cfg_path, encoding="utf-8")); B = chain.load_bars(cfg)
    d = chain.deals(report); pos = chain.pair(d)[0]
    dep = float(d.balance.iloc[0] - d.profit.iloc[0] - d.commission.iloc[0] - d.swap.iloc[0])
    tt, e_lo, e_hi, _ = chain.path(pos, *B, dep)
    s = pd.DataFrame({"t": pd.to_datetime(tt, unit="s"), "lo": e_lo, "hi": e_hi})
    g = s.groupby(s.t.dt.date)
    close = g.lo.last(); worst = g.lo.min(); prev = close.shift(1).fillna(dep)
    pd.DataFrame({"date": close.index, "ret": ((close - prev) / prev).values,
                  "worst": ((worst - prev) / prev).values}).to_csv(out, index=False)
    print(out, len(close), "days")


def episodes(days):
    days = sorted(days); ep = []; cur = []
    for d in days:
        if cur and (d - cur[-1]).days > 3:
            ep.append(cur); cur = []
        cur.append(d)
    return ep + ([cur] if cur else [])


def measure(bd_csv, engines, protect=None, n_boot=5000, seed=7):
    bdf = pd.read_csv(bd_csv, parse_dates=["date"]).set_index("date")
    bd = bdf["worst"] if "worst" in bdf else bdf.ret          # BD's tail = its worst intraday days
    tail = set(bd[bd <= bd.quantile(0.05)].index)
    if protect:
        tail |= set(pd.to_datetime(pd.read_csv(protect).date))
    eps = episodes(list(tail)); rng = np.random.default_rng(seed); res = {}
    for f in engines:
        ef = pd.read_csv(f, parse_dates=["date"]).set_index("date"); e = ef.ret
        ew = ef["worst"] if "worst" in ef else ef.ret
        own = set(e[e <= e.quantile(0.05)].index)
        common = [[d for d in ep if d in e.index] for ep in eps]
        common = [c for c in common if c]
        if not common:
            res[os.path.basename(f)] = {"days": 0}; continue

        def stats(group):
            days = [d for c in group for d in c]; r = e.loc[days]; w = ew.loc[days]
            return (r < 0).mean(), float(-w[w < 0].mean()) if (w < 0).any() else 0.0, np.mean([d in own for d in days])
        p, es, jt = stats(common)
        boots = np.array([stats([common[i] for i in rng.integers(0, len(common), len(common))]) for _ in range(n_boot)])
        lo, hi = np.percentile(boots, 5, axis=0), np.percentile(boots, 95, axis=0)
        res[os.path.basename(f)] = dict(days=int(sum(map(len, common))), episodes=len(common),
            p_loss=round(float(p), 3), p_ci90=[round(float(lo[0]), 3), round(float(hi[0]), 3)],
            es_pct=round(100 * float(es), 3), es_upper90_pct=round(100 * float(hi[1]), 3),
            joint_tail=round(float(jt), 3), joint_ci90=[round(float(lo[2]), 3), round(float(hi[2]), 3)],
            passes=bool(p <= 0.5 and jt <= 0.2 and 100 * hi[1] <= 1.0))
    out = dict(bd=os.path.basename(bd_csv), tail_days=len(tail), episodes=len(eps), engines=res)
    print(json.dumps(out, indent=1, default=str))
    return out


if __name__ == "__main__":
    if sys.argv[1] == "daily":
        daily(*sys.argv[2:5])
    else:
        args = sys.argv[2:]; prot = None
        if "--protect-days" in args:
            k = args.index("--protect-days"); prot = args[k + 1]; args = args[:k] + args[k + 2:]
        measure(args[0], args[1:], prot)
