# RESULTS t368: US tariff-announcement event study (TiRADE v1.10)
Run 23.11.2026 ~21:12-21:14 Asia/Jerusalem, after PREREG_t368.md (sha256 59a5914f7f538ecd17051c404d44e3294f1fe392b2c7c737da180324576e70e8, mtime 21:09:21 IST; first price file SPY_daily.csv mtime 21:09:39 IST, i.e. after it).
Code: code/build_events.py (no prices), code/download_prices.py, code/analyze_t368.py. Full numbers: results_t368.json. Research only; no trading recommendation; decisions are Nadav's.

## Verdict
- **Event study: NO-GO (no effect).** No primary item is close to significance (all Holm p = 1.00; smallest raw p = 0.20). n = 66 event-days (1d) / 40 declustered (5d), so it is not an ANECDOTE.
- **Rule B (long after a drop on announcement day, 5 sessions): NO-GO.** DEV n is 12-17 trades per asset (< 20 -> ANECDOTE by the gate), DEV Holm p = 0.62, DSR(K=3) <= 0.49. Holdout 2026 is negative net for all three assets.
- **Reverse causality:** not significant (Holm p >= 0.55); prior-day returns on event days were slightly negative (SPY pct 8.3 vs random samples) - descriptive.
- Confounders: 6/66 event-days have CPI/NFP/FOMC in (base, day1]; removing them changes nothing (all unconfounded raw p >= 0.18).

## 1. Events (VERIFIED from TiRADE CSV, sha matches the published sha)
- 151 qualifying event_ids -> 66 timed event-days (DEV 2025: 45, HOLDOUT 2026: 21); dc5 = 40 (25/15); secondary incl. 2 untimed = 67.
- Data forced deviation (documented in PREREG before prices): TiRADE starts 2025-01-21, so DEV=2025 and HOLDOUT=2026 instead of "through 2024 / 2025+".

## 2. Event study vs random non-event days (pool n = 392 sessions; 20,000 same-size samples; circular-shift placebo as robustness)
| item | n | event mean | pool mean | pct vs samples | p two-sided | Holm | circ p | unconfounded mean (n) / p | 2025 / 2026 mean |
|---|---|---|---|---|---|---|---|---|---|
| SPY 1d | 66 | +0.146% | +0.047% | 83.1 | 0.346 | 1.00 | 0.44 | +0.181% (60) / 0.225 | +0.153 / +0.132 |
| SPY 5d | 40 | +0.050% | +0.201% | 31.0 | 0.622 | 1.00 | 0.39 | +0.215% (35) / 0.966 | +0.039 / +0.067 |
| QQQ 1d | 66 | +0.232% | +0.043% | 90.1 | 0.202 | 1.00 | 0.29 | +0.255% (60) / 0.181 | +0.260 / +0.173 |
| QQQ 5d | 40 | -0.068% | +0.227% | 24.6 | 0.498 | 1.00 | 0.31 | +0.051% (35) / 0.709 | +0.001 / -0.182 |
| BTC 1d | 66 | +0.069% | -0.076% | 69.2 | 0.621 | 1.00 | 0.67 | +0.154% (60) / 0.453 | +0.179 / -0.168 |
| BTC 5d | 40 | -1.174% | -0.392% | 18.1 | 0.363 | 1.00 | 0.26 | -0.783% (35) / 0.668 | -1.091 / -1.313 |
BTC = BTC/USD price at 16:00 ET (Alpaca crypto 1h bar 15:00-16:00 ET), aligned to equity sessions.
Descriptive (OBSERVED, not a test): the mean 1d is lifted by 9.4.2025 (90-day pause post at 13:18 ET, coded by TiRADE as a new 125% China rate; QQQ +12.0%). The 2.4.2025 Rose Garden event gave QQQ -5.35% / SPY -4.93% / BTC -5.72% on 3.4.2025. Without 9.4.2025 the QQQ 1d mean is about +0.05%, i.e. the pool level.

