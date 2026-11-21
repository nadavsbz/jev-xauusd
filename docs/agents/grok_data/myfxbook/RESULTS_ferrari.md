# RESULTS — FERRARI2009 / IC Markets MT4 (Myfxbook 3534905)

**Author:** Grok (המאסטרו).  
**Written:** 2026-11-11 22:14 Asia/Jerusalem (IST, UTC+2).  
**Status:** Fingerprint + frozen cost pre-screen. **FAIL / DROP. No PREREG, no holdout backtest, no MQL5 spec.**

Cost screen: `COST_PRESCREEN_20261111_2214_ferrari.md`.  
Tape: `myfxbook/ferrari2009_history.csv` (2,709 Buy/Sell rows, no deposit rows in this export).  
Machine tables: `results_ferrari/`.

Every quantitative claim below is tagged **VERIFIED** (computed from the tape or from a page opened this session), **OBSERVED** (read from a published page or from the shortlist and not re-measured), **ASSUMED**, or **UNKNOWN**.

## 1. Fingerprint (VERIFIED on the tape unless noted)

**Book as advertised (OBSERVED, Myfxbook shortlist 2026-11-11):** real verified IC Markets MT4 EUR account, from 2019, +7,265.73% cumulative, 5.00%/month average, max DD 20.03%, PF 1.80, ~70% win, average hold 1h37m.

**Recomputed on the 2,709 closed trades, 2019-08-19 00:01 .. 2026-11-11 02:37 broker time:**

| | All | Train (open < 2024-01-01) | Holdout (2024–2026) |
|---|---:|---:|---:|
| Trades | 2,709 | 1,138 | 1,571 |
| Win rate | 70.43% | 75.75% | 66.58% |
| Profit factor | 1.804 | 2.287 | 1.546 |
| Sum of Profit (account ccy, OBSERVED as EUR on the shortlist) | 2,924.22 | 1,631.51 | 1,292.71 |
| Mean Profit | 1.08 | 1.43 | 0.82 |
| Mean win / mean loss | +3.44 / −4.56 | +3.36 / −4.64 | +3.50 / −4.51 |
| Mean pips (IC-net) | 4.48 | 3.80 | 4.97 |

Mean hold is right-tailed: **mean 96 minutes** (matches the advertised 1h37m), **median 48 minutes** (8.3% of trades last 2–3h, 3.2% 3–4h, 4.0% longer, 32 trades >12h). About 35.5% of exits match the recorded TP to 0.6 pip; only 2.2% match the recorded SL. Weekdays only (Mon 735 … Fri 295; no Saturday/Sunday). Pip reconstruction from Open/Close matches the Pips column (median abs error ~0, none above 0.15 pip) — the file is clean (VERIFIED).

### Session

This is a **night / Asian-session scalper**, not a London book.

- 91.7% of entries in broker hours 22:00–07:59; 90.4% in 22:00–04:59; **48.1% in 00:00–04:59**; mode hour is **23:00** (816) then **00:00** (718).
- 56.6% of entries in hours 23–00. **26.2% (710 trades)** sit in 23:50–00:10. Of GBPUSD’s 154 trades, **95 (62%)** are in that ten-minute window, including 65 in 00:00–00:05.
- 24.6% of trades are overnight (close calendar date after open, or a late-evening hold into the early morning).

**Broker clock (OBSERVED on Dukascopy M15 mid for the majors we already have):** best match is **GMT+2 with US DST**, the same convention already used for Gold Reaper on IC Trading. In-bar hit rates: EURUSD 87.8%, USDCAD 86.4%, GBPUSD 75.3%. Europe/Athens is close (84.4 / 83.9 / 70.8). Fixed GMT+2, fixed GMT+3 and UTC are worse. M15 is a coarse bar, so this is not a tick-level verification. If that clock is aligned with the 17:00 New York roll, hour 00:00 in winter (hour 23:00 in summer) is the spread-spike window, and a large fraction of this book trades into it.

### Per symbol

Counts, IC-net pips, win rate, median TP/SL (as recorded), median hold, and train vs holdout:

