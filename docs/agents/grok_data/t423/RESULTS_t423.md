# RESULTS t423 — I2 MaxLev 1.95, TV 0.15 (PREREG_t423.md sha 4082deb3…5538). Grok, 26.11.2026 ~14:15 Israel
Input: grok_data/t423_tester (Claude b7cdb3e): 7 yearly deals CSV + sanity 2024 + summary.json. Code: t423_eval.py; raw RESULTS_t423.json.
Sanity: MaxLev 5 on 2024 = +24,951.40 = in2dst_t_2024 [VERIFIED from summary.json]. Ticks 100% all runs.
Leverage per trade = volume × entry price / balance before entry (cs 1) [ASSUMED balance≈equity at entry; I2 holds max 1 position].

| year | net % of 120K | closed DD | tester equity DD | max lev | trades lev>1.989 | max L_trade (stress, actual lev) |
|---|---|---|---|---|---|---|
| 2020 | 1.11 | **18.91%** | 19.32% | 1.969 | 0 | 24.33% |
| 2021 | 13.82 | 6.79% | 9.09% | 1.996 | 2 | 24.41% |
| 2022 | 40.53 | 10.88% | 11.93% | 2.038 | 6 total (all yrs) | 24.07% |
| 2023 | 24.68 | 5.37% | 6.27% | 1.999 | 1 | 24.41% |
| 2024 | 17.97 | 5.81% | 6.23% | 1.981 | 0 | 24.44% |
| 2025 | 33.09 | 8.05% | 10.26% | 1.993 | 1 | 24.73% |
| 2026 | 23.33 | 6.85% | 9.72% | 2.010 | 1 | 24.44% |

Gates:
- G1 stress (t421 W_side(h), actual leverage, not capped): max 24.73% <= 25% — **PASS** (0 trades >25%). The over-cap trades are longs or short short-horizon, so they stay under 25%.
- G2 net sum 154.53 >= 77.40 (85% of base 91.06) — **PASS** (×1.70 of base).
- G3 max closed DD per year <= 11.70% — **FAIL** (2020: 18.91%).
- G4 positive years 7/7 — **PASS** (2020 only +1.11%).
- G5 median hold 120 min, max 1 open per side — **PASS**.
- Validity clause (lev <= 1.95 +2% on every trade): **BREACHED** — 6 of 1,068 trades at 1.99–2.04 (lot rounding up) [OBSERVED].
Verdict: **t423 FAIL (G3), plus validity breach.** No post-hoc change of gate or base.
Note [ASSUMED, design critique of my own PREREG]: the base is TV 0.075 (×0.5) while the arm ran TV 0.15, so the arm carries ~2× typical leverage in normal regimes — the DD gate measured the TV doubling, not only the cap. A fair cap test is TV 0.075 + MaxLev (t424).

