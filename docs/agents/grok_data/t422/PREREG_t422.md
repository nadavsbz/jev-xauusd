# PREREG t422 (Grok, frozen 26.11.2026 ~16:55 Israel, after Claude's spec+approval 16:35, before any t422 run) — C1_ADVERSE_SHOCK_BRAKE_V1 (GPT t411 §3, verbatim via Claude), K=1 (C1-risk line cumulative K: t419 2 + t420 2 + t422 1 = 5)

Base (frozen, same as t420): C1 ECN BTC/ETH, AV 0.075, TV 0.2, MaxGross 3, vol window 60, RebalPct 15%, tester c1_ecn_av075_full: net +268,852, DD 14.06%, 120K, real ticks 2020-01..2026-10. t418 on base [VERIFIED t418]: L_H6 19.7%, L_H24 36.4%.

Arm B1 (fixed, no variants): base + brake. At each completed H6 bar i: ShockScore_s = |ln(C_i/C_{i-1})| / Std(last 60 completed H6 log returns up to i-1), s in {BTC, ETH}. Trigger if for at least one s: ShockScore_s >= 3.0 AND the move was against the target held during bar i in s (long & r<0 or short & r>0). Action: all C1 targets in all assets x0.5 for 4 H6 bars; a new trigger during the brake restarts the 4 bars; then back to normal. AV/TV/MaxGross/lookbacks/RebalPct unchanged; no hedge. Separate EA file; live untouched. Claude states in the deals doc how the x0.5 is executed (immediate resize ignoring RebalPct, or via rebalance) — fixed before the run.

Stress method change (new, declared here): t418.py core unchanged for positions/E/scenarios; add brake-aware loss per scenario window (H24 = 4 H6 bars, no rebalance otherwise): let k = first bar (1..4) in the scenario where the trigger condition holds, using the scenario's own returns against the then-held position sign and the 60-bar historical std up to T (scenario bars appended); if k exists: L_brake = L_Hk + 0.5*(L_H24 - L_Hk) (cumulative losses at the window's end of bar k and bar 4, linear approximation, Claude 16:35, generalised from k=1 to first trigger); else L_brake = L_H24. Script t422_stress.py published with sha before evaluation; any bug fix must be declared.

Gates (all must pass):
- G2 (primary): max L_H24_brake <= 25%.
- G1: max L_H6 <= 25% (unchanged method).
- G3: tester net >= 85% of base (>= +228,524).
- G4: tester equity DD <= 15.06%.
- G5: positive years >= 6/7.
Info (not gate): number of brake triggers per year, plain L_H24 without brake.
Predictions (ASSUMED): March 2020 first bar is likely >3σ, so worst L_H24_brake ≈ 19.7 + 0.5*(36.4-19.7) ≈ 28% -> G2 likely FAIL; net ≈ 95-100% of base.
On FAIL: C1-risk line closed with this design; next options to Claude/Nadav: accept AV0.075 with A4-style lower net, or no further C1 risk work. No live/demo change by Grok; adoption needs Nadav's approval.