| Symbol | n | WR | PF | Mean pips | Med TP | Med SL | Med hold | Night / roll share | Buy share | Train n / mean pips / WR | Hold n / mean pips / WR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| GBPCAD | 740 | 65.5% | 1.54 | 1.84 | 8.4 | −250 | 43m | 78% / 33% | 56% | 165 / 2.93 / 75% | 575 / 1.52 / 63% |
| EURAUD | 452 | 75.4% | 2.24 | 3.05 | 7.5 | −44 | 38m | 99% / 82% | 77% | 352 / 3.25 / 77% | 100 / 2.37 / 69% |
| EURSGD | 345 | 70.1% | 1.68 | 1.97 | 6.6 | −250 | 48m | 91% / 27% | 34% | 59 / 1.51 / 73% | 286 / 2.06 / 70% |
| EURCAD | 189 | 69.3% | 1.53 | 2.25 | 9.0 | −250 | 49m | 89% / 40% | 69% | 60 / 1.61 / 63% | 129 / 2.55 / 72% |
| GBPUSD | 154 | 79.9% | 3.85 | 3.15 | 4.1 | −20 | 48m | 100% / 89% | 64% | 89 / 3.47 / 79% | 65 / 2.70 / 82% |
| CHFJPY | 133 | 76.7% | 2.66 | 3.88 | 6.0 | −38 | 65m | 100% / 80% | 3% (almost all shorts) | 91 / 3.46 / 82% | 42 / 4.79 / 64% |
| XAUUSD | 128 | 68.0% | 2.79 | 52.1 pts | 200 | −170 | **7m** | 98% / 36% | 56% | 28 / 55.6 / 82% | 100 / 51.2 / 64% |
| EURGBP | 125 | 73.6% | 1.81 | 1.18 | 2.0 | −20 | 68m | 100% / 98% | 88% | 72 / 1.24 / 81% | 53 / 1.09 / 64% |
| USDCAD | 125 | 66.4% | 1.12 | 0.61 | 3.7 | −20 | 63m | 100% / 90% | 67% | 77 / 0.39 / 66% | 48 / 0.96 / 67% |
| GBPAUD | 95 | 66.3% | **0.81** | 0.27 | 5.3 | −250 | 63m | 100% / 69% | 61% | 9 / 1.03 / 67% | 86 / 0.18 / 66% |
| EURUSD | 90 | 77.8% | 2.29 | 1.95 | 4.3 | −30 | 55m | 99% / 76% | 81% | 57 / 0.90 / 79% | 33 / 3.77 / 76% |
| EURCHF | 63 | 63.5% | 1.03 | 1.32 | 5.9 | −16 | 129m | 95% / 38% | **100% long** | 50 / 1.87 / 68% | 13 / **−0.78** / 46% |
| AUDCAD | 36 | 58.3% | 1.04 | 0.99 | 3.0 | −250 | 71m | 100% / 100% | 28% | 0 / — | 36 / 0.99 / 58% |
| USDCHF | 18 | 83.3% | 5.84 | 3.54 | 9.4 | −20 | 56m | 100% / 89% | **0% (all shorts)** | 15 / 3.47 / 87% | 3 / 3.87 / 67% |
| CADCHF | 15 | 80.0% | 0.59 | 0.28 | 4.9 | −22 | 239m | 100% / 100% | 100% | 14 / 0.27 / 79% | 1 |
| AUDUSD | 1 | — | — | 4.00 | 4.0 | −50 | 9m | — | — | 0 | 1 |

Gold is a **separate short-hold sleeve** (median 7 minutes, TP often 200–1,286 points, almost no exact TP hits). The FX book is a tight-TP night scalper (typical TP 2–9 pips).

### Structure change over time (decay, mix, stops)

- **Win rate and PF decay:** 2019–2023 WR 75.7% / PF 2.29 → 2024 68.1% / 1.44, 2025 67.7% / 1.65, 2026 64.7% / 1.52 (through 11 Nov). Still profitable on this IC tape, weaker.
- **Universe shift.** EURAUD dominates the train (352 of 1,138). Holdout is 54.8% **GBPCAD + EURSGD** (575+286). EURSGD appears only from 2022 and explodes in 2025–2026. AUDCAD is holdout-only. GBPAUD is almost holdout-only and is net negative (PF 0.81).
- **Hard SL regime change.** Until 2023, typical stops were tight and pair-specific (−15 to −44, GBPUSD −20, EURAUD −44, CHFJPY −38). Share of SL ≤ −200 pips: 0% in 2019–2022, 0.4% in 2023, **20.7% in 2024, 72.7% in 2025, 86.1% in 2026**. The late book uses a ~250-pip “disaster stop” on the crosses and often on the majors too. That is a different risk shape, not a fixed-SL mean-reversion EA frozen since 2019.
- Yearly mean lots rise from 0.017 (2019) to 0.20 (2022) then settle near 0.09 (2025–2026), tracking a growing then withdrawn account rather than a crash-driven martingale. Median implied equity from Gain% is ~122 in 2019 and ~1,709 in 2026. Official max DD 20.03% is left as OBSERVED from Myfxbook; a naive close-to-close walk on Profit is contaminated by unlabelled withdrawals (seven large implied-equity jumps) and is **not** used as a DD figure.

### Averaging / martingale

**Equal-lot scale-in / basket close, not a classic lot-multiplier martingale.**

