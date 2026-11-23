# PREREG t362: RoboQuant "Daily Anchored VWAP Signal Strategy" (promoted by Algo Jan)
Written 23.11.2026 (Asia/Jerusalem) BEFORE any backtest. Author: Grok. Task: Claude outbox 23.11.2026 16:10 (t362) + 19:20 evening order.
Status: research only. No gate approval, no trading. Decisions are Nadav's.

## 0. Source (published showcase, VERIFIED from https://roboquant.dev/t/67412d15-7437-4e3e-a9bb-bb714e4769d3, fetched 23.11.2026)
Published: MES 3m, 2023-01..2026-09, 396 trades, +299.9% (+$29,985), MaxDD 22.0%, PF 1.84, win 56.6%, Sharpe 1.55, 3 contracts/order, max 3 held. "Backtest results: not actual trading".
Published rules (MES 3m preset):
- VWAP anchored at the start of each New York trading day, from typical price (H+L+C)/3.
- EMA 11 (fast EMA).
- Signals read only inside session 09:30-16:00 ET.
- Long: EMA > VWAP and bar closes above EMA. Short: EMA < VWAP and bar closes below EMA.
- Exit: a close back across the EMA.
- Re-entry: after an exit, if the EMA crosses to the other side of VWAP, the first close back through VWAP against the new direction is a pullback entry.
- Daily limits: stop after the first winning trade of the day; after a first loss allow up to 2 further attempts.
- Volatility filter ON: skip entries when ATR14 > 1.1 x ATR50 baseline.
- ATR stop OFF. No time-based exit (positions may be held past session close).
- Size 3 MES.

