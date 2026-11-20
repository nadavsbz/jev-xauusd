# RESULTS: C1 exit variants (Grok), 17.11.2026 00:09 IST (Asia/Jerusalem)
- **PREREG:** `PREREG_c1_exits_grok.md`, sha256 `89acc43e1f5124dc600bc25d08973ff92b2469d9380efca881d6a758ffada13c`. Written 00:06 IST, before any return computation.
- **Script:** `c1_exits_grok.py`, sha256 `9a0202df600bdb4ed8a57a07e2cc813d966e3a1391c936618203f53464e60254`. It's a port of `research/scan/r82_c1_exit.py` BASE from feat/portfolio, read from git.
- **Logs:** `log_rf_dev_base.txt`, `log_rf_dev.txt`, `log_binance_dev.txt`. JSON results: `res_rf_dev.json`, `res_binance_dev.json`.

## 1. Base reproduction (gate: Sharpe 1.52 ± 0.15). PASSED
| | Sharpe dev 2017–22 | MDD |
|---|---:|---:|
| Claude r82 BASE (on Benzaquen) | 1.52 | −20.1 |
| Grok port, RF H1 on box (`research_new_component/data/cfd_h1`) | **1.57** | **−18.4** |

- **Years (%, sum of daily):** 2017 +51, 2018 +28, 2019 −2, 2020 +41, 2021 +13, 2022 −4.
- **Likely reasons for the +0.05 Sharpe and the 1.7-point MDD gap:**
  - tc = 1.5 bp/side for both assets. The `ecn_costs_20261030.csv` table isn't on the box, so the median spread came from the file with point = 0.01 (ASSUMPTION).
  - Swap was taken as −4.75%/yr for both assets (ETH ASSUMED).
  - The box H1 file may differ from Benzaquen's `loadh` source (to verify).
- The reproduction is inside the gate, so the variants were run.

## 2. Dev 2017–2022 (RF, the gate). All 3 FAIL
| Variant | Sharpe | Δ vs base | MDD | corr to base | Gate (Sh ≥ base+0.10 and MDD not worse) |
|---|---:|---:|---:|---:|---|
| BASE | 1.57 | — | −18.4 | — | — |
| E1 ATR chandelier 3×ATR22·√(n/22), replaces n/2 | 1.57 | −0.00 | −19.8 | 0.95 | **FAIL** |
| E2 half out at 2σ√n, rest on n/2 | 1.62 | +0.04 | −17.0 | 0.98 | **FAIL** (Sharpe) |
| E3 exit on an adverse H6 bar beyond 3σ | 1.61 | +0.03 | −17.1 | 0.96 | **FAIL** (Sharpe) |

- **Years E1:** 17 +51, 18 +25, 19 −4, 20 +44, 21 +13, 22 −5.
- **Years E2:** 17 +49, 18 +27, 19 0, 20 +40, 21 +15, 22 −4.
- **Years E3:** 17 +51, 18 +29, 19 −4, 20 +39, 21 +13, 22 +2.

**Holdout 2023–26 was NOT run** (no variant passed dev, per the prereg).

## 3. Secondary check, not a gate: Binance BTCUSDT/ETHUSDT 1h, 10 bp/side taker, dev 2017-08..2022
| | Sharpe | Δ | MDD |
|---|---:|---:|---:|
| BASE | 1.10 | — | −16.8 |
| E1 | 1.10 | +0.00 | −17.2 |
| E2 | 1.12 | +0.02 | −14.8 |
| E3 | 1.12 | +0.02 | −14.9 |

- The base is lower because of the cost (10 bp vs 1.5 bp) and the short warm-up (the data starts 17.08.2017).
- The ranking is the same as on RF.

## Conclusion
- **Nothing passes.** With r82, 6 exit trials have now failed: V1–V3 and E1–E3. Changing the exit moves Sharpe by at most ±0.05, and the correlation to the base is 0.95–0.98.
- The 7-lookback ensemble and the vol targeting already smooth out the exit choice. This matches the prior that the n/2 exit is not a lever.
- **HUNCH, not a pass:** E2 and E3 lower dev MDD by about 1.3 points on both data sets. That's weak and was not pre-registered as a goal. It isn't worth a holdout trial unless Nadav specifically wants lower DD at the same Sharpe.
- **No EA change is recommended.**
