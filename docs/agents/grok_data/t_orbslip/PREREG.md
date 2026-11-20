# PREREG — t_orbslip: ORB exit-mechanism slippage cross-check (NOT a strategy test)
Written 17.11.2026 ~20:05 (Asia/Jerusalem) by Grok, BEFORE any ORB computation was run.
Data was being downloaded while this was written; no trade-level number had been computed.

## Purpose
Measure, for the Concretum 5-min ORB *mechanism* (no stocks-in-play / relative-volume filter),
how many R the per-share costs consume when risk = 10% of ATR14, by ATR bucket.
It is a cost-sensitivity measurement on a fixed large-cap universe, not an attempt to reproduce the paper's Sharpe.

## Data (public, no signup)
- Dukascopy public datafeed, US stock CFDs (`<ticker>.US/USD`), 1-minute candles, BID and ASK separately,
  via the open-source `dukascopy-node` CLI. Period 2018-01-01 .. 2025-12-31.
- Universe (fixed in advance, 30 large US stocks with Dukascopy ticks since 2017):
  AAPL MSFT AMZN GOOGL META(FB) NVDA TSLA NFLX INTC CSCO JPM BAC C WFC GS XOM CVX JNJ PFE KO PG DIS HD V T BA AMD MU CAT AAL.
- Prices: MID = (bid+ask)/2 per OHLC field. Timestamps converted UTC -> America/New_York. Bar label = bar start.
- RTH = bars 09:30..15:59 NY. Day is kept only if it has >= 380 RTH bars and all of 09:30..09:35 present
  (this drops half-days and gappy days; count reported).
- Prices are CFD quotes, not consolidated exchange prints; Dukascopy does not apply split adjustment uniformly —
  any day with |RTH open / previous RTH close - 1| > 30% is dropped and counted (split artefacts).

## Mechanism (fixed)
1. First 5-min candle: O = mid open of 09:30 bar, C = mid close of 09:34 bar.
   C > O -> long, C < O -> short, C == O -> skip (doji).
2. Entry at mid OPEN of the 09:35 bar.
3. ATR14 = simple mean of the last 14 daily True Ranges computed from RTH-aggregated daily OHLC of the same data,
   using days strictly BEFORE the trade day (no look-ahead). Needs 14 prior valid days.
4. Risk per share R$ = 0.10 * ATR14. Stop = entry - R$ (long) / entry + R$ (short).
5. Walk bars 09:35..15:59. If bar low <= stop (long) / bar high >= stop (short): exit at stop,
   or at the bar open if the open is already beyond the stop (gap-through, worse fill).
   The 09:35 entry bar itself is included: if its range touches the stop, the trade is counted as STOPPED
   (conservative same-bar ambiguity rule).
6. Otherwise exit at mid CLOSE of the 15:59 bar (= 16:00 close).
7. Gross R = dir * (exit - entry) / R$.

## Costs (per share, per side; applied to entry and exit)
- slippage s in {0.00, 0.01, 0.02} $/share/side; commission 0.0035 $/share/side.
- cost_R(s) = 2*(s + 0.0035) / R$ ; net R = gross R - cost_R(s).
- Sensitivity B (data-quality): fill long entries / short exits at ASK and short entries / long exits at BID
  (i.e. cross the Dukascopy quoted spread) instead of mid, no extra slippage. Reported separately.

## Reported (no tuning, single run)
- Trades, mean R, median R, win rate (gross R > 0), stop-out share — overall, per year, per stock.
- By R$ bucket (risk per share): <0.10, 0.10-0.25, 0.25-0.50, 0.50-1.00, >=1.00 $:
  n, mean gross R, cost_R at s=0/0.01/0.02 (incl. commission), mean net R at each s.
- Median Dukascopy quoted spread at 09:35 per stock (in $ and in R) and flat-bar share in RTH (data-quality flags).
- Interpretation rule (fixed now): a bucket is "cost-killed" at a given s if mean net R <= 0.
