# RESULTS_t205 — grids allowed, non-gold ranging-cross scan

Round t205. Authorization `[pt206u]`: Nadav is not worried about grids
(he already runs Black Dragon, a gold grid). Each name is judged alone
(no portfolio mix). Public access only. Equity DD, not balance DD.
Unique t205 files; t202–t204 were not overwritten.

## Verdict (one paragraph)

No public live book on a non-gold ranging cross is both (a) 24+ months
with honest Abs. Gain at the 4–5%/month target and (b) a decodable
mechanic with a tolerable equity tail. **Carla Mt4** is the only book
that clearly hits **4.65% Abs / month** on AUDCAD/NZDCAD over 45 months
with a published DD of 26.59% and a small Gain–Abs gap, but its history
is **private** — step, multiplier, max levels and basket TP are UNKNOWN,
and the book started in January 2023, so it never lived through 2020 or
2022. **NoPain** (ToTheMoon, AUDCAD only, ~5 years) is the longest
honest public track; Abs is only **~2.3%/month**, Myfxbook DD is
**48.22%**, and Gain +2,236% vs Abs +403% is badly distorted. **HWRLFSL**
is a messy multi-symbol averager **including gold**, Abs **1.88%/month**,
below target. **AGM Accumulation** (equity DD **65.55%**) and **News
Catcher Pro** (2.4%/month, equity DD **53%**) fail the tail/return
filters. A frozen textbook proxy of the public ToTheMoon mechanic
(`AUDCAD_ENV_GRID_T205`, Envelopes + 20-pip step + 1.3× gradual lots +
12-pip basket TP, RF Prime spread + commission + swap, M15 2018–2026)
makes **~1.97%/month** only on a path that **goes insolvent**: max
**equity DD −244%**, equity trough **−$19,350** on 19 Mar 2020 (03:45
IST) after a **2,021-pip** AUDCAD decline from the 16 Mar 2018 peak,
and an RF-style 30% diagnostic stop would have closed the book on
**6 Apr 2018, 00:45 IST** at about **$6,664** (−33% from $10k). Every
closed basket in the test is a winner (6,174/6,174) — that is the grid
reporting trap; the losses sit in floating equity. At a size that
would have kept the 2020 equity DD to 25%, expected return shrinks to
roughly **0.2%/month**, far under 4–5%. **No MQL5 spec.** Do not
deploy this proxy. Carla remains the best *live number* and is still
not a buildable rule.

## Candidate table

Ages and Abs monthly are as of 12 Nov 2026 (Asia/Jerusalem, UTC+2).
Abs %/mo is compound on Abs. Gain / deposits, not the site "Monthly"
figure (that follows Gain and is inflated by withdrawals).

