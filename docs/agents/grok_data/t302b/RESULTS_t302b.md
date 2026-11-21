# RESULTS t302b — full t239/t241 gate on six MQL5 history exports

As-of 2026-11-20 10:41 Asia/Jerusalem (IST, UTC+2).
Requester: Claude, `claude_outbox.md` 19.11.2026 22:35 (export then t239/t241 gate, new PREREG, TycheCerf aside).

**PREREG_t302b.md** sha256 `0a98af8f4a71112b299ab7725420e57ae4d4eb41926020df5a0134b75b5244b7`.
The header inside the PREREG says 10:33 IST; the file was written and hashed at 10:34:44 IST, before the first P&L path. The hash below is of the file as hashed, and it was asserted again at the start of the gate.

Read-only on Benzaquen except the copy of this folder into `docs/agents/grok_data/t302b/` and an append-only inbox note. No terminals, no live accounts, no secrets printed.

Official bars (frozen in the PREREG): honest TWR ≥ 3.0%/month, age ≥ 18 months (start on or before 2025-05-21), max(closed TWR DD, official floating DD) ≤ 25%, top-10 close-days of log-TWR < 50%, gold ≥ 10 bp after RF ECN $0.31/oz, FX ≥ 5 pips (4 pips is a sensitivity only), median hold ≥ 15 min, hard-SL coverage ≥ 80%, +1 pip/side stress must also clear the same net bars, grid rule (max same-symbol ≥ 5 and averaging-down ≥ 20, or lot escalation ≥ 20% of ≥ 10 sequences), GR/family unique-event match ≤ 20%, sibling DD ≤ 40%. The t241 3.5%/month and 5-minute hold lines are sensitivities only.

## Verdict

**No book is an official GO. There is no passer and no SPEC.**

All six official starts clear 18 months and all six lifetime honest TWRs clear 3.0%/month. The failures are in replicability (RF recost, hard SL, median hold), concentration, grid/averaging, floating DD, and in two cases a family unique-event match.

Closest to a numeric pass is **Soft Chili (2389887)**: it clears honest 4.69%/mo, closed and official floating DD ~19.5%, top-10 days 42.5%, gold 25.3 bp (stress 24.8 bp), median hold 17.7 hours, no grid, GR match ~0.4%. It fails the official hard-SL bar (only 12.0% of closes show `[sl …]`; there is no S/L column). Timing-vs-random does not beat a ±4h null (percentile 28.8). Average loss is 5.3× average win, same skew t302 already flagged. Official verdict is **NO-GO**.

## Method notes

- Two layouts. 2385553, 2394167, 2373216, 2031876 are standard t239/t241 closed-trade exports. 2391620 and 2389887 are MT5 deal exports, paired FIFO as **one closed trade per Out deal** (frozen in the PREREG).
- Vendor P&L = profit + commission + swap. Honest monthly uses cash-flow TWR, as-of 2026-11-20, months = (as-of − official start) / 30.4375.
- Symbol suffixes `.std`, `.i` and `-E` were stripped before recost (the first typ-fix pass had left `-E` in place and produced nonsense JPY pip figures for 2385553; those figures were discarded; the numbers below use the corrected typ).
- Official floating DD is only for gold-only / gold-majority books (2394167, 2389887), marked-to-market on Dukascopy XAU mid. Gold-slice MTM on mixed books (2391620, 2031876) is descriptive and did not drive the 25% bar.
- RF recost: gold $0.31/oz ECN RT; FX conservative spread from the PREREG plus file commission when present, otherwise imputed $14/standard-lot RT scaled by inferred contract. +1 pip/side stress is official.
- Direction permutations N=2000 seed 302302; gold timing N=2000 seed 302301, ±4h on the same mid. They cannot rescue a failed house bar.
- Crash dates: 26 UTC dates in `results_t209/crash_G_ASIA_LONG.csv`, official broker offset UTC+2.

CSV SHA-256 (unchanged from the structural peek):

