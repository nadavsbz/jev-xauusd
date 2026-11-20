# RESULTS t203 — JustLookClub 11966799 decode and backtest

**Written:** 2026-11-12, Asia/Jerusalem (IST, UTC+2). Author: Grok.
**Cost screen (first):** `COST_PRESCREEN_20261112_0730_t203.md` (SHA-256 `be3c3212a93822c3148d095d997a8545efacaef6f8754487d23f1ee0d1e326a3`).
**PREREG (hashed before P&L):** `PREREG_20261112_0730_t203.md` SHA-256 `92499b4b5d2b97784e41da80bcd47250f9c16c92f60835466694f5b931ee1abe` (sidecar `.sha256`; asserted in `code/backtest_t203_jlc.py`).
**Code:** `code/backtest_t203_jlc.py` SHA-256 `1b14a9212ffade3f4628d4545399a3104c6e08978ff64aecaad9c2fb20195253`.
**Outputs:** `results_t203/` (`t203_results.json` `016ed2c615e394cfc440b3d780009763fa86df3f977c5d6c615e193a7d5c69a9`, `t203_daily.csv`, `JLC_GOLD_NEWS_1M_trades.csv`). Mkdir only in `main()`, `exist_ok=False`.
**Tags:** OBSERVED = from the scrape; VERIFIED = computed from the scrape or from Dukascopy / calendars; ASSUMED = stated as such.

Frozen method: train 2018–2023, holdout 2024 through last gold M1 bar (2026-10-26). **2026 is in-sample** (the rule was read off this live book). A 2024–2025 slice is reported as a cleaner holdout; it is not a second gate. 2020 is inside the train window and is therefore seen. No Benzaquen work. No file overwritten. No MQL5 (see verdict).

---

## 1. Decode (VERIFIED from `myfxbook/jlc_hist_all.tsv`)

2,629 Buy/Sell trades, 2026-02-02 through 2026-11-12. No pre-2026 history. Profit **€76,417.64** matches the site. Deposit €100k on 28.01.2026. Lots, commission and swap are not in the TSV (site totals: commissions −€11,204.58, interest +€39.89). Account facts given by the parent (OBSERVED): +77% abs, DD 5.74%, PF 1.61, 43% WR.

**Broker time (VERIFIED):** America/New_York **+ 7** (GMT+2 with US DST), same offset as RoboForex. Gold M1 Dukascopy: 590 matchable fills through 2026-10-26, NY+7 in-bar **98.8%**, median error $0; in US/EU DST disagreement weeks NY+7 **98.1%** vs Athens **7.8%**. Function: NY wall = broker − 7h, then `tz_localize("America/New_York")`. So 15:30 broker = **8:30 ET**; 21:00 broker = **14:00 ET**.

### 1.1 By symbol (all close-months)

| Symbol | n | P&L € | WR | PF | med hold | SL set |
|---|---:|---:|---:|---:|---:|---:|
| **XAUUSD** | 646 | **+79,137** | 35.4% | 2.12 | 5.5 m | 81% |
| USDJPY | 391 | +3,790 | — | — | — | 62% |
| USDCAD | 126 | +1,550 | — | — | — | 45% |
| GBPJPY | 29 | +589 | — | — | — | 100% |
| EURUSD | 526 | −3,520 | — | — | — | 25% |
| DJ30 | 209 | −3,125 | — | — | — | 77% |
| NAS100 | 28 | −1,555 | — | — | — | 100% |
| other FX / BTC | — | losers | — | — | — | — |
| **All non-gold** | 1,983 | **−2,719** | — | — | — | — |

Gold is **more than 100%** of account P&L.

Gold by close month (8/10 green; only Oct is a loss): Feb +3,927; Mar +3,445; Apr +427; May +1,365; **Jun +10,465**; Jul +2,438; **Aug +28,024**; **Sep +24,558**; Oct **−649**; Nov +5,136. Without Aug–Sep, gold is still +26,555 and the account +20,748 — gold still carries the rest. Jun is the other large month and is **not** an 8:30 window month (see §1.5).

### 1.2 Monthly account P&L, and February vs later

