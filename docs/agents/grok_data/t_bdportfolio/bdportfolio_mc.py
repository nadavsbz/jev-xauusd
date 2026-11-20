"""T_BDPORTFOLIO Monte Carlo (SIMULATED illustration; inputs per PREREG.md, sha 6286e2bf...aadd).
R10 = REAL tester output (clone base v16/v17-off, RF XAUUSD M15 real ticks, 2016-2025, % of deposit per year),
copied from CRASH_LINK_PLAN rounds 22-23 table (VERIFIED by Claude, research/bd1/every22_results.jsonl).
Everything else (MC2 grid, shifts) is parametric/hypothetical and labelled as such in the outputs."""
import numpy as np, pandas as pd, itertools, math
SEED = 20261118
R10 = np.array([-31, -45, -17, -29, 2, 15, 5, 12, 10, -1]) / 100.0
NP, YEARS = 20000, 5

def boot(rng, r, block=1):
    if block == 1:
        return rng.choice(r, size=(NP, YEARS), replace=True)
    starts = rng.integers(0, len(r) - block + 1, size=(NP, math.ceil(YEARS / block)))
    out = np.concatenate([r[starts + j][:, :, None] for j in range(block)], axis=2).reshape(NP, -1)
    return out[:, :YEARS]

def run_policy(R, f, pol, m=1 / 0.45, floor=0.85):
    W = np.ones(NP); B = f * W.copy(); C = W - B; M = W.copy(); seed = f
    maxdd = np.zeros(NP); wiped = np.zeros(NP, bool); prev = np.zeros(NP)
    for t in range(R.shape[1]):
        r = R[:, t]
        if pol == "P1":
            B = f * W; C = W - B
        elif pol == "P2":
            A = np.clip(m * (W - floor * M), 0, W); B = A; C = W - A
        elif pol == "P4":
            r = np.where(prev <= -0.15, 0.0, r)
        Bn = np.maximum(B * (1 + r), 0.0)
        wiped |= (B > 0) & (Bn <= 0)
        B = Bn
        if pol == "P3":
            ex = np.maximum(B - 1.5 * seed, 0.0); B -= ex; C += ex
            reseed = (B <= 0) & (B + C >= floor * M)
            add = np.where(reseed, np.minimum(seed, C), 0.0); B += add; C -= add
        prev = R[:, t]
        W = B + C; M = np.maximum(M, W); maxdd = np.maximum(maxdd, 1 - W / M)
    return W, maxdd, wiped

def summ(W, dd, wiped):
    return dict(median_multiple=np.median(W), median_cagr=np.median(W) ** (1 / YEARS) - 1,
                mean_multiple=W.mean(), p_dd15=(dd >= 0.15).mean(), p_dd25=(dd >= 0.25).mean(),
                p_bd_wipe=wiped.mean(), p5_multiple=np.quantile(W, 0.05))

def kelly(r):
    fs = np.linspace(0, 1.5, 1501); g = [np.mean(np.log(np.maximum(1 + f * r, 1e-12))) for f in fs]
    return fs[int(np.argmax(g))], max(g)

rows = []; rng = np.random.default_rng(SEED)
scen = {"REAL_R10": R10, "HYPO_mean+10": R10 + (0.10 - R10.mean()), "HYPO_mean+20": R10 + (0.20 - R10.mean())}
for name, r in scen.items():
    fk, gk = kelly(r)
    R = boot(rng, r)
    for f in [0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 1.00]:
        rows.append(dict(scenario=name, data_label="REAL tester R10 bootstrapped" if name == "REAL_R10" else "HYPOTHETICAL shift of R10",
                         f=f, policy="P0_buyhold", kelly_f_star=fk, half_kelly=fk / 2, **summ(*run_policy(R, f, "P0"))))
pd.DataFrame(rows).round(4).to_csv("mc1_allocation.csv", index=False)

rows = []; rng = np.random.default_rng(SEED + 3)
for name, r in scen.items():
    for block in (1, 2):
        R = boot(rng, r, block)
        for pol in ["P0", "P1", "P2", "P3", "P4"]:
            rows.append(dict(scenario=name, bootstrap="iid" if block == 1 else "block2", f=0.15, policy=pol,
                             **summ(*run_policy(R, 0.15, pol))))
pd.DataFrame(rows).round(4).to_csv("mc3_reset.csv", index=False)

# MC2: parametric event model (SIMULATED)
rows = []; rng = np.random.default_rng(SEED + 7); K = 12; f = 0.15
for g, lam, L, rho, N in itertools.product([0.03, 0.05], [1, 2, 3], [0.15, 0.5, 1.0], [1.0, 0.7, 0.3], [1, 2, 4, 8]):
    n = np.minimum(rng.poisson(lam, NP), K)
    t = np.sort(np.where(np.arange(K)[None, :] < n[:, None], rng.random((NP, K)), 2.0), axis=1)
    valid = t <= 1.0
    common = rng.random((NP, K)) < rho
    one = rng.integers(0, N, (NP, K))
    hit = common[:, :, None] | (one[:, :, None] == np.arange(N)[None, None, :])
    hit &= valid[:, :, None]
    surv = np.cumprod(np.where(hit, 1 - L, 1.0), axis=1)          # after event k
    before = np.concatenate([np.ones((NP, 1, N)), surv[:, :-1, :]], axis=1)
    grow = lambda tt: (1 + g) ** (12 * np.minimum(tt, 1.0))
    a_before = (f / N) * grow(t)[:, :, None] * before; a_after = (f / N) * grow(t)[:, :, None] * surv
    W_before = (1 - f) + a_before.sum(2); W_after = (1 - f) + a_after.sum(2)
    W_before = np.where(valid, W_before, np.nan); W_after = np.where(valid, W_after, np.nan)
    W_end = (1 - f) + ((f / N) * grow(np.ones(NP))[:, None] * np.prod(np.where(hit, 1 - L, 1.0), axis=1)).sum(1)
    runmax = np.fmax.accumulate(np.where(valid, W_before, -np.inf), axis=1); runmax = np.maximum(runmax, 1.0)
    dd = np.nanmax(np.where(valid, 1 - W_after / runmax, 0.0), axis=1)
    ret = W_end - 1; q = np.quantile(ret, 0.05)
    rows.append(dict(data_label="SIMULATED parametric", g_month=g, lam_per_year=lam, loss_per_hit=L, rho=rho, N_accounts=N, f=f,
                     p_total_dd15=(dd >= 0.15).mean(), p_total_dd5=(dd >= 0.05).mean(), median_ret=np.median(ret),
                     mean_ret=ret.mean(), cvar5=ret[ret <= q].mean()))
pd.DataFrame(rows).round(4).to_csv("mc2_split.csv", index=False)

# lot granularity (deterministic)
rows = []
for mult in (1.5, 1.3):
    for s in (1, 2, 4, 10, 100):
        exact = 0.01 * s * mult ** np.arange(10)
        near = np.maximum(np.round(exact / 0.01) * 0.01, 0.01); flo = np.maximum(np.floor(exact / 0.01 + 1e-9) * 0.01, 0.01)
        rows.append(dict(multiplier=mult, base_lot=0.01 * s, exact_total_L10=exact.sum().round(4), nearest_total_L10=near.sum().round(4),
                         floor_total_L10=flo.sum().round(4), max_level_err_nearest=np.max(np.abs(near / exact - 1)).round(4),
                         max_level_err_floor=np.max(np.abs(flo / exact - 1)).round(4),
                         lots_nearest="|".join(f"{x:.2f}" for x in near)))
pd.DataFrame(rows).to_csv("mc2_lot_granularity.csv", index=False)
print("done")
