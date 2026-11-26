# PREREG t423 (Grok, frozen 26.11.2026 ~13:05 Israel, after Claude approval 12:40, before any t423 run) — I2 MaxLev cap, K=1 (I2-risk line: t421 K=0 -> K=1)

EA: mql5/IndexNoiseLev.mq5 (only change: input MaxLev replaces constant 5.0 at line 120). Fixed value MaxLev = 1.95, TV 0.15, same ECN server/model as in2dst_t; 7 yearly runs 2020–2026, each from 120K.
Sanity (must hold before evaluation): MaxLev=5 on 2024 reproduces +24,951.40 (in2dst_t_2024); else run is invalid.
Deals: Claude exports in the t402 column format (year, ts, dir, type, price, vol_per_100k, profit_pct, swap_pct, commission_pct) to grok_data/t423/, plus tester DD per year.

Base for comparison = in2dst_t (TV 0.15) × 0.5 (= TV 0.075, demo set), computed by Grok from grok_data/t402/i2_deals_2020_2026.csv.gz [non-compounded, % of 120K]:
net per year 2020 6.40, 2021 7.38, 2022 21.73, 2023 13.05, 2024 10.40, 2025 20.73, 2026 11.37; sum 91.06; positive years 7/7; closed-trade DD per year 10.70/6.55/5.97/3.66/3.69/6.89/4.19 (max 10.70).

Gates (all must pass):
- G1 (primary): t421 stress (t421.py method, sha e9e59e16…0d45, same scenario set W_side(h)) with k=1 and cap = MaxLev 1.95: max L_trade <= 25% equity.
- G2: sum of yearly net >= 85% of base (>= 77.40 % of 120K).
- G3: max closed-trade DD per year <= base max + 1pt (<= 11.70%); tester DD reported as info.
- G4: positive years >= base (7/7).
- G5: median hold >= 15 min, no stacking (max 1 open per side) — as t402.
Measured leverage per trade must be <= 1.95 (+2% tolerance for rounding); otherwise the cap is not enforced and the run is invalid.
Prediction (ASSUMED): stress ≈ 24.5% (pass by construction if cap enforced); net ≈ 75–95% of base (G2 borderline, because the cap binds mainly in high-lev quiet periods that earn); G4 risk in 2020/2021.
On FAIL: next = daily loss brake (GPT t411-b) or MaxLev+TV variants as a new PREREG (K counted). No live/demo change; adoption needs Nadav's approval.
