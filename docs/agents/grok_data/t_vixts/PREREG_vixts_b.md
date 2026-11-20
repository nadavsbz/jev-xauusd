# PREREG (b) - VIX/VIX3M term-structure switch for long US500 / USTECH
Written 17.11.2026 08:25 Asia/Jerusalem, BEFORE any run on this hypothesis. No results seen.

## Hypothesis
Long index exposure is earned when the VIX curve is in contango (VIX/VIX3M < k) and should be flat in backwardation.
Goal per Claude's 16.11 21:00 push: >=1%/month net, low correlation to BD.

## Data (frozen, on the box)
- research_new_component/data/yahoo/VIX_daily.csv, VIX3M_daily.csv (Yahoo, VIX3M starts 2006-07-17)
- research_new_component/data/yahoo/GSPC_daily.csv (US500 proxy), NDX_d.csv (USTECH proxy)
- Dev: 2006-08-01 .. 2015-12-31. Holdout: 2016-01-01 .. 2026-11-11 (untouched until dev is frozen).

## Rule
- r_t = VIX_close(t) / VIX3M_close(t). Position for day t+1 (close-to-close) = L if r_t < k else 0. No lookahead.
- k grid (dev only): {0.90, 0.95, 1.00}. 3 values x 2 assets = 6 dev trials. Pick ONE k per asset by dev Sharpe.
- Leverage L: chosen on dev so dev MDD = 20%, then frozen.

## Costs (RF ECN, per Claude 21:18 table)
- Long swap 8.6%/yr on notional x L, charged per calendar day held (incl. weekends).
- 2bp per side on each switch (in/out), plus 1bp slippage per side.

## Gates (holdout, single run, both assets reported)
PASS only if ALL: net >= 1.0%/month; MDD <= 25%; Sharpe >= buy&hold(same L, same swap) Sharpe + 0.20;
>= 7 of 11 calendar years positive; correlation of daily returns to BD live deals <= 0.3 on overlap.
Kill: if dev best Sharpe - B&H Sharpe < 0.10 on both assets, stop before holdout.
Cumulative trials: report DSR with this family's 6 trials added to the running count.
