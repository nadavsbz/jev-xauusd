# RESULTS t241b — full gate on QuantumStar, EAs Happy Forex Portfolio, Smart Owl FX, and LazyProV2

Written: 2026-11-14 10:00 Asia/Jerusalem (IST, UTC+2).

**PREREG SHA-256 (hashed 2026-11-14 09:55 IST, before any P&L):** `f74f4744796ae0278b7c0e4456413239158fae6ee9011d7df6dae26468ac0ee4`  
File: `PREREG_t241.md` (also under `results_t241/`).

Gate script: `results_t241/run_t241_gate.py`, output `results_t241/analysis_t241.json`. Same house bars as t239. Seeds 241242 (direction) and 241241 (timing), N=2,000. Official broker offset UTC+2 (EET default), not picked to flatter crash-day P&L. Vendor P&L = profit + commission + swap. As-of 2026-11-13. Months = (as-of − official start) / 30.4375.

Work was box-only. The Benzaquen machine was not touched. No costs, no settings changes, no deletions, no credentials printed.

**Official verdict: no complete passer, no SPEC, no GO.**

---

## Official scoreboard

| Book | Official start (age) | Honest %/mo | Closed TWR DD | Top-10 log-TWR | Replicability (gold 10 bp / FX 5 pips, hold ≥5 min, +1 pip/side) | Official verdict |
|---|---|---|---|---|---|---|
| **QuantumStar 2332164** | 2025-05-08 (**18.20 mo**, listing 2025-09-16 is 13.90 mo) | **7.037%** | **−9.08%** (matches page 9.08%) | **44.36%** (pass, close to the bar; “80% in 19 days” is a warning, not a substitute) | Gold **+9.93 bp** unstressed (**FAIL** 10 bp by 0.065 bp), stress **+9.45 bp FAIL**. FX **+0.04 pips FAIL**, stress **−1.96 pips**. Hold 25.5 min passes. | **NO-GO** — replicability, and it is the **Solnce book** (96.6% unique-event overlap) |
| **EAs Happy Forex Portfolio 2393287** | 2024-06-27 (**28.55 mo**, listing 2026-09-28 is 1.51 mo) | **4.661%** | **−10.82%** | **23.98%** | FX **+5.72 pips** unstressed (clears), stress **+3.72 pips FAIL**. Hold 415 min (mean 7.0 days) passes. Visible SL only **1.17%**. | **NO-GO** — Happy-author sibling DD (Japanese floating 74.7%, GridNews 88.83%), standing closed family, and stress |
| **Smart Owl FX 2196221** | 2023-07-20 (**39.82 mo**, listing 2024-02-05 is 33.25 mo) | **4.190%** | **−12.82%** (page bal 12.73%, eq 24.61%) | **22.28%** | FX **+0.31 pips FAIL**, stress **−1.69 pips**. Hold 73.4 min passes. All 538 trades have a visible SL. | **NO-GO** — recost. Page equity DD sits next to the 25% cap; FX floating was not derivable (no local FX M1). |
| **LazyProV2 2378478** | 2023-01-06 (**46.23 mo**, listing 2026-06-18 is 4.86 mo) | **2.840%** (fails 3.5% and the 3.0% hunt floor) | **−3.27%** | **34.50%** | FX **+1.66 pips FAIL** after a corrected XM-micro $14/lot scale (`lot_scale=0.01`), stress **−0.34 pips**. Hold 995 min passes. Visible SL **0.30%**. | **NO-GO** — monthly and recost. No local NoPain tape; style resemblance is not a unique-event close. |

The bars did not move: 3.5%/month (3.0% hunt floor), 25% DD, 1.5y age, 50% top-10 log-TWR, 40% sibling DD, gold 10 bp, FX 5 pips, 5-minute median hold, 20% unique-event family match, official +1 pip/side stress.

---

## QuantumStar 2332164 (RoboForex-ECN; XAUUSD 624 / GBPUSD 129 / USDJPY 20) — priority

File SHA `c6a1a8037f09982163972bd2804c3f005a5a2fc6aff32e35c49c508dcadf5028`. Official start **2025-05-08** (first live trade / 80-week clock). Page “Started: 2025.09.16” is a listing lag, not the age clock.

