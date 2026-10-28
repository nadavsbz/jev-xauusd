"""After a top US release (NFP, CPI, Fed...), does gold keep moving in the direction of the release bar? (docs/HYBRID_PLAN.md, step 3)
Release bar = the M15 bar that starts at the event time (broker clock, data/derived/news/news_top_<rf|eg>.txt).
Entry at the close of the release bar (+1 bar delay = close of the next one, more realistic), exit h bars later; signed by the
release bar's direction; gross bp, and net of 2x the median spread of the bar after entry (wide after news).
Usage: python research/hybrid/news_reaction.py"""
import glob
import numpy as np, pandas as pd

PT = {"rf": 0.01, "eg": 0.001}
for delay in (0, 1):
    print(f"entry delay {delay} bar(s)")
    for f in sorted(glob.glob("data/derived/crash_signs/bars_*_PERIOD_M15.csv")):
        p = f.split("bars_")[1].split("_")[0]
        b = pd.read_csv(f).set_index("time")
        ev = [int(x) for x in open(f"data/derived/news/news_top_{p[:2]}.txt")]
        idx = {t: i for i, t in enumerate(b.index)}
        c = b.close.values; o = b.open.values; s = b.spread.values
        cells = []
        for h in (1, 2, 4, 8, 16):
            v = []
            for t in ev:
                i = idx.get(t)
                if i is None or i + delay + h >= len(c): continue
                d = np.sign(c[i] - o[i]); e = c[i + delay]
                g = d * (c[i + delay + h] - e) / e * 1e4
                v.append((g, 2 * s[i + delay] * PT[p[:2]] / e * 1e4))
            v = np.array(v); n = v[:, 0] - v[:, 1]
            cells.append(f"h{h}:{v[:, 0].mean():+.1f}/{n.mean():+.1f}(t{n.mean() / n.std() * np.sqrt(len(n)):+.1f})")
        print(f"  {p} n{len(v)} " + " ".join(cells))
