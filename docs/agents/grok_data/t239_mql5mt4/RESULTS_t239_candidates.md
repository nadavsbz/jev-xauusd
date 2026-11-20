# RESULTS t239 — full gate on TP TRADER, qiangshangs, and Solnce

As-of: **2026-11-13**, Asia/Jerusalem (IST, UTC+2). Written 2026-11-14 06:50 IST.

PREREG: `results_t239/PREREG_t239.md` and `PREREG_t239.md`  
PREREG SHA-256 (hashed **before** any new P&L):

`96471bd3dfe9073a6d3e7576bacd3f00342040840755c5c0008f87e3e1ef967a`

This file’s SHA-256 is written next to it after the text is frozen.

**Official verdict: no complete passer. No SPEC issued. No GO.**

All three books were run through the Happy/Kenni gate on the box copies of the MQL5 history exports. Work stayed on this box; the Benzaquen machine was not touched. Read-only. No credentials printed, no costs, no settings changes, no deletions.

Vendor P&L = profit + commission + swap. Honest monthly uses official start → 2026-11-13, months = days / 30.4375, TWR deposit/withdrawal-adjusted. Broker clock treated as UTC+2 for crash-day and gold MTM (EET); GR offset search independently preferred 0h or is stated. Gold RF cash RT = $0.31/oz ECN (t233). FX recost adds a conservative spread and uses file commission when present, otherwise $7/lot/side. USD/HKD = 7.80 (peg) for 2396034 cash-RT only; the 10 bp / 5 pip bars do not depend on it.

---

## Headline

| Book | Official start (age) | Honest %/mo | Closed TWR DD | Top-10 log-TWR | Replicability (gold 10 bp / FX 5 pips, hold ≥5 min, +1 pip/side) | Official verdict |
|---|---|---|---|---|---|---|
| **TP TRADER 1932739** | 2019-12-17 (82.89 mo) | **4.193%** (clears 3.5) | **−19.06%** (clears 25; matches the page 19.06%) | **12.44%** (clears 50; the “80% in 108 days” banner is not a top-10 fail) | **FAIL** — gold +0.56 bp (stress −0.42); FX **−2.02 pips** (stress −4.02). Hold 24.9 min passes. | **NO-GO** |
| **qiangshangs 2396034** | 2023-07-11 (40.11 mo) | **5.077%** | **−17.04%** (matches the page 17.04%) | **17.40%** | **FAIL** — gold **−0.21 bp** (stress −0.87); FX +2.23 pips (n=61, stress +0.23). Hold 10.0 min passes. **No visible SL or TP** on any closed trade. | **NO-GO** |
| **Solnce 2288975** | 2025-02-12 (20.99 mo) | **5.566%** (first-trade clock 4.989% / 23.36 mo) | **−13.09%** | **53.04% FAIL** (matches the “80% in 23 days” banner) | Gold +10.01 bp unstressed (clears), stress **+9.51 bp FAIL**; FX **−0.65 pips FAIL**. Hold 26.6 min passes. | **NO-GO** — standing closed family, plus top-10 and replicability |

None of the three is a clone candidate under the frozen bars. No `SPEC_*.md`.

---

## TP TRADER 1932739 — year-by-year and the risk-vs-edge verdict

Public page (fetched 2026-11-14): growth 2,931.20%, profit $144,243.17, initial $10,000, deposits $0, withdrawals $50,000, 14,852 trades, hold 3 hours, PF 1.64, balance DD 19.06%, equity DD 1.99%, balance $104,243.17. Banner: “80% of growth achieved within 108 days.” CPTMarkets-Live01. Page “Started: 2025.12.02” is a page anomaly (361 weeks and a public log dated 2023-04-22 point back to 2019); official start remains **2019-12-17** as frozen in PREREG.

**Reconciliation.** File cash matches the page exactly: two +$5,000 rows on 2019-12-17, −$20,000 on 2025-02-26, −$30,000 on 2025-12-03. Closed Buy/Sell = 14,795 vs page 14,852 (−57). Vendor P&L $143,692.70 vs page profit $144,243.17 (**−$550.47**). Reconstructed terminal $103,692.70 vs page balance $104,243.17, same $550.47 gap. The missing 57 tickets (likely still-open or a slightly shorter export) explain a residual of that size. Closed TWR DD of **19.0577%** matches the published 19.06% to two decimals, so the path is the same book.

