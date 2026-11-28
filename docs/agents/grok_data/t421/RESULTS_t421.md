# RESULTS t421 — I2 intraday stress (PREREG_t421.md sha 8d814bac…f020). Grok, 26.11.2026 ~12:40 Israel
Code: t421.py. Raw: RESULTS_t421.json.
- Trades: 1,068 (2,136 deals); cs inferred 1.0000; median hold 2.0h; 7 trades hold >6h (h capped at 6, flagged).
- Worst adverse USTECH move (H1 high/low, 2018-01..2026-10, no gap windows):
  - long: 5.56% (1h) … 7.81% (4–5h), 16.03.2020.
  - short: 7.86% (1h, 23.03.2020) … 12.58% (5–6h, 09.04.2025 tariff-pause rally).
- Leverage lev = vol_per_100k × price / 100K [ASSUMED per-100K-of-equity]; max at k=1: 5.0 (2020, 2025) — Claude measured 4.88 in tester.

| arm | lev cap | max L_trade | at (trade entry) | trades L>25% | gate ≤25% |
|---|---|---|---|---|---|
| k=0.5 (TV 0.075 = demo set) | 5 | **33.46%** | 10.10.2025 short, h5, lev 2.66 | 11 | **FAIL** |
| k=1.0 (TV 0.15, info) | 5 | 62.89% | 10.10.2025 short, lev 5.0 | 202 | FAIL |
| k=1.25 (TV 0.1875) | 5 | 62.89% | 21.02.2020 short, lev 5.0 | 357 | **FAIL** |

Per-year max L_trade, k=0.5: 2020 30.6%, 2021 26.8%, 2022 16.5%, 2023 20.1%, 2024 17.6%, 2025 33.5%, 2026 22.3%.
Per-year max L_trade, k=1.25: 2020 62.9%, 2021 62.9%, 2022 41.3%, 2023 50.3%, 2024 43.9%, 2025 62.9%, 2026 55.8%.
Info — realised MAE inside trades × lev (H1): k=0.5 max 3.0%; k=1.25 max 7.5% (2020). The 25% breach is a scenario (worst historical 5–6h short squeeze applied to the year's max leverage), not something that happened to I2.
Binding scenario: short at max leverage into a +12.6% 5h rally (09.04.2025). Lev that meets 25% under the worst short scenario: ≤ 25/12.58 = 1.99; worst long: ≤ 25/7.81 = 3.2.
Verdict: t421 FAIL for both requested arms (×0.5 and ×1.25). No live/demo change by Grok.

