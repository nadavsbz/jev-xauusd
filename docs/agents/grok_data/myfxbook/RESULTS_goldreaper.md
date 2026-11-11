# Results — Gold Reaper V3.0 reverse-engineering (t191u / t193u)

**Author:** Grok (המאסטרו).  
**Written:** 2026-11-11 22:08 Asia/Jerusalem (IST, UTC+2).  
**Pre-registration:** `PREREG_20261111_2203_goldreaper.md`  
**PREREG SHA-256:** `a84c1ceae64af2e7a7c2fbbda1ea9c2ed0281d561c985408cdd7932f2c4e3358` (verified at backtest start; unchanged).  
**Official verdict: FAIL.** The loose family proxy `GR_D96` does not pass the frozen bar. It is not recommended. No MQL5 spec.

This is not a rewrite of goldA, goldfade, or t190u. No portfolio-combination work was done (t190u). Accounts, terminals, and `accounts.json` were not touched.

Tags below follow the usual bind: **VERIFIED** (computed or matched in this run), **OBSERVED** (pattern in the live book), **ASSUMED** (a modelling choice), **UNKNOWN**.

---

## 0. Source and offset

The Myfxbook file was copied to `/workspace/research_new_component/myfxbook/goldreaper_history.csv`. SHA-256 `be5b30b2974e012e321e0032269a2de8137dace2740ba902dfc62647b4e5ce7c` matches `/workspace/goldreaper_history.csv`. 928 rows: 926 XAUUSD trades, one deposit $1,615.05 (2024-10-22 16:32 broker time), one withdrawal −$100 (2024-12-04 08:19). Dates are `MM.DD.YYYY HH:MM`. Tag: VERIFIED.

**‘Pips’ are points of $0.01.** Trade pips equal 100 × (signed price move) to machine precision. Tag: VERIFIED.

**Broker offset is GMT+2, plus one hour during US DST** (America/New_York + 7 hours), not Europe/Athens and not a fixed UTC+2 or UTC+3. Dukascopy M1 bid (sell) and ask (buy), window ±2 minutes:

| Candidate | n matched | In-bar | Median \|error\| | ≤ $0.50 |
|---|---:|---:|---:|---:|
| GMT+2 / US DST | 906 | **98.0%** | **$0** | **99.3%** |
| Europe/Athens (EU DST) | 906 | 89.4% | $0 | 90.4% |
| UTC+3 fixed | 900 | 63.2% | $0 | 64.6% |
| UTC+2 fixed / Johannesburg | 901 | 44.3% | $1.26 | 46.6% |
| UTC, Berlin, New York | — | 6–12% | $6–14 | — |

The 20 unmatched trades are all after Dukascopy ends (2026-10-26). The 18 in-sample misses have median error $0.36 (broker vs Dukascopy quote). 714 of 888 in-bar fills match the exact minute. 107 trades fall in US–EU DST disagreement weeks; Athens fails there, US-DST does not. DST and standard-time slices both ~98% in-bar. Tag: **VERIFIED**.

---

## 1. Descriptive statistics (live book)

Window: 2024-10-29 to 2026-11-10 (≈742 days, 201 unique UTC days with trades). All figures below are OBSERVED on this book unless noted.

| Item | Value |
|---|---|
| Trades | 926 (559 buy 60.4%, 367 sell 39.6%) |
| Trades / month | mean 35.6, median 33–35; 8.73 / week |
| Win rate | **70.8%** (656 / 926; 0 BE) |
| Profit factor | **2.011** |
| Mean / median PnL | $5.38 / $2.15 |
| Mean gross edge | **11.07 bp** of entry price (median  only 3.4 bp; right-skewed) |
| Mean net | 10.70 bp; implied cost 0.37 bp |
| Deposit / withdrawal / end balance | $1,615.05 / $100 / **$6,506.10** |
| Simple ROI on deposit (adding back the withdrawal) | **+309.0%** in ~24 months |
| Max equity DD (M15 mark-to-market, through 2026-10-26) | **−20.23%** on 2025-03-10 17:15 UTC (peak $1,975 → $1,576). Tag: OBSERVED estimate; last two weeks of trades have no M15 path. |
| Realized-balance max DD | −16.78% |