Close-month totals match the parent: Feb 890 / +3,570; Mar 231 / +5,094; Apr 90 / −2,066; May 127 / +999; Jun 169 / +5,673; Jul 189 / −353; Aug 125 / +27,923; Sep 160 / +27,746; Oct 201 / −276; Nov (to the 12th) 447 / +8,108. **Aug+Sep = €55,670 = 72.8%** of profit. History is 9.5 months.

**February is a different regime.** 890 trades, 11 symbols, SL on only 32%, median hold 79 min. 821 non-gold trades, **−€357**. After February those FX pairs shrink or vanish; DJ30/NAS100 appear May–Jul and Nov and lose; EURUSD stays and loses; USDJPY is choppy (Mar +1,238, Apr −660, Sep +2,571, Nov +1,552). Non-gold after Feb: 1,162 trades, **−€2,362**, not consistent across months. Later trades set SL more often (66%).

### 1.3 Direction, weekday, entry hour, hold time

- **Direction:** Buy 1,395 / +34,827 (43.2% WR); Sell 1,234 / +41,590 (43.3%). Gold: Buy +30,272, Sell +48,865. Both sides contribute.
- **Weekday (entry):** Friday +34,465; Wednesday +32,234; Thursday +10,309; Mon/Tue roughly flat to slightly negative. Classic NFP-Friday / midweek-CPI pattern.
- **Broker entry hour:** hour 15 (8:30 ET window) n=180, **+€53,661 (70% of all profit)**, WR 51%, PF 5.53. Hour 17 +8,291; hour 9 +7,337; hour 21 +3,769; hour 18 +3,448; hour 6 **−4,866**. On-the-hour (:00) 640 trades, +13,598 — not the main story.
- **Hold (all trades):** **≤1 minute: 347 trades, +€78,232** — more than the entire account. 1–15 m +8,058. Everything from 15 m to 24 h is a net **loss**. Gold ≤1 m: 244 / +74,968. The book is a seconds-to-a-minute gold scalp sitting on a losing longer-hold book.

### 1.4 SL / TP in pips (gold pip = 0.01, VERIFIED: a 0.25 price move = 25 pips)

SL set on 54% of all trades, TP on 36%. Gold SL set 81%, TP 54%. Gold SL **mode is 25–26 pips ($0.25)**: 243 of 521 gold trades with an SL (24 of 29 at 8:30). Gold TP mode **6890** (101 trades, ≈ $68.90, a runner). News TP modes 904, 958, 940, 949 (≈ $9). RR when both are set on news is very wide (904/25 ≈ 36R). Index "pips" in the TSV are unreliable (parent warning). Other FX SL modes are messy and often unset (Feb regime).

### 1.5 What drove Aug–Sep — not a "gold trend"

Gold 8:30 ET window (broker 15:25–15:40; 30 trades): **+€57,041**, WR 43%, PF 19.4, median duration **0.04 minutes**, max +€16,396. Tight 15:28–32: 27 trades, +57,863, PF 26.4.

| ET date | Event | n | P&L € | Hold | Notes |
|---|---|---:|---:|---|---|
| 11 Feb | NFP | 1 | +705 | 1 s | |
| 10 Apr | CPI | 2 | −171 | 3 h / 1 s | |
| 15 Jul | ? | 2 | −578 | 4 h 52 m / 0 s | not NFP/CPI/FOMC |
| 29 Jul | FOMC *morning* | 2 | −1,231 | 4 h 43 m / 1 s | 8:30, not 14:00 |
| 30 Jul | ? | 1 | +1,516 | 11 s | |
| **7 Aug** | **NFP** | 2 | **+10,367** | 1 s / 5 s | two buys, SL −25, TP 904 |
| **12 Aug** | **CPI** | 2 | **+4,659** | 1 s / 12 s | both directions |
| 14 Aug | ? | 1 | −83 | 2 s | |
| **26 Aug** | **?** | 1 | **+16,396** | **7 s** | largest trade; event UNKNOWN |
| 28 Aug | ? | 1 | −244 | 3 s | |
| 3 Sep | ? | 2 | +774 | 3 s | |
| **4 Sep** | **NFP** | 3 | **+13,706** | 28 s / 0 s / 1 s | three sells |
| **11 Sep** | **CPI** | 5 | **+7,239** | 0–5 s | straddle; two +€3,812 sells |
| 6 Nov | NFP | 2 | +4,080 | 1 s / 0 s | |
| 10–11 Nov | ? | 3 | −94 | | |

