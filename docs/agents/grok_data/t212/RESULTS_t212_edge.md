# RESULTS t212 — EdgeTrader decode gate

Written: 2026-11-12 09:17 Asia/Jerusalem (IST, UTC+2).

**Decode-gate verdict: PASS.** Timing beats same-side random entry at **p = 0.00050** (0 of 2,000 permutations ≥ the real mean; p = 1/2001), and recorded EUR profit **survives dropping the 10 best close-days** (€1,220.84 remains, PF 1.415).

**Entry-rule inference: NOT recovered.** The four templates frozen in the PREREG all fail g1 (holdout Sharpe). Closest holdout Sharpe is `ASIA_FADE` at **+0.33** (train −3.08, pre-sample −3.95). No MQL5. This is not a deployable book. The vendor history does show real timing and direction skill on 2024-08–2026-10; a naive session + prior-M15 follow (or fade) with a 30-minute / 1.5×ATR stop does not reproduce it after RoboForex costs.

No accounts, terminals, testers, or `accounts.json` were touched. `/tmp/h.py` was deleted as asked, before any computed P&L, and was not recreated. Unique t212 names; t199c–t211 were not overwritten.

---

## 0. Method and hashes

PREREG `PREREG_20261112_0908_t212_edge.md` was written and hashed **before** any mid-price, random-path, or inferred-rule P&L. The vendor TSV’s own Profit (EUR) was profiled first (given data, not computed here).

| File | SHA-256 |
|---|---|
| `PREREG_20261112_0908_t212_edge.md` | `51d600f23659bfa805a380577f7b1c392918c781c88ce40c61076106cf9fb29f` |
| `code/backtest_t212_edge.py` | `96d2c2535b4ba5f9ea6be35ab1425baa6444298bda7906dcc1f63bee494aafe7` |
| `code/backtest_t212_infer.py` | `6a6c836e85f1a2dc82e84649e1c26adcee229b0b3f195458e5a005afa1beef45` |
| `results_t212_edge/summary.json` | `fba034249d5c83a376dbb459146e9fa0aba03ecfb969b2621639c52c8ab821fb` |
| `results_t212_edge/infer_summary.json` | `62de626c1cdc6e483604a1aa1f39e19fad2bb5a8a4e4beb630f1b03438ab6da4` |

Pass rule (frozen): timing one-sided p < 0.05 on equal-weight mean net bp, **and** remaining recorded EUR profit > 0 with PF ≥ 1.0 after dropping the 10 best close-days. Inference runs only if both pass, on the three pre-registered templates, train 2018–2023 / holdout 2024 through last mid bar, RF costs, double-touch = loss, g1–g5.

Costs (t208, dollars **VERIFIED**): RoboForex XAU **$0.12/side** ($0.24 RT); swap **−$0.60/oz/night long**, **+$0.19/oz/night short**, charged at each **21:00 UTC** in [entry, exit) including a synthetic Saturday and Sunday 21:00 if the hold spans the gold weekend; **no Wednesday triple** (schedule **ASSUMED**, same as t208). Broker stamps **≈ America/New_York + 7 hours** (**ASSUMED**, as the brief). Mid = Dukascopy M1 bid∩ask close, 2022-01-02 23:00 UTC → 2026-10-26 18:48 UTC (inner join; **VERIFIED**).

