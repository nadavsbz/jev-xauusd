"""Path to the goal (a real month with >= $30,000 trading profit = $1,000/day), Monte Carlo from the LIVE monthly returns.
Inputs: data/derived/lars/live_monthly_returns.csv (per account, Apr-Nov 2026, cents/100). Start capital $7,500 (user, 25.11).
Deposits $1,000/month only while 'stable' (from month 7, and the fleet is less than 25% below its peak).
Two return models: (1) FLEET: the month's capital-weighted fleet return (8 months, keeps cross-account correlation);
(2) ACCOUNT: any single account-month (41 obs, more volatile). Scenarios: as-is, haircut -2pp/month, and a regime break
(each year 25% chance the edge turns to N(-2%, 20%) for 12 months). 25.11: + TESTER_t399 (32 tester months 2022-2026, BD + 15% floor + live lot rule, Grok t399) and MIX (live + tester).
Usage: py -3.12 research/fleet/goal_sim.py"""
import numpy as np, pandas as pd

R = pd.read_csv("data/derived/lars/live_monthly_returns.csv")
ACC = R.ret.clip(-0.95).values
FLEET = R.groupby("m").ret.mean().values          # equal-weight across the accounts active that month
_T = pd.read_csv("docs/agents/grok_data/t400/t400_monthly.csv"); _T = _T[_T.complete == True]   # Grok t400 (final coverage): tester 2022-2026, BD + 15% floor + live lot rule (A7)
TESTER = (_T[_T.arm == "A7"].ret_pct / 100).values
MIX = np.concatenate([FLEET, TESTER])                                                # 8 live fleet months + 32 tester months
N = 20000; rng = np.random.default_rng(25112026)


def sim(pool, months, deposit, haircut=0.0, regime=False):
    hit = np.zeros(N, bool); ruin = np.zeros(N, bool); first = np.full(N, np.nan)
    for i in range(N):
        c = 7500.0; peak = c; bad = 0
        for m in range(months):
            if regime and m % 12 == 0 and rng.random() < 0.25: bad = 12
            r = rng.normal(-0.02, 0.20) if bad > 0 else rng.choice(pool) - haircut
            bad = max(0, bad - 1)
            gain = c * r; c += gain; peak = max(peak, c)
            if gain >= 30000 and not hit[i]: hit[i] = True; first[i] = m + 1
            if c < 750: ruin[i] = True; break
            if deposit and m >= 6 and c >= 0.75 * peak: c += 1000
    return dict(p_goal=round(hit.mean(), 3), median_month=None if not hit.any() else int(np.nanmedian(first)), p_ruin=round(ruin.mean(), 3))


if __name__ == "__main__":
    print("fleet monthly (equal-weight):", np.round(FLEET, 3), "geo", round(float(np.exp(np.log1p(FLEET).mean()) - 1), 3))
    rows = []
    for name, pool in (("FLEET", FLEET), ("TESTER_t400", TESTER), ("MIX", MIX)):
        for sc, kw in (("as-is", {}),):
            for dep in (False, True):
                for H in (36, 60):
                    rows.append(dict(model=name, scenario=sc, deposits=dep, years=H // 12, **sim(pool, H, dep, **kw)))
    T = pd.DataFrame(rows); T.to_csv("data/derived/lars/goal_sim.csv", index=False); print(T.to_string(index=False))
