# RESULTS t218 — Limitless Gold V3 decode gate

Written 12:45 IST (Asia/Jerusalem), Thursday 12 Nov 2026.

Official decode gate (t212 rule): **PASS**. Timing p = 0.00050 and the recorded USD edge survives dropping the 10 best close-days (remaining $2,061.12, PF 1.438). Direction control also passes (p = 0.00050). Brief thresholds also clear: 2.03 years, honest TWR 5.75%/month, closed-trade max DD 16.78%.

Inference (four frozen stop-entry templates, run only because the gate passed): **not recovered**. All four fail g1 (holdout Sharpes −1.00, −0.49, −0.16, −0.66). No MQL5. GR_D96 was not rerun.

This book is the **Gold Reaper V3** family under a new name: `lim_open.txt` comments are `The Gold Reaper_XAUUSD_1`–`_7`, and the deposit/withdrawal fingerprint ($1,615.05 on 2024-10-22, $100 on 2024-12-04) matches the earlier Gold Reaper Myfxbook book (926 trades then, 927 now, one extra day). The earlier GR_D96 *proxy* failed g1/g4; this job is the first t212-style decode gate on the full TSV, which that work did not run.

---

## Files and hashes

| File | SHA-256 |
| --- | --- |
| `PREREG_20261112_1226_t218_limitless.md` | `4ee413c383713da0341a3f70988454ddb67d79743d06548a6bd325cec3d5801e` |
| `/home/box/Downloads/lim_hist_all.tsv` | `5faa7ffea4ad27e70ee01696bad8ac4a17996064ec313bacbd8f077d47439f2f` |
| `/home/box/Downloads/lim_open.txt` | `7f0754829a602b2ec23215f4d546c193ca4e6ced13a03397cfad49336b09210a` |
| `code/backtest_t218_limitless.py` | `2d1f7586fcd5a01c3ce428411913da13a5b756f316503892972ba18fa9f8653d` |
| `results_t218_limitless/summary.json` | `8e2e9e3a0ac6d7b599803d53f3119cc48b4dd250e8aea1022d2975b3a5c709a7` |

PREREG was hashed **before** any mid-price or random-path P&L. The script asserts that SHA and the TSV SHA before those steps. Seeds frozen: timing **218218**, side and cluster **218219**, ≥2-minute sensitivity **218318**. N = 2,000. Broker clock NY+7 (VERIFIED on this deposit fingerprint in the goldreaper PREREG). RF costs as t208/t212: $0.12/side, swap −$0.60 long / +$0.19 short, 21:00 UTC including synthetic Sat/Sun, **no** Wednesday triple. Mid lookup is in nanoseconds (the t212 us-vs-ns bug is not repeated).

Benzaquen / Claude files were not touched. t199–t217 were not overwritten.

---

## 1. Parse and reconcile

929 nonempty rows, no header, 11 columns. **927 XAUUSD** (559 Buy, 368 Sell) + Deposit $1,615.05 (22 Oct 2024 16:32) + Withdrawal −$100.00 (4 Dec 2024 08:19). First open 29 Oct 2024 03:33, last close 11 Nov 2026 17:35 (broker). Capital Point Trading MT5, 1:500. 11 pending BUY STOP / SELL STOP, **no live positions**.

- Sum of TSV Profit = **$4,999.29** exactly (error $0.0000). Balance identity 1615.05 − 100 + 4999.29 = **$6,514.34**.
- Pip identity: recorded pips = `100 × s × (P_out − P_in)` with median / p99 / max absolute difference all **0**. 1.00 lot = 100 oz.
- Residual (recorded profit − gross $) sums to **−$140.68**, identical to the vendor’s commissions −$93.98 plus swap −$46.70.
- WR **70.87%**, PF **2.0128**, matching the brief’s 70.9% and 2.01.

---

## 2. Monthly TWR, honest %/month, DD

True TWR, split at the deposit and the withdrawal. Final balance **$6,514.34**. 26 calendar months (partial first and last included).

| | Value |
| --- | --- |
| Geometric honest %/month | **5.75%** |
| Abs-gain span (profit/deposit over 750 days) | **5.89%/month** (Abs +309.54%) |
| Vendor Myfxbook monthly | 5.98% |
| Max closed-trade equity DD | **−16.78%** (matches vendor 16.78% to 2 dp) |
| Months negative | **6 / 26**: 2024-10 (−0.44%), 2025-02 (−6.63%), 2025-10 (−4.57%), 2026-07 (−2.04%), 2026-10 (−3.73%), 2026-11 (−1.97%) |
| History | **2.03 years** (≥ 1.5y) |

Best months: 2025-04 +19.85%, 2026-01 +18.50%, 2025-05 +15.18%, 2026-09 +14.39%. 2026 is still positive on net despite three down months at the end. **≥5%/month honest: yes. DD ≤ 25% (not borderline): yes.**

