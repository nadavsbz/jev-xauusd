# PREREG t368: US tariff-announcement event study (TiRADE v1.10) + one reversal rule + C1/I2 description
Written 23.11.2026 ~21:10 Asia/Jerusalem, BEFORE any price was downloaded for this round. Author: Grok (המאסטרו).
Task: Claude outbox 23.11.2026 21:00 (t368). Standing protocol: /workspace/t363/event_claims_protocol.md (t363).
Status: research only. No gate approval, no trading recommendation. Decisions are Nadav's.

## 0. Event source (VERIFIED)
- TiRADE v1.10 rate statements, https://www.globallinkages.org/datasets/tirade/v1.10/tirade-v1.10-rate-statements.csv
  (free, no licence/login; downloaded 23.11.2026 21:04). sha256 73153ba2abb489ebbf872298826ace0eb7dbb2469a5298b1f5a18b9466c777f1 = the sha published on the dataset page.
  773 rows, coverage 2025-01-21 .. 2026-11-12, times in US Eastern.
- **Deviation forced by the data (decided before prices):** TiRADE starts 2025-01-21 (second Trump term). There are no events before 2025,
  so Claude's "DEV through 2024 / holdout 2025+" split is impossible. Replacement, locked now:
  **DEV = events with day1 in 2025 (2025-01-21..2025-12-31); HOLDOUT = day1 in 2026 (2026-01-01..2026-11-12)**. Holdout opened once, after DEV verdict is written.
- Disclosure (ASSUMED risk): public knowledge of the 2025 tariff episode (April 2025 sell-off and rebound after the 90-day pause) exists in general background knowledge. DEV 2025 is therefore not "blind"; 2026 is the honest test.

## 1. Event definition (mechanical; code/build_events.py, sha in §9)
- Presidential channels only: source_type in {Speech, Social, Executive Order, White House statement}.
- A "new tariff announcement" = a TiRADE event_id that contains at least one row with role in {first_statement, modification}
  (TiRADE: first mention of a measure / new rate for the same measure), tag in {signal, instrument} (not story/musing/no_rate),
  event_type containing Threatened/Announced/Implemented (not Court event, not "Announced (deal)"), rate_value > 0. Climbdowns excluded.
- Timestamp of the event: (T1) earliest timed row of any role in the same event_id; else (T2) the earliest timed presidential tariff row on the same date
  (needed because e.g. 2.4.2025 EOs are untimed while the Rose Garden speech is timed 16:00); else (T3) untimed -> SECONDARY set only.
  Result: 151 event_ids: T1=91, T2=58, T3=2.
- Session mapping (exchange calendar, Alpaca /v2/calendar incl. early closes): base = last session whose close <= event time; day1 = first session whose close > event time.
  (Intraday event -> base = previous close, day1 = same-day close. After close / weekend -> day1 = next session.) Multiple events with the same day1 collapse to one event-day.
- **PRIMARY set** (timed, T1+T2): 66 unique event-days (DEV 45, HOLDOUT 21). n >= 20 -> not ANECDOTE.
- **PRIMARY_dc5** (for 5-day tests): keep earliest, drop any event-day whose day1 is < 5 sessions after a kept day1 -> 40 event-days (DEV 25 / HO 15).
- SECONDARY (all incl. untimed, T3 mapped to 00:00 of its date): 67 event-days; descriptive only.
- Files frozen: data/EVENTS_PRIMARY_locked.csv, data/EVENTS_PRIMARY_dc5_locked.csv, data/EVENTS_SECONDARY_locked.csv, data/events_rows_all.csv.

## 2. Prices (to be downloaded only after this file is hashed)
- SPY, QQQ: Alpaca daily bars, feed=sip, adjustment=all, asof=- ; official close. Range 2024-12-01..2026-11-20.
- BTC: Alpaca crypto (v1beta3, BTC/USD) 1-hour bars; BTC "close" for a session date = close of the hour bar 15:00-16:00 ET on that date (aligned to the equity close). Fallback if Alpaca crypto fails: Coinbase public BTC-USD 1h candles, same rule (documented if used).
- 1-minute SPY/QQQ (sip, adjustment=all) only for PRIMARY events whose timestamp is inside RTH of day1 (reverse-causality description).
- C1 daily pnl: /workspace/independent_review/results/c1_live_daily.csv ; I2 daily pnl: /workspace/independent_review/results/i2_USATECHIDXUSD_daily.csv (both end 2026-11-10; dates are MT5 server dates, alignment to ET dates ASSUMED).

## 3. Windows and measures (fixed)
- R1 = close(day1)/close(base) - 1. R5 = close(day1 + 4 sessions)/close(base) - 1 (5 sessions after base).
- Reverse causality (daily): Rpre = close(base)/close(base - 1 session) - 1 (the session before the event).
- Reverse causality (intraday, descriptive): for RTH events, pre = prev close -> last 1-min close before event minute; post = event minute -> day1 close.

