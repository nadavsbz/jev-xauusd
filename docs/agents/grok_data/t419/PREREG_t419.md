# PREREG t419 (Grok, 26.11.2026 09:40 Israel) — C1 exposure-tail fix, K=2 (cumulative trial count for the C1-risk line: t417 K=0, t418 K=0, t419 K=2)

Base (frozen): C1 ECN BTC/ETH, AV 0.075, TV 0.2, MaxGross 3, vol window 60, tester c1_ecn_av075_full: net +268,852, DD 14.06%, deposit 120K, real ticks 2020-01..2026-10. t418: L_H6 19.7%, L_H24 36.4%.

Arms (fixed, no other variants, no re-tuning):
- A1: MaxGross 0.6, everything else = base (existing EA input).
- A2: per-asset vol window 20 H6 bars instead of 60 (new input in a separate EA file written by Claude; live file untouched), everything else = base.

Tester: Claude runs both arms on the same server/period/deposit/model as base; exports deals (same columns as t418) to grok_data/t419/. Grok computes the stress with the frozen t418.py method (sha de171394…f28a), unchanged.

Gates per arm (all must pass):
- G2 (primary): max L_H24 (no rebalance inside window) <= 25% equity.
- G1: max L_H6 <= 25%.
- G3: tester net >= 85% of base (>= +228,524).
- G4: tester equity DD <= 14.06% + 1pt (<= 15.06%).
- G5: positive years >= base (6/7).
Arm passes only if G1–G5 all pass. If both pass: prefer higher net/L_H24 ratio. If none: next family = vol-of-vol trigger / regime gross cap (new PREREG).

Informational only (not a gate), per Claude's P1: L_H24_reb = scenario loss with simulated H6 rebalancing inside the window — exposure recomputed each H6 bar using the arm's vol window updated with in-scenario returns (TV overlay kept as in the base position, i.e. k fixed at its value at t; ASSUMED simplification), lower-bound realism check.

Predictions (ASSUMED): A1 L_H24 ≈ 36.4×0.6/0.875 ≈ 25% (borderline), net −10..−20%; A2 L_H24 drops less than A1 (vol(20) still lags a 24h crash), net change ±10%.
No live/demo change from this PREREG; any adoption needs Nadav's approval.
