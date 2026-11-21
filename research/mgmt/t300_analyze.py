"""t300 analysis (preregistered in docs/prereg/bd_live_set_t298.md).

Per path: monthly return = product of (eq_end/eq_start) over the segments that start in that month.
Live account 1: monthly return = profit / opening balance (withdrawals make balance-diff invalid).
Gate: account 1 inside the p5..p95 band of the paths in >=5 of the 6 clean months (2025-12..2026-05).
Usage: py -3.12 research/mgmt/t300_analyze.py
"""
import glob, json, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLEAN = ["2025-12", "2026-01", "2026-02", "2026-03", "2026-04", "2026-05"]


def path_months(fn):
    m = {}
    segs = [json.loads(l) for l in open(fn, encoding="utf-8") if l.strip()]
    for s in segs:
        mon = s["start"][:7]
        r = s["eq_end"] / s["eq_start"] if s["eq_start"] > 0 else 0.0
        m[mon] = m.get(mon, 1.0) * r
    return {k: v - 1 for k, v in m.items()}, segs


def main():
    live = {r[0]: r[3] / r[1] for r in json.load(open(os.path.join(ROOT, "research/bd1/cmp_live_months.json")))}
    files = sorted(glob.glob(os.path.join(ROOT, "data/derived/mgmt/t300_p*.jsonl")))
    paths, finals, hits = [], [], []
    for f in files:
        m, segs = path_months(f)
        paths.append(m)
        finals.append(segs[-1]["eq_end"] / segs[0]["eq_start"])
        hits.append(sum(1 for s in segs if s.get("hit")))
    n = len(paths)
    print(f"paths: {n}")
    inside = 0
    rows = []
    for mon in sorted(live):
        vals = np.array([p.get(mon, 0.0) for p in paths])
        p5, p50, p95 = np.percentile(vals, [5, 50, 95])
        ok = p5 <= live[mon] <= p95
        clean = mon in CLEAN
        if clean and ok:
            inside += 1
        rows.append(dict(month=mon, live=round(live[mon], 4), p5=round(p5, 4), p50=round(p50, 4),
                         p95=round(p95, 4), inside=bool(ok), clean=clean,
                         frac_paths_ge_live=round(float((vals >= live[mon]).mean()), 3)))
        print(f"{mon} {'C' if clean else ' '} live {live[mon]*100:+7.1f}%  p5 {p5*100:+7.1f}  p50 {p50*100:+7.1f}  p95 {p95*100:+7.1f}  {'IN' if ok else 'OUT'}")
    fa = np.array(finals)
    live_mult = float(np.prod([1 + live[m] for m in sorted(live)]))
    summ = dict(paths=n, clean_inside=inside, clean_total=len(CLEAN), gate_pass=inside >= 5,
                final_p5=float(np.percentile(fa, 5)), final_p50=float(np.median(fa)), final_p95=float(np.percentile(fa, 95)),
                final_max=float(fa.max()), wipes=int((fa < 0.05).sum()), hits_median=float(np.median(hits)),
                live_compound_mult=round(live_mult, 2), frac_paths_ge_live=float((fa >= live_mult).mean()))
    print(json.dumps(summ, indent=1))
    out = os.path.join(ROOT, "data/derived/mgmt/t300_summary.json")
    json.dump(dict(summary=summ, months=rows), open(out, "w", encoding="utf-8"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