**House bars on the live full path:** age yes; honest 4.193%/mo yes; closed DD 19.06% yes; top-10 12.44% yes; GR unique-event match 0.13% (3 of 2,267 events) yes; crash-day mean daily TWR +0.47%, non-loss 76.9%, pass. Direction vs random (N=2,000, seed 239239): real mean recosted $ +4.47 / trade vs null −6.85, p=0 (the book is not a random-side coin flip in dollar terms). **Timing vs random on gold** (N=2,000, ±4 hours, seed 239240): real mean **+0.56 bp** vs null **+7.24 bp**, p_right=1.0 — **actual gold entries are worse than a random time in a 4-hour window after ECN recost.** That is the opposite of a timing edge.

**Replicability fail (official).** Median hold 24.85 minutes (gold 19.5, FX 26.7) clears 5 minutes on the *full* file, but 2024–2026 median hold is **4.15 minutes** (53.6% of later trades under 5 minutes; 2024 4.97, 2025 3.56, 2026 3.98). Visible SL on 99.95% of closed trades (almost all hard SL; comments `[sl]` 8,542 vs `[tp]` 228). After RF recost, gold average net is **+0.56 bp** (median **−3.84 bp**) against a 10 bp bar; FX average **−2.02 pips** against a 5 pip bar. +1 pip/side stress makes both worse (gold −0.42 bp, FX −4.02 pips). This is why copy-subscriber reviews on the signal page (slippage, short breakout, follower accounts lose while the provider prints) are consistent with the recost, not anecdotes to set aside.

**Stacking.** Allowed, but extreme in 2020–2023: max concurrent **108** tickets, **44** on one symbol, 44,458 same-side opens within 1 minute, 1,528 averaging-down adds. 2024–2026 stacking collapses to max 4–6 concurrent. The later book is not “the same grid with more lots”; it is **bigger lots, much shorter holds, and ~94–96% SL exits**.

**Gold-only floating DD** (Dukascopy mid at event times; FX marks not available, so this is **not** an official full-book floating path): gold-only TWR MDD **−31.3%** (2025-03-10 to 2025-03-21), equity MDD −74.9% (the equity figure is contaminated by the 2025-12-03 −$30,000 withdrawal and should not be used). Full-book floating DD is **not fully derivable** without FX M1. The gold-only TWR estimate already exceeds 25% and is a risk warning, not a clean official fail of the mixed book.

### Calendar years (broker time; TWR from the official path)

These line up with Claude’s reported +17 / +27 / −4 / +23 / then ~+150%/yr:

| Year | n | Year TWR | Intra-year DD | Vendor P&L | Median lots | Median lots/balance | Median hold (min) | Max concurrent (symbol) | `[sl]` % | Gold avg RF bp | FX avg RF pips |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 72 | +0.44% | −0.90% | +44 | 0.01 | 1.00e-6 | 81.2 | 20 (20) | 6% | −7.32 | +15.69 |
| 2020 | 2,492 | **+16.56%** | −18.09% | +1,663 | 0.01 | 1.02e-6 | 74.2 | 91 (44) | 12% | +10.05 | −5.88 |
| 2021 | 2,151 | **+26.94%** | −2.51% | +3,154 | 0.01 | 0.86e-6 | 40.5 | 108 (40) | 43% | −0.33 | −2.04 |
| 2022 | 3,203 | **−3.62%** | −15.99% | −538 | 0.10 | 6.58e-6 | 20.1 | 90 (40) | 61% | −6.81 | −4.31 |
| 2023 | 2,997 | **+23.14%** | −5.22% | +3,314 | 0.10 | 5.81e-6 | 24.1 | 74 (34) | 56% | −1.80 | +0.75 |
| 2024 | 1,303 | **+157.90%** | −8.13% | +27,849 | **1.42** | **4.97e-5** | **4.97** | 6 (4) | 96% | +0.83 | −0.34 |
| 2025 | 1,490 | **+163.58%** | −7.34% | +45,797 | **1.15** | **2.52e-5** | **3.56** | 5 (4) | 96% | +0.88 | +0.31 |
| 2026 | 1,087 | **+151.17%** | −0.98% | +62,409 | **1.15** | **1.53e-5** | **3.98** | 4 (4) | 93% | +2.84 | −0.57 |

Median lots/balance in 2024 is **45×** the 2020–2023 median; 2025 is 23×; 2026 is 14× (risk came down from the 2024 peak but stayed an order of magnitude above the calm window). Median lots jumped from 0.01 (2020–21) / 0.10 (2022–23) to 1.15–1.42, while median open-balance only rose from ~$10–16k to ~$31–75k.

### Windows