| File | SHA-256 |
|---|---|
| 2391620_history.csv | `8ea7bff7b77868ac27801d0dbab704b00d0722827dbf61fde0a3a6579c919812` |
| 2385553_history.csv | `010150a76e829cc28ac6902c5aca606537935a3935d1f410f0feba60e2d4b3ba` |
| 2394167_history.csv | `2a4c997bd085fc03af68d65de4a86c08c63addf539fe312af8b25de1b1a738c8` |
| 2373216_history.csv | `b52ee3d507b8a1998991731c83ec4c1544f3256e19f480022344a810225303ce` |
| 2031876_history.csv | `b5f84931149c3b9f64954e554cd0104ff2a793b329099b248948ab05d3603458` |
| 2389887_history.csv | `9882a30110d652aa91b97ea0012e650ef93873296ae3ea4b6268f1ead2f8fb37` |

## Summary table

| Book | Start | Age (mo) | Honest %/mo | Closed DD | Official float DD | Top-10 days | Gold bp (stress) | FX pips (stress) | Med hold | Hard SL | Grid | Family | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Van PM 2391620 | 2024-10-23 | 24.90 | **4.13%** | 10.37% | n/a (mixed; gold-slice 22.93% descr.) | **38.3%** | 4.43 (3.96) | 6.23 (4.23) | 149 min | 0.0% | FAIL (9 / 64) | no | **NO-GO** |
| EU Zone Arsenal 2385553 | 2024-12-02 | 23.59 | **3.47%** (3.5% sensitivity fail) | 6.01% | n/a (no gold) | **35.0%** | — | −7.59 (−9.59) | 190 min | 18.2% | flag (30 concurrent, 19 avg-down; under the frozen auto-fail line) | no | **NO-GO** |
| Gold EA SL 2394167 | 2024-08-12 | 27.27 | **3.68%** | 23.36% | **84.25%** | **66.0%** | 3.49 (2.95) | −2.46 (−4.46) | 8.2 min | **99.9%** | FAIL (9 / 97) | Solnce 32.5%, QuantumStar 41.5% | **NO-GO** |
| Stable Sky 2373216 | 2024-04-19 | 31.05 | **3.54%** | 3.64% | n/a (no gold) | **21.1%** | — | **8.02 (6.03)** | 1,327 min | 67.3% | FAIL (21 / 33, lot escalation too) | no | **NO-GO** |
| Blue Agressive FIC04 2031876 | 2022-11-30 | 47.67 | **3.06%** (3.5% sensitivity fail) | 14.44% | n/a (mixed; gold-slice 44.8% descr.) | **52.5%** | −0.52 (−1.41) | −0.45 (−2.45) | 1.5 min | 78.7% | FAIL (12 / 449) | **Happy Gold 70.2%** | **NO-GO** |
| Soft Chili 2389887 | 2024-11-05 | 24.48 | **4.69%** | 19.35% | **19.48%** | **42.5%** | **25.27 (24.78)** | — | 1,062 min | **12.0%** | no (max concurrent 1) | GR 0.4% | **NO-GO** |

Crash-day pass bar (descriptive except where a book is otherwise a GO; none is): all six have mean daily TWR on the 26 dates ≥ −0.10% and a non-loss rate ≥ 50% at UTC+2. That bar is not enough to pass.

---

## 1. Van PM — 2391620 (Layout B) — NO-GO

Reconciliation is clean: 2,093 closed trades (exact page count), vendor P&L $67,896.18 (exact page profit), cash $14,506.96 (exact initial + deposits − withdrawals), final capital $82,403.14 (exact page balance). 15 leftover open Ins (3.6 lots, mostly AUDCAD from 2024-11-04 to 2026-11-06) sit between page equity $80,009.98 and balance $82,403.14. Unmatched Outs: 0. Last deal 2026-11-06, consistent with t302’s “0 trades/week now.”

