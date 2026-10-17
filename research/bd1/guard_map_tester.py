"""Map of equity-floor levels on the calibrated BD tester run at 0.04 lot (docs/BD1_CRASH_CAUSE.md):
exact positions from the report, floating from EGlobal M1 bars, guard = research/btc/guardian_sim.guarded
(floor below the equity peak closes everything; after_stop reset_when_flat or kill). Descriptive only:
no level is chosen here and nothing is claimed for another period.
Usage: python research/bd1/guard_map_tester.py REPORT.htm BARS_CSV DEPOSIT OUT_JSON"""
import json, sys, os
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "btc"))
import guardian_sim as g  # noqa: E402

rep, bars_csv, dep, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
bars = pd.read_csv(bars_csv); bt, lo, hi, cl = bars.time.values, bars.low.values, bars.high.values, bars.close.values
pos, left = g.pair(g.deals(rep))
tt, eq_lo, _ = g.equity_path(pos, bt, lo, hi, dep); pk = np.maximum.accumulate(eq_lo)
res = {"positions": len(pos), "unmatched": left, "validation_max_dd_cents": round(float((pk - eq_lo).max()), 0)}
for floor in (None, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
    for kill in (False, True):
        if floor is None and kill:
            continue
        r = g.guarded(pos, bt, lo, hi, cl, dep, floor, False, False, kill)
        key = f"floor={floor} after_stop={'kill' if kill else 'reset_when_flat'}"
        res[key] = {k: r[k] for k in ("final", "max_dd_pct", "floor_stops", "wiped")}
        res[key]["mult"] = round(r["final"] / dep, 3)
        print(key, res[key], flush=True)
json.dump(res, open(out, "w"), indent=1)
