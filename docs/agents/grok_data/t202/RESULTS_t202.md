# RESULTS — t202: platform scan + NR7 / inside-day backtest

**Written:** 2026-11-12 07:20 Asia/Jerusalem (IST, UTC+2). Author: Grok.
- Shortlist (platforms, candidates, URLs that need a login): `shortlist_t202.md` (`30fed4ba…ff56b5`).
- Cost screen first: `COST_PRESCREEN_20261112_0710_t202.md` (`de91dfce…0a2632`).
- PREREG hashed before any P&L: `PREREG_20261112_0710_t202.md`, SHA-256 `03cb45691cb55ef14aeca01f66b89877a283da198c0b5d6952c55aba96bc2fb6` (asserted in code).
- Code (new): `code/backtest_t202.py` (`1c42393f…235580a`). Outputs: `results_t202/`.
- Benzaquen was not touched. No existing file was overwritten.

This is a **literature proxy** (Crabel NR7 / inside-day), not a clone of JustLookClub, Gold Trade Pro, or Gold Reaper. goldA already tested every-day prior-day / Donchian breakouts and failed on 2018–2023; these rules fire only after a narrow or inside day. **2020 is inside the train window and was therefore seen.**

## 1. Official frozen verdict: 3 / 3 pass the Sharpe gates. No MQL5 spec yet.

The high-return brief is **not** met at the usual 10% vol size (about 1–2.5%/month). It is only approached at a much larger, train-DD=25% size, and that size **exceeds 25% DD in the 2005–2017 pre-sample**. Yahoo daily fill at the exact stop is optimistic when the market gaps through it (~45% of US500 trades). A post-verdict gap-adjusted fill (not used to pick) still passes the gates, with a smaller edge. **Verify on CFD M1 with stop-fills before any MQL5 or live size**, the same way Claude is checking US500_3DD.

| Name | Train Sh / CAGR / DD | Holdout Sh / CAGR / DD | Overlap | Corr book (C1) HO | Book → +add | Pre-sample Sh | Trades train → HO (skip-both) | Mean net bp train → HO | Failed gates | Verdict |
|---|---|---|---:|---|---|---|---|---|---|---|
| **NR7_US500** | **3.03** / +18.8% / −1.8% | **2.80** / +9.7% / −1.2% | **2.90** | −0.05 (−0.05) | 1.554 → **2.454** | 2005–17: **2.58** (413 fills, +45 bp, t = 10.4) | 194 fills (44 skip) → 93 (23 skip) | +54 → +29 bp; WR 78% → 71%; PF 9.7 → 6.2 | none | **PASS** the frozen bar. See sizing and fill caveats. |
| **NR7_XAU** | **1.99** / +6.0% / −0.3% | **2.18** / +8.4% / −0.7% | **2.05** | −0.04 (−0.04) | 1.518 → **2.593** | 2015–17: **2.51** (only 29 fills, 58 skip-both, WR 93%) | 57 (106 skip) → 25 (48 skip) | +62 → +91 bp; WR 88% → 84% | none | **PASS** the bar, but **few trades** and most NR7 days are skipped (both sides touched). 24h gold, almost no gap issue. |
| **ID_US500** | **1.99** / +6.2% / −1.4% | **2.34** / +7.5% / −0.7% | **2.10** | −0.00 (−0.02) | 1.554 → **2.571** | 2005–17: **2.38** (336 fills, +41 bp) | 109 (25 skip) → 49 (18 skip) | +34 → +42 bp; WR 74% → 80% | none | **PASS** the bar. Overlap corr with NR7_US500 = 0.29 (same family). More sensitive to gap fills (below). |

Year raw CAGR, frozen fills (VERIFIED):

- NR7_US500: 2018 15%, 2019 13%, **2020 20%**, 2021 11%, **2022 43%** (bear-market shorts worked), 2023 14%, 2024 7%, 2025 15%, 2026 5.6%.
- Shorts are profitable on their own (train +57 bp, WR 73%; holdout +33 bp, WR 73%). This is not a long-only bull artefact. Tag: VERIFIED.
- NR7_XAU is essentially uncorrelated with the two US500 names (−0.00 to −0.004).

## 2. High-return profile (the actual brief: ≥5%/month, ≤25% annual DD)

Scales are frozen on **train** only. `vol10` = 10% annual train vol. `dd25` = scale that sets train max DD to 25%. Tag: VERIFIED.

### Frozen fill (official, stop = prior H/L, no gap adjustment)

