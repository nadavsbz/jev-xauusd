# PREREG t420 (Grok, frozen 26.11.2026 ~12:20 Israel, after Claude approval 12:10) — C1 gross cap with drift enforcement, K=2 (cumulative C1-risk line: t419 K=2 -> K=4)

Base (frozen): C1 ECN BTC/ETH, AV 0.075, TV 0.2, MaxGross 3, vol window 60, tester c1_ecn_av075_full: net +268,852, DD 14.06%, 120K, real ticks 2020-01..2026-10.
Motivation [OBSERVED t419 A1]: cap enforced only at target/rebalance (RebalPct 15%) let realised gross drift to 0.671 > 0.6.

Arms (fixed, no other variants, no re-tuning):
- A3: MaxGross 0.6 + drift enforcement: on each check (Claude's EA, new input, separate file; live untouched) if current gross = sum|notional|/equity > MaxGross, reduce immediately to MaxGross ignoring RebalPct. Everything else = base.
- A4: MaxGross 0.5 + the same enforcement. Everything else = base.
Claude must state the check frequency (OnTick or bar) in the deals doc; whichever it is, it is fixed before the run.

Tester: Claude, same server/period/deposit/model as base; deals (t418 columns) to grok_data/t420/ plus tester DD, net, net per year. Grok runs t418.py unchanged (sha de171394…f28a) via a filename-only wrapper.

Gates per arm (all must pass, same as t419):
- G2 (primary): max L_H24 (no rebalance inside window) <= 25%.
- G1: max L_H6 <= 25%.
- G3: tester net >= 85% of base (>= +228,524).
- G4: tester equity DD <= 15.06%.
- G5: positive years >= 6/7.
Both pass -> prefer higher net/L_H24. None -> 'gross cap' family closed; next = t422 C1_ADVERSE_SHOCK_BRAKE_V1 (GPT t411), new PREREG.
Informational (not gate): L_H24_reb with l_h24_reb.py (sha cad4ca45…056c), cap re-applied each H6.

Predictions (ASSUMED): A3 max gross ≈0.61, L_H24 ≈24.6% (borderline), net ≈91–93%; A4 L_H24 ≈20.5%, net ≈80–88% (G3 borderline).
No live/demo change; adoption requires Nadav's approval.
