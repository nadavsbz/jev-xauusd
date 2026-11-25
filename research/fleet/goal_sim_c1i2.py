"""Goal path if capital + deposits go to C1 and I2 (two stand-alone accounts, half each, no rebalancing), from tester
monthly returns (grok_data/t401: C1 at AssetVol 0.075 -> x2 = ProCent level 0.15 [ASSUMED linear]; I2 in2dst runs at
TargetVol 0.15). Months are drawn jointly (same calendar month for both) to keep their correlation. Start $7,500,
deposits $1,000/month split evenly from month 7. Goal = a month with >= $30,000 total profit.
Usage: py -3.12 research/fleet/goal_sim_c1i2.py"""
import numpy as np, pandas as pd
c = pd.read_csv("docs/agents/grok_data/t401/c1_monthly.csv"); i = pd.read_csv("docs/agents/grok_data/t401/i2_monthly.csv")
M = c.merge(i, on="month"); N = 20000; rng = np.random.default_rng(2511)
def run(c1x, months, dep, since=None, i2x=1.0):
    m = M[M.month >= since] if since else M
    a = (m.c1_ret * c1x).values; b = (m.i2_ret * i2x).values; hit = 0; ruin = 0; first = []
    for _ in range(N):
        x = y = 3750.0
        for t in range(months):
            k = rng.integers(len(a)); gx, gy = x * a[k], y * b[k]; x += gx; y += gy
            if gx + gy >= 30000: hit += 1; first.append(t + 1); break
            if x + y < 750: ruin += 1; break
            if dep and t >= 6: x += 500; y += 500
    return dict(p_goal=round(hit / N, 3), median_month=int(np.median(first)) if first else None, p_ruin=round(ruin / N, 3))
rows = []
for since, c1x, i2x in ((None, 1.0, 0.5), ("2022-01", 1.0, 0.5)):    # demo/live levels (C1 AV 0.075, I2 TV 0.075; Grok t404 haircut request)
    for H in (60, 84, 120):
        rows.append(dict(months_from=since or "2020", c1_scale=c1x, i2_scale=i2x, deposits=True, years=H // 12, **run(c1x, H, True, since, i2x)))
for since in (None, "2022-01"):
    for c1x in (1.0, 2.0):
        for dep in (False, True):
            for H in (36, 60, 84, 120):
                rows.append(dict(months_from=since or "2020", c1_scale=c1x, i2_scale=1.0, deposits=dep, years=H // 12, **run(c1x, H, dep, since)))
print(len(M), "joint months"); print(pd.DataFrame(rows).to_string(index=False))
