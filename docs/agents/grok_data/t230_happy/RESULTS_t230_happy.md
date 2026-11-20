# RESULTS t230 — EA Happy News, Happy Gold, Happy Japanese: full gate, recost, decode

Written: 2026-11-13, Asia/Jerusalem (IST, UTC+2).

**PREREG** `results_t230/PREREG_t230.md`, SHA-256 `48b614dcd03683fda379550c9895cf1dad9e59a891d30ea605f8643d36b97bd1`, hashed at 06:57 IST **before** any P&L, permutation, recost or crash-day computation on these histories.

Trade files (SHA-256, frozen in the PREREG):

- `1864588.history.csv` (News) `62eb00b292fde82d497314955b809be38faff5581432ef63b361ba7d8fcebce6`
- `1862128.history.csv` (Gold) `265ce6ad875007e94981dc0cecdfcc7bb2e91427370c1df8f25854b2365376f6`
- `2295123.history.csv` (Japanese) `b98f74c87746b53eb721355cfae54318392b09574aaaa11d82b22d0894e75c85`

Deposits from SHORTLIST_t228 / `family_stats.json`, confirmed by Balance rows in the exports. Broker clock **verified**: Eightcap stamps are Europe/Athens (EET/EEST, UTC+2/+3). News pendings sit 2–3 seconds before official US 08:30 ET releases (NFP-like lead median **2.0 seconds**, 72 matches). RoboForex ECN contract specs fetched from public pages on 2026-11-13 (`results_t230/raw/rf_ecn_*.html`).

---

## Verdict (go / no-go for a RoboForex demo)