**Reconciliation is exact.** Vendor P&L **$4,869.23** = page profit. Trade count 773 = page. Cash positives $19,167.08 (= page initial $3,324.36 + deposits $15,842.72; two 2025-05-08 rows are the initial $3,324.36, plus 456 later unlabeled + and one `Deposit` $138.89). Cash negatives **−$12,491.78** = page withdrawals (15 rows). Final **$11,544.53** = page balance. File commission −$220.30, swap −$40.24. Recost rule: file commission + conservative spread. Closed TWR DD **−9.081%** matches published balance DD 9.08% to two decimals.

**The 7.2%/mo headline survives cash-flow TWR.** Official honest monthly is **7.037%** on a +244.82% TWR over 18.20 months. Page growth 245.00% on the same clock is 7.041%/mo — they are the same number, not a withdrawal artefact. What *is* distorted is profit/(initial+deposits) = **25.40%** total, **1.25%/mo**: that money-weighted check looks weak because $15.8k of deposits and $12.5k of withdrawals swamp a $4.9k trading profit. Official is the cash-flow TWR, and it is the high number, not the low one.

**The 80%-in-19-days banner is a real concentration warning, but the official top-10 bar still passes.** Top-10 close-days are **44.36%** of log-TWR (bar 50%). Without those days the TWR is +99.12%, **3.86%/mo**, still above 3.5%. The ten days: 2026-09-28 +$1,071.88, 2026-10-30 +$872.99, 2026-05-18 +$301.13, 2026-08-05 +$284.53, 2026-10-07 +$265.25, 2026-06-11 +$259.08, 2026-08-06 +$245.41, 2026-03-23 +$237.66, 2026-09-29 +$218.32, 2026-11-12 +$214.50. The first two days are the same dates that carried Solnce in t239.

**This is the Solnce book under another signal id.** Versus t239 `2288975.history.csv` (same author, Dmitrii Kuropatkin), official offset 0: **315 / 326** QuantumStar unique `(symbol, minute, side)` events in the overlap window match Solnce (**96.63%** of QS events, **93.20%** of Solnce events). Ticket-level hits 677 / 773 (87.6%). Gold-only unique-event match **96.53%** (278 / 288), ticket rate 94.6%. That is far past the 20% family-close line. It is not a cousin and not a coincidence. Solnce remains a standing closed name; a 96% overlap is a family close even though this signal id was not pre-listed as closed in the PREREG. No SPEC.

**Replicability (the numeric fail, and a near-miss only on gold):**

| Slice | N | Mean net after RF | Stress +1 pip/side | Median hold |
|---|---|---|---|---|
| XAUUSD | 624 | **+9.93 bp** (median 3.70) | **+9.45 bp** | 19.8 min |
| GBPUSD | 129 | +1.63 pips (median 5.80) | −0.37 | 44.2 min |
| USDJPY | 20 | −10.22 pips | −12.22 | 20.0 min |
| FX combined | 149 | **+0.04 pips** | **−1.96** | 40.2 min |
| Book | 773 | — | — | **25.5 min** (pass) |

Gold misses the official 10 bp bar by **0.065 bp**. That is the closest gold recost we have measured (Kenni was 7.65 bp; Solnce itself was +10.01 bp unstressed and +9.51 bp on stress — same neighbourhood, same fail under stress). FX is not close. All 773 trades have a visible SL and TP. Comments: `[sl]` 470, `[tp]` 190, empty 113. RF-recosted honest monthly 6.99%, DD −9.63%; stress monthly 6.92%, DD −10.57% (the *path* still clears 3.5% and 25%; the *average-net* bars do not).

**Stacking / pending ladder, not a long grid.** Max concurrent **15** tickets (15 same-symbol), 0.48 lots. Same-side opens within 1 minute: 998; averaging-down adds: 166; opposite hedges: 0. Cancelled pendings 1,732 vs 773 fills (ratio 2.24) — a pending-stop ladder, Solnce/Kenni-shaped, not TP-TRADER-scale. Median lot 0.01 in 2025 and 0.02 in 2026; lots/balance is stable (median 3.0e-6 vs 4.0e-6) — this is not a 2024-style leverage-up.

**Crash days (official 26 UTC dates, gold-majority book, offset UTC+2):** mean daily TWR **+0.73%**, non-loss **84.6%**, **pass** the standing bar. There are real loss days, including **2026-04-23 −3.68%** (−$246) and 2026-05-04 −1.66%. Direction vs random: real mean recosted $ **+6.04** / trade vs null −0.63, **p=0**, pass. Gold timing vs random (±4 h, Dukascopy mid): real **+9.93 bp** vs null **+9.67 bp**, p_right=0.423, percentile 57.7% — **no timing edge**. GR unique-event match 1.74% (5 of 288), not a close.