| Window | TWR | Honest %/mo | DD | Notes |
|---|---|---|---|---|
| Live **2020–2023** (calm) | **+75.59%** | **1.181%/mo** (~**15.12%/yr** compound) | **−18.09%** (2020-03-13 → 2020-10-29) | 10,843 trades. Gold RF **+0.31 bp**, FX **−2.80 pips**, median hold 34.9 min. This is exactly the “~15%/yr, low-teens/high-teens DD” book Claude asked about. It does **not** clear 3.0% or 3.5%, and it fails replicability. |
| Live **2024–2026** | +1,607.4% | 8.61%/mo | −8.13% | 3,880 trades. The headline acceleration. Gold RF still only +1.46 bp; FX −0.14 pips; median hold **4.15 min**. |
| 2024–2026 at **2020–2023 median risk** (start with end-2023 capital $17,637.45; scale each later year’s P&L by k = med_risk_calm / med_risk_year; withdrawals omitted) | **+40.69%** | **0.997%/mo** | −0.69% | Scaled later P&L $7,176 vs raw $136,055. With 2025 withdrawals also × k_2025: +44.52%, **1.076%/mo**, DD −0.72%. |
| Full live path 2019-12-17 → 2026-11-13 | +2,911.4% | 4.193%/mo | −19.06% | The 3.5% full-period bar is carried by the leveraged 2024–2026 window. |

A first attempt to scale 2024–2026 P&L while leaving the live −$50,000 withdrawals unchanged blew the TWR path up (as expected: withdrawals were sized to the leveraged equity). That sensitivity is discarded. The two constant-risk later figures above are the valid ones.

### Official risk-vs-edge verdict: **RISK INCREASE**

The 2024–2026 ~+150%/yr is **not a genuine extra edge**. At the 2020–2023 risk level, 2024–2026 returns collapse to about **1%/mo**, the same band as the calm window (1.18%/mo, 15.1%/yr). There is also a **style shift** (holds from tens of minutes down to ~4 minutes, SL-exit rate from ~12–61% to ~94–96%, stacking from ~100 tickets down to 4–6), so it is not only “the same engine at higher k”. It is leverage-up plus a tighter, shorter scalp/breakout mode.

The calm 2020–2023 window is a serious *descriptive* object (~15%/yr, 18% DD, long live age) but it is **not** a conservative official GO: honest monthly 1.181% is under both 3.5% and 3.0%, and RF recost fails (gold +0.31 bp, FX −2.80 pips). It should not be cloned as a 3%+ hard-SL book. A later research thread could study it as a low-edge stacked breakout, not as a gate passer.

**NO-GO.** No SPEC.

---

## qiangshangs 2396034 (Vantage, HKD, mostly gold)

Public page: growth 642.94%, profit HK$50,911.40, initial HK$15,600, deposits HK$110,323.63, withdrawals HK$151,653.28, 2,234 trades, hold 7 hours, PF 2.02, balance DD 17.04%, equity DD 3.93%, balance = equity HK$25,181.75. Win rate 89.7%. Page “Started: 2026.10.18” is a page anomaly (166 weeks, growth since 2023); official start **2023-07-11**.

**Reconciliation.** File cash net **HK$−25,729.65**, exact match to page initial + deposits − withdrawals. Vendor P&L HK$50,880.64 vs page HK$50,911.40 (**−HK$30.76**). Closed 2,232 vs 2,234. Reconstructed HK$25,150.99 vs page 25,181.75, same HK$30.76 gap. Cash rows mix labeled `Deposit`, unlabeled large deposits/withdrawals, `Credit` bonus/clawback at the same timestamps, and small weekly ~HK$100–126 credits; all were treated as cash, not trading P&L, which is what the page does.

**House bars:** age yes; honest **5.077%/mo** yes (this is why TWR, not profit/(initial+deposits) ≈ 0.9%/mo, is the official number — deposits and withdrawals are huge); closed DD **−17.04%** yes; top-10 **17.40%** yes; GR 0%; crash-day mean +0.42%, non-loss 100%, pass. Direction vs random p=0 (real +HK$16.96 / trade vs null −5.99). Gold timing vs random: real −0.21 bp vs null −4.21 bp, better than random but still negative after recost.

**Replicability fail.** 2,171 / 2,232 trades are `XAUUSD.`. **Zero visible SL or TP.** Median hold 10.0 min (gold 9.0; the 61 FX trades sit at 645 min and do not drive the book). Gold average net **−0.21 bp** (median +2.50 — a right-skew book with a thin average after ECN costs). FX +2.23 pips on n=61, under 5 pips; both fail +1 pip/side stress. Max concurrent 9 (6 same-symbol); some same-side clustering (221 within 1 min) but not a 100-ticket grid.

Gold-only floating TWR MDD of −115% is **not trustworthy** as official DD: the path mixes large 2025–2026 cash events with gold MTM and has no FX marks. Official DD remains the closed TWR −17.04%.