NFP∩8:30: 8 trades, +€28,858, WR 75%, PF 101. CPI∩8:30: 9 trades, +€11,727. NFP-or-CPI∩8:30: 17 / +40,585. 8:30 but not NFP/CPI: 13 / +16,456, **dominated by 26 Aug**. Gold *outside* 8:30: 616 trades, +€22,096, WR 35%, PF **1.33**, Aug rest **−3,071**.

The 8:30 window itself is **not** consistent every month: Feb +705 (1); Mar 0; Apr −171; May 0; Jun 0; Jul −294; **Aug +31,095 (7)**; **Sep +21,720 (10)**; Oct 0; Nov +3,986 (5). JLC traded 8:30 gold on only **4 of 10** NFP days and **3 of 8** CPI days in the account window (missed Mar/Apr/May/Jun/Jul/Oct NFP at 8:30; missed Feb/Mar/May/Jun/Jul CPI). This is a selective (or discretionary) news book, not "every NFP/CPI".

**June gold +10,465 is not 8:30 news.** 52 gold trades. Three short holds dominate: 17 Jun 17:23 broker (10:23 ET, **FOMC day**) buy, 56 s, **+€6,655**; 8 Jun 08:34 sell, 19 s, +2,057; 15 Jun 11:32 buy, 2 m, +1,646. Plus a 5 Jun NFP-day fill at 07:51 ET, +950. Not a clock-hour rule.

**The "consistent" leftover gold is also bombs.** Of the +€22,096 non-8:30 gold, the four trades with |P&L| > €3,000 (17 Jun FOMC-day +6,655; 29 Jul 21:00 / **14:00 ET FOMC** +4,939 in 2 s; 9 Jul 09:00 +4,379 in 14 s; 17 Sep 10:10 +3,204 in 8 m) sum to **+€21,533**. Excluding them: 612 trades, **+€2,920, PF 1.04, WR 35%** — a tight-SL ($0.25) scalp that is essentially flat. Non-8:30 gold is 8/10 months green only because of those spikes (and Aug rest is negative).

### 1.6 Stop vs market vs prior bars (gold, NY+7, Dukascopy mid, through 2026-10-26)

588 matchable gold opens. **Daily S/R is not the story:** buys within $2 of prior UTC-day high 2.8%; sells near prior day low 6.7%. H1 "near" ($1) is 18–22%. Prior M15: only ~6% *near* ($0.50) the exact prior high or low, but **81%** of buys are at or **through** the prior M15 high and 81% of sells at or through the prior M15 low (8:30: **100%**, and 0% inside the prior M15 — as expected for a news spike). This is momentum / market (or a stop already beyond the last M15), **not** a goldA-style daily Donchian and not a tight bracket at the prior M15 high. Same-timestamp clusters: 385 multi-entry stamps, max 7; same time+symbol+dir up to 6 — parallel systems or scale-in, not a classic grid on the open book.

---

## 2. Candidate rules

Only one component is both (a) large and (b) sharp enough to write down. Everything else is DROP (no definition, or a net loser).

**JLC_GOLD_NEWS_1M** (tested; full text in the PREREG):

- Events: every official **NFP** and **CPI** at 8:30 America/New_York (calendars cited in the PREREG). Not FOMC, not "all 8:30s", not a discretionary skip filter. JLC themselves did *not* trade every event; this is a systematic proxy, not a clone.
- Buy-stop at the high of the 8:29 ET M1, sell-stop at its low, on the 8:30 M1. Skip if both sides of the 8:30 bar are touched (no first-touch data; conservative vs a straddle, but see the look-ahead caveat in §4). Gap-through: fill at the 8:30 open. Exit at the 8:30 mid close (~1 minute). No $0.25 SL and no $9 TP (not honest on M1; the TP is a 2026 fit).
- Cost: **$1.50 / oz RT**, every year, no swap. 1 oz raw; 10% vol and train-DD=25% scales frozen on train.