**Floating DD.** Gold-only mark-to-market on Dukascopy mid is derivable. Cash-flow-adjusted floating TWR DD **−15.77%** (peak 2026-06-24, trough 2026-07-29), under 25%. Raw equity DD **−67.57%** is **not** the official figure: large withdrawals sit in that window (2026-07-28 −$3,049, 2026-09-08 −$2,550). Mid coverage ends 2026-10-26; 226 event times had no mid within 5 minutes. FX floating is not in this path.

**Siblings.** Measured Solnce closed TWR DD is 13.09% (under 40%). Other kuropatkin cards (Gold Spike, SolarFlare, NebulaEA, …) were not all in the local page cache; a missing page is not a pass. The 96% overlap already closes the family question.

---

## EAs Happy Forex Portfolio 2393287 (Ava; 10 FX majors/crosses, 9,341 trades)

File SHA `81ecb4cbf405adaf84ca9d44f2cd2607c0cb93f90c86d04899f3316e66ba1dd3`. Official start **2024-06-27**. Page “Started: 2026.09.28” is a large listing lag (sensitivity monthly on that clock is a meaningless 136%/mo). Author Jaroslav Rajcher (`happyforex`).

**Reconciliation is exact.** Vendor P&L **$267,167.98** = page profit. Trades 9,341 = page. One deposit $100,000.00 on 2024-06-16; no withdrawals. Final **$367,167.98** = page balance (page equity 307,692.94 — about $59k of open float, not in the closed file). File commission and swap are $0; recost uses imputed $14/standard-lot RT + spread (`lot_scale=1.0`; inferred value-per-price is a mixed 100k / cross-conversion book). Closed TWR **+267.17%**, honest **4.661%/mo** over 28.55 months, DD **−10.82%**. RF-recosted monthly 4.26%, DD −11.80%; stress monthly 3.91%, DD −12.69%. Top-10 share **23.98%**; without those days, 3.52%/mo still clears 3.5%.

**It is not Happy News repackaged.** After stripping the Eightcap `.I` suffix, unique-event overlap with `results_t230/1864588.history.csv` is **13 hits**: **0.14%** of the portfolio events and **1.65%** of News events (best offset +2 h). Ticket hits 5. That is not a >20% close. Overlap with Happy Japanese is 0. A short-hold slice exists (155 trades <1 min, $908 vendor, 99.4% WR, 4.6 pips; 1,147 trades at 1–15 min, $8,448, 99.8% WR, 5.4 pips) but it is a few percent of dollars. The book’s mean hold is **7.0 days** (page “7 days”); the median is 415 minutes. The engine that makes the money is the multi-hour / multi-day book, not the news scalp.

**The long-hold slice does not stand alone after RF recost.** Holds >1 day: 3,230 trades, vendor **+$150,750** (more than half of book dollars) but mean RF net **−2.28 pips**. Shorter buckets are greener (15 min–4 h: +8.79 pips; 4 h–1 d: +14.43 pips). By symbol, unstressed RF means: EURJPY +19.20 (stress +17.20), NZDUSD +18.57, EURUSD +11.29, EURCHF +7.32, AUDUSD +6.78, EURGBP +4.83, GBPUSD +3.61, USDJPY +2.25, USDCHF +0.67, **USDCAD −3.87**. Overall **+5.72 pips** clears 5 unstressed and **fails** the official +1 pip/side stress at **+3.72**. Visible SL on only **109 / 9,341** (1.17%); 8,961 `[tp]` closes.

**Stacking is material.** Max concurrent **190** tickets, **50** same-symbol, 52 lots; 67 opposite hedges; 34 averaging-down adds. This is not a one-position hard-SL book, and FX floating DD was not derivable without an M1 tape. Page equity DD 21.44% already uses the open float.

**Official NO-GO** even if stress had cleared: same author as Happy Japanese (measured floating DD **74.7%**) and Happy Gold GridNews (equity DD **88.83%**), both over the 40% sibling bar, and the Happy family is standing closed. Direction vs random: real mean recosted $ +24.55 / trade vs null −10.48, p=0 (descriptive). No SPEC.

