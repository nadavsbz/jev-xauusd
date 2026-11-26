# PREREG t424 (Grok, frozen 26.11.2026 ~14:35 Israel, after Claude approval 14:10, before any t424 run) — I2 at TV 0.075 + MaxLev 1.90, K=1 (I2-risk line cumulative K=2: t423, t424)

EA: mql5/IndexNoiseLev.mq5 (input MaxLev; lots MathFloor; sizing on day open price R[io].open — source of post-entry lev drift [VERIFIED by Claude from code]).
Arm (fixed): live set nasdaq_ecn_x15 (TV 0.075) + DstFix + LateSec, MaxLev = 1.90; 7 yearly runs 2020–2026 from 120K, same ECN server/model, real ticks.
Sanity (must hold): MaxLev 5 on 2023 reproduces t375_orig_2023 = +15,430.96; else invalid.
Deals: same CSV format as t423 (ts,type,dir,volume,price,profit,swap,commission,balance) + summary.json to grok_data/t424_tester/.

Base (unchanged from t423): in2dst_t × 0.5: net per year 6.40/7.38/21.73/13.05/10.40/20.73/11.37 (sum 91.06, % of 120K), 7/7 positive, max closed DD 10.70%.
Note [OBSERVED]: the true TV 0.075 run for 2023 is +12.86% (15,430.96) vs ×0.5 proxy 13.05%; the proxy base is kept as frozen; the sanity run is reported alongside as info.

Gates (all must pass; evaluated with t423_eval.py method, sha 3a0c4ca4…337f, only file paths changed):
- G1: stress (t421 W_side(h), leverage measured per trade = volume×price/balance before entry) max L_trade <= 25%.
- G2: net sum >= 85% of base (>= 77.40).
- G3: max closed-trade DD per year <= 11.70%.
- G4: positive years 7/7.
- G5: median hold >= 15 min, max 1 open per side.
- Validity: every trade lev <= 1.989 (1.95 +2%, as before); breach = INVALID.
Predictions (ASSUMED): cap binds only at peak-lev periods (2020/2025, ~2.6); G1 pass, net 80–95 (G2 borderline-pass), G3 ≈ base, G4 7/7.
On FAIL: next = daily loss brake (GPT t411-b), new PREREG, K counted. No live/demo change by Grok; adoption needs Nadav's approval.