**Entry hour (UTC, after the offset fix).** Peak is the New York morning, not a single clock print: hours 13–16 UTC hold 357 trades (**38.6%**). Hour 13 alone has 120. Asia 00–02 UTC is the second lump (63+55+41). London 07–08 is weak (14+21). Only 10.5% of entries sit on :00/:15/:30/:45 (uniform would be 6.7%); 27% sit on a 5-minute mark vs 20% uniform. This is intra-bar / stop-like, not “trade the M15 close only.” 13:30 UTC exact = 0 trades (18 within ±2 minutes). Tag: VERIFIED.

**Weekday (UTC):** Wed 220, Tue 195, Thu 169, Mon 162, Fri 154, Sun 26, Sat 0. Sunday trades are after the weekend reopen, not Saturday deals. Tag: VERIFIED.

**Hold time** (Myfxbook duration field, else timestamp difference): median **30 minutes** (train-slice 42.5), mean 234 minutes (fat right tail). p10 3 min, p25 9, p75 146, p90 533. 33 trades < 1 minute, 34 holds ≥ 1 day, overnight share **13.2%** (16.4% on the train slice). Tag: VERIFIED.

**SL / TP (as recorded at close — not necessarily the initial order).** 480 have an SL field (381 positive, 87 negative, 12 zero), 344 have a TP, only 35 have both, 137 have neither (445 SL-only, 309 TP-only). Positive SL median $1.13–1.38 (0.35 × M15 ATR on the train slice). TP median **$14.24** overall, **$12.65 / 3.17 × ATR** on the train slice (p10 $8.98, p90 $29.28). About 59% of trades that have a TP close within $0.35 of the classic TP; the SL field often sits near the realized close (trailing / last level), so it is a weak “initial stop” measure. Big losers show SL distances of tens of dollars (e.g. −$21 to −$58), i.e. protection is loose or absent on those tickets. Tag: OBSERVED; the initial intended stop is UNKNOWN.

**Lot sizing vs balance.** Lots: 0.01 × 749 (80.9%), 0.02 × 107, 0.03 × 40, 0.04 × 12, 0.05 × 13, 0.06 × 5. Correlation of lots with realized balance at open: **0.40** — mild scaling as the account grew from ~$1.6k to ~$6.5k, not a formula we recovered. Not a classic martingale: mean basket lots after a losing basket 0.032 vs 0.031 after a winner; share of “larger than previous basket” is 38.7% after a loss vs 35.3% after a win. Tag: OBSERVED.

**Baskets / scale-in, not a grid.** 395 baskets (same direction, entries within 2 minutes). 234 have ≥2 legs, 165 have ≥3, max 9. **664 / 926 trades (71.7%)** share an exact broker minute with at least one same-direction mate (235 such groups) — this is the “3 sells at 18:20” pattern. Multi-leg median price range only **$0.77**, mean time span 35 seconds: split tickets at almost the same price, not a wide averaging grid. 105 mixed SL/TP baskets (some legs carry a TP, some an SL). Opposite-side overlap is rare (7 trades). True scale-in (same direction already open for >2 minutes): 318 trades; 94 averaged down, 223 added at a better/running price; median gap 12 minutes. Tag: OBSERVED.

**Costs vs edge.** Fill prices already include the broker spread. Implied commission+swap = (pips × lots) − Profit: median **$8 / lot = $0.08 / oz** (constant; 75th percentile also $8/lot; mean $12.5/lot because of overnight swap). At the live median gold price that is ~0.22 bp of commission, total mean cost 0.37 bp. RoboForex decision RT **1.64 bp** (goldA fact sheet, $0.288 at the 2018–2023 train mid) is about 15% of the live mean gross 11.07 bp — well under the one-third bar — **but this 11 bp is a 2024–2026 vendor number and is not an official screen input.** Tag: VERIFIED arithmetic; the IC $8/lot figure is OBSERVED on this ledger.

**Monthly trade PnL (USD, not equity):** 2024-10 −7; 11 +182; 12 +82; 2025-01 +120; 02 **−125**; 03 +200; 04 +285; 05 +342; 06 +256; 07 +45; 08 +213; 09 +242; 10 **−153**; 11 +267; 12 +150; 2026-01 +669; 02 +139; 03 +322; 04 +53; 05 +287; 06 +492; 07 **−114**; 08 +573; 09 +869; 10 **−258**; 11 (partial) **−139**. Losing months: 2024-10, 2025-02, 2025-10, 2026-07, 2026-10, 2026-11. Tag: VERIFIED.