---

## Smart Owl FX 2196221 (Tickmill; 10 FX symbols, 538 trades)

File SHA `79ed24dc093706570e371ae8dd642c9cd25e25f846bc86cad7c36469d668f30c`. Official start **2023-07-20** (weeks clock ≈ first trade; page Started 2024-02-05 is a six-month listing lag). Author Ivan Bebikov. Tiny account: page initial $49.54, deposits $54.79, withdrawals $147.00, profit $142.44, balance = equity **$99.77**. Page max deposit load **34.01%**.

**Reconciliation is exact.** Vendor P&L $142.44 = page. Trades 538 = page. Cash +$104.33 / −$147.00 = page initial+deposits − withdrawals. Final $99.77 = page balance. File commission −$37.11, swap −$10.11; recost is file commission + spread (`lot_scale=1.0`, standard 100k). Honest TWR **+412.61%** = page growth, **4.190%/mo** over 39.82 months. That *is* the brief’s ~4.1% geo, on a cash-flow TWR, not a tiny-account optical illusion in the monthly rate — the optical illusion is the dollar scale ($142 total profit). Closed TWR DD **−12.82%** (page balance 12.73%). Top-10 share **22.28%**; without those days, 3.24%/mo (hunt floor only). Listing-clock monthly 5.04% over 33.25 months.

**Replicability fails cleanly:** mean RF net **+0.31 pips** (median 0.53), stress **−1.69**. Median hold 73.4 min, all 538 trades have a visible SL and TP (502 `[tp]`, 4 `[sl]`, 32 empty). The recosted TWR path on this ~$50–$100 book is unstable: RF-path DD **−89.9%**, stress-path DD **−112%** and stress monthly **−7.84%**. Official house DD remains the vendor TWR (−12.82%); the recosted hole is reported as a replicability fact, not as a rewrite of the official closed bar. Page equity DD **24.61%** is already next to 25%. FX mark-to-market was **not derivable** (no local FX M1, per PREREG); we do not invent it.

**Pending-limit hunt, modest live stacking.** **16,102** cancelled limits vs 538 fills (ratio **29.93**). Max concurrent 6 tickets (3 same-symbol), 0.14 lots; 235 same-side opens within 1 minute; 23 averaging-down adds; 0 hedges. Lots/balance does not trend up through 2023–2026. Direction vs random p=0 on a +$0.09 vs −$0.27 mean (descriptive, and the edge is far too small to pay RF). Crash-day table on the 26 gold dates is descriptive only (this book does not trade gold): mean +0.15%, non-loss 96%. No GR / Happy / cross-book overlap.

**Official NO-GO** on the 5-pip bar (and the stress bar). The 34% load and the 16k cancelled limits are flags, not a separate auto-fail.

---

## LazyProV2 2378478 (XM; AUDCADmicro only, 996 trades)

File SHA `f7b076465af339b96ef86d6b2ade57867139e3fc7c2cb0b8f75936d2e854495a`. Official start **2023-01-06**. Page “Started: 2026.06.18” is a large listing lag (4.86 months). Author Ade Yonathan Lisanto. The t232 symbol scrape (EURUSD/XAUUSD) is the author’s other signals, not this file.

**Reconciliation is exact.** Vendor P&L **$915.30** = page profit (file commission and swap are $0). Trades 996 = page. Cash positives $3,534.98 (= page initial $194.47 + deposits $3,340.51) and negatives **−$3,844.92** = page withdrawals, split across 16 Balance rows ( +$2,237.03 / −$2,656.88) and 16 Credit rows ( +$1,297.95 / −$1,188.04). Final **$605.36** = page balance.

**Inferred contract (frozen method, computed after the hash):** median value per price-unit per file lot = **726.83** (p25 710, p75 743), i.e. a **1,000-unit XM micro lot** with an implied USD/CAD-like factor 0.727. Official recost scales the $14/standard-lot RT by **0.01**. (An unscaled $14/file-lot path is wrong and was not used.)

**The 3.35% “geo” is vendor growth, not honest TWR.** Page growth 362.70% on the official 46.23-month clock is ~3.35%/mo — the brief’s number. Cash-flow TWR is **+264.94%**, honest **2.840%/mo**, which **fails 3.5% and the 3.0% hunt floor**. Large deposits, withdrawals and XM credits are why the two diverge. Closed TWR DD **−3.27%** (page 7.03% balance / 3.00% equity — not a perfect match; credits and a $2.64 residual on equity are reported, not forced). Top-10 share **34.50%**; one close-day (2025-04-07 +$426.19) is heavy. Without the top 10, 1.85%/mo.

