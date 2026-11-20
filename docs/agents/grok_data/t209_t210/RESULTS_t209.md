# RESULTS t209 — structural / flow edges

Written: 2026-11-12 08:45 Asia/Jerusalem (IST, UTC+2).
Round: t209. **Verdict: no deploy. All four new pre-registered specs fail g1 (and g3, g4). Both gold names also fail g5. No MQL5. No retune.**

This round switched from price-pattern impulse rules (t207–t208, failed on cost) to **scheduled structural / flow** edges with a published economic cause. Parameters were taken from the literature, not searched. Several of the brief’s examples were **already finished** in this programme or rejected by later literature; those were **not** re-run (see §1). Four new specs were frozen in the PREREG **before any P&L**.

---

## 1. Literature check, and what was not retested

| Brief example | Published version | This programme | t209 action |
|---|---|---|---|
| Unconditional turn-of-month, long last days → 3rd of next month | Lakonishok & Smidt (1988); McConnell & Xu, FAJ (2008); Quantpedia | **R1 C**, exact McConnell-Xu window, 4 indices. Train Sharpe −0.11, holdout 0.56, overlap 0.38. Failed g1 and g4. | **Not retested.** |
| Monthly OPEX week, US500 | Stivers & Sun; Quantpedia (Friday before 2nd Saturday → next Thursday close) | **t188u D10**, that exact rule. Train −0.32, holdout 0.33, no book lift. | **Not retested.** |
| Payday / pre-holiday | Ma & Pratt; Hansen & Lunde | **t188u D6 / D7.** D6 failed; D7 holdout 0.62, not a permitted standalone. | **Not retested.** |
| BTC weekend→Monday, CME-gap, MAX nights | Caporale & Plastun FRL 2019; Baur et al. FRL 2019 (not persistent); FRL 2024: Monday effect **does not persist after 2015**. CME-gap fade is *not* supported (returns continue with the gap); CME 24/7 from May 2026. Quantpedia MAX(10) = our BTC_MAX10 (failed). | t187u declined to PREREG weekend-long crypto. Claude R18: do not restart. | **Not PREREGed.** Literature is not robust. |
| Month-end EURUSD | — | Claude R19 and R2-G failed. | **Not retested.** |

The four *new* specs, and why they are not clones:

| Spec | Source | Economic cause | Why it is new |
|---|---|---|---|
| `PENSION_REBAL` | Harvey, Mazzoleni & Melone, NBER w33554 (2025/26) | 60/40 calendar rebalancing: if equities led bonds MTD, funds sell equity into month-end | **Conditional two-sided**, last **5** days (paper’s N). Not R1 ToM (unconditional long −1..+3). Equity leg only on RF US500 (paper also hedges 10Y; stated before P&L). |
| `DASH_CASH` | Etula, Rinne & Suominen, RFS 2020 | Institutional *cash/redemption* needs: sell T−8..T−4, buy T−3..T+3 | Short-then-long path. The long leg is **not** tested alone (that would be a ToM rerun). |
| `G_ASIA_LONG` | Donati & Jung 2019; “London bias” | Physical Asia demand; gold rises in eastern hours | Scheduled **long 00:00–08:00 UTC**, no swap. Not goldA / fade / GR_D96 / real-yield / t208 ORB. Hours are the standard Asia box, **not** taken from Wei’s 2024–2026 (holdout) sample. |
| `G_WEST_SHORT` | Same 2019 hat-shaped pattern | Gold depreciates in London/Western hours | Scheduled **short 08:00–16:00 UTC**. Distinct from t208 London *range-break*. Separate spec, not combined after P&L. |

---

## 2. Cost screen (written first)

File: `COST_PRESCREEN_20261112_0840_t209.md`.

US500: IR coefficients (spread 0.60 pts RT + 5e-6/side), swap long **8.6%/yr**, short **1.8%/yr debit**, Friday ×3. Cash ≈ **1.73 bp** RT at the train mid $3,677.95. Gold: $0.12/side, **no swap** on either session (neither window crosses 21:00 UTC).

- `PENSION_REBAL`: Harvey’s 17 bp is a **next-day** 1 s.d. effect. Half = 8.5 bp vs ~7–11 bp for a 5-day hold → official screen **DROP**. Tested anyway because it is a new requested family; labelled DROP.
- `DASH_CASH`: two RTs + mixed swap ≈ 19–22 bp/month vs conservative half of a 50 bp ToM-scale episode → **MARGINAL/DROP** (~0.8). Tested as a new path, not a ToM clone.
- Gold legs: conservative 2.5 bp vs 1.36 bp cash → **0.54 MARGINAL**.

IEF (7–10y Treasury ETF total return, 2002-07-31–**2026-10-16**) is the bond *signal* only, not a traded RF leg. Pension holdout ends when IEF ends.

---

## 3. Data and method