---

## 3. Direction vs random (control; not a substitute pass)

Dukascopy M1 mid at the **real** entry and exit minutes, RF costs, fair coin side, seed 218219, N = 2,000, n = 906.

| | |
| --- | --- |
| Real-side mid+RF mean | **9.348 bp** |
| Perm mean | **−0.775 bp** |
| Excess | **+10.123 bp** |
| p = (1 + #{perm ≥ real}) / (N+1) | **0.00050** (0 of 2,000; percentile 100) |

Real beats the 95th percentile. **Direction is skilled.**

---

## 4. Official random timing

TSV fills minus RF cash and RF swap, equal-weight mean net bp. Same-side, same duration, same ISO week (broker), M1 mid, 2-minute exit window, pool ≥ 10. Mid coverage 2022-01-02 23:00 UTC → **2026-10-26 18:48 UTC**; **21 trades excluded** (all after the file ends). Universe and used: **906**. Dropped for empty/small pools: **0**.

| | Official | Sensitivity, duration ≥ 2 min (seed 218318, not official) |
| --- | --- | --- |
| n | 906 | 806 |
| Real mean fill+RF bp | **10.455** | 11.941 |
| Perm mean (sd) | 3.627 (1.135) | 4.150 |
| q05 / q95 | 1.73 / 5.55 | — |
| Excess | **+6.829 bp/trade** | +7.791 |
| n_ge | **0 / 2,000** | 0 / 2,000 |
| p | **0.00050** | 0.00050 |
| Pass p < 0.05 | **YES** | yes (cannot change the official verdict) |

Cluster robustness (491 same-minute-same-side groups, shared uniform quantile, seed 218219): p = **0.00050**, perm mean 3.647, excess +6.808. Cannot alone declare a pass; it agrees.

**Timing is skilled.** The live book’s 10.5 bp/trade at RF costs is not a same-week random-entry artefact. M1 cannot see inside a 1-minute bar; 100 of 906 used trades have duration < 2 minutes, and dropping them does not change the picture.

---

## 5. Top-10 close-days

| | |
| --- | --- |
| Total recorded profit | $4,999.29 |
| Top-10 close-days | $2,938.17 (**58.77%** of profit) |
| After drop | **$2,061.12**, 881 trades, **PF 1.438** |
| Pass (remaining > 0 and PF ≥ 1) | **YES** |

Top days (broker close date): 2026-09-28 +549.74, 2026-10-07 +423.34, 2026-05-18 +305.17, 2026-01-12 +285.44, 2026-08-05 +268.32, 2026-08-06 +247.04, 2026-06-24 +245.73, 2026-06-11 +217.28, 2026-10-30 +209.85, 2026-03-18 +186.26. Concentrated, but the residual book still has a genuine PF.

---

## 6. Clustering / grid flag (not an auto-fail)

Heavy stacking, **flagged**, not a fail.

| | |
| --- | --- |
| Same-minute same-side | **664 / 927 (71.6%)** in 235 groups |
| Another same-side open within 5 minutes | **813 / 927 (87.7%)** |
| Entered with same side already open | **800 / 927 (86.3%)** |
| Averaging-down (worse price than live same-side mean) | **386 / 927 (41.6%)** |
| Max concurrent positions | **17** (19 Aug 2026 16:12 broker) |
| Max concurrent lots | **0.32** (22 Oct 2026 08:47) — small notional, many legs |
| Lots vs balance at open | corr **0.397**; lots 0.01–0.06, median 0.01. Steps with balance, **not** a classic martingale lot-doubler |

**22 Oct 2026 7-loss streak:** confirmed. 7 consecutive losing closes, **−$504.78**, first open 08:44, last close 15:47 broker. The day’s 10 closes net **−$417.61** (a later +$85.76 sell offsets some of it). Morning cluster is all **Sells** at 08:44–08:47, prices 4074 down to 4066 (selling lower into a bounce that ran to 4090–4098), lots 0.01 / 0.02 / 0.03 / 0.03 / 0.05 / 0.03 / 0.06 — **averaging down, size stepping up**. Afternoon, another sell cluster (0.05 + 0.06) at 14:15–14:21. This is the Gold Reaper multi-pending / multi-leg pattern, not a single-shot stop. Flag only.

---

## 7. Cost environment and RF recost

Vendor: commissions −$93.98, swap −$46.70, total **−$140.68**, already identical to the TSV residual.

RF on the same fills and timestamps (1 oz cash RT $0.24, swap −$0.60 / +$0.19, 21:00 UTC including weekend, no Wednesday triple):

| | RF | Vendor |
| --- | --- | --- |
| Cash RT, all 927 trades | **$294.72** | $93.98 commission |
| Swap | **$65.71** debit net (115 overnight trades, mean 0.187 nights) | $46.70 |
| Net dollar P&L | **$4,779.54** | $4,999.29 |
| Difference | RF is **$219.75** more expensive | |

Equal-weight mean fill+RF bp: **10.20** on all 927, **10.46** on the 906-trade official universe. Median 3.03 bp. Mean recorded move **417 pips** ($4.17) vs a $0.24 RT of **24 pips** — the average winner clears the spread comfortably; the median trade is thinner (3 bp ≈ 12 pips of net after costs, against 24 pips of RT, so the median is carried by the right tail and by shorts’ swap credit). Instrument still **PASS**es the 2 bp/side cap ($0.12/side at gold prices is ~0.3–0.7 bp).

---

## 8. Replicability (inference, only because the gate passed)

Live-book fingerprint (recorded TSV, not mid P&L): median hold **31 minutes** (mean 249 min, p90 545 min, 83 holds ≥ 10 h). Long share 60.3%. Wins: median $8.18, 23.4% of wins within $3 of the pending **$14 TP** layer; almost none near $67 / $83. Losses: median $5.64, 12.7% near a $20 SL, 9.3% near $14. Busiest broker hours 16–18 (NY morning under NY+7) and 03–04; hour 03 alone is +$1,324 on 68 trades. Wednesday is the most profitable weekday (+$2,303). Pending book is layered BUY STOP / SELL STOP at prior-range extremes (near ~4146–4148 and far ~4691 / ~3872) with SL/TP clusters (14/67, 20/83–127, 82–174/14) — a **breakout** EA, several layers at once.

Four frozen templates (PREREG, no search, M15 mid, fills mid ± $0.12, double-touch = loss, 8-hour time stop, Friday flatten 20:00 UTC). **GR_D96 was not rerun.** Train 2018–2023, holdout 2024-01-01 through 2026-10-26, gates g1–g5, calendar Sharpe × √365.25, exact 25% train-DD leverage via binary search on `(1+L·r)`.

| Template | n (train / HO) | Train Sharpe | HO Sharpe | Pre-sample Sharpe | g1 | g2 corr | g3 lift | g4 | g5 | Pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `LIM_STOP_TIGHTSL` (SL $14, TP $67) | 10,526 (4,739 / 3,479) | +0.06 | **−1.00** | −0.67 | no | yes (0.03) | no (1.52→0.31) | no | **yes** (mean +0.31%, non-loss 62%) | **no** |
| `LIM_STOP_WIDESL` (SL $80, TP $14) | 10,533 (4,789 / 3,425) | +0.08 | **−0.49** | −1.09 | no | yes (−0.02) | no (1.52→0.79) | no | **no** (mean −0.64%, non-loss 38%) | **no** |
| `LIM_STOP_MID` (SL $20, TP $83) | 9,812 (4,643 / 2,870) | −0.33 | **−0.16** | −1.17 | no | yes (0.08) | no (1.52→0.93) | no | **yes** (mean +0.37%, non-loss 73%) | **no** |
| `LIM_STOP_BOTH` (layers 1+3) | 20,338 (9,382 / 6,349) | −0.15 | **−0.66** | −0.98 | no | yes (0.06) | no (1.52→0.58) | no | **yes** | **no** |

They over-fire by an order of magnitude versus the live 927 trades (most exits are the 8-hour time stop: 7,486 / 7,523 / 7,879). A naive prior-M15-high/low stop on every bar is the right *family* (breakout, pending stops) and the wrong *filter*. That is the same qualitative gap as GR_D96 (precision ~12% on the live book, train Sharpe −0.62). Closest holdout miss here is `LIM_STOP_MID` at **−0.16**, still negative, and its train is already −0.33. L25 does not flip any Sharpe (leverage is a scale). **Inference is not recovered. No MQL5.**

---

## Verdict

**Official t212 decode gate: PASS.**

1. Timing: real 10.455 bp vs perm 3.627, excess +6.83, **p = 0.00050**.
2. Concentration: after the 10 best close-days, **$2,061.12 remains, PF 1.438**.

Direction control: **p = 0.00050**. Cluster and ≥2-minute sensitivities agree. Brief bars: **2.03 years**, honest **5.75%/month**, DD **16.78%** — all clear. RF-recosted P&L is still $4,779.54 (about 5.5%/month on the same TWR base).

**Do not deploy from a recovered rule.** The four frozen stop-entry templates all fail g1; this is a skilled live book whose entry filter we have not reproduced, plus a heavy multi-leg / averaging-in signature (flag, 17 concurrent legs, 42% averaging-down, the 22 Oct 2026 −$505 sell-into-a-bounce). Same situation as EdgeTrader in t212: the gate can pass and the deployable rule can still be missing.

No MQL5. No retune. GR_D96 stays closed and was not retested.