---

## 2. Price context and rule reproduction

Features use the last **closed** M15 mid bar before each entry (no lookahead). Split: first 556 trades (through 2025-12-05 14:47 UTC) vs the remaining 370. Both slices are inside 2024–2026. Tag: VERIFIED construction.

**Fingerprint (stable on train and check):** this is a **with-trend breakout / momentum** book, not mean-reversion, not a session ORB, not an EMA bounce, and not a grid.

| Feature | Longs | Shorts |
|---|---:|---:|
| Median position in 20-bar channel | 0.98 | 0.02 |
| Median position in 48-bar channel | 0.98 | 0.04 |
| Above / below EMA20 | 98.9% / — | — / 94.8% |
| After 1-hour move in trade direction | 92.8% | 92.9% |
| RSI(14) median (bars overall: 51) | **71** | **30** |
| Already through prior-day high / low | 68.0% | 51.0% |
| Close already beyond Donchian 20 | 43.6% | 42.5% |
| Fade of a 20-bar break | **0%** | **0%** |

Longs are a median 0.10 ATR below the 20-bar high; 58% are within 0.25 ATR of it. Combined with intra-bar (not close-aligned) fills, the live entries look like **buy/sell stops into a new N-bar extreme**, not a fade of one. Tag: OBSERVED.

**Reproduction (selected).** Direction of every breakout / momentum rule is ~100% on both slices. Mean-reversion rules have ~0% direction agreement. Precision is the problem: the bot is much more selective than “take every break.”

| Rule (fitted on first 60% only) | Train rec / prec / dir (±15m) | Check rec / prec / dir |
|---|---|---|
| Donchian 96 first M15 *close* | 60.1% / **11.8%** / 100% | 72.2% / 12.6% / 100% |
| Donchian 96 intra first + EMA20 + 1h mom | 66.0% / 10.3% / 100% | 68.6% / 9.5% / 99% |
| Donchian 48 first close | 63.8% / 8.9% / 100% | 72.2% / 8.9% / 100% |
| Prior-day intra first + EMA20 | 36.5% / 11.3% / 100% | 38.6% / 8.5% / 100% |
| Prior-day first *of day* (v1) | 25.0% / **18.5%** / 100% | 30.8% / 14.8% / 100% |
| NY 15-min ORB | 11.7% / 7.4% / 98% | 7.3% / 3.5% / 100% |
| EMA20 bounce | 9.7% / 0.7% / 98% | 5.7% / 0.3% / 100% |
| RSI mean-reversion | (dir ~0%) | — |

A complete, tight, codeable clone **did not emerge**. Best simple precision is ~12–18%, i.e. five to eight false signals per true live entry. What *did* emerge, clearly and stably, is the **family**. Tag: OBSERVED.

---

## 3. Pre-registered proxy and backtest

Because the family is clear, one loose proxy was pre-registered **before** any 2018–2023 or official holdout P&L: `PREREG_20261111_2203_goldreaper.md`.

**`GR_D96` (frozen):** first M15 close beyond Donchian(96) high/low; one position, no scale-in; TP 3.0 × M15 ATR(14, last completed bar); disaster SL 6.0 × ATR; 12-hour time stop; Friday flatten 20:00 UTC; no NFP skip; RoboForex $0.24 width, Pro commission $0, official metals swap, triple on Wednesday, Athens midnight (ASSUMED server clock). N=96 and the rounded exits were chosen on the first 60% of *live* trades only. Friday flatten is ASSUMED vs the vendor (the live book has some multi-day holds). The official 2024–2026 holdout is **contaminated** by that discovery; 2018–2023 is the honest test. A disclosure bar (train Sharpe ≥ 0.8) was pre-declared in the PREREG and is not a sixth official gate.

Data: Dukascopy M15 bid+ask through **2026-10-26 18:15 UTC**. Artifact: `results_goldreaper/report_GR_D96.json`.

### Official gates — FAIL