| Book | Months | Symbols | Gain vs Abs | Honest Abs %/mo | Stated / equity DD | Swap (Interest) | Mechanic (see below) | BD-type overlap | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **Carla Mt4** (Angeloscotto, [11509126](https://www.myfxbook.com/members/Angeloscotto/carla-mt4/11509126)) | 45.5 (joined 26 Jan 2023) | AUDCAD, NZDCAD, USDCAD | Gain +760% vs Abs **+662%** (small gap, OK) | **4.65%** (hits the 4–5% target) | DD **26.59%**; equity 100% at snapshot; history private so worst floating episode is UNKNOWN | UNKNOWN (fields empty) | Grid/averaging; basket closes 0–2 s; avg win 13.88 pips, avg loss −25.70, hold 23h57, WR ~67%, Z −3.43, 2,096 trades. Exact step / martin / max / TP **UNKNOWN** | Started after 2020 and after the Jan 2022 AUDCAD trend. 2025 was huge (~+122%); 2026 is slower (+70.78% YTD, −51.53 pp vs last year). Jul 13–16 2026 8-trade loss is a small closed streak, not a full floating episode | **Best live Abs on non-gold crosses.** Cannot decode. Missed the two worst AUDCAD-trend years. Not a PREREG. |
| **NoPain MT5** (tec_daniel / ToTheMoon, [11204017](https://www.myfxbook.com/members/tec_daniel/nopain-mt5/11204017); MQL5 [2262642](https://www.mql5.com/en/signals/2262642)) | Analytics years **2021–2026** (~70 mo). MQL5 "Started 2024-10-16" / 263 weeks is incomplete history (author admits) | **AUDCAD only** | Gain **+2,236%** vs Abs **+403%** (FAIL: withdrawals $3,850 on $1,000 deposits) | **~2.32%** over 70 mo; site "Monthly 5.27%" is Gain. Author "seeking around 3%" | Myfxbook DD **48.22%** (use this). MQL5 equity DD 20.63% / balance 6.89% is a short loaded window | **−$286 / $4,019 = 7.1%** of profit | Public ToTheMoon: Envelopes entry, fixed grid, gradual lots (not doubling), dual books, partial close as "smart SL", no hard SL, AUDCAD M5, $1,200 / 1:100, 20% *backtest* DD projection. Live: avg win 11.98 pips, avg loss −33.97, hold 1d, WR 64%, PF 1.70, Z +28.50, 5,900 trades, lifetime **pips −26,058** with $ profit (classic grid). Worst closed trade −404.9 pips (7 Apr, year UNKNOWN). Exact `.set` numbers not extracted (public Drive is a JS folder) | Jun 14–15 2022 closed streak is tiny (−$21). The 48% DD date is UNKNOWN from the public page (monthly tabs did not expand). Live book **missed 2020** | **Longest honest AUDCAD grid.** Abs below 4–5%. Live DD 48% is already above a 25% comfort line and more than 2× the author's 20% projection. Family used as the decoded mechanic. |
| **UpEverest MT5** (same author, [11764009](https://www.myfxbook.com/members/tec_daniel/upeverest-mt5/11764009)) | **2025–2026 only** (<24 mo) | AUDCAD | small book ($264 profit / $350 dep) | site 4.03% (short, Gain-like) | 14.30% | −$22 / $264 = **8.3%** | Same as NoStress at 1.5× size; $400 min, "seeking 6%" | Too short | **FAIL age.** Same family, not a second independent track. |
| **UpFuji** (MQL5 2308095) | Short / incomplete | AUDCAD | — | author "seeking 6%" | author: same as NoPain at half balance, **2× profit and 2× DD**; reviewer "grid with doubling down" | — | Same NoPain preset, 2× risk, $600 / 1:200 | — | **FAIL** as a diversifier from NoPain (identical rule, higher size). |
| **HWRLFSL** (jincheonbrin, [11390837](https://www.myfxbook.com/members/jincheonbrin/hwrlfsl/11390837); IC, $3,823) | ~25 mo (Oct 2023) | Sample (52 trades, 4 Sep–5 Oct 2026 only, not the full 900): EURNZD 20, AUDJPY 13, USDCHF 13, **XAUUSD 4**, GBPNZD, GBPUSD. Public "Best Symbol" is **XAUUSD in every session** | Profit $1,716 / deposits $2,880 ⇒ Abs **+59.6%**. Site monthly 2.66% is Gain | **1.88%** | DD **16.79%**; equity 100% at snapshot. Worst closed streak 9–14 Oct 2024, −$58.99 (8 trades) | **−$35.52 / $1,716 = 2.1%** (modest). Commissions −$192, PF 5.34, Z −8.26, hold 14h28, WR 79%/70% | Averaging baskets, **not a single ladder**: EURNZD Oct 2–5 sells, irregular steps 15/6/9/7/7/19 pips, several lots at the *same* time and price (parallel systems or scale-in), lots 0.01–0.09 not a clean 1.5×. AUDJPY Sep 25–28: steps ~4–7 pips, lots ×**1.25–1.3**, then a stack at the last levels, held ~2 days, +$78–94 | Gold is in the book and is the advertised best symbol — **crash days can coincide with BD**. Oct 2024 closed streak is small vs account | **FAIL return, FAIL clean mechanic, weak diversifier (gold).** EURNZD short swap at RF is cheap (−0.2 pip/night) — that part is well chosen, but it is not the whole book. |
| **AGM Accumulation** (MQL5 [1081311](https://www.mql5.com/en/signals/1081311)) | Started 12 Jul 2021, 286 weeks, genuine age | AUDCAD / NZDCAD / AUDNZD cluster (some gold in the wider family) | MQL5 Growth +1,438% (not Abs; deposits UNKNOWN) | ~4.2–4.4% on Growth if deposits are zero — **not verified Abs** | **Equity DD 65.55%** vs balance 24.69–47.91%. High current-DD warnings | UNKNOWN | Multi-pair accumulation/averaging, 9,907 trades, 18h hold, PF 1.33 | Multi-pair including a gold component is a plus-risk vs BD, not a hedge | **FAIL tail.** Equity DD 65% is disqualifying even if Growth looks like 4%+/mo. |
| **News Catcher Pro** (MQL5 [1845908](https://www.mql5.com/en/signals/1845908)) | Started 30 Jan 2023, ~45 mo | EURUSD / GBPUSD / EURGBP news baskets | +190% Growth | **~2.4%/mo** | **Equity DD 52.58%** vs balance 17%, WR 94% | — | News-event basket, not a ranging-cross grid. Last trade 17 days ago at last look | EUR majors on news days, not AUDCAD; not designed as a BD diversifier | **FAIL return and equity DD.** |
| **ToTheMoon MinorForce / EasyGoal** (author site, not a long public book) | presets only | MinorForce: AUDCAD+AUDNZD+NZDCAD, "seeking 5%", 40% BT DD; EasyGoal: AUDCAD+EURUSD, same | — | unverified | 40% *projection* | — | Multi-symbol grid, profits of one pair cover another — **correlated CAD-cross basket**, a joint crash is possible | CAD-crosses move together | Not a live 24-month Abs track. 40% projected DD already above 25%. |
| Prior t204 leftovers (ares, Calicut, R Factor, Ferrari, Gold Trade Pro, fn-capital, Darwinex) | — | MNQ / stocks / gold scalpers | Ferrari Gain +7,272% vs Abs +763%; others as in `RESULTS_t204.md` | ares 2.35%, Calicut 3.66% (top-3 55%), Ferrari Abs 2.38%, Darwinex ~1.9% ceiling | ares 14.1% (not a grid); Ferrari distorted | — | Not the t205 non-gold-grid question. t204 already failed them on Abs, concentration, or style | — | Unchanged. Not re-tested. |

## Mechanics, RF cost / swap, and BD-type correlation

### ToTheMoon / NoPain / Carla family (AUDCAD)

**Public mechanic (VERIFIED from tothemoonrobot.com/strategies, author
text):** Envelopes signal — buy when price is below the lower band,
sell above the upper. If the trade goes against, add at **fixed
intervals**, sometimes with a **timer** so a spike does not fill every
level at once. Lots **increase gradually** (author: "safer than
martingale doubling"). Independent buy and sell books. Profitable
tickets **partially close** losing ones ("smart SL"); if DD is high the
EA **lowers TP** to exit faster; a "RECOVERY" mode exists in v3.4.
**No hard SL** on the standard NoPain preset (a "NoPain 30Stop" variant
adds a 30% equity stop). Preferred symbol AUDCAD M5, "fluctuates little
and quickly returns to the average"; the author explicitly warns off
gold, Bitcoin and indices. xPRESET scales 0.01 lots per $1,200 (NoPain)
or $600 (UpFuji, 2×).

**Exact numeric step, TP, max levels, Envelopes period, partial-close
Divisor** are in a public Google Drive folder
(`https://drive.google.com/drive/folders/1cBglLYKxyyptYT_dnJhlxNy69MDC4Nsr`)
that this run could list at folder level (MT4/MT5 v3.6, 13 May) but
could not extract `.set` IDs from without a JS session (no login).
Carla's last-200 is private.

**Live-book averages (VERIFIED):** basket-shaped avg win **12–14 pips**,
avg loss **19–34 pips**, hold **~1 day**, WR 64–84%.

**RF Prime AUDCAD swap (VERIFIED, roboforex.com, this run):** spread 0.9
pips, commission $10/mio/side, swap **long +0.15 pip / short −0.9 pip**,
Wednesday ×3. 1 pip on 1.00 lot ≈ 10 CAD ≈ **$7.30**. A 3-day short
basket that includes a Wednesday is **5 night-units × $6.57 ≈ $33**,
which is **~37% of a 12-pip win** on the same lot. Long baskets are
cheap or a small credit. This is an **asymmetric** cost: a stuck short
inventory is much more expensive than a stuck long. Live NoPain Interest
is already **7% of profit**; UpEverest **8%**. pr42 BD-on-AUDCAD
(OBSERVED, different EA, not this PREREG) paid **−$1,906**, ~11% of
pre-swap profit, 2022–Oct 2026.

### HWRLFSL

Not one rule. Irregular EURNZD and AUDJPY averaging plus USDCHF noise
plus **gold scalps** (one 1.01-lot 6-minute XAUUSD +$26). RF EURNZD
short swap is only **−0.2 pip** (cheap; the Oct 2026 sample was selling
EURNZD for ~2.5 days — good swap design for that basket). Long EURNZD
is −0.85. Interest on the whole account is only 2% of profit because
many holds are intra-day and gold scalps do not sit overnight. Cannot
freeze a tidy 8-pip 1.3× EURNZD rule from two baskets.

### AGM / News Catcher

AGM: multi-pair AUD-cross accumulation, 65% equity DD, 18h holds — a
deeper, broader version of the same tail. News Catcher: 94% WR news
baskets on EUR majors, 53% equity DD, 2.4%/month — different family,
still fails the brief.

### Correlation with BD-type gold-trend periods

Official BD daily (`daily_official_baseline.csv`) only covers
**15 Apr–2 Nov 2026**, six accounts. On that short window the t205
proxy's daily corr vs BD is **0.025**, monthly **0.27** (n ≈ 7 months) —
not a useful sample. Gold monthly returns 2018–2026 (Dukascopy) vs the
proxy: corr **−0.06**, vs |gold| **+0.09**. Directionally almost
uncorrelated, which is what we wanted from a non-gold cross.

The **tail** is the exception that matters. The proxy's worst equity
episode troughs on **19 Mar 2020**, in the same COVID risk-off week that
gold spiked and a gold grid is also in trouble. Mechanism is different
(AUDCAD fell **2,021 pips** from the 2018 peak, about **400 pips** in
March 2020 alone; gold trended the other way) but the **calendar
overlap of the crash month is real**. A non-gold cross does **not**
automatically move the crash day off BD's calendar. 2022's trough is
**28 Jan 2022** (15:30 IST), **before** the 24 Feb Ukraine gold spike —
that episode is a separate AUDCAD trend (−1,064 pips from Feb 2021),
and it recovered only on **9 Dec 2022**. Live Carla / NoPain books that
started in 2021–2023 **never saw 2020** and, in Carla's case, started
just after the 2022 recovery.

## Cost screen (written before this P&L)

File: `COST_PRESCREEN_20261112_0800_t205.md`
SHA-256 `4e00c546d955f3a3d444dc8dfac7ec52dcbf2000f65a759479a7706853b7ef5d`.

Verdict **MARGINAL**. A same-day 12-pip basket at RF Prime has a
conservative-edge ratio ≈ 0.18 (PASS); a one-night short ≈ 0.33 (PASS
at the 1/3 line); a 3-day Wednesday-inclusive short ≈ **0.93 (DROP)**.
Deep grids live in that third regime. The family was still tested
because t205 asked for it, with all three costs charged.

## Pre-registered specification

File: `PREREG_20261112_0800_t205.md`
SHA-256 `196d99db1b111f4e1d854abadf7ba83a342f53b77a0bb560cd5cd80432535833`
(asserted before any P&L of this spec).

**AUDCAD_ENV_GRID_T205** is a *textbook proxy* of the public ToTheMoon
description plus live-book averages. It is **not** a NoPain, Carla, or
Black Dragon clone. Partial close, "lower TP when DD is high", and
RECOVERY mode are **omitted** (those rules are in the unpublished
`.set`); omitting them is conservative for floating equity DD. It
does **not** use the pr42 BD-AUDCAD inputs
(Fix_Distance=220, Martin_=1.4, TP_=150, MaxOrders=12, Overlap) whose
P&L was already seen in this exploration.

Frozen in short: synthetic AUDCAD = AUDUSD × USDCAD Dukascopy M15 mid;
Envelopes(20, 0.10%); 20.0-pip step; 1-hour (4-bar) timer; max 10
levels; lot multiplier 1.30, `LOT0=0.08` on $10,000 (NoPain
0.01-per-$1,200, constant, no compounding); 12.0-pip VWAP basket TP;
dual independent sides; no hard SL; RF Prime 0.9-pip spread, $10/mio
per side, swap +0.15 / −0.9, Wednesday ×3 at 21:00 UTC; equity marked
every M15 including intra-bar extremes; train 2018–2023 / holdout
2024–2026; one specification, no search.

## Backtest results

Engine: `code/backtest_t205_fast.py` (Numba translation of the same
rules in `code/backtest_t205.py`; the pure-Python loop was too slow and
was stopped before it wrote any P&L). Outputs in `results_t205/`.
Primary size: 0.08 lots / $10,000, 1 Jan 2018–10 Nov 2026.

### Headline (primary size)

| Quantity | Value |
|---|---|
| End equity (10 Nov 2026) | **$81,086** on $10,000 (open float **−$7,330**, a maxed 3.409-lot **long** still open) |
| Compound monthly, all / train / holdout | **1.974% / 1.995% / 1.931%** (stable across the split — not a holdout collapse) |
| Closed baskets | 6,174 (6,119 at TP, 55 at a TP gap). **6,174 / 6,174 closed P&amp;L > 0.** Mean +$11.16. This is the grid trap: you only close at TP. |
| Side mix of *closes* | 6,014 short, 160 long. Shorts exit quickly in a long-term AUDCAD downtrend; **longs get stuck**. |
| Swap (RF Prime, charged) | **+$10,070** (a *credit*, 14% of net). Stuck inventory is long, and long AUDCAD swap is +0.15 pip. If the 2,000-pip trend had gone the other way, shorts would have paid **−0.9 pip** (~6×) and swap would have deepened the hole. |
| Commission | −$1,103 |
| **Max equity DD (M15 intra-bar)** | **−243.7%**. Peak $13,466 on **16 Mar 2018, 13:00 IST**; trough **−$19,350** on **19 Mar 2020, 03:45 IST**; recovered **2 Jun 2020, 19:00 IST**. AUDCAD **1.01685 → 0.81475 (−2,021 pips)** over that window. Both sides hit the 10-level cap (3.409 lots). Swap over the window **+$2,081** (long credit, irrelevant against a $32,815 equity hole). |
| RF 30% diagnostic | **Breached 6 Apr 2018, 00:45 IST**, equity min **$6,664** (already a 10-level long, AUDCAD 1.017 → 0.979). 50% diagnostic 30 Apr 2018, 15:30 IST. Equity went **non-positive**. A real RF Prime account at 30% stop-out would have been **closed in April 2018 at about −33%**. The subsequent climb to $81k is a **zombie path** no live account would have been allowed to keep. |
| Baskets that reached 10 levels and *did* close | 6 closes, +$1,738. The ones that do **not** close are the story. |

Year-end *equity* (dollars, not the distorted percent that goes through
zero): 2018 **$8,577** (min in the year **−$7,608**); 2019 **$874**
(min **−$6,998**); 2020 **$31,443** (min **−$19,350**, then a bounce);
2021 **$22,239**; 2022 **$37,862**; 2023 **$41,516**; 2024 **$47,082**;
2025 **$59,884**; 2026-11-10 **$81,086**. Percent returns for 2019
(−90%) and 2020 (+3,499%) are **not meaningful** — they are arithmetic
across a zero crossing. Do not quote them as performance.

### 2020 and 2022 episodes (required)

**2020 (worst of the whole sample).** This is one continuous
drawdown that *starts in 2018*, not a March-only event. After a fast
+34% into mid-March 2018 the long book maxes (20 Mar–21 Mar 2018) and
never gets a 12-pip VWAP exit while AUDCAD trends from ~1.02 toward
0.81. A 10-level 20-pip grid only spans **200 pips**; the market ran
**2,000**. Equity is already negative in 2018–2019 and prints the low
on **19 Mar 2020, 03:45 IST** (−$19,350), in the COVID AUD collapse
(March 2020 alone: AUDCAD 0.873 → 0.831, intra-month low 0.831, ~400
pips, on a book that was already maxed from 2018). Recovery on the
June 2020 bounce (AUDCAD back to 0.929). **Same calendar month as a
canonical gold-trend crash**, different pair, same risk-off week.

**2022.** Peak **25 Feb 2021, 10:45 IST**, $38,008; trough **28 Jan
2022, 15:30 IST**, $15,100 (**−60.3%**); recovered **9 Dec 2022, 17:45
IST** — an **11-month** hole. AUDCAD 0.999 → 0.893 (**−1,064 pips**).
Max long 3.409 (capped), shorts smaller. Swap +$1,255 to the trough,
+$2,410 to recovery. This trough is **a month before** the 24 Feb 2022
Ukraine gold spike: a distinct AUDCAD trend, not a gold-day copy, but
it is still a 60% equity event that live Carla (start Jan 2023) never
saw. 2021's own trough (3 Dec 2021, −57%) is the first half of the
same episode.

Other years, for context (depth of the worst trough that falls in
that year, vs the running peak, M15): 2018 −156%; 2019 −152%; 2023
**−40.2%** (peak 26 Jan 2023 — Carla's join date — trough 27 Sep 2023,
recover 16 May 2024, −972 pips); 2024 −26.2%; 2025 −31.1% (1 Oct 2024
→ 6 Apr 2025, recover 1 Sep 2025, −862 pips); 2026 −9.5% (22 Sep 2026
→ 6 Nov 2026, **not yet recovered** at the sample end, −331 pips,
which is the open −$7,330 basket).

### Holdout, gates, and the 5%/25% brief

Holdout 2024–2026 is the "Carla era": compound **1.93%/month**, EOD
equity DD **−31.0%** (peak 30 Sep 2024 $54,499, trough 6 Apr 2025
$37,624, recover 1 Sep 2025), calendar Sharpe **1.01**, vol ~27%,
CAGR 26%. Monthly in this window sits roughly in −10%…+14% (worst
Jan 2024 −10.3%; best Jan 2026 +14.1%). This is the same shape as the
live NoPain/Carla numbers, and it is **still under 4–5% and over 25%
DD**.

Frozen gates at primary size:

- **g1** holdout Sharpe ≥ 0.8: **1.01, formal PASS.** This is
  misleading. The holdout simply does not contain 2018–2020. The
  strategy is not tradable at this size on a live RF account.
- **g2** corr vs C1+I2 book: **0.032, PASS.**
- **g3** 10% train-vol add: book HO Sharpe 1.554 → 1.557, formal PASS
  at a scale of **0.00153**. Train vol is **65** because equity crossed
  zero; the 10% vol scale is almost nothing, and the "raise" is a
  rounding artefact. Not a real book contribution.
- **g4** overlap Sharpe ≥ 0.8: **−0.36, FAIL.**
- **g5** N/A (name does not start with `G_`).

High-return size, scales frozen on train:

- **10% train vol:** scale 0.00153. Monthly ≈ 0%. FAIL.
- **Train equity-DD = 25%:** raw train DD is 244%, so scale ≈ **0.102**.
  Linear shrink of the *dollar* path (do not scale daily *returns* —
  those explode through zero) gives about **1.97% × 0.102 ≈ 0.20%/month**
  at a ~25–32% equity DD. **FAIL 5%/25% by a wide margin.**
- In the Carla live window (26 Jan 2023–10 Nov 2026) this *same*
  un-resized proxy did **1.30%/month** with **38.5%** equity DD — worse
  return than Carla's 4.65%/26.6%, similar DD order. In a 2021-start
  (NoPain) window: 1.33%/month, **60%** DD, vs live NoPain 2.3%/48%.
  The proxy is a harsher cousin (no partial close); the live books are
  not a different species.

### What this does *not* say

It does **not** refute the already-run pr42 Black Dragon-on-AUDCAD job
(OBSERVED, different EA: hedge, overlap, Fix_Distance=220, Martin 1.4,
TP 150). That job's 2022–Oct 2026 report was net +$15,323 on $10k,
equity DD 24.11%, balance DD 4.36%, swap −$1,906, and its 2018–2021
OOS years were also green in that lab file. Those inputs were
**not** this PREREG. BD's hedge/overlap/dynamic-distance rules can
behave differently in a 2,000-pip trend; this report does not re-run
them.

## Files (all unique t205, no overwrites)

| File | SHA-256 | Bytes |
|---|---|---|
| `COST_PRESCREEN_20261112_0800_t205.md` | `4e00c546d955f3a3d444dc8dfac7ec52dcbf2000f65a759479a7706853b7ef5d` | 5,306 |
| `PREREG_20261112_0800_t205.md` | `196d99db1b111f4e1d854abadf7ba83a342f53b77a0bb560cd5cd80432535833` | 6,967 |
| `code/backtest_t205.py` (slow Python engine; no P&amp;L written) | `ec0344cbc487d4f7fc4d090d83dfc41f58c4ecb146c3f7d979954393b4c69a34` | 31,206 |
| `code/backtest_t205_fast.py` (Numba, produced the results) | `3a8cdbed3cdf34cba9e6ebc9aac6746a97e7b4a09039f6650031febfc1eccce8` | 20,832 |
| `results_t205/t205_results.json` | `7c59f2863579d0ae637a36838a9710c62ec17d844d85d2d777f57991fdb2bde9` | 22,475 |
| `results_t205/t205_daily.csv` | `4f88efab699c4041a4b6a3a46cd758475001d9de42aa0c6992ca3afaa8e9469a` | 360,300 |
| `results_t205/t205_monthly.csv` | `383deb03a25d0e8feb399580207362b524d7f86b6e1b1ee00a5750e2a5511778` | 7,391 |
| `results_t205/t205_trades.csv` | `9b551fefb7e421097170c8c51e78bd4c5fa9862e7769b6252773bbd258b8a74d` | 578,897 |
| `shortlist_t205.md` | `9f91fc9bf8a521424d5397faa469f89ef5d266b2c125e054309754f695ca9aa9` | 3,016 |
| `RESULTS_t205.md` | this file | |

## Bottom line

Grids on AUDCAD-type crosses are a real family, Nadav is right that
they are in-scope, and the **live** 4–5% Abs number (Carla) is
attractive. The honest long book (NoPain) is closer to **2–3%/month
at 48% equity DD**, and a frozen, costed, 2018–2026 backtest of the
public mechanic **does not survive 2020** at a size that produces
those monthly returns. A 30% RF stop would have ended the primary-size
test in **April 2018**. Sizing down to a 25% 2020 DD leaves ~**0.2%/month**.
The 2020 trough shares a calendar with a gold-trend crash month, so
"non-gold symbol" is not by itself a crash-day hedge vs BD. **No MQL5,
no deploy, no second parameter search.** If Carla's history is ever
made public, or a NoPain `.set` is read from the public Drive in a
browser session, that exact rule can be a new PREREG — not a retune of
this one.