- US500: Yahoo GSPC cash close, `/workspace/research_new_component/data/yahoo/GSPC_d.csv`, 2000-01-03–2026-11-10. Pre-sample from 2000 (pension signal from 2002-08).
- Gold: Dukascopy M15 bid/ask mid → H1, 2015-01-01–2026-10-26, same as t208. Pre-sample 2015–2017. All 26 official BD crash dates are inside the file.
- PREREG `PREREG_20261112_0840_t209.md`, SHA-256 `6b9ee03cca1136cced9ec02c034270a794e5e0a09b3ee970a6b38d2c19610214`, asserted before P&L.
- Sharpe = calendar × √365.25, matches `metrics_pack`. Daily sums match trade-net **exactly** for three specs; `PENSION_REBAL` daily and trade-net differ by 0.75% of cumulative P&L (74 bp over 26 years) — gates use the daily series. 10% vol and exact 25% train-DD scales frozen on train. g5 only on the gold names.

---

## 4. Results (all four, equally)

Monthly is geometric. Trade stats are **net** bp (after cash and swap), by entry period. Book holdout Sharpe is 1.55–1.57 depending on the series’ last date.

### 4.1 Train (2018–2023)

| Spec | n | WR | PF | Mean net bp | Sharpe 1× | Vol 1× | DD 1× | Mo. @ 10% vol | DD @ 10% vol | Mo. @ 25% train-DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PENSION_REBAL | 72 | 47.2% | 1.233 | **+19.73** | **+0.25** | 9.4% | −15.1% | **+0.17%** | −16.1% | **+0.23%** |
| DASH_CASH | 144 | 49.3% | 1.144 | **+13.04** | **+0.27** | 14.0% | −31.9% | **+0.18%** | −23.6% | **+0.19%** |
| G_ASIA_LONG | 1,548 | 49.0% | 0.923 | −1.14 | **−0.46** | 6.4% | −20.5% | **−0.42%** | −30.5% | **−0.33%** |
| G_WEST_SHORT | 1,548 | 48.3% | 0.937 | −1.58 | **−0.37** | 10.9% | −31.7% | **−0.35%** | −29.4% | **−0.29%** |

Pension and Dash-for-Cash have a **thin** train edge after 8.6% long / 1.8% short swap (pension full-sample mid +41 bp, cash 3.5 + swap 8.6 ≈ 12 bp of cost). That edge is already small (Sharpe 0.25–0.27) and is **not** stable by year: pension 2018 +13.4%, then 2019–2023 mixed to negative; Dash 2021 **−21.1%**, then 2022–23 green. Gold Asia mid +1.43 bp vs 1.44 bp cash — a fair coin after costs, net negative on train. West mid +0.54 bp, also short of 1.44 bp cash.

### 4.2 Holdout (2024 through each series’ last date)

| Spec | n | WR | PF | Mean net bp | Sharpe 1× | Mo. @ 10% vol | DD @ 10% vol | Mo. @ 25% tr-DD | corr book | Book + 10% vol |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PENSION_REBAL | 34 | 44.1% | 0.927 | −4.28 | **−0.04** | −0.04% | −7.3% | −0.07% | −0.057 | 1.574 → **1.479** (no lift) |
| DASH_CASH | 68 | 41.2% | 0.572 | **−37.12** | **−0.97** | −0.58% | −23.7% | −0.62% | −0.039 | 1.554 → **1.047** (no lift) |
| G_ASIA_LONG | 728 | 52.6% | 1.120 | +2.78 | **+0.62** | +0.80% | −22.3% | +0.66% | 0.042 | 1.518 → **1.437** (no lift) |
| G_WEST_SHORT | 728 | 47.5% | 0.981 | −0.59 | **−0.11** | −0.18% | −24.5% | −0.14% | −0.052 | 1.518 → **1.139** (no lift) |

`G_ASIA_LONG` is the closest Sharpe (0.62 < 0.8) and is **not** a pass: train is −0.46, **g5 fails**, and 2024–25 is the Asia-gold bull that Wei (2026) studied **inside our holdout**. Treating that holdout as confirmation would be using the contaminated sample we refused to take hours from. Dash-for-Cash **breaks** in 2024 (−17.6%) and 2025 (−12.9%). Pension holdout is flat-to-negative (2026 −4.2%).

### 4.3 Pre-sample and overlap

| Spec | Pre n | WR | PF | Mean bp | Sharpe 1× | Pre note | Overlap Sharpe |
|---|---:|---:|---:|---:|---:|---|---:|
| PENSION_REBAL | 185 | 57.3% | 1.799 | +38.6 | **+0.53** | 2008 +33%; several other green years; already decaying by 2016–17 | **+0.18** |
| DASH_CASH | 432 | 52.8% | 1.106 | +8.5 | **+0.14** | 2008 −16%, 2009 −22%; noisy | **−0.04** |
| G_ASIA_LONG | 773 | 46.4% | 0.976 | −0.35 | **−0.14** | 2016 +5%, 2017 −7% | **+0.04** |
| G_WEST_SHORT | 773 | 51.0% | 1.009 | +0.20 | **+0.05** | 2015 +14%, 2017 −12% | **−0.27** |