- 15.7% of trades overlap another same-symbol, same-side trade. When stacked, mean stack 2.94, **max 10** (GBPCAD). 173 groups share an exact close timestamp (433 trades); basket sizes 2 (127 groups), 3 (25), up to 7.
- GBPCAD is the most stacked (26.8% overlapping). Gold does not stack. “Added after a worse price” on the raw open is rare in the flag as coded (the later legs often close as a basket at one price, which is still averaging).
- Median lot multiplier after a loss is **1.0** (same after a win). Same-symbol lot increases after a loss: only 11.2%. Lots-per-1k implied equity has a median of 0.075, not a blow-up after losses.

This is closer to a night scalper that **adds equal size and exits the basket** than to a geometric martingale. Combined with the 2025–2026 move to a −250 pip stop, it is still a left-tail structure: many +6 to +9 pip wins, occasional large losers, and more of the recent book has no tight hard stop.

### Candidate rule (descriptive only — not fitted, not tested)

OBSERVED from the tape, not from a price-level match (Dukascopy datafeed timed out from this box; only majors M15 mid were already on disk):

- Trade a basket of FX crosses and majors, plus a smaller gold sleeve, almost only in the quiet 22:00–05:00 broker window, often around midnight.
- Tight take-profit (typically 4–9 pips on the crosses, ~4 on GBPUSD, ~2 on EURGBP); flatten on TP, on a time cap around 1–2 hours, or as a same-direction basket.
- Early years: tight hard SL. Later years: wide 250-pip SL and more stacking on GBPCAD / EURSGD / EURCAD.
- Direction is pair-specific, not a single always-fade or always-breakout rule (EURAUD 77% longs, EURSGD 66% shorts, CHFJPY 97% shorts, EURCHF 100% longs, USDCHF 100% shorts).
- A price-level rule (band / MA / range fade in the Asian window) was **not** estimated, because no symbol survived the cost screen and therefore no pre-registration was opened.

## 2. Cost-screen verdict

Full method and table: `COST_PRESCREEN_20261111_2214_ferrari.md`.

**Primary case (the decision):** RoboForex Prime commission 0.2 bp RT, plus ForexBenchmark IC Markets (Raw) 30-day **night** average spread (22:00–04:00) for night entries, day average otherwise. Train-only IC-net mean as conservative gross. User cap 0.02%/side.

**Every symbol is a DROP.** Closest FX is GBPUSD (conservative ratio 0.49, generous 0.35, both above 1/3). XAUUSD conservative ratio 0.336, just over the line, with only 28 train trades and uncertain gold pip units on ForexBenchmark. EURSGD is not on the RF Pro/ECN/Prime specification table (VERIFIED, same consultation 2026-11-11). CHFJPY also fails the 0.02%/side cap at the night spread. EURCHF’s holdout mean pips is already negative. AUDCAD/AUDUSD have no train trades, so they cannot pass.

Official RF 24h averages would formally pass GBPUSD (and tiny USDCHF, plus gold). That case is **not** used: 100% of GBPUSD and 95%+ of the other FX names trade at night, and 62% of GBPUSD is inside the ten-minute midnight window. The 1-hour rollover mean (GBPCAD 18.6 pips, GBPUSD 7.7) is reported only as a stress — it is too skewed to assign to every 00:00 fill.

## 3. What was not done, and why

- No `PREREG_*_ferrari.md`, no 2018–2023 / 2024–2026 backtest, no correlation with C1+I2, no MQL5 spec. The frozen cost rule forbids a full test of a name that fails the screen, and no name passed the primary case.
- No mid-to-mid fill match on GBPCAD / EURAUD / EURSGD: Dukascopy `datafeed.dukascopy.com` timed out from this box (VERIFIED this session). Timezone was scored only on already-local M15 majors.
- Official Myfxbook equity DD was not recomputed; withdrawals are not in the export.

## 4. What not to do with this result

- Do not “rescue” GBPUSD or gold by switching to the official 24h average, by using holdout pips, or by treating the generous ratio as the official test.
- Do not implement EURSGD at RoboForex; it is not on the official list, and it is 18% of the live holdout tape.
- Do not treat the 2019–2023 tight-SL version and the 2025–2026 −250-SL / heavy-GBPCAD-EURSGD version as one frozen EA.
- Do not start a tester job, a live or demo account, or a copy of this signal.

Artifacts: `results_ferrari/trades_clean.csv`, `by_symbol.csv`, `by_year.csv`, `by_year_symbol.csv`, `entry_hour_broker.csv`, `stacking_by_symbol.csv`, `sl_tp_dist.csv`, `cost_screen_fb_icraw.csv`, `timezone_m15_scores.csv`, `fxbm_ic_raw_30d.json`, `summary.json`.