| Name / window | vol10: mean month / CAGR / max DD / worst month | dd25: mean month / CAGR / max DD |
|---|---|---|
| NR7_US500 train (scale 1.74× / 13.76×) | **2.54%** / 34.7% / −3.2% / −0.4% (Jun 2023) | 21.3% / 744% / −25% — **not a realistic size** |
| NR7_US500 holdout | **1.33%** / 17.3% / −2.1% / −2.0% (Aug 2025) | 11.1% / 226% / −16.0% |
| NR7_US500 2018–26 | 2.15% / 28.8% / −3.2% | 18.0% / 521% / −25% |
| NR7_US500 2005–17 (clean) | 2.11% / 27.9% / **−5.4%** | 18.1% / 471% / **−42.7%** — **over 25%** |
| NR7_XAU train (3.40× / 87×) | 1.68% / 21.5% / −1.0% | 87× is meaningless (raw DD is 0.3%) |
| NR7_XAU holdout | 2.29% / 30.7% / −2.3% | at 87×, holdout DD **−50%** |
| ID_US500 train (3.26× / 17.8×) | 1.67% / 21.4% / −4.6% (Jan 2022) | 9.4% / 160% / −25% |
| ID_US500 holdout | 1.97% / 26.1% / −2.1% | 11.5% / 218% / −11.5% |
| ID_US500 2005–17 | 2.96% / 40.4% / −8.4% | 17.3% / 408% / **−45.6%** |

At 10% vol, the best holdout month is **1.3–2.3%**, not 5%. A scale that would print ~5% holdout months on the frozen NR7_US500 series is about **6.6× raw** (~3.8× the 10% vol sleeve): holdout DD ≈ −8%, train DD ≈ −12%, **pre-sample DD ≈ −20%**. That is inside 25% on these daily bars, but only if the optimistic fills survive a CFD M1 test.

### Post-verdict sensitivity: fill at the open when the session gaps through the stop (not used to pick)

~45% of US500 trades (2018–2026) gap through H_t / L_t. Gold, being 24h, is almost unaffected (2 gaps in train).

| Name | Train Sh (gap) | Holdout Sh (gap) | Overlap | Mean bp train → HO | vol10 HO mean month / DD | dd25 HO mean month / DD | Pre-sample dd25 DD |
|---|---|---|---|---|---|---|---|
| NR7_US500 | 2.64 (still) | **2.09** | 2.46 | +37 → +17 bp; WR 73% → 61% | **1.00%** / −2.9% | **4.27%** / −11.7% | **−28.9%** (over 25%) |
| ID_US500 | 1.45 | 2.04 | 1.63 | +20 → +27 bp | 1.54% / −5.4% | 4.03% / −13.5% | −26.4% |
| NR7_XAU | 1.95 | 2.18 (unchanged) | 2.03 | +61 → +91 | almost the official numbers | — | — |

The edge is **smaller but still clearly positive** after a honest gap fill, on both the long and the short side. Gates would still pass. The 5%/month target at a 25% train-DD size is then about **4.3%/month holdout** with **−29% pre-sample DD**. Close, not clean.

## 3. Why there is no MQL5 spec

1. Yahoo ^GSPC daily is not the RoboForex US500 CFD. US500_3DD already showed that a 15:00 vs 17:00 ET fill can drop overlap Sharpe from 0.87 to 0.58. The same risk applies here, and more so because this is a **stop** entry.
2. "Skip if both sides are touched" needs a tick or M1 path to be fair; on daily bars we simply take no trade (pre-registered, conservative in intent).
3. 5%/month at ≤25% DD is **not** achieved at 10% vol, and the size that gets close **fails the 25% DD cap on 2005–2017**.
4. This is not a decode of a live 5%/month book.

**Next check (for Claude, same spirit as US500_3DD):** M1 or H1 US500 CFD, buy/sell stop at the prior day's high/low after an NR7 day, fill at the first touch (open if it gaps), flatten at 16:00 ET, RF 2.31 bp RT, 2018–2023 / 2024–2026 frozen. Do not retune N or the skip rule.

## 4. Platform scan — verdict in one paragraph

Public pages on Myfxbook, MQL5 Signals, Darwinex, Collective2, FXBlue, ZuluTrade, eToro, and cTrader Copy were read without logging in (`shortlist_t202.md`). **No verified, non-grid, ≥12-month book with a public trade list currently prints a stable 5%/month at ≤25–30% DD** on those surfaces. The near-miss is **JustLookClub** (€100k real, 6.09%/month, 5.74% DD, 43% WR, 2:1, SL+TP on every visible open trade, clock-hour entries, London/NY gold is the profit centre). Its closed history was not fully public in this fetch, and the honest age may be ≲12 months. Gold-breakout EAs that *do* print 4–6%/month (EdgeTrader, Gold Trade Pro, Gold Reaper) belong to a family this program already failed to reproduce on 2018–2023. Darwinex's honest ceiling is ~1.2–1.9%/month. Collective2's best long futures track (**ares**) is ~2.5%/month, 14% DD, 6 years. Many headline 5%+ names are grid, or Myfxbook Gain vs Abs. Gain distortions (Trading Pro X1: +1,401% gain vs **+74% abs**; Wisdom EA: +380% vs **+9.5% abs**).

URLs for a logged-in history scrape are in `shortlist_t202.md` §5. Priority: JustLookClub.

## 5. Next ideas (not run)

1. **Claude M1 tester on NR7_US500** (above). This is the highest-priority follow-up if the goal is a high-return sleeve.
2. **JustLookClub closed trades**, once scraped: decode the clock-hour, multi-asset, 2:1 rule and pre-register a new name. Cost screen already PASSES.
3. Do **not** retest Gold Reaper / Gold Trade Pro / EdgeTrader daily S/R, London FX breakouts (dropped on cost), or 0.7%/month diversifiers.
