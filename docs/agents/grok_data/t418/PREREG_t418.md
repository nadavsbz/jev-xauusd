# PREREG t418-STRESS (Grok, 26.11.2026 09:05 Israel) — K=0, engineering/risk test, not alpha

Question: can C1 (BTC/ETH, ECN, 120K deposit) at AssetVol 0.15 suffer a scenario loss above 25% of equity because exposure peaks in quiet regimes, even though historical tester DD = 18.6%?

Data (frozen): grok_data/t418/t417_av15_tv20_deals.csv.gz (AV 0.15), c1_ecn_av075_full_deals.csv.gz (AV 0.075, control). Prices: Binance BTCUSDT/ETHUSDT 6h 2018-06..2026-10 (/workspace/t417_kL, sha in SHA256SUMS_t417.txt) as a MtM and scenario proxy.

Method:
1. Rebuild signed net position (lots) per symbol after every deal. Contract size per symbol inferred from closed deals: cs = median(profit / (volume x price change vs. matched entry)); report it.
2. At every H6 close 2020-01..2026-10: net notional N_s = lots x cs x Binance close; equity E = balance + floating (MtM at Binance close vs. avg entry). Gross = sum|N_s|/E.
3. Scenarios = every historical joint (rBTC, rETH) return of the same window in the Binance 2018-06..2026-10 data, for horizons H6 (1 bar), H24 (4 bars), H48 (8 bars), no rebalancing inside the window. Scenario loss L_h(t) = max over windows of -(sum_s N_s(t) x r_s(window)) / E(t).
4. Report per AV: max gross, max L_h over time (with timestamp and scenario window), share of bars with L_h > 25%, per-year max.

Gates (fixed before computing):
- G1 (PRIMARY, pass/fail): max over time of L_H6 <= 25% equity. H6 = one bar the EA cannot react within (gap / no-tick).
- G2 (pass/fail): max L_H24 <= 25% equity (EA rebalances every H6, so this is conservative).
- H48 reported only (informational).
- C1 at AV 0.15 is "stress-OK for Nadav's 25% cap" only if G1 AND G2 pass. Control AV 0.075 is reported with the same gates. No re-tuning of horizons/gates after seeing results.

Prediction (ASSUMED): G1 pass for both; G2 at AV 0.15 borderline-fail (worst 24h BTC/ETH moves ~ -40%..-50% in 03.2020, gross up to ~1.4).
Tags: positions VERIFIED from deals; Binance as RF price proxy ASSUMED (basis < 1%).