- Honest TWR 173.75% in 24.90 months = **4.13%/mo** (page Growth 173.75% / 4.18% agrees). Last-12m honest 6.71%/mo. Money-weighted check is not used officially; large withdrawals ($35,931.85) are handled by TWR.
- Closed DD **10.37%**. Top-10 close-days **38.3%** (the t302 top-10 *weeks* flag of 59% does not fail the official day bar). Residual monthly without those days 2.53%.
- Median hold **149 min**. Hard SL **0%** (no S/L column, all comments empty).
- Recost: gold 594 trades, **4.43 bp** (stress 3.96) — fails 10 bp. FX 1,499 trades, **6.23 pips** unstressed (clears 5) but stress **4.23 pips** fails the official 5-pip stress line (would clear the 4-pip sensitivity). By symbol: AUDCAD 10.45 pips (stress 8.45, 886 trades); EURUSD −3.07 pips (447); gold as above. After RF, monthly TWR falls to 2.47% with DD 17.1%; stress path is negative.
- Grid: max concurrent same-symbol **9**, averaging-down **64** — official grid FAIL. 157 same-side opens within 1 minute. No pending row in this export.
- Swap ≈ −0.16%/yr of equity. Direction vs random: real mean above 100% of the null (p_right 0). Gold timing vs random: percentile 99.95 (descriptive). GR unique-event match 0%. Crash bar passes (descriptive). Sibling 2391627 DD 6%, under 40%.

Fails: gold 10 bp and its stress, FX stress, hard SL, grid.

---

## 2. EU Zone Arsenal — 2385553 (Layout A, EUR) — NO-GO

Reconciliation is clean: 947 trades, vendor P&L and cash match the page exactly (profit €16,066.74, initial €13,000, final €29,066.74). 200 cancelled pendings.

- Honest TWR 123.59% in 23.59 months = **3.47%/mo** (clears 3.0%; fails the t241 3.5% sensitivity). Last-12m honest **2.67%/mo**. Closed DD **6.01%** (page equity DD 12.82% is higher — held risk). Top-10 days **35.0%**.
- Median hold **190 min**. Hard SL **18.2%** (172/947 visible S/L). File commission + spread.
- Recost FX **−7.59 pips** (stress −9.59). The mean is dragged by EURJPY (268 trades, −35.4 pips) and CHFJPY (15, −69.7). GBPUSD (298) is +6.81 unstressed / +4.81 stress; EURUSD (213) is only +2.05 / +0.05. Official bar uses the all-FX mean and fails. After RF, monthly TWR 2.62%, DD 14.2%.
- Hold-losers, as t302 suspected: median hold of losers **1,552 min** vs winners **114 min**; average loss €95 vs average win €54 (1.76×). Max concurrent same-symbol **30**, averaging-down 19 — just under the frozen auto-fail line (needs ≥20 averaging-down), so official grid is a **flag**, not a FAIL. 30 overlapping tickets on one symbol is still a basket.
- Swap ≈ **−4.47%/yr** of equity, just inside the ~5%/yr soft screen. No gold, so no GR match and no official floating DD. Crash full-book table is descriptive and passes. Sibling Australian Arsenal 2385551 DD 10%.

Fails: FX recost (and stress), hard SL. Also last-12m below 3%, hold-loser / high-concurrent flag.

---

## 3. Gold EA Stop Loss No Martingale — 2394167 (Layout A) — NO-GO

Reconciliation is clean: 816 trades, vendor P&L $1,524.18 and cash match the page. 376 cancelled pendings (0.46 per fill). Many deposits/withdrawals on a ~$1,300 book, handled by TWR.

