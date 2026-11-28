# RESULTS t419 FINAL (PREREG_t419.md, Grok, 26.11.2026 ~11:45 Israel)

## A2 (VolBars 20) — t418.py core unchanged (sha de171394…f28a), wrapper run_t419_A2.py
- G1 max L_H6 20.38% PASS
- G2 max L_H24 37.63% (2024-06-06 00:00 UTC, scenario 2020-03-12/13) FAIL — worse than base 36.4%
- G3 net from deals balance column: final 344,509.04 - 120,000 = +224,509 = 83.5% of base +268,852 (< 85%) FAIL [OBSERVED from deals; Claude's tester report not yet seen]
- G4 tester DD: not reported by Claude yet (UNKNOWN). Info: reconstructed H6 MtM DD 16.26%, balance-column DD 11.95%
- G5 not computed (needs tester report)
- deals 5587 vs base 4950; commission -9,964 vs base -8,385; swap -16,378 [OBSERVED]
- max gross 0.913 (2023-01-11)
Verdict A2: FAIL (G2, G3).

## A1 (MaxGross 0.6): FAIL G2 27.5% (delivered 10:40, RESULTS_t419_A1.md)

## L_H24_reb (informational only, not a gate; l_h24_reb.py)
Method: same scenario set (all overlapping 4-bar H6 joint BTC/ETH paths 2018-06..2026-10), rebalance after each H6 bar inside the window:
target notional_i = E_t × (N_i0/E_0) × vol_i0/vol_i,t, vol = sample std of last n H6 simple returns (n=60 A1, 20 A2) rolling in scenario returns; TV overlay k fixed (ASSUMED); RebalPct 15% threshold ignored (always rebalance, ASSUMED); A1 gross cap 0.6 re-applied at each rebalance.
| arm | L_H24 (no reb, gate) | L_H24_reb (info) | bars >25% reb |
|---|---|---|---|
| A1 MG0.6 | 27.52% | 19.81% (T 2023-10-24 00:00, window from 2020-03-12 06:00) | 0 |
| A2 VB20 | 37.63% | 22.38% (T 2023-09-06 12:00, window from 2025-03-02 06:00) | 0 |
Note: vol(20) helps only when rebalancing inside the crash; the frozen gate (G2, no rebalance) is unchanged.

## t419 verdict: 0/2 arms pass. Cumulative trial count C1-risk line: K=2 (t417 0, t418 0, t419 2).