## 4. Comparison with random days (protocol §4)
- Universe: all sessions s with base in [2025-01-17, 2026-11-12] such that the 5-session window exists; "random day" = a session used as base, same formulas.
- Comparison pool = non-event base sessions (bases of PRIMARY events removed).
- Statistic: mean over events. p-value = two-sided, from 20,000 random same-size samples (without replacement) of the pool: p = share of samples with |mean - pool mean| >= |event mean - pool mean|. Also report percentile of the event mean in the sample distribution, and the median per-event percentile rank vs all pool days.
- Robustness (not gating): circular-shift placebo of the whole event-day pattern (preserves clustering), 20,000 shifts.
- 1-day tests use PRIMARY (66); 5-day tests use PRIMARY_dc5 (40). Full PRIMARY 5d reported descriptively.

## 5. Tests, multiplicity, verdict for the event study
- Primary family (Holm, alpha 0.05): 6 items = {SPY, QQQ, BTC} x {R1, R5}.
- Reverse-causality family (Holm, 3 items): Rpre for SPY, QQQ, BTC.
- Confounders (protocol §5): event-day is CONFOUNDED if a FOMC, CPI or NFP release (data/CONFOUNDERS_locked.csv) falls on day1 or on any date in (base, day1]. Earnings/other news: UNKNOWN (not checked).
- Verdict:
  - EFFECT: at least one primary item Holm p < 0.05, and the same item on the unconfounded subset has raw p < 0.05 with the same sign.
  - CONFOUNDED: Holm-significant on full set but not on the unconfounded subset.
  - NO-GO (no effect): no primary item Holm-significant.
  - If the reverse-causality item for an asset is Holm-significant, the effect for that asset is flagged "reverse causality not excluded".

## 6. Trading rule (search track) - exactly ONE, locked before prices: (b) reversal
- Rule B: on each PRIMARY event-day, if R1 of the asset < 0 (asset fell from base close to day1 close), go LONG at day1 close, exit at close of day1 + 5 sessions. One position per asset at a time (signals while a position is open are skipped). Assets traded separately: US500 CFD (SPY proxy), US100/USTEC CFD (QQQ proxy), BTCUSD CFD (BTC 16:00 ET proxy). Rule (a) "short after announcement" is NOT tested.
- Costs (frozen project model, research_new_component COST_PRESCREEN_20261110 / t210): US500 round trip 2.31 bp; USTEC 0.54 bp; long index swap 8.6%/yr x calendar days held / 365. BTC: conservative 10 bp round trip + long swap 4.75%/yr x calendar days / 365. Stress: costs x2 reported.
- K = 3 trials (3 assets) in this round; Holm over 3.
- DEV gate (entries in 2025): n_trades >= 20 (else rule = ANECDOTE, no PASS possible); mean net/trade > 0; one-sided t-test Holm-adjusted p < 0.05; DSR(K=3) >= 0.95 on per-trade net returns; and the rule mean exceeds the 95th percentile of a baseline = 20,000 random same-size samples of "long 5 sessions after ANY down day" from non-event DEV sessions (net of same costs).
- HOLDOUT gate (entries in 2026, opened once): only for assets passing DEV. n >= 10, mean net > 0, t > 1.0, baseline percentile >= 80.
- Rule verdict: PASS only if DEV and HOLDOUT gates pass; otherwise NO-GO (or ANECDOTE if n too small). Holdout numbers for non-passing assets are still reported (descriptive).

## 7. C1/I2 track (description only; no filter, no tuning)
- For each PRIMARY event: C1 and I2 pnl summed over calendar dates in (base, day1] (1d) and (base, day1+4 sessions] (5d); mean, share negative, percentile vs the same windows for all non-event base sessions. Reported per DEV/HO. Missing series dates -> UNKNOWN.

## 8. Not allowed after this point
No change of event filter, timestamp hierarchy, windows, assets, rule, threshold (R1 < 0), hold (5), costs or gates after prices are seen.

## 9. Frozen inputs (sha256)
- data/tirade-v1.10-rate-statements.csv 73153ba2abb489ebbf872298826ace0eb7dbb2469a5298b1f5a18b9466c777f1
- code/build_events.py c6b813af6b6233b6fdcb64eef171f723fe09f2b7970e586e70be01de3d465250
- data/calendar_2025_2026.json 86667b918f20f2ac925bdc9567890ad3ad4a6ab4dbc5addde64e18346002adcd
- data/EVENTS_PRIMARY_locked.csv b3bb0eb08a13f4b136f18975c23cf6ad5a8429faf60de0cb9735b778c633e814
- data/EVENTS_PRIMARY_dc5_locked.csv 58c9cc4075d6538fef8efe5535c0729890691526e14aab390041197182b2ee51
- data/EVENTS_SECONDARY_locked.csv c9f8a3f8d74589874eccc45c8ce4c18a80654ea4162d0517def51ce9a2b1fe30
- data/events_rows_all.csv 7d9ee82077771f812925a585a8f341aed9e76df4deb4da038ba0ce5ac6fa3588
- data/CONFOUNDERS_locked.csv 989dddba1ff6ca458ddb425d094fb3382c67be42b35d5bfc1a51faadd9a9b55f