Pension’s **pre-sample is the best window** (Sharpe 0.53, still under 0.8). That is the familiar “published sample looks fine, 2018–2026 does not” pattern, and 8.6% long swap is a large part of why a 17 bp one-day academic effect does not become a 0.8 Sharpe CFD sleeve.

---

## 5. BD crash-day gate (gold only, 26 official dates)

Official g5: mean ≥ −0.10% and non-loss rate ≥ 50%. **Both gold names fail.**

| Spec | Mean | Non-loss | Pos / Neg / Flat | Pass |
|---|---:|---:|---:|---|
| G_ASIA_LONG | **−0.092%** | **34.6%** | 9 / **17** / 0 | **FAIL** (g5a close; g5b clear fail) |
| G_WEST_SHORT | −0.017% | **46.2%** | 12 / 14 / 0 | **FAIL** (g5b) |

Long-Asia during BD crash days is the wrong side of a gold shock more often than not (17 of 26 days red, including 2026-09-22 −1.55%, 2026-07-30 −1.14%, 2026-05-01 −1.05%). That is exactly the gate Nadav kept for gold. Per-day files: `results_t209/crash_G_ASIA_LONG.csv`, `crash_G_WEST_SHORT.csv`.

---

## 6. Gates and the high-return brief

| Spec | g1 HO Sh ≥ 0.8 | g2 corr ≤ 0.2 | g3 book lift | g4 overlap ≥ 0.8 | g5 | Pass | ≥5%/mo @ 10% vol or 25% DD |
|---|---|---|---|---|---|---|---|
| PENSION_REBAL | FAIL (−0.04) | PASS (−0.06) | FAIL (1.574→1.479) | FAIL (0.18) | n/a | **NO** | FAIL (mo ~0) |
| DASH_CASH | FAIL (−0.97) | PASS (−0.04) | FAIL (1.554→1.047) | FAIL (−0.04) | n/a | **NO** | FAIL |
| G_ASIA_LONG | FAIL (+0.62) | PASS (0.04) | FAIL (1.518→1.437) | FAIL (0.04) | **FAIL** | **NO** | FAIL (mo +0.80%) |
| G_WEST_SHORT | FAIL (−0.11) | PASS (−0.05) | FAIL (1.518→1.139) | FAIL (−0.27) | **FAIL** | **NO** | FAIL |

All four have **low** correlation to the C1+I2 book (g2 passes). Adding any of them at 10% train-vol **lowers** holdout book Sharpe. The 5%/month brief is not close.

---

## 7. Multiple-testing honesty

Four specs were frozen before P&L and all four are reported. None passed g1. There is no “best of four” to promote. `G_ASIA_LONG` holdout 0.62 would be the closest Sharpe and is invalidated by a negative train, a failed crash-day gate, and overlap with the 2024–26 sample we refused to calibrate on.

The two equity-flow rules have a modest pre-2018 / thin 2018–2023 net after RF swap, then a 2024–2026 fade (pension) or a sharp reversal (Dash-for-Cash). That is consistent with the COST screen’s DROP / MARGINAL-DROP labels: these are 17–50 bp academic episodes facing 8–22 bp of RF cash-plus-swap on a multi-day hold.

Already-closed examples (ToM, OPEX, BTC Monday) were not given a second chance. No parameter was changed after P&L. **No MQL5. No deployment. No fifth look.**

---

## 8. Files (unique t209 names; t202–t208 untouched)

t208 hashes re-checked unchanged: `RESULTS_t208.md` `58c44448139fdee7a7ff6ff8a81380d4b9df6987385fce29d3bbf3f95491a6a9`; `PREREG_20261112_0830_t208.md` `81c5475b752538c511d785b46f6ca93974ae4edb88bf2d49eeaf0f5549005a1e`.

| File | SHA-256 |
|---|---|
| `COST_PRESCREEN_20261112_0840_t209.md` | `137dea661084e8c5e746be10d255f7a61baf9259df7e67fb373c9cb79f6a8651` |
| `PREREG_20261112_0840_t209.md` | `6b9ee03cca1136cced9ec02c034270a794e5e0a09b3ee970a6b38d2c19610214` |
| `code/backtest_t209.py` | `cc24220361b6fe25682817be12f1836890eb1a07fbfd3344078379e6ececff79` |
| `results_t209/summary.json` | `74055719f661b6b503c37cbf784ce477ef5ed4ed521ba1a6d5eb68b8fa41192f` |
| `RESULTS_t209.md` | this file |