- Honest TWR 167.64% in 27.27 months = **3.68%/mo**. Last-12m 5.20%. Closed TWR DD **23.36%** (equals the page balance DD, just inside the cap).
- Official floating / equity DD on gold-majority MTM: **84.25%** (TWR-path floating 74.45%). This **fails 25%**. Peak 2025-01-15, trough 2025-02-14 on the equity path (75 mid gaps of >5 min were treated as missing, not invented).
- Top-10 close-days **66.0%** (fails). Residual monthly without those days 1.24%.
- Median hold **8.2 min** (fails 15 min; would clear the 5-min sensitivity). Hard SL **99.9%** (815/816) — the only book that clearly passes this bar, consistent with the vendor’s “Stop Loss” claim.
- Recost: gold 687 trades, **3.49 bp** (stress 2.95) fails 10 bp. FX 129 trades, **−2.46 pips** (stress −4.46). After RF, monthly 1.09% with DD 64%.
- Grid: max same-symbol 9, averaging-down 97 — official FAIL.
- Family de-dup (official offset maximising unique-event overlap, here 0h): **Solnce 32.5%** and **QuantumStar 41.5%** unique `(open-minute, side)` events, with 106 and 104 ticket-level hits. Authors differ (Ajaya Pokhrel vs Dmitrii Kuropatkin). The frozen >20% line is an official family close anyway; it may also be shared gold-session timing, but it is not a few coincidental prints. GR itself is only 1.1%. Crash bar passes (descriptive).
- Siblings 2394142 DD 22% and 2397478 DD 4%, under 40%.

Fails: official floating DD, top-10 days, gold and FX recost and stress, median hold, grid, Solnce/QuantumStar unique-event match.

---

## 4. Stable Sky — 2373216 (Layout A) — NO-GO

Reconciliation is clean: 513 trades, vendor P&L $19,427.88, cash $10,000, final $29,427.88. One cancelled pending. File activity ends **2026-09-10**; the last 2+ months to the as-of date are flat. Age still counts from 2024-04-19 (31.05 months).

- Honest TWR 194.28% = **3.54%/mo**. Last-12m 3.11%. Closed DD **3.64%** (page equity DD 14.41% already showed held floating risk; we have no FX mid, so official floating DD is not derivable). Top-10 days **21.1%** (comfortably inside).
- Median hold **1,327 min** (~22 h). Hard SL **67.3%** (345/513) — fails 80%.
- Recost FX **8.02 pips** (stress **6.03**) — this is the only book that clears the FX 5-pip official bar and the stress. After RF, monthly 2.95% (just under 3%) with DD 4.96%. Commission was imputed ($14/lot RT) because the file commission is zero. Swap ≈ **−4.91%/yr**, at the soft-screen edge.
- Grid: NZDCAD/AUDNZD/AUDCAD trio, max same-symbol **21**, averaging-down **33**, and lot escalation after losses **fails** (the only book to trip that clause). Official grid FAIL, same pattern t302 already flagged versus Harmonizer / LazyPro / FX Fun. Losers are held much longer than winners (median 4,543 vs 938 min).
- No gold. Crash full-book table is descriptive and passes. No listed siblings.

Fails: hard SL, grid (including lot escalation). Recost after RF also drops honest monthly just under 3%. Inactive since 2026-09-10.

---

## 5. Blue Agressive CFDs Fiat FIC04 — 2031876 (Layout A) — NO-GO

Trades 4,304 exact. Vendor P&L matches page profit $64,216.37. Cash in the file is a single $20,000 balance row vs page initial $20,004.29 (gap **$4.29**); final vs page balance is the same $4.29. Not material. **13,904 cancelled pendings** vs 4,304 fills (3.23 cancelled per fill).

- Honest lifetime TWR 321.08% in 47.67 months = **3.06%/mo** (clears 3.0%; fails 3.5% sensitivity). Last-12m honest **+1.20% total, 0.10%/mo** — the book has effectively stopped paying. Top-10 close-days **52.5%** (fails). Closed DD 14.44% (matches the page).
- Median hold **1.53 min** (fails 15 and the 5-min sensitivity). Hard SL **78.7%** (3,386/4,304) — just under 80%.
- Recost: gold 1,323 trades **−0.52 bp** (stress −1.41); FX 2,981 trades **−0.45 pips** (stress −2.45). Both fail. After RF the TWR path is negative (monthly −10.3%, DD ~100%). File commission was ~0 so the $14/lot RT was imputed; even before that imputation the gold mean is below 10 bp.
- Grid: max same-symbol 12, averaging-down 449 — official FAIL.
- Family: **Happy Gold unique-event match 70.2%** (198 of 282 Happy Gold events in the overlap window; ticket-level hit rate 74.8%, 989 hits). This is an official family close against a standing closed family (Happy). GR itself is 0%. Gold-slice floating DD 44.8% is descriptive only (mixed book). Crash bar passes (descriptive). Sibling FIC08Milion DD 8%.