| Book | Official RF path, honest %/mo | Official RF TWR DD | Top-10 remaining honest | Direction p (N=2,000) | Other fatal flags | **Demo** |
|---|---|---|---|---|---|---|
| **EA Happy News Eightcap** [1864588](https://www.mql5.com/en/signals/1864588) | **12.87%** (stress 12.23%; Eightcap-fills+RF-cash 11.11%; book 10.95%) | **11.86%** (stress **28.67%**) | **12.09%** (stress 11.28%) | **0.0005, PASS** (9.58 bp vs perm p95 0.23) | Stress DD exceeds 25% if half-spreads are floored at 2 pips/side. | **GO, conditional**, RoboForex **ECN** demo of the **vendor EA**. Not Pro-Cent. Not a signal copy. See conditions below. |
| **EA Happy Gold Eightcap** [1862128](https://www.mql5.com/en/signals/1862128) | **9.59%** (book 10.68%; RF-cash 10.30%) | **35.36% — FAIL** | 7.86% (share 52% of official $) | **0.0005, PASS**; timing also PASS (p=0.0005) | BD crash-day g5 **PASS**. Zero grid on this book. GridNews sister still 88.83% DD. Official $ 90% from 2026. 18 of 46 official months negative. | **NO-GO** for RoboForex. The Eightcap book itself is clean; RF gold spreads + $20/mio commission blow DD through 25%. |
| **EA Happy Japanese Market FM** [2295123](https://www.mql5.com/en/signals/2295123) | **4.01%** RF-cash (book 4.86% from Started; **3.64%** from first fill) | Closed TWR **24.34%** RF (book 22.76%, matches the page). **Floating TWR-adjusted DD 74.7% — FAIL.** | **3.27% — FAIL** | **0.0005, PASS**; timing PASS | Martingale scale-in (lots 0.10→0.51, 6 concurrent shorts). GBPJPY only. Swap-free book; RF swap −$1,767. 6.5-month back-fill (35% of $ profit before listing). | **NO-GO.** |

**Only Happy News is a candidate for a RoboForex demo**, and only under these conditions, already implicit in the PREREG and in the vendor’s own warning:

1. **ECN or ECN-ProCent only**, never Pro / Pro-Cent (the published Pro averages of 1.3–1.7 pips are quiet-time figures; at release they would sit on or beyond the stress path).
2. Run the **vendor EA** on an unlimited RoboForex demo (the Full Pack is €699 with 30-day money-back — **do not buy yet**). Do **not** subscribe to the $999/month MQL5 signal. Both the vendor and MQL5 warn that a 2-minute news scalp will slip when copied.
3. **Measure real RoboForex bid–ask in the two-second window before NFP, CPI and Claims** over several releases. The official path uses Dukascopy ticks (median entry width 1.6 pips, p90 4.3, max 22.4) and **passes** 12.87%/month at 11.86% DD. The pre-registered **stress** (half-spread floored at 2 pips/side) still makes 12.23%/month but **DD is 28.67%**. If RF news widths routinely live at that floor, the book is not a 25% DD product on this broker.
4. A purchase, a cent account, or any live run still needs Nadav’s explicit approval after that demo.

Decode specs for a clone are in `SPEC_HappyNews.md`, `SPEC_HappyGold.md`, `SPEC_HappyJapanese.md`. For News, a clone is feasible; the 2-second lead is operationally hard, which is why the vendor EA on a demo is the faster and safer first step. For Gold, ZigZag parameters were not uniquely recovered. For Japanese, a clone is not worth writing.

---

## 1. EA Happy News Eightcap — conditional GO

### 1.1 Book path (Eightcap, net = Profit + Commission + Swap)

Reconciles **exactly** to the MQL5 page: 1,697 fills, gross $121,998.32, commission −$17,550.47, swap −$0.09, **net $104,447.76**. Initial $1,000 on 2023-02-09, no further cash. First fill 2023-02-16 02:30:04, last close 2026-11-10 15:30:08. Official Started 2023-02-15. **No back-fill.** `months = 44.83`. Honest monthly **10.95%**. Geometric product-of-monthly-TWR **10.66%**. Final balance $105,447.76.

- 46 calendar months, **43 positive**, 3 negative and tiny: 2026-01 −0.15%, 2026-04 −0.66%, 2026-06 −0.66%.
- Win rate **85.4%** net, profit factor **4.24** (page PF 4.23). All 1,697 exits are `[sl]` (the SL is modified after fill; see the SPEC).
- Hold: **median 5 seconds**, mean 134 seconds (~2.2 minutes, matching the page), p90 82s, p99 42 minutes, 10 trades ≥ 1 hour, 17 sub-second. 1,516 of 1,697 close inside a minute.
- Closed / TWR DD **−9.14%** (2023-08-30 $3,568.66 → 2023-09-01 $3,242.32), recovered 2023-09-06. **Matches the page “By Balance” 9.14%.** Daily equity-chart DD on the t216 TSV is −5.24%; the page “By Equity” 3.12% is a coarser chart. All are well under 25%.
- Top-10 close-days: 38.2% of $ profit (same as the t216 daily-equity figure 38.8%). Remaining **$64,530**, PF 3.03, honest **9.78%/month — passes**.
- Symbols (net $): USDJPY 49,745 (490), GBPUSD 26,720 (498), EURUSD 21,039 (389), AUDUSD 6,944 (320). Sides nearly balanced.
- Lots scale with balance, correlation **0.945**. Median risk ≈ **1.0% of balance** at an 18-pip placement SL. Lots per $1,000 median: AUD 0.050, EUR 0.060, GBP 0.057, USDJPY 0.081 (pip-value calibrated). Not a martingale.
- Grid flags: 9 same-second same-symbol groups (max 2 legs); 82–86 both-side fills (whipsaw / hedge) net **+$4,356**; max concurrent same-symbol 4 is a rare overlap, not a grid. Flag only, not a fail.

### 1.2 Official RoboForex recost (Dukascopy ticks ± a few minutes around each fill)

Ticks downloaded for 1,665 of 1,697 fills (the 32 misses are the long-hold outliers, hold 25 minutes–4 hours, outside the 15-minute tick window; their book-net is −$4,814 and is used as a fallback). 398k–703k ticks per major.

**RF ECN commission is cheaper than Eightcap** ($10,653 vs $17,550). Swap is negligible (−$3).

| Path | Net $ | Honest %/mo | WR | PF | TWR DD | Top-10 remaining honest |
|---|---|---|---|---|---|---|
| Book (Eightcap fills) | 104,448 | 10.95 | 85.4% | 4.24 | 9.14% | 9.78% |
| RF cash, Eightcap fills | 111,342 | 11.11 | — | — | 8.50% | 10.00% |
| Mid + RF cash (optimistic) | 268,761 | 13.30 | 83.8% | 18.8 | — | — |
| **Official: Dukascopy bid/ask + RF cash** | **226,302** | **12.87** | 79.0% | 10.36 | **11.86%** | **12.09%** |
| Stress: half-spread floored at 2 pips/side | 175,324 | 12.23 | 62.5% | 5.65 | **28.67%** | 11.28% |

Eightcap fills are **worse** than Dukascopy conservative bid/ask: median entry slip vs mid **+5.75 pips adverse** (p90 12.1). Book captures a median **3.0 pips**; the official BA path a median **7.1 pips**; mid 8.85. That is why official $ is above the book — we are **not** assuming better fills than a real ECN, we are using a public tick tape. If RF execution is only as good as Eightcap, the relevant path is “RF cash, Eightcap fills”: **11.11%/month, DD 8.50%, top-10 remaining 10.00%**, still a clean pass.

Dukascopy entry width at the fill instant: median **1.6 pips**, mean 2.12, p90 4.3, max 22.4. The 2-pip-per-side stress is about 2.5× the median observed width and is the “what if RF is meaningfully worse than Dukascopy at the spike” test. It keeps the return (12.23%) and the top-10 bar (11.28%) and **fails DD (28.67%)**. That is the condition in the verdict: a demo must show that RF news widths are in the Dukascopy neighbourhood, not at the 2-pip/side floor.

### 1.3 Direction vs random, timing, clustering

- **Direction**, seed 230230, N=2,000, 1,665 trades with ticks: real equal-weight mean **9.58 bp**, permutation mean −0.41, p95 0.23, p99-ish max 1.18, **p = 0.0005, PASS**. For a two-sided straddle this is “the filled side is the skilled side at those times,” which is mechanical if the pending is a breakout, and is still the pre-registered test.
- **Random timing** on full FX M1 was not completed in this round (M1 for four majors over 45 months was not finished; ticks were prioritised for the recost, which is the binding News risk). The same-week 1-minute null is close to tautological for a 5-second news scalp (expected random mean ≈ 0, costs negative). Gold, which has the same sub-minute hold structure and *did* get a full M1 timing test, passed at p=0.0005 (real 2.82 bp vs perm p95 −0.16). A News fail on this null would be a surprise; it is **not** treated as a substitute for the recost. The second, event-window null (“other high-impact events”) was not run; event-family P&L already shows the edge is concentrated on a stable USD high-impact set (NFP block $43.8k, CPI $30.8k), not on a single freak day.
- Grid: flag only, as above.

### 1.4 Decode (see SPEC_HappyNews.md)

News straddle, both pending stops, **2 seconds** before the release, **10 pips** from mid (mode 10.0, median 10.35, on 1,200 both-pending observations). Placement SL **16–20 pips** (median 17.9), TP **exactly 100 pips** on every pending. Untriggered side cancelled after **64 seconds** (median, tightly 63–65). After a fill, SL is moved; every exit is at that SL; winners lock a median **+3 pips in 5 seconds**; losers take the original 16–20 pip SL (~15%). Lot = **1% risk**. Event universe: high-impact USD first (NFP block, CPI, Claims, ISM/PMI, ADP, JOLTS, PPI, FOMC, Retail), plus GBP/EUR flash PMIs and some AUD employment/CPI. 1,012 clusters, 66% matched to a calendar event (94% of $ P&L); 341 unmatched clusters hold only $6.3k, many after the FF snapshot ends on 2025-04-07 or at GBP/AUD times. Calendar sources: HuggingFace ForexFactory 2007–2025-04, workspace US news and MT5 USD calendars through 2026.

---

## 2. EA Happy Gold Eightcap — NO-GO for RoboForex

### 2.1 Book path

749 fills (page says 750; **page profit $95,755 vs our $94,650**, gap **$1,106**). Identity check on 749 trades is exact (profit = 100 oz × lots × move). The t216 equity TSV ends at $96,755 on 2026-11-12, consistent with one close (or an open that closed) after the export’s last fill on 2026-11-11 16:37:26. One missing trade of ~$1.1k is 1.2% of profit and does not change the gate. Commission on this Eightcap book is **$0**; swap −$12.13. Initial $1,000 on 2023-02-09, first fill 2023-02-14, Started 2023-02-13, **no back-fill**, months 44.93. Honest **10.68%/month**. 46 months, **43 positive**. WR 75.8%, PF 6.61. Hold median **7 seconds**, mean 138s. Closed TWR DD **−11.70%** (2023-06-13 $1,743 → 2023-06-29 $1,539), matches the page By Balance 11.70%. Top-10 share 32.1%, remaining honest **9.75%**, PF 4.81.

**Max concurrent positions = 1. Zero averaging, zero same-second legs.** This is the scalp book the vendor described, not GridNews. Lots track balance at correlation **0.997**. Median risk **2.0%** of balance at the $2.56 hard SL; a second mode near 4%.

### 2.2 Crash-day gate — PASS, strongly

Official 26 BD dates (2026-04-21 … 2026-10-12, same list as t209 / t229): **15 up, 1 down, 10 flat**. Mean daily return **+0.80%**, non-loss rate **96.2%**. Both g5a and g5b pass. The only loss is 2026-10-12, −$1,715 (−2.00%). Sum on crash days **+$9,176**. On the 20 worst Dukascopy XAU close-to-close down-days in 2023-02–2026-10 (including 2026-01-30, gold −9.9%): **12 up, 0 down, 8 flat**, sum **+$5,797**, and **+$1,310 on that −9.9% day**. Same pattern on the 20 worst intra-day range-downs. This book is on the right side of gold shocks, or flat.

### 2.3 Official RoboForex recost — DD fails

RF ECN gold: commission **20/mio** ≈ $16 RT per lot at $4,000/oz (total **−$13,668** on the book), swap −$0.60/oz long / +$0.19 short (only −$28 here). Dukascopy tick width at the fill instant is **large**: median **42 points ($0.42)**, mean $0.53, p90 $0.77, max **$6.53**. That is far above the published ECN *average* of 5 points, because these fills sit in volatile seconds.

| Path | Net $ | Honest %/mo | WR | PF | TWR DD |
|---|---|---|---|---|---|
| Book | 94,650 | 10.68 | 75.8% | 6.61 | 11.70% |
| RF cash, Eightcap fills | 80,965 | 10.30 | — | — | 15.51% |
| Mid + RF cash | 126,078 | 11.38 | 81.7% | 8.34 | — |
| **Official: Dukascopy bid/ask + RF cash** | **60,302** | **9.59** | 54.2% | 2.44 | **35.36% FAIL** |
| Stress: $0.50/side floor | 23,990 | 7.43 | 33.1% | 1.40 | blown (path through zero) |

183 trades that win on the book become official losses. Official profit is **90% from 2026** ($54,540 of $60,302); 2023–2025 together are only $5,762, and **18 of 46 official months are negative**. Top-10 share of official $ is 52%; remaining honest 7.86% would still clear 3.5%, but **DD 35% is fatal**. Direction (733 trades, 2.84 bp vs perm p95 −0.02, p=0.0005) and random timing (727 trades, 60s minimum duration on M1, p=0.0005) both **PASS**. The edge is real on Eightcap. It is not a 25% DD product at RoboForex costs and gold tick spreads.

### 2.4 Decode (see SPEC_HappyGold.md)

Not a news straddle. Pendings are **breakout stops at ZigZag / swing extremes**, mostly placed at **06:00:00–01** (716 of 1,239), cancelled at **22:00** (646) or **15:00** (201). Distance from mid is **not** a tight offset: median **$36.50**, mean $57, tail above $1,000. Signed distance is almost always on the breakout side. Often one side only (both sides at the same second in 39 of 1,200 placement times). **SL exactly $2.56**, **TP exactly $10.00** on every pending. After fill, SL is moved into profit: 745 `[sl]`, only 4 `[tp]`; median capture **$0.35** in 7 seconds. Fills all day, peak 15–16h. Some 15:30 placements exist, but news is not the engine.

Sibling **EA Happy Gold GridNews [1714611]**, equity DD **88.83%**, remains a vendor-settings warning. This Eightcap book does not itself grid.

---

## 3. EA Happy Japanese Market FM — NO-GO

### 3.1 Book path

262 fills, **GBPJPY only** (the page lists USDJPY / EURJPY / GBPJPY; this book never traded the other two). All 262 exits are `[tp]`. Commission $0, **swap $0** (swap-free / “no swap” badge). Net **$7,850.37**, exact page match.

Balance rows: **+$2,000** on 2024-08-23 16:35:55 (first cash, 197 days before official Started 2025-03-11), **+$3,000** on 2024-12-02 20:00:29, **−$3,000** on 2024-12-04 14:32:23. Capital-in $5,000. First fill 2024-08-26 00:00:11, last close 2026-11-06 19:53:35.

- From **Started**, months 19.90, honest **4.86%/month** (page 4.81, as-of one week later).
- From **first fill**, months 26.38, honest **3.64%/month**.
- Pre-listing: **81 trades, $2,729, 35% of all profit**. Mild 6.5-month back-fill, as SHORTLIST said.
- 28 calendar months, **all 28 positive** on realized TWR, but the rate fades (2024-09 +23%, 2026 months typically +1–3%).
- WR 73%, PF 2.48. Hold median **1.69 days**, mean 4.72, max 38 days. Entry: **92.7% at 00:05** broker, 109 of 262 **exactly 00:05:01**.
- Closed TWR DD **−22.76%** (peak 2024-11-20, trough 2024-12-05), **matches the page By Balance 22.76%**. The raw-balance DD of −59.8% is the $3,000 withdrawal and is **not** the bar. On 2024-12-05 six legs closed in the same second; deal order walks through four losers then two winners, which is how the 22.76% prints, and the basket’s *net* was positive.
- Top-10 share 25.0%, remaining book honest **3.99%** (just above 3.5%).

SL at placement is huge and almost never used: median **1,024 pips** (10.24 yen, about 5%). TP median **40 pips** (0.40 yen); some TPs are moved, even into a loss, to flatten a basket together.

### 3.2 RoboForex cash recost (swap is first-order)

RF ECN GBPJPY, public page 2026-11-13: swap short **−2.85 pips**, swap long **+0.62**, Wednesday triple, commission 20/mio, avg spread 0.5 pips (immaterial vs a 40-pip TP). 1,444 night-units (mean 5.5, median 2, max 48).

- RF swap **−$1,766.64** (shorts pay −$2,056, longs earn +$290). Commission **$155**.
- RF-cash net **$5,928.56**, honest from Started **4.01%/month**, from first fill **2.86%**.
- RF-cash TWR DD **24.34%** (borderline, still under 25%).
- Top-10 remaining honest **3.27% — fails** the 3.5% remaining bar.

Spreads at 0.5 pips do not change this. The official RF path for Japanese is the cash path.

### 3.3 Floating DD and the martingale — FAIL

Up to **6 concurrent same-side legs**. Lot path on the 2024-12 basket: **0.10, 0.10, 0.15, 0.23, 0.34, 0.51** (≈1.5× step). 71 averaging-down pairs. This is a martingale / scale-against, not a mild add.

Combined mark-to-market on Dukascopy GBPJPY M1 mid, TWR-adjusted so the $3,000 deposit/withdrawal does not create a fake hole: **floating DD −74.7%** on 2024-12-02 16:34 UTC. Closed balance $3,258, float −$2,436, equity **$823**, five short legs, the oldest already **−787 pips**. The same basket later closed in *realized* profit on 2024-12-05 (the 22.76% closed DD). They survived a near-wipe once. The page equity DD of 23.19% is a daily/closed view and **misses this intra-hold hole**. Per the PREREG, the floating estimate is part of the 25% bar. **74.7% is a hard fail.** Trade-level MAE: median −99 pips, worst −870 (the 1,024-pip SL is a backstop, not a tight risk cap).

Direction on M1 mid: 262 trades, 15.85 bp vs perm p95 2.32, **p=0.0005, PASS**. Timing (same-week M1, 262 trades, 0 dropped): **p=0.0005, PASS**. The direction is skilled. The risk is not.

---

## 4. RoboForex ECN costs used (frozen, public, 2026-11-13)

Commission **$20 per $1,000,000 USD notional per side** on all of these symbols. Wednesday triple swap. Pip and swap (pips):

| Symbol | Pip | Lot | Avg ECN spread | Swap short | Swap long |
|---|---|---|---|---|---|
| EURUSD | 0.0001 | 100,000 EUR | 0.1 | +0.19 | −0.98 |
| GBPUSD | 0.0001 | 100,000 GBP | 0.4 | −0.30 | −0.37 |
| AUDUSD | 0.0001 | 100,000 AUD | 0.3 | −0.30 | −0.10 |
| USDJPY | 0.01 | 100,000 USD | 0.2 | −2.10 | +0.38 |
| GBPJPY | 0.01 | 100,000 GBP | 0.5 | −2.85 | +0.62 |
| XAUUSD | 0.01 | 100 oz | 5 | +19 ($0.19/oz) | −60 ($0.60/oz) |

Pro / Pro-Cent published averages (EURUSD 1.3, GBPUSD 1.5, XAU 18, commission $0) are **not** a viable schedule for the two scalps.

Seeds: direction **230230**, timing **230231**, N=2,000, as pre-registered.

---

## 5. What was not done, and what is next

- News same-week FX M1 timing and the second (other-event) timing null were not run on a full 2023–2026 M1 tape. Recost, which was the binding News test, was. Gold timing on XAU M1 passed.
- No MT5 tester, no demo account, no purchase, no signal subscribe, no terminals, no `accounts.json`, no Benzaquen inbox write.
- One Gold trade (~$1,106) appears to sit after the export. Immaterial.
- **Next, only if Nadav agrees:** RoboForex ECN demo, vendor EA Happy News, settings taken from `SPEC_HappyNews.md`. Log bid–ask at NFP/CPI/Claims for several releases. Buy the €699 pack only after that, and only with a fresh approval. Our clone can be written in parallel. Gold and Japanese stay closed for this broker.

---

## 6. Files

Under `/workspace/research_new_component/`:

- `results_t230/PREREG_t230.md` and `.sha256`
- `RESULTS_t230_happy.md` (this file) and `.sha256`
- `SPEC_HappyNews.md`, `SPEC_HappyGold.md`, `SPEC_HappyJapanese.md`
- `results_t230/1864588.history.csv`, `1862128.history.csv`, `2295123.history.csv`
- `results_t230/fills_*.csv`, `path_*.csv`, `monthly_*.csv`, `pend_*.csv`, `profile_*.json`
- `results_t230/news_cluster_map.csv`, `news_events_freq.csv`, `gold_crash_days.csv`
- `results_t230/recost_news.csv`, `recost_gold.csv`, `recost_summary_*.json`
- `results_t230/raw/forex_factory_cache.csv`, `raw/rf_ecn_*.html`
- `results_t230/market/ticks_*.pkl`, `market/m1_GBPJPY_*.pkl`
- `code/gate_t230_happy.py`, `code/gate_t230_recost.py`, `code/download_t230_market.py`

SHA-256 of this file is written immediately after the final write, in `RESULTS_t230_happy.md.sha256`.