**NO-GO.** No SPEC.

---

## Solnce 2288975 (RoboForex-Prime; gold + GBPUSD + USDJPY)

On the standing closed list. Gated anyway because a full export was supplied. The brief’s “GBPUSD” label is incomplete: closed trades are **XAUUSD 668, GBPUSD 341, USDJPY 152, EURUSD 1**.

Public page: growth 211.62%, profit $6,633.37, initial $3,168.55, deposits $2,487.88, withdrawals $1,620.00, 1,162 trades, hold 7 hours, PF 1.95, balance DD 13.09%, equity DD 10.92%. Banner: “80% of growth achieved within 23 days.” Official start **2025-02-12**. First trade 2024-12-02 is a 2.3-month pre-listing lead (under the 1-year flag).

**Reconciliation is exact.** Vendor P&L $6,633.37 = page profit. Cash: one `Deposit` $3,168.55, 420 unlabeled positive rows summing to the page deposits $2,487.88, 11 withdrawals summing to $−1,620.00. Final $10,669.80 = page balance. Trade count 1,162 = page. Closed TWR DD −13.088% matches the published 13.09%.

**House bars:** age yes on both clocks; honest 5.566%/mo (listing) / 4.989%/mo (first trade) yes; closed DD −13.09% yes; **top-10 53.04% FAIL** (top days include 2026-09-28 +$1,314.91 and 2026-10-30 +$876.10). GR 1.48%. Crash-day mean +0.77%, non-loss 84.6%, pass. Direction vs random p=0. Gold timing vs random: real +10.01 bp vs null +8.80, percentile 83.5% (weak, not a standout timing edge). All 1,162 trades have a visible SL and TP. Max concurrent 16 (14 same-symbol); 1,561 same-side opens within 1 min; 146 averaging-down adds — a modest stack, not TP-TRADER-scale.

**Replicability:** gold **+10.01 bp** unstressed (clears 10 bp by a hair), **+9.51 bp after +1 pip/side — FAIL**. FX **−0.65 pips**, stress −2.65, FAIL. Median hold 26.6 min passes (gold 17.7, FX 34.2).

Gold-only floating TWR MDD **−17.81%** (2026-06-24 to 2026-07-29), close to the closed 13% and under 25%; this book’s cash path is milder, so the estimate is more believable than qiangshangs’, but still gold-only.

Cross-book gold unique-event overlap with TP TRADER is **14.8% of TP events / 31.95% of Solnce events** in the overlap window (108 hits, offset 0). That is the 20–50% “related / mixed” band for Solnce, not a GR-family close, and not enough to call them the same engine. qiangshangs does not overlap either of the others.

**NO-GO** (closed family, top-10, FX recost, gold stress). No SPEC.

---

## Gate bars, in one place

Hunt floor 3.0% and standing 3.5% honest monthly; equity/TWR DD ≤ 25%; age ≥ 18 months; top-10 close-days < 50% of log-TWR; sibling DD ≤ 40%; not GR-family (>20% unique-event match); gold avg net ≥ 10 bp; FX majors ≥ 5 pips; median hold ≥ 5 minutes; official +1 pip/side stress must still clear those bars. Solnce stays closed even if the numbers had cleared.

All three clear age and (on official starts) the 3.5% honest-monthly and 25% *closed* DD bars. All three fail replicability. Solnce also fails top-10 and is a closed family. TP TRADER’s full-period 4.2%/mo is leverage-up from a ~15%/yr 2020–2023 core that itself misses 3% and misses recost.

---

## Files to copy to Claude’s `grok_data/t239_mql5mt4/`

Copy these (public artifacts only; no investor logins, no account numbers):

- `results_t239/1932739.history.csv`
- `results_t239/2396034.history.csv`
- `results_t239/2288975.history.csv`
- `PREREG_t239.md` and `PREREG_t239.md.sha256` (also under `results_t239/`)
- `RESULTS_t239_candidates.md` and its SHA sidecar, once written
- `results_t239/analysis_t239.json` (full numeric dump)
- `results_t239/run_t239_gate.py`

Do not copy `data/private/`, Wine prefixes, or any credential file.

---

## Bottom line

**All three are NO-GO. No SPEC.** TP TRADER’s 2024–2026 acceleration is a **risk increase** (and a shorter-hold style shift), not a new edge: at 2020–2023 risk it falls back to ~1%/mo, in line with the calm window’s 15%/yr and 18% DD. That calm window is not a 3% gate passer and does not recost to 10 bp / 5 pips. qiangshangs and Solnce also fail replicability; Solnce additionally fails top-10 and remains a closed name.