| Gate | Result | Pass? |
|---|---|---|
| 1. Holdout net Sharpe ≥ 0.8 | **0.788** | **NO** (just short) |
| 2. Holdout corr vs C1+I2 `pnl` ≤ 0.2 | **0.031** | YES |
| 3. Train-vol scaled overlay lifts the book’s holdout Sharpe | 1.518 → **1.616** (scale 1.034 from train vol 9.67%) | YES |
| 4. Overlap net Sharpe ≥ 0.8 | **−0.032** | **NO** |
| 5. BD crash days: mean ≥ −0.10%, non-loss ≥ 50% | mean **+0.16%**, non-loss **69.2%** (17 up, 8 down, 1 flat; n=26) | YES |
| Official `pass_all` | | **NO** |
| Disclosure: 2018–2023 net Sharpe ≥ 0.8 | **−0.617** | **NO** |
| Recommended | | **NO** |

Long-share of trades that overlap a crash date (reported, not a gate): 50%. Corr vs the short 2026 BD proxy: −0.02 (overlap), −0.02 (holdout). Tag: VERIFIED.

### Train vs holdout (1 oz, calendar days, flats = 0, √365.25)

| Window | Sharpe | CAGR | Vol | Max DD | Trades | WR | PF | Gross bp | Net bp | Hold med | Overnight | Long % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2018–2023 train | **−0.62** | **−6.2%** | 9.7% | **−37.1%** | 2,693 (8.6/wk) | 57.7% | 0.97 | **+0.39** | **−0.73** | 5.0 h | 28.4% | 53.8% |
| 2024–2026 holdout | 0.788 | +11.1% | 14.7% | −10.5% | 1,323 (9.0/wk) | 61.1% | 1.14 | +3.30 | +2.74 | 5.0 h | 26.4% | 59.8% |
| Overlap 2018–2026-10-26 | −0.032 | −1.0% | 11.5% | −37.5% | — | — | — | — | — | — | — | — |

Train calendar years: 2018 −16.0%, 2019 −10.4%, 2020 −1.0%, 2021 −11.9%, 2022 +3.4%, 2023 +0.1%. Holdout: 2024 +3.5%, 2025 +2.8%, 2026 (to 26 Oct) +26.4%. Train exits: 1,319 TP / 715 time / 486 SL / 173 Friday. Tag: VERIFIED.

The 2018–2023 gross is **0.39 bp** against a 1.64 bp decision cost (cost is ~4× the gross). That is the same qualitative failure as goldA’s H1 Donchian default (gross −5.9 bp), on a different frozen spec (M15, N=96, TP 3 ATR, wide SL, 12 h). The 2024–2026 window, which is also the vendor’s live track and a strong gold trend, looks much better and still misses Sharpe 0.8 by 0.012. Tag: VERIFIED; the “why 2024–2026 worked” attribution is OBSERVED, not a new test.

**Sensitivities (after the verdict, not used to pass):** Donchian 48 first-close, same exits: train Sharpe **−1.07**, gross **−0.22 bp**, holdout Sharpe 1.08. That holdout number is not a rescue. 2× spread on GR_D96: train Sharpe −1.14, holdout 0.61.

---

## 4. Verdict

- **Offset found (VERIFIED):** IC Trading MT5 = GMT+2 / GMT+3 with **US** DST.
- **Behavioral fingerprint:** a with-trend gold breakout / momentum book that splits a position into a same-minute basket of mixed SL/TP tickets, mild balance scaling, no martingale and no real grid. Entries cluster in NY morning hours (UTC 13–16) but also trade Asia and some London; median hold half an hour, with a fat tail and occasional large unprotected losers. Live WR 70.8%, PF 2.01, ~+309% on $1,615, max equity DD about 20%.
- **Best candidate rule:** first M15 close beyond Donchian 96, which reproduces *direction* perfectly and *timing* only loosely (precision ~12%). A tight clone of the vendor filter is **UNKNOWN** and was not claimed.
- **Frozen proxy `GR_D96` does not pass.** Honest 2018–2023 Sharpe −0.62, gross 0.39 bp (swallowed by RF costs). Official holdout Sharpe 0.788, overlap Sharpe −0.03. Crash-day and correlation gates pass. Not recommended. No MQL5 spec.

Artifacts: `myfxbook/goldreaper_history.csv`, `results_goldreaper/desc_stats.json`, `feature_fingerprint.json`, `rule_reproduction_v2.csv`, `train_exit_stats.json`, `trades_GR_D96.csv`, `daily_GR_D96.csv`, `report_GR_D96.json`, this file.
