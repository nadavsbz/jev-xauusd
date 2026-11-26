# RESULTS t426 — max scale factor k under one-day stress, C1-A4 + I2-ML1.90 (PREREG_t426.md sha256 070760f3928d1ac8bc688f44125f700cea847ca9c627972af5dac9089d0e3ff3)
Grok, 27.11.2026 (Israel time). Code: t426.py. Raw: RESULTS_t426.json. MEASUREMENT ONLY: K+0, no gate, not a recommendation.

## Sanity (step 0) [VERIFIED, all reproduced to 0.01]
C1-A4: max L_H24 21.12% (at 2023-04-14 06:00:00 UTC, scenario BTC/ETH 12.03.2020 24h), max L_H6 11.45%, max gross 0.503. I2-ML1.90: max L_trade 24.08% (short 2025-10-10 18:00:00, h=5, scenario USTECH 09.04.2025 +12.58%), net 87.84% of 120K, closed DD 9.83%, tester eq DD 10.05%, max lev 1.916. sanity_ok=True.

## Stress loss per mode (% of equity) [VERIFIED computation; linear-in-k model ASSUMED]

| k | M1 C1 alone (H24) | M1 C1 (H6, info) | M2 I2 alone | M3 both (C1 H24 + I2) | M3 both (C1 H6 + I2, info) | M3 time-aligned (info) |
|---|---|---|---|---|---|---|
| 1 | 21.12 | 11.45 | 24.08 | 45.19 | 35.53 | 42.96 |
| 1.5 | 31.67 | 17.17 | 36.12 | 67.79 | 53.29 | 64.44 |
| 2 | 42.23 | 22.90 | 48.16 | 90.39 | 71.05 | 85.92 |
| 2.5 | 52.79 | 28.62 | 60.19 | 112.98 | 88.82 | 107.40 |
| 3 | 63.35 | 34.34 | 72.23 | 135.58 | 106.58 | 128.87 |

**Exact max k (stress = 25%):** M1 C1 H24 **1.1840** (H6: 2.1838); M2 I2 **1.0383**; M3 both (H24) **0.5532** (C1 H6 + I2: 0.7037; time-aligned: 0.5820).
Note: at k=1 the combined book already fails 25% in mode M3 (45.19%); only k <= 0.553 meets it under the coinciding-crash assumption.

## Historical net / DD under linear scaling [A]

| k | C1 net % of 120K (compounded 2020-01..2026-10) | C1 DD MtM H6 | C1 DD balance col | C1 max gross | I2 net sum % of 120K (7 yearly runs) | I2 closed DD max | I2 eq DD x k (lin) | I2 max lev | Combined net (sum of yearly, % of year-start) | Combined DD (max within-year) | Combined gross |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 182.51 | 13.51 | 10.91 | 0.503 | 87.84 | 9.83 | 10.05 | 1.916 | 208.12 | 10.00 | 2.419 |
| 1.5 | 358.28 | 19.67 | 15.93 | 0.754 | 131.76 | 13.88 | 15.08 | 2.875 | 312.19 | 13.46 | 3.629 |
| 2 | 626.04 | 25.44 | 20.67 | 1.006 | 175.68 | 17.49 | 20.10 | 3.833 | 416.25 | 16.33 | 4.838 |
| 2.5 | 1023.44 | 30.86 | 25.16 | 1.257 | 219.60 | 20.72 | 25.12 | 4.791 | 520.31 | 18.96 | 6.048 |
| 3 | 1597.87 | 35.94 | 29.41 | 1.508 | 263.52 | 23.63 | 30.15 | 5.749 | 624.37 | 21.23 | 7.258 |

## Assumptions / flags
- [ASSUMED] k scales every position (MaxGross 0.5k, MaxLev 1.90k). Loss on a crash is NOT linear near margin call / stop-out; broker margin/stop-out levels not modelled [UNKNOWN]. Combined gross reaches 4.84 at k=2 and 7.26 at k=3.
- [ASSUMED] At k>=2.61 I2 lev would exceed the EA hard cap lev=min(5,..) (k=3: 5.75); the table ignores that cap (pure linear).
- [ASSUMED] M3 = simple additive equity loss on a shared account, both sized on the same equity; the worst C1 and worst I2 scenarios are added even though their maxima occur at different times (conservative). Time-aligned info column uses C1 L_H24 at the last H6 bar <= each I2 entry (server time vs UTC offset ignored).
- [ASSUMED] C1 net/DD: per-H6 returns of reconstructed Binance-MtM equity x k, compounded. I2: non-compounded yearly runs from 120K (t424 basis). Combined: per calendar year, 1 + k(rC1 + rI2), net = sum of yearly results (non-compounded), DD = max within-year (cross-year drawdowns not captured; C1's own DD 13.51% falls within 2023, offset in the combined index by I2's 2023 gains).
- [OBSERVED, from claude_outbox, not verified] Claude reports Nadav approved C1 A4 and I2 MaxLev 1.90 for demo on 26.11.
- Measurement only. Per Nadav's standing preference, leverage/portfolio-combination games are not pursued without his approval.