**Not written, not tested:**

- Non-8:30 gold (entry not decoded; residual PF 1.04 after four spikes).
- USDJPY / EURUSD / Feb FX / DJ30 / NAS100 (net losers or inconsistent months).
- FOMC 14:00 (one clear JLC fill; the other FOMC-day winner was at 10:23 ET).
- Other 8:30 releases (26 Aug is UNKNOWN; we do not harvest every 8:30).
- A 5-minute exit cousin (would have been a scan).

---

## 3. Cost screen and contamination

Quiet RF gold 1.64 bp is the wrong cost for an 8:30 print. Train-only (2022–2023) Dukascopy M1 bid-ask, NFP+CPI (VERIFIED): 8:30 close one-way median $0.424 → RT **$0.85**; 8:29 pre-print RT **$1.30**. An M1 close understates the 8:30:00 flash (ASSUMED). Conservative screen cost **$1.50 / oz RT**.

JLC 8:30 window: 30 trades, avg €1,901. Lot inference (ASSUMED) from 7 Aug TP $9.04 / ≈ €5,183.50 → ≈ 573 oz; per-oz average ≈ $3.32; conservative edge **$1.66**. Ratios: $0.85 / $1.66 = **0.51 MARGINAL**; $1.30 / $1.66 = 0.78 and $1.50 / $1.66 = 0.90 would be DROP. Tested as MARGINAL because the brief asked for this family, and the backtest **charges $1.50** so a pass cannot hide behind the M1-close understatement.

---

## 4. Backtest verdict — JLC_GOLD_NEWS_1M

Gates **pass** (g1–g4; g5 is not a gate, name does not start with `G_`, and happens to be true). Last bar 2026-10-26.

| Window | n fill | skip both | WR | mean bp (net) | gross bp | cost bp | Sharpe | raw CAGR | raw max DD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Pre 2015–17 (CPI only; NFP calendar starts 2018) | 23 | 12 | 57% | +3.8 | 16.0 | 12.2 | 1.03 | 0.29% | −0.19% |
| **Train 2018–2023** | **86** | 53 | 73% | **+15.6** | 25.1 | 9.5 | **2.20** | 2.26% | −0.39% |
| Holdout 2024–2026 (**2026 in-sample**) | 35 | 29 | 97% | +40.7 | 45.5 | 4.9 | **2.63** | 5.16% | −0.02% |
| **Holdout 2024–2025 (cleaner)** | **26** | 20 | 96% | **+27.0** | 32.3 | 5.4 | **2.86** | 3.56% | −0.02% |
| Overlap 2018–2026 | — | — | — | — | — | — | **2.28** | 3.18% | −0.39% |

- **g1** holdout Sharpe 2.63 ≥ 0.8 PASS. Cleaner 2024–2025 is also 2.86 — the holdout is **not** only Aug–Sep 2026.
- **g2** corr to C1+I2 `pnl` **−0.015** (C1 −0.025, I2 +0.009) ≤ 0.2 PASS.
- **g3** book holdout Sharpe 1.52 → **3.01** at the 10% train-vol add (scale 9.81) PASS.
- **g4** overlap Sharpe 2.28 ≥ 0.8 PASS.

Raw 1-oz calendar sums by year (all positive 2018–2026): 2018 +1.38%; 2019 +0.59%; 2020 +0.68%; 2021 +3.19%; 2022 +5.10%; 2023 +2.67%; 2024 +4.34%; 2025 +2.78%; 2026 +7.45%. Pre-sample is weaker (2016 almost flat: 7 fills, WR 43%, +0.1 bp net) — $1.50 was a large fraction of the then-smaller news range. The dollar edge in train is +$234 / 86 fills ≈ $2.73/oz net after $1.50 ($363 gross, $129 cost), in the same ballpark as the JLC per-oz inference.

**High-return profile** (scales frozen on train; 2020 is seen):