## 3. Reverse causality
- Daily (session before the event; Holm over 3): SPY -0.074% vs pool +0.087% (pct 8.3, p 0.18, Holm 0.55); QQQ -0.068% vs +0.101% (pct 14.7, p 0.29, Holm 0.59); BTC -0.209% vs -0.010% (pct 25.2, p 0.50, Holm 0.59). Not significant.
- Intraday (21 RTH-timed events, descriptive): SPY prev close->event minute mean +0.16% (47.6% negative), event->close +0.32% (57.1% negative); QQQ pre +0.32% (33% neg), post +0.32% (57% neg). Of the 12 SPY events that fell after the timestamp, 8 were already down before it.

## 4. Rule B (long at day1 close if day1 return < 0, exit after 5 sessions; non-overlapping; net of frozen RF costs incl. swap)
| asset | period | n | mean gross | mean net | net x2 cost | win | t | p one | Holm | DSR K3 | baseline "after any down day" pct | gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| US500 (SPY) | DEV 2025 | 14 | +0.24% | +0.045% | -0.15% | 50% | 0.10 | 0.46 | 0.62 | 0.22 | 26.4 | FAIL (n<20) |
| US100 (QQQ) | DEV 2025 | 12 | +0.61% | +0.43% | +0.25% | 58% | 0.69 | 0.25 | 0.62 | 0.42 | 50.1 | FAIL (n<20) |
| BTCUSD | DEV 2025 | 17 | +1.42% | +1.23% | +1.03% | 47% | 0.84 | 0.21 | 0.62 | 0.49 | 93.4 | FAIL (n<20) |
| US500 | HOLDOUT 2026 | 9 | -0.24% | -0.44% | -0.64% | 33% | -0.89 | - | - | - | 19.8 | descriptive |
| US100 | HOLDOUT 2026 | 8 | -0.65% | -0.84% | -1.02% | 38% | -1.22 | - | - | - | 18.0 | descriptive |
| BTCUSD | HOLDOUT 2026 | 8 | -0.54% | -0.73% | -0.93% | 38% | -0.18 | - | - | - | 50.7 | descriptive |
Costs: US500 2.31 bp RT, USTEC 0.54 bp RT, index long swap 8.6%/yr; BTC 10 bp RT + 4.75%/yr. K = 3 in this round (company-wide cumulative K: UNKNOWN to me; DSR at K=100 <= 0.04). Worst trade: BTC holdout -16.7%, BTC DEV -10.8%.
Holdout opened once, after the DEV numbers were computed in the same run (all DEV gates failed, so holdout rows are descriptive only).

## 5. C1 / I2 on event days (description only; no filter, no tuning; dates are MT5 server dates, alignment to ET sessions ASSUMED)
| series | window | n | event mean | pool mean | share < 0 | worst | pct vs random samples | 2025 / 2026 mean |
|---|---|---|---|---|---|---|---|---|
| C1 | 1d | 66 | +0.089% | +0.035% | 54.5% | -1.94% | 74.2 | +0.067 / +0.136 |
| C1 | 5d | 66 | +0.849% | +0.119% | 56.1% | -2.06% | 99.8 | +0.829 / +0.893 |
| I2 | 1d | 66 | +0.055% | +0.050% | 30.3% (51.5% flat) | -2.83% | 55.2 | +0.073 / +0.015 |
| I2 | 5d | 66 | +0.470% | +0.211% | 48.5% | -1.97% | 96.7 | +0.615 / +0.158 |
5d windows overlap between clustered events (not declustered here), so the 5d percentiles overstate independence; median C1 5d is negative (56% < 0) while the mean is positive -> a few large windows drive it (OBSERVED). No harm seen on tariff days; no claim of an edge. C1/I2 series end 2026-11-10 (no UNKNOWN windows for the 66 events).

## 6. Tags
- VERIFIED: TiRADE file + sha, event list, FOMC dates (federalreserve.gov), Alpaca SIP/crypto prices, all computed numbers in results_t368.json.
- OBSERVED: CPI/NFP dates from the project calendar (BLS via Wayback) and 2 CPI dates for Oct/Nov 2026 from a BLS-page search snippet (bls.gov returns 403 to the box).
- ASSUMED: T2 timestamp rule (untimed EO takes the earliest timed tariff statement of that day); C1/I2 server-date alignment; RF cost model = frozen project coefficients; SPY/QQQ/BTC 16:00 ET as proxies for RF US500/USTEC/BTCUSD.
- UNKNOWN: earnings/other news confounders (not checked); company-wide cumulative trial count.
