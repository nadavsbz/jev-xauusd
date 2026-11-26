# PREREG t421 (Grok, frozen 26.11.2026 ~12:20 Israel, before any computation) — I2 intraday stress, K=0 (risk test, not a strategy trial)

Input: grok_data/t402/i2_deals_2020_2026.csv.gz (Claude b96d8a8; TV 0.15, each year from 100 = 120K; columns vol_per_100k, price, profit_pct). Prices: USTECHCash H1 OHLC (RF, server time, 2017-12..2026-11, box copy /workspace/t295/in/USTECHCash.csv).
Leverage per trade: lev = vol_per_100k × cs × entry_price / 100,000 with cs inferred from profit_pct / (vol × dPrice) (median; expected 1). [ASSUMED: vol_per_100k is per 100K of equity at entry.]
Arms: k ∈ {0.5, 1.25} as Claude asked (+ k=1.0 info): lev_k = min(5, k × lev) (cap 5 as in EA: lev=min(5,TV/vol)).

Scenario set: for every H1 bar start t in 2018-01..2026-10 and horizon h = 1..6 bars (only windows whose span ≤ h+1 hours, i.e. no weekend/holiday gap), adverse move for long = 1 - min(low[t..t+h-1])/open[t]; for short = max(high[t..t+h-1])/open[t] - 1. W_side(h) = max over all t.
Per trade: h = ceil(hold hours) capped at 6 (hold > 6h: use 6 and flag); L_trade = lev_k × W_side(h). Per year: L_year = max over that year's trades; also 'Claude form' = (max lev_k in year) × W_side(6) (worst side).
Gate (per arm): max over all trades of L_trade ≤ 25% equity. Secondary (info): Claude form, realised MAE within trade from H1 high/low × lev_k, count of trades with L_trade > 25%.
No re-tuning; any variant after seeing results = new trial. No live/demo change; I2 scaling decision stays with Nadav.
