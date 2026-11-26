# PREREG t426 (Grok, frozen 27.11.2026 before any t426 computation) — max scale factor k under one-day stress, combined book C1-A4 + I2-ML1.90. MEASUREMENT ONLY: K+0, no gate, no recommendation.

Inputs (frozen, box paths):
- C1-A4: /workspace/t420/bars_t420_A4_MG0.5_drift.csv.gz (t418.py per-H6 output: E, gross, L_H6, L_H24, L_H48), /workspace/t420/t420_A4_deals.csv.gz.
- I2-ML1.90: /workspace/t424/tt/t424_lev190_20{20..26}.csv (7 yearly runs from 120K), /workspace/t424/tt/summary.json (tester eq DD), /workspace/t421/RESULTS_t421.json (W_long/W_short per horizon h=1..6).
- Method reused unchanged: t418 (C1: L_h(t) = max over historical BTC/ETH windows of -(sum N_s r_s)/E, no rebalance inside window) and t421/t424 (I2: L_trade = lev x W_side(h), lev = volume x price / (balance before entry commission), h = ceil(hold) in 1..6).

Step 0 (sanity, must reproduce): C1 max L_H24 21.12%, max L_H6 11.45%; I2 max L_trade 24.08%, net sum 87.84% of 120K, max closed DD 9.83%, max tester eq DD 10.05%, max lev 1.916. If not reproduced -> report INVALID.

Scaling model [ASSUMED]: k multiplies every position size (C1 notional/E and I2 lev) by k at every moment, i.e. EA caps scale too (MaxGross 0.5k, MaxLev 1.90k). Scenario loss then = k x L (linear in exposure/equity). Not modelled: margin call / stop-out, broker leverage limits, slippage in gaps -> loss on crash is NOT linear near margin/stop-out [ASSUMED, flagged].

Stress per mode (k grid 1, 1.5, 2, 2.5, 3):
- M1 C1 alone: S1(k) = k x max_t L_H24(t) (primary, "one day"); also k x max L_H6 (info).
- M2 I2 alone: S2(k) = k x max L_trade.
- M3 both same day (worst case): shared account, both strategies sized on the same equity, losses as % of equity add [ASSUMED simple additive]. Primary S3(k) = k x (max L_H24_C1 + max L_I2) (maxima need not coincide in time; conservative). Variant (info): k x (max L_H6_C1 + max L_I2). Info: time-aligned = max over I2 trades of (L_I2(trade) + L_H24_C1 at last C1 H6 bar <= trade entry), timestamps compared as-is (I2 server time vs Binance UTC, offset ignored [ASSUMED]).
- Max k per mode = 25 / (per-unit stress in %), exact, also for the info variants.

Historical net/DD under linear scaling [A] (per k):
- C1: per-H6-bar returns of reconstructed E (bars file) x k, compounded from 120K -> net % of 120K over 2020-01..2026-10 and max DD (MtM H6). Also tester-balance-column closed DD under same scaling.
- I2: per yearly run, bal_k = 120K + k x (bal - 120K); net = k x net_pct (sum of 7 years, % of 120K, non-compounded, as t424); closed DD = max over years of DD of bal_k. Tester eq DD x k (info, linear approx).
- Combined (shared account, per calendar year, non-compounded across years like t424): within year y, combined index = 1 + k x (rC1(t) + rI2(t)), rC1 = E(t)/E(year start)-1 on C1 H6 grid, rI2 = I2 closed balance/120K - 1 stepped onto the same grid (last I2 deal <= t). Net = sum over years of final index-1; DD = max over years of max DD of the index.

Claude's claim that Nadav approved C1 A4 and I2 MaxLev 1.90 for demo on 26.11 is tagged OBSERVED (from claude_outbox), not verified.