| Scale | Train %/mo, DD | HO 2024–26 %/mo, DD | HO 2024–25 %/mo, DD |
|---|---|---|---|
| 10% train vol (×9.81) | 1.84%, −3.78% | 4.17%, −0.22% | **2.89%, −0.22%** |
| Train DD = 25% (×**64.3**) | 12.6%, −23.6% | 29.6%, −1.45% | 19.8%, −1.45% |
| Raw 1 oz | 0.19%, −0.39% | 0.42%, −0.02% | 0.29%, −0.02% |

The brief's **≥5%/month at ≤25% annual DD, at a reasonable size**, is **not** met at 10% vol (2.89% clean, 4.17% contaminated). The ×64 scale that puts train DD at 25% is **not a reasonable size** for a one-minute news fill (a single worse-than-train print would blow the 25% cap; train worst month at that scale is already −15.4%, 2018-07). No MQL5.

**Two caveats that sit above the gate numbers:**

1. **Skip-if-both uses the whole 8:30 bar.** If a buy-stop fills at 8:30:01 and the low later takes out L_prev, a live order is already in; the backtest *cancels* the trade. 53 of 144 train events and 29 of 65 holdout events are skipped this way (2024: 14 skips vs 10 fills). This is the same convention as t202 NR7, frozen in the PREREG, and it has no first-touch look-ahead *inside* a fill — but it **selects one-sided news bars**, which is where a 73–97% WR comes from. A first-touch / tick rule was not tested (no tuning). This is the main methodological risk.
2. **Fill at exact H_prev / L_prev is optimistic at the print.** 9 of 144 fills are open-gaps (modelled). The rest assume a fill at the stop with only the $1.50 RT. Real 8:30:00 gold often jumps through the stop. M1 cannot settle this. Holdout WR 97% (one loser: 15 Jul 2025, a cost scratch) is a **small-sample flag** (35 fills), even though 2024–2025 is also 96%.

2026 systematic fills (contaminated, for information): the proxy is long on 7 Aug NFP and short on 4 Sep NFP — the same direction as JLC — and also takes several NFP/CPI days JLC skipped (6 Mar, 10 Jun, 2 Jul, 14 Jul, 2 Oct), all winners under this fill. It does **not** take 26 Aug (not NFP/CPI) and skips two-sided bars (likely including some JLC CPI straddles). It is a cousin, not a clone.

---

## 5. Honest assessment

**JustLookClub's headline +77% / 6%/month / 5.74% DD is a lucky Aug–Sep news book, not a reproducible 6% machine.** Gold is more than the entire profit; ~70% of the account is thirty gold fills around 8:30 ET, most of them seconds long, and the bulk of *those* is four prints in Aug–Sep (7 Aug NFP, 12 Aug CPI, **26 Aug unknown**, 4 Sep NFP) plus 11 Sep CPI. JLC skipped most NFP/CPI days at 8:30. The leftover gold "grind" (PF 1.33, 8/10 months green) collapses to PF 1.04 once four more spikes are removed. Non-gold loses money. February is a high-turnover FX regime that did not pay. The history is 9.5 months with no pre-2026 data. That is the decode.

**Separately:** a *systematic* NFP/CPI 8:29-range break, flattened at the 8:30 close, charged a conservative $1.50/oz, **does** show a train (2018–2023) Sharpe 2.20 and a **2024–2025** Sharpe 2.86, all raw years 2018–2026 green, corr to C1+I2 ≈ 0, book lift at 10% vol. That is a real, frozen, pre-registered result, and it is **not** "only Aug–Sep 2026". It is also **not** evidence that JLC's 6% will repeat: 10% vol delivers about **3%/month** on the clean holdout (4% if one trusts 2026), well below JLC's headline and below the 5%/25% brief, and the result still depends on (i) skipping two-sided bars with end-of-minute information and (ii) getting filled near the 8:29 high/low at the news print. Those are execution questions for a tick tape, not for another M1 parameter scan.

**Verdict:** 1/1 name **passes the Sharpe gates**, **fails the high-return size bar** at a reasonable scale, **no MQL5**. JLC-as-advertised was a lucky Aug–Sep (plus a handful of other gold bombs). The news-momentum *proxy* is interesting and cleaner than the live book, but it is not a ready 5%/month system.
