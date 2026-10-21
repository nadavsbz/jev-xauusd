"""Time to the $1,000/day goal under full compounding with the deposit taken out once doubled (user, 21.10.2026:
no routine profit sweeps). Descriptive, not a selection.
Worlds: A = account 1's real weeks (11.2025-10.2026); B = A mixed 50/50 with the tester's weekly runs on
4.2024-10.2025 under the user's rule (mgmt/bd_sel24, lot 1:600k), the period where the tester wiped.
Weekly returns at lot scale s: real weeks rebuilt from baskets with returns x s (s=1 is the real ~1:418k);
tester weeks scaled linearly by s/0.7 (ASSUMED). 4-week block bootstrap, 2,000 paths, 8 years.
Start $1,400 (account 1 today). Goal: $365,000 working capital (~100%/yr -> $1,000/day, ASSUMED).
Deposit rule: when equity >= 2x the deposit of the current cycle, the deposit moves to the reserve; if equity falls
below 10% of the cycle start (a wipe), a new cycle starts from the reserve (if it is empty: ruin)."""
import json
import numpy as np, pandas as pd

o = pd.read_csv("data/derived/bd1_rescue/clusters_strict.csv"); o["d"] = pd.to_datetime(o.t0, unit="s")
wk = o.d.dt.to_period("W")
ch = [json.loads(l) for l in open("data/derived/mgmt/bd_sel24.jsonl")]
tw = np.array([x["eq_end"] / x["eq_start"] - 1 for x in ch if x["eq_start"] > 15000])   # before the 0.01 lot floor
rng = np.random.default_rng(7); GOAL, START, YEARS, N = 365000, 1400, 8, 2000


def real_weeks(s):
    return (1 + s * o.pnl_pct / 100).groupby(wk).prod().values - 1


def paths(world, s):
    a = real_weeks(s); b = np.clip(tw * s / 0.7, -0.99, None)
    out = []
    for _ in range(N):
        eq, dep, res, start, years = START, START, 0.0, START, None
        w = 0
        while w < YEARS * 52:
            src = a if world == "A" or rng.random() < 0.5 else b
            i = rng.integers(0, len(src) - 4)
            for r in src[i:i + 4]:
                eq *= 1 + r; w += 1
                if eq >= 2 * dep and dep > 0:
                    res += dep; eq -= dep; dep = 0
                if eq < 0.1 * start:
                    if res <= 0:
                        eq = 0; break
                    eq = start = res; dep = res; res = 0
                if eq + res >= GOAL and years is None:
                    years = w / 52
            if eq <= 0 or years is not None:
                break
        out.append(years if years is not None else np.inf)
    out = np.array(out)
    return dict(median_years=round(float(np.median(out)), 1), p_goal_5y=round(float((out <= 5).mean()), 2),
                p_goal_8y=round(float((out <= 8).mean()), 2))


res = {}
for world in ("A", "B"):
    for s in (1.0, 0.7, 0.5, 0.4):
        res[f"{world}_s{s}"] = paths(world, s); print(world, s, res[f"{world}_s{s}"], flush=True)
json.dump(res, open("docs/evidence/goal_sim.json", "w"), indent=1)