Fails: top-10 days, gold and FX recost and stress, median hold, hard SL (narrowly), grid, Happy Gold family match. Last-12m is also far below 3%/mo.

---

## 6. Soft Chili — 2389887 (Layout B, gold only) — NO-GO

241 closed trades vs page 242 (one leftover open Buy 0.10 XAUUSD from 2026-11-18 14:49, which explains the count gap). Unmatched Outs: 0. File vendor P&L $20,717.08 vs page profit $19,626.82 (**gap +$1,090.26**). The file is internally consistent (deal profit + commission + swap = our vendor P&L). Page Growth 196.27% equals page profit / $10,000 initial. Official TWR uses the file: 207.17% in 24.48 months. Cash matches the $10,000 deposit. Final file capital $30,717 vs page balance $29,627, same $1,090 gap. We do not invent a reconciling adjustment.

- Honest TWR **4.69%/mo**. Last-12m 3.67%. Closed DD **19.35%**. Official floating DD **19.48%**. Both inside 25%. Top-10 days **42.5%** (inside). Residual monthly without those days 2.67%.
- Median hold **1,062 min** (~17.7 h). Hard SL **12.0%** (only 29 `[sl …]` comments on 241 Outs; 212 are `[tp …]`, which do not count). Official FAIL.
- Recost gold **25.27 bp** (stress **24.78 bp**) — clears 10 bp with a wide margin. After RF, monthly 4.59%, DD 19.77%; stress monthly 4.52%, DD 20.06%. Still above 3% and inside 25%.
- No grid (max concurrent 1, averaging-down 0). Single lot 0.10.
- Negative skew, confirming t302: 212 wins, 29 losses; average win $352 vs average loss **−$1,862** (5.3×); median hold of losers 6,494 min vs winners 911 min.
- GR unique-event match 0.41%. Direction vs random: percentile 95.25. Timing vs random: real 25.3 bp vs null mean 27.7, percentile **28.8** — the gold edge does not beat a random ±4h shift of the same holds. Crash: mean +0.67%/day, non-loss 100% on the 26 dates (descriptive). No listed siblings. Swap ≈ −1.90%/yr.

Fails: **hard SL only**, on the official bars. That is still a NO-GO. No SPEC is written.

---

## Cross-book and family de-dup

Among the six t302b books, unique-event overlap is at most a few hits (<1%), except Gold EA vs Blue Agressive (5 hits, ~0.9%). No intra-round close.

External official closes already stated: Blue Agressive vs Happy Gold 70.2%; Gold EA vs QuantumStar 41.5% and Solnce 32.5%. Happy News / Happy Japanese / GR / Limitless matches on the other books are well under 20%.

## Crash-day (descriptive)

All six pass the frozen mean ≥ −0.10% and non-loss ≥ 50% at official UTC+2. Soft Chili and Gold EA are gold-majority; the others are full-book or mixed descriptive tables. None is otherwise a GO, so this bar does not promote a book.

## Direction / timing (descriptive)

Van PM, EU Zone, Stable Sky and Blue Agressive have direction percentiles at or near 100% (side is not random). Soft Chili 95.25. Gold EA 99.9. Gold timing (where run): Van PM 99.95; Gold EA 23.4 (does not beat the null); Blue Agressive 99.85; Soft Chili 28.8 (does not beat the null). FX-only books had no local M1 mid; timing was not run for them, as frozen.

## Outputs

- `/workspace/t302b/PREREG_t302b.md` sha256 `0a98af8f4a71112b299ab7725420e57ae4d4eb41926020df5a0134b75b5244b7`
- `/workspace/t302b/RESULTS_t302b.md` (this file) and `/workspace/t302b/t302b_results.json`
- Copies plus the six CSVs to `docs/agents/grok_data/t302b/`
- No `SPEC_*.md` (no official GO)

No trading recommendation; the decision is Nadav’s.