**Recost:** mean **+1.66 pips** (median +6.83), stress **−0.34**, **FAIL** the 5-pip bar and the stress bar. Median hold 995 min (~16.6 h); mean is longer (427 of 996 trades last >1 day, and that bucket is **−9.53 pips** after recost). WR 77.2%. Comments: `[tp]` 991, `[sl]` 2, empty 3. Visible SL on **3 / 996**. 92 cancelled limits vs 996 fills (not a pending flood). Max concurrent 9 tickets, 137 micro-lots; almost no averaging-down (2) or hedges (1). Lots/balance is stable across 2023–2026. Direction vs random p=0 (real +$0.78 / trade vs null −$0.15), descriptive. Crash-day table is descriptive (no gold): non-loss 100% on the 26 dates.

**NoPain / NoStress family.** No local NoPain, NoStress, UpEverest, ToTheMoon, MajorForce, MinorForce or RetireNow ticket tape was present on the box (searched the t230/t239/myfxbook/t218 folders and name patterns). Unique-event de-dup was therefore **not run** and is not invented. Style markers *resemble* that family: AUDCAD mean-reversion, limit entries, 99.5% `[tp]`, almost no visible SL, multi-day holds. Style alone is not a >20% unique-event close, and no vendor sentence on the cached page claimed “same strategy as NoStress.” Sibling published DDs for this author were not in the t234 cache. The book is already a numeric NO-GO.

---

## Cross-book de-dup and permutations

GR / Limitless unique-event match is 1.74% on QuantumStar gold and zero on the three FX-only books. Cross-overlap among the four t241 files is 0–0.6% (noise). The only family close in this round is **QuantumStar ↔ Solnce (t239), 96.6%**.

Direction vs random (N=2,000, seed 241242) has p=0 on all four books and cannot rescue a failed cost or DD or monthly bar. Gold timing was run only on QuantumStar (the only gold book; mid available through 2026-10-26) and is not a timing edge. FX timing was **not run** (no local FX M1, per PREREG).

---

## What this does — and does not — change

QuantumStar is the most interesting *numeric* object in t241b: 18.2 months, 7.04%/mo honest TWR that is *not* a withdrawal artefact, 9.08% closed DD, top-10 44% (pass), 25-minute median hold, hard SL on every trade, crash-day standing bar passed, and gold only **0.065 bp** under 10 bp. That near-miss does **not** mint a GO. The official 10 bp bar does not move; FX is 0.04 pips; stress misses; the book is a 15-ticket pending-stop ladder; and it is **Solnce**, already closed, at 96% unique-event identity. Do not write `SPEC_QuantumStar.md`. Do not reopen Solnce under a new name.

The other three fail more ordinarily: Happy Portfolio is a same-author closed family with a failed stress bar, almost no visible SL, and 190-ticket stacking, and it is **not** a News clone; Smart Owl’s 4.19%/mo on a $100 book does not pay 5 pips and sits next to the equity-DD cap; LazyPro’s 3.35% geo is vendor growth, honest TWR is 2.84%, and recosted AUDCAD is 1.66 pips.

No book in this round is a RoboForex live or demo-as-a-path-to-live candidate. In-house OwnGold v1 (already specified) remains the parallel build track.

---

## Files to copy to Claude’s `grok_data/t241_mql5mt4b/`

- `PREREG_t241.md` and `PREREG_t241.md.sha256`
- `RESULTS_t241_candidates.md` and `RESULTS_t241_candidates.md.sha256`
- `results_t241/2332164.history.csv`
- `results_t241/2393287.history.csv`
- `results_t241/2196221.history.csv`
- `results_t241/2378478.history.csv`
- `results_t241/run_t241_gate.py`
- `results_t241/analysis_t241.json`

Optional context, already on the box if he has prior grok_data: `results_t239/2288975.history.csv` (Solnce, for the 96.6% overlap), `results_t230/1864588.history.csv` (Happy News, for the 0.14% overlap). No SPEC file.

---

SHA-256 of this file is written next to it after the text is frozen (`RESULTS_t241_candidates.md.sha256`).
