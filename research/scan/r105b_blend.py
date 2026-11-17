"""Round 105b (prereg in docs/prereg/r105_c1_paper_daily.md): 50/50 blend of frozen C1 and the paper-daily C1, holdout only."""
import sys, contextlib, io, runpy
import numpy as np
sys.path.insert(0, "research/scan")
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv = ["x", "hold"]; g = runpy.run_path("research/scan/r105_c1_paper_daily.py")
from scan import scale
BASE, NEW, st = g["BASE"], g["NEW"], g["st"]
J = (0.5 * BASE + 0.5 * NEW.reindex(BASE.index).fillna(0)); BL = scale(J)
a, b = "2023", "2026"
sb, mb, yb = st(BASE[a:b]); sn, mn, yn = st(BL[a:b]); sp, mp, yp = st(NEW[a:b])
ok = sn >= sb + 0.05 and mn >= mb - 2
print(f"holdout {a}-{b}:")
print(f"  BASE C1      Sh {sb:.2f} MDD {mb:.1f} | {yb}")
print(f"  [desc] PAPER Sh {sp:.2f} MDD {mp:.1f} | {yp}")
print(f"  BLEND 50/50  Sh {sn:.2f} ({sn - sb:+.2f}) MDD {mn:.1f} -> {'PASS' if ok else 'FAIL'} | {yn}")