## 1. Data (no ES/MES intraday with volume on the box; no RF US500 M1 on the box -> RF execution test NOT run)
- SPY 1-minute bars, Alpaca SIP feed, adjustment=all (split+dividend adjusted, so ex-dividend drops do not create fake overnight P&L; futures have no dividend drop). 2019-01-01..2026-09-30, all sessions 04:00-20:00 ET as delivered.
- Aggregated to 3-minute bars aligned to 09:30 ET (bar labels :30,:33,...). O=first, H=max, L=min, C=last, V=sum. Bars with no trades are absent (not filled).
- RTH session per day from Alpaca trading calendar (early closes respected: the session ends at that day's close).
- Coverage check: an RTH day with < 90% of expected 3m RTH bars is flagged; reported, not dropped unless < 50% (dropped and reported).

## 2. Unpublished parameter choices (documented before running)
1. VWAP anchor: 09:30 ET RTH open (task instruction; "New York trading day"). VWAP_t = cumsum(TP*V)/cumsum(V) over RTH 3m bars of the day up to and including bar t. SPY volume is used (proxy for MES volume).
2. EMA11, ATR14, ATR50 are computed on the continuous 3m series including SPY extended-hours bars (04:00-20:00), because MES trades ~23h and its indicators at 09:30 reflect overnight bars. EMA: alpha=2/12, seeded with first close. ATR: Wilder smoothing of True Range (TR uses previous bar close). "ATR50 baseline" = Wilder ATR(50) on the same bars. Filter: entry allowed only if ATR14 <= 1.1*ATR50 at the signal bar.
3. Signals and exits are evaluated only on RTH bars (bar start 09:30 .. last bar before session close). Outside RTH a position is simply held (this is how "held past the session close" arises). Reason: "Signals are read only inside a configurable session window".
4. Execution: signal on bar t close -> fill at open of bar t+1 (next RTH bar of same day). If bar t is the last RTH bar of the day, fill at bar t close (16:00 / early-close close). No same-bar reversal: entries are evaluated only when flat at the bar close; after an exit signal, the earliest new entry signal is the next bar's close.
5. Daily limits (per ET session date): max 3 entries per day (1 + 2 further attempts after losses); no new entries for the rest of the day once a trade closes as a winner that day (win/loss credited to the day the trade exits, net of costs). A trade carried overnight does not count as an entry of the next day.
6. Pullback re-entry: after an exit, track EMA vs VWAP; if EMA crosses to the opposite side of VWAP relative to the exited trade (exited long -> EMA moves below VWAP), the setup is armed in the new direction (short). While armed, an entry triggers on the first RTH bar whose close crosses VWAP in the new direction (short: prev close >= prev VWAP and close < VWAP; long mirrored) with EMA still on the new side. Arm is cleared on any entry and at session start. Base entries remain active in parallel; whichever triggers first is taken. Same daily limits and volatility filter apply.
7. Price mapping: MES = $5 x ES index; ES ~= 10 x SPY (basis ignored, ASSUMED). 3 MES P&L in $ = 3*5*10*dir*(SPY exit - SPY entry) = 150*dir*dSPY.
8. Starting capital for replication units: $10,000 (implied by +$29,985 = +299.9%). Non-compounded $ equity (fixed 3 contracts).
9. Unlevered "1x": position notional = 100% of current equity (compounded), long or short, one position at a time. No financing cost on overnight holds (futures-like; ASSUMED).

## 3. Costs
- Base (1x): MES 0.25 index point slippage per side + $0.62 commission per side per contract. In SPY terms per side: (0.25*5 + 0.62)/ (5*10*P) = 0.0374/P fraction of notional (~0.6-0.9 bp/side). Round trip per 3 MES = $11.22.
- Stress: 2x costs.
- RF US500: not tested (no data on box).

## 4. Periods (run order)
(a) Replication 2023-01-01..2026-09-30 (their in-sample). Reported, no gate.
(b) DEV 2019-01-01..2020-12-31. Gate below.
(c) Holdout 2021-01-01..2022-12-31: run ONCE and only if DEV passes all gates (corr gate UNKNOWN counts as "pending", holdout then still runs only if all other DEV gates pass). If DEV fails, holdout is NOT run and its data stays unexamined.
Indicator warm-up: each run starts 10 trading days earlier for indicators only; no trades in warm-up.

## 5. Density check (first)
DEV must have >= 100 trades total and >= 40 per year; else verdict INCONCLUSIVE (density) and no holdout.

## 6. DEV gate (all at base costs, 1x unlevered)
- PF >= 1.3 (trade-level net returns).
- Annualized Sharpe >= 0.8 (daily 1x returns, all trading days incl. flat days, sqrt(252), close-to-close at 16:00 ET marks).
- Both 2019 and 2020 calendar-year returns > 0.
- Daily correlation to I2 <= 0.5 (Pearson, common trading days). I2 source: Claude's official I2 daily series if found on the box; else the Grok clean-room replica /workspace/independent_review/results/i2_USATECHIDXUSD_daily.csv (demo-set I2 on Nasdaq CFD, net costs) used as PROXY and labeled OBSERVED-proxy; official value then UNKNOWN pending Claude.
Holdout uses the same thresholds (PF>=1.3, Sharpe>=0.8, both 2021 and 2022 > 0).

## 7. Replication match (pre-declared tolerance)
"Replicates" iff trades within +-25% of 396, PF within +-0.30 of 1.84, win rate within +-5pp of 56.6%, and net $ P&L same sign and within +-50% of $29,985. Otherwise "does not replicate" (with notes on likely causes: SPY vs MES, volume source, interpretation).

## 8. Reporting
Per year; long vs short; share of net P&L from overnight segments (16:00 close -> next RTH open) and from trades held overnight; comparison with I2 on the same days; replication vs published; unlevered vs their ~x6-x10 notional leverage (3 MES notional / $10K equity, reported per year).
Sharpe/DD for their units: daily $ P&L / ($10K + cum P&L), sqrt(252). Their exact Sharpe method is UNKNOWN.

## 9. Multiple testing
This is ONE pre-specified configuration (the published preset) = 1 trial added to the company Holm/DSR count (t362). Replication and stress-cost runs are not selection trials. No parameter search, no tuning.