Official real bp uses **TSV fill prices** minus those RF costs (so sub-minute scalps keep their realized move). Random paths use M1 mid at a uniform entry in the **same ISO week, broker time**, same side, duration and lots, exit within 2 minutes of entry+duration, N = 2,000, seed **212212**. p = (1 + #{perm ≥ real}) / (N+1). EURUSD excluded. Trades with open or close after mid coverage excluded (14 trades, €84.83).

A first implementation compared the 2-minute window in nanoseconds against a `datetime64[us]` index (an accidental ~33-hour window). That run was **discarded**. The official figures are the ns-corrected rerun, same seeds, same PREREG.

---

## 1. Profile (recorded EUR, 852 closed trades)

Source: `/home/box/Downloads/edge_hist_all.tsv` and `edge_info.txt`. Figures below match the vendor page on profit, peak, DD, and PF (**OBSERVED**).

- 852 trades: **851 XAUUSD**, 1 EURUSD. Opens 2024-08-30 20:01 → 2026-11-11 16:37 broker; deposit €1,410 on 08.29.2024 15:08.
- Profit **€2,637.17**, final balance **€4,047.17**, peak **€4,364.60** at 2026-09-28 05:55, close-equity max DD **−15.325%**. PF **1.8895**, WR **79.1%** (674 / 178 / 0 flats). Vendor gain 187%, monthly 4.01%, Sharpe 0.38, Z-score −13.71 (99.99%), commissions −€87.17, interest −€20.42 — the TSV profits already sum to the published Profit line (likely already net).
- Long 500, WR 80.2%, **€1,994.86**. Short 352, WR 77.6%, **€642.31**.
- The EURUSD row is 2025-09-29 07:00–07:01 Sell 0.01, 0 pips, **−€0.02**. Profile only; excluded from the gold random test.

### Monthly returns (close-profit / start-of-month balance)

28 months, geometric **3.838%/mo** (vs claimed 4.01%); arithmetic mean 3.99%. Seven negative months. Annualized (1+gmean)^12−1 ≈ **57.1%**. Best: 2026-01 **+18.84%**. Worst: 2026-10 **−6.67%** (−€291.30). 2025-02 −5.64%; 2025-04 +11.09%; 2025-06 +11.12%; 2025-12 +13.34%. 2024-08 −0.53% (1 trade). 2026-11 −0.64% (7 trades, incomplete).

### Duration (close−open stamps; text duration for sub-minute)

Gold n=851: mean **177.6 min** (matches claimed 2h 57m), median **24 min**, p25 6, p75 81, max 6,412 min (~4.5d). ≤1m 10.3%; ≤5m 24.3%; ≤30m 54.7%; ≤3h 85.8%; >1d 3.2%. Profit is front-loaded on scalps: ≤1m n=88, **€837.03**, WR 85%; 1–5m €690.33; 5–15m only €106.69; 3–24h **−€10.53**, WR 63%. Use stamp duration, not the rounded text, for the random test.

### Hour and weekday of entry (broker time, NY+7)

No Saturday/Sunday entries. Peaks at broker 15–18 (89, 93, 100, 60 trades) — NY morning (15:00 broker ≈ 08:00 NY; 16:30 broker = NY cash 09:30). Profit: hour 15 **€607.88** WR 85%; hour 03 **€470.59** WR 92%; 02 €293.73; 17 €291.70; 18 €246.28. Weak: 08 **−€132.46** WR 57%; 05 −€53.68; 20 −€44.34; 22 −€29.91. Weekdays: Wed €817.92, Tue €653.27, Fri €602.42, Mon €325.26, Thu €238.30. Sessions: Asia 00–08 n=224, **€1,018.92**, WR 81%; Europe 08–16 n=260, €789.75, WR 80%; NY overlap 16–23 n=361, €819.00, WR 77%.

### Lot sizing: not martingale; stepped with the account

Only **0.01 / 0.02 / 0.03**. 0.01 n=570 from the start through 2026-02-27, balance mean ~€1,827; first 0.02 at **2025-12-18 18:10**; first 0.03 at **2026-04-29 12:50**, then through the end. corr(lots, bal_at_open) = **0.918**. After a losing close, the next open is the **same** lot 177 times and **larger once** (the scheduled 0.01→0.02 step, not a doubling rule); never smaller.

### Grid / averaging-in: strong cluster signature

- Same-minute same-side clusters: **219 events, 637 trades** (75% of the book), max **7** (e.g. 2024-09-12 15:41 Buy ×7; 2026-09-28 03:31 Sell ×6, 0.18 lots, **€186.19** — that whole top close-day).
- Entered while ≥1 same-side trade already open: **314 (36.9%)**; ≥2: 227. Max concurrent same-side at entry **14**.
- Same-close-timestamp baskets: **170 events, 426 trades**, max 7.

This is averaging-in / split-lot stacking at one timestamp, **not** classic martingale. The vendor Z-score −13.71 is consistent with dependence.

### Concentration

- **Top-10 trades:** €755.37, **28.64%** of profit. Best: 2026-06-24 Sell 0.03, **€126.34**, 36m (matches “Jun 24”); 2026-09-28 Sell 0.03 €125.66; 2026-08-05 Buy 0.03 €125.30. Worst: 2026-10-22 Sell 0.03 **−€73.13**, 42m (matches “Oct 22”).
- **Top-10 close-days:** €1,416.33, **53.71%** of profit (2026-06-24 €205.82, 2026-09-28 €186.19, 2025-12-18 €160.55, 2026-08-05 €146.56, 2026-01-12 €141.84, 2024-10-29 €140.60, 2026-01-27 €114.41, 2026-10-30 €110.96, 2026-03-03 €106.52, 2025-12-22 €102.88). 169 up / 54 down / 223 days.
- **After dropping those 10 close-days:** **€1,220.84** remains (46.29%), 775 trades, WR 77.4%, **PF 1.415**. Under the frozen bar (remaining profit > 0 and PF ≥ 1) this **survives**. More than half of profit is still in 10 days; the remainder is just not zero.

---

## 2. Random-timing test

Universe: **837** gold trades with both timestamps inside M1 mid coverage. Excluded: 1 EURUSD, **14** gold trades after 2026-10-26 18:48 UTC (opens 2026-10-30 through 2026-11-11, €84.83). Pool dropped: 0. Valid entry pools were all ≥ 10.

| Test | n | Real mean bp | Perm mean | Excess | p | Percentile |
|---|---:|---:|---:|---:|---:|---:|
| **Official timing** (fills + RF cost vs random same-side same-week) | 837 | **5.830** | 2.067 | **+3.763** | **0.00050** | 100th (0 of 2,000 ≥ real; perm sd 0.80, q05 0.80, q95 3.38, max 4.54) |
| Sensitivity, duration ≥ 2 min | 750 | 5.176 | 2.366 | +2.810 | 0.00200 | 99.85th |
| Cluster robustness (shared U(0,1) inside each same-minute same-side group) | 426 groups, 837 trades | 5.830 | 2.090 | +3.740 | 0.00150 | 99.9th |
| **Random-side control** (M1 mid at **real** times, fair coin on side) | 834 | **4.809** | −0.776 | **+5.585** | **0.00050** | 100th |

Official timing **passes p < 0.05**. So do the sensitivity and the cluster robustness (neither can change the official definition; both agree).

Random same-side paths are themselves **+2.07 bp** after RF costs — gold’s 2024–2026 drift plus the book’s long bias (500/352) is a positive backdrop, not the whole story. The **+3.76 bp/trade excess** is the timing gap. Random-side at the actual timestamps is **−0.78 bp** (costs eat an unskilled coin-flip); their real mid+RF mean is **+4.81 bp**, so **direction at those times is also skilled**.

Fills vs mid, 834 trades with a mid at both ends: fill mean 5.757 bp, mid 4.809, difference **+0.95 bp**, corr **0.880**. They capture some intra-bar move that M1 mid misses. Three in-coverage trades have no mid within 2 minutes, all at **2025-10-30 21:50 UTC** (gold daily-close gap); they stay in the official timing test via fills (35.8, 22.0, 20.8 bp). Nights: 783 zero, 49 one, 15 three (weekend span), 3 four, 1 five; RF swap on the fill path totals about $27 — small next to the cash $0.24/trade.

---

## 3. Verdict

**PASS** on the decode gate: timing p = 0.00050 < 0.05, **and** drop-top-10-days leaves €1,220.84 at PF 1.415.

This is a skill test of the vendor book, **not** a promotion of EdgeTrader and **not** a copy of their engine. The program has already failed to reproduce gold-breakout EAs in this family on 2018–2023 (t206 note). The gate says their **entries are not interchangeable with a random time in the same week**, and the edge is **not only the ten best days**.

---

## 4. Inference (run because the gate passed)

Templates were frozen in the PREREG before this P&L, taken from the book’s session shape and a prior-M15 sign, **not** from a post-P&L search. **Honest caveat:** the vendor history starts 2024-08-29 and sits **entirely inside the frozen holdout**. The 15:00–18:00 and 02:00–04:00 broker windows were read off that book, so holdout is **not** a clean out-of-sample for the session choice. Formal train **2018–2023** is the unseen window for that shape. M15 bid/ask mid 2015-01-01–2026-10-26 (t208 path); ATR = SMA(TR, 14) shifted so bar t uses ATR through t−1; entry at the first in-window M15 **open** of the broker-day; time stop 2 M15 bars (**30 min**, the PREREG “~30 min”); SL 1.5×ATR; no TP; double-touch does not arise without a TP (SL in-bar exits at SL, gap-through at the open). Grid: same NY follow entry, adds at 0.5 and 1.0 ATR adverse, max 3 equal legs, flatten together; no add in a bar that also hits SL. Daily sums identity-exact (0 or machine epsilon). Sharpe is calendar × √365.25 via the allowed `gates` / `metrics_pack`.

| Spec | n (train / HO) | Train Sharpe | Holdout Sharpe | Pre 2015–17 Sh | g1 | g2 corr | g3 book lift | g4 | g5 crash | Pass |
|---|---:|---:|---:|---:|---|---|---|---|---|---|
| `NY_FOLLOW` | 1548 / 727 | **−1.50** | **−1.31** | −1.97 | fail | pass (−0.01) | fail (1.518→0.414) | fail | **pass** (mean +3.0 bp, nonloss 54%) | **NO** |
| `ASIA_FOLLOW` | 1544 / 727 | **−3.40** | **−2.14** | −3.61 | fail | pass (+0.01) | fail | fail | **pass** (mean +0.4 bp, nonloss 50%) | **NO** |
| `ASIA_FADE` | 1544 / 727 | **−3.08** | **+0.33** | −3.95 | fail | pass (−0.01) | fail (1.518→1.178) | fail | **pass** (mean +0.1 bp, nonloss 65%) | **NO** |
| `NY_GRID3` | 2871 / 1281 legs | **+0.32** | **−0.03** | −0.88 | fail | pass (−0.01) | fail (1.518→1.221) | fail | **pass** (mean +5.8 bp, nonloss 62%) | **NO** |

All four pass g5 (official 26 BD crash days: mean daily P&L ≥ −0.10% and non-loss rate ≥ 50%) and g2. None reach holdout Sharpe 0.8. None produce anything near 5%/month at a 25% train-DD scale (`ASIA_FADE` holdout at L25 is Sharpe 0.33, monthly gmean ~0.09%). **No MQL5.** Closest holdout is `ASIA_FADE` +0.33, invalidated by train −3.08 and pre-sample −3.95 (2024–2026 luck, not a rule). `NY_GRID3` is the only template with a positive train Sharpe (+0.32) and is flat-to-negative in holdout.

### Observational conditions at their actual entries (book only, 2024-08–2026-11; no lookahead)

Last **already-closed** M15 bar at entry (a first pass that used the forming bar’s close was corrected; these numbers are the no-lookahead file in `entry_snapshot.csv`):

- They **follow** the prior M15 close-to-close **84.4%** of the time (buys after an up-bar 85.0%; sells after a down-bar 83.5%). Prior H1 follow **89.4%**. Prior M15 bp by side: buys +12.3, sells −16.1. This is a strong momentum-following signature, and it is **the same on winners (84.4%) and losers (84.2%)**.
- Implementing “follow the last M15 at the first session bar, 30-minute / 1.5 ATR stop” is **exactly** `NY_FOLLOW` / `ASIA_FOLLOW`, and those **lose after RF costs** in both train and holdout (win rate ~37–42% vs the vendor’s 79%). Follow-the-last-M15 is **not sufficient**. They must be selecting minutes, stretching a grid, cutting short scalps, or using a filter (levels, news, intra-bar) that these templates do not have.
- Entry ATR median is 5.44 vs 5.99 for all M15 in the same period (slightly quieter than average, not a volatility spike rule on its own). Distance to the prior UTC day’s high/low: about **−2.6 ATR** from PDH, **+5.5 ATR** from PDL (upper half of a bull-market daily range, not a systematic PDH/PDL fade).

We did not scan hours, ATR multiples, or news calendars after seeing P&L. A news-time filter was not pre-registered as a backtest template; NFP/FOMC alignment is left untested.

---

## 5. What this means

EdgeTrader’s published 2024-08–2026-11 gold book has **timing skill** (and direction skill) that survives a same-week random-entry test at p = 1/2001 and is not only the ten best days. It is **not** a martingale; it **is** a clustered, same-minute, averaging-in book with lots that step up with the balance, a 79% win rate, and a lot of profit in ≤5-minute trades. We did **not** recover a frozen, costed, 2018–2023-trainable rule that passes g1. Do not deploy, do not write MQL5, do not retune these templates. If a later round tries to decode further, new templates must be pre-registered before their P&L, and the 2024–2026 book cannot be treated as a clean holdout for anything discovered from it.

---

## 6. Files

- `PREREG_20261112_0908_t212_edge.md`
- `code/backtest_t212_edge.py`, `code/backtest_t212_infer.py`
- `results_t212_edge/` — `summary.json`, `infer_summary.json`, `profile.json`, `real_trade_bp.csv`, `entry_snapshot.csv`, perm arrays, infer trades/daily per spec
- This file: `RESULTS_t212_edge.md`
