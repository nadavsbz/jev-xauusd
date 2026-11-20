# BD_CRASH_SURVEY: BD crash-day containment (axis 3): the 17.11.2026 event and a survey of grid/martingale protections
Prepared by Grok for Claude (request "ציר 3", claude_outbox 17.11.2026 22:50). Compiled 17.11.2026 ~23:20 Asia/Jerusalem.
Public sources only. No sign-ups, logins, purchases or cost. Read-only on Benzaquen (I read `docs/BD_CLONE.md`, `docs/BD_EVERYYEAR_PLAN.md`, `docs/SCAN_PLAN.md`, `docs/HANDOFF.md` and the frozen `bd_v7_d24ntop_20261026` folder so I wouldn't re-propose rules you've already killed). Nothing on the demo or live terminals was touched.
**Tags:** **[V]** VERIFIED = I read the primary source or computed it from raw data myself. **[S]** = secondary source, or the author's own model or claim (in-sample, not independently checked). **[U]** = UNVERIFIED (anecdote, marketing, or absence of evidence). "(arith)" = my own arithmetic.
**Exploratory** = my own quick computations on free data. These were NOT pre-registered and are NOT tests of BD. They only inform which rule to pre-register.

> Nothing here changes BD's logic or live settings. Both recommended rules are candidates for a pre-registered dev + holdout test on the clone (v7 d24ntop) only.

---
## 0. Bottom line
1. **The premise needs a correction: Retail Sales did not cause the ladder.** The release (13:30 UTC = 15:30 Israel = 15:30 RF server) produced a fast drop: 3857.04 → 3836.66 by 13:40 UTC, −$20.4 in 10 minutes [V, Dukascopy ticks]. That drop was **fully retraced by about 14:05 UTC**. Gold then spiked +$35 to **3890.69 at 15:43 UTC (17:43 server)** on reports of US strikes on Qeshm [S, FXStreet/Euronews]. The ladder came on the **slow unwind of that spike**: 3890.69 → 3854.44 by 18:55 UTC (−$36.25 in about 3h12m) [V].
2. **There was no early velocity signal before or during the ladder.** In each 15/30/60-minute window during the ladder, the move sat between the 11th and 41st percentile of all 2026 windows. That is ordinary (§1.3) [V, exploratory]. The clone's own `G_Crash` score (15 M1 bars, ×3.0) peaked at 2.91 at the Retail Sales minute and **never fired on 17.11** [V, exploratory]. The only abnormal thing that day (Retail Sales, 90th percentile of 13:30 UTC impulses) was over before the ladder began, and the d24ntop news pause (15:00–16:30 server) already covers that window.
3. **Why speed rules don't fit BD:** the clone's own measured rule `OneAddPerBar` means **L4 takes at least 45 minutes and L6 at least 75 minutes** after L1. In 2025–26 the $3 step is smaller than a typical M15 bar (median M15 range $4.45 in 2025 and $8.43 in 2026), so depth builds **by time in a drift, not by speed**. On a simplified BD-like ladder (2018–10/2026, exploratory), **ladder speed carried no information about going deep**: P(reaching L8 | reached L4) was 0.11–0.15 in every speed bin, and P(L8 | L6) was 0.35–0.46 in every speed quartile (§3.2).
4. **The public evidence base is weak.** I found **no** protection mechanism for grid/martingale EAs with real out-of-sample or forward evidence in a peer-reviewed source. What exists is theory (ruin is certain eventually: Taranto & Khan), in-sample ablations (GTSbot), vendor models on Dukascopy ticks (Midas Grid, in-sample 2025–26), and vendor docs with no evidence. Your own clone has already killed most of the families (G_Crash, bstop5/8/10, news alone, depth hedge, spread regime r90, TA gate) (§2.2).
5. **Recommendation (§4):**
   - **R1 (primary): a volatility-normalized minimum step,** `dist_k = max(BD_dist_k, c × Ref5)`, with c = 1.5, where Ref5 is the median M15 range of the previous 5 days.
   - **R2 (secondary, lower prior): depth-dependent time spacing,** where level k+1 for k ≥ 5 needs at least (k − 3) completed M15 bars since the last add.
   - Neither rule loosens a gate. Both only remove adds.
   - **Evidence level:** R1 has the best theory behind it (volatility clustering is VERIFIED academically; vol-scaling *returns* is not robust out of sample) plus [S] vendor-model support. R2 has only in-sample [S] support. Exploratory runs on my crude model point the right way for R1 in 2023–26 (cuts −27%, L8+ baskets −66% at F=300) and show little effect in 2018–22, as expected because the step was already larger than σ then.

---
## 1. 17.11.2026: what moved gold, and when
### 1.1 Time assumption
- **RoboForex server = GMT+2 on 17.11** (EET winter time; US and EU are both on standard time). On that day it **equals Israel time** (UTC+2).
- **Evidence:** the clone's own `news_top_rf.txt` (RF server clock, read-only) lists **2026-11-17 15:30**, which is Retail Sales at 13:30 UTC. So Nadav's "17:00–20:00 server" = 15:00–18:00 UTC = 17:00–20:00 Israel.
- If the server were GMT+3, the window would be 14:00–17:00 UTC. That fits a "$22 fall" much worse, because gold mostly rose then (§1.2).

### 1.2 Timeline (UTC / server = Israel). Prices are Dukascopy XAUUSD bid [V] unless marked
| UTC | Server/IL | Event | Gold |
|---|---|---|---|
| Mon 16.11 | | 13-month low near $3,830, about five sessions after a ~$4,150 high on 9.11 [S FXStreet]. Context: 10y UST ~5%+, DXY at a 19-month high, a December Fed **hike** ~91–97% priced [S Kitco/CNBC/FinScans] | |
| 11:00–13:29 | 13:00–15:29 | Drift up to 3870.86 (11:45 bar), then back to ~3857 | 3853 → 3857 |
| **13:30** | **15:30** | **Oct Retail Sales:** headline +0.2% (consensus +0.1%/+0.2%, sources differ), **ex-autos +0.6% vs +0.4%, control +0.6% vs +0.3–0.4%**, September revised up. Import/export prices hot at the same time [S investinglive/ING/Kitco]. DXY up "a dozen pips" [S investinglive], 19-month high ~103.80 [S FinScans] | 3857.04 open |
| 13:30–13:40 | 15:30–15:40 | Fast drop: −$17.49 in 15 min (2.2nd percentile of 2026 15-min changes). **Max excursion $20.38 = 90th percentile** of all 13:30–13:44 UTC windows from 1/2025 to 10/2026 (n=469) | low **3836.66** at 13:40 |
| 13:41–14:05 | 15:41–16:05 | Full retracement | ~3851–3858 |
| 14:15 | 16:15 | **Industrial production −0.4% vs +0.1%** (utilities −4.3%) [S ING/Fed G.17]. DXY faded to ~103.40 and the 10y slipped to ~5.13% [S FinScans] | → 3873.04 high (14:30 bar) |
| 15:00–15:43 | 17:00–17:43 | Spike while **Iranian media report US strikes on Qeshm** [S FXStreet: "Gold's high came while those reports were running"; Euronews] | 3855.68 → **3890.69 (15:43)** |
| 15:43–18:55 | 17:43–20:55 | **Slow unwind, no single impulse.** Session range 3836.66–3890.69 | → **3854.44 (18:55)** |
| 19:01 | 21:01 | FXStreet: "trading around $3,850, about where it was before the release" [S] | |
| 19:03 (14:03 ET) | | CNBC: spot −0.08% at $3,853.25. "10-year pinned around 5.14%, dollar at a fresh 19-month peak" [S] | |
- **DXY/UST intraday data:** Dukascopy throttled my requests (HTTP 429/503, then TLS refusal) after the XAUUSD ticks came through. So I have **no intraday DXY or yield series** and give the dollar/yield side only from articles [S]. I did not invent any intraday DXY numbers.

### 1.3 Was there an early signal? Velocity percentiles vs every 2026 minute (1/1–19/10/2026) [V, exploratory, `data/velocity_1711.csv`]
| Point (UTC / server) | Δ15m $ (pct) | Δ30m $ (pct) | Δ60m $ (pct) | Δ180m $ (pct) | G_Crash score |
|---|---|---|---|---|---|
| Retail Sales +10m (13:40 / 15:40) | −17.49 (2.2) | −18.98 (3.7) | −19.27 (6.9) | −20.17 (16.0) | **2.91** (< 3.0) |
| Spike top (15:43 / 17:43) | +17.04 (97.7) | +28.40 (98.4) | +20.85 (93.6) | +27.20 (88.3) | 1.69 |
| Candidate L1-A (16:00 / 18:00) | −12.00 (4.7) | +4.54 | +13.95 | +11.74 | 0.92 |
| (16:52 / 18:52) | −5.62 (15.7) | −0.21 (49) | −14.45 (11.1) | +16.95 | 0.56 |
| Candidate L1-B (17:30 / 19:30) | −2.69 (29.9) | +1.49 (58) | −2.43 (40.8) | +3.95 | 0.61 |
| (18:00 / 20:00) | −2.10 (33.8) | −4.43 (27.3) | −2.94 (38.8) | +2.82 | 0.47 |
| (18:46 / 20:46) | −6.79 (12.2) | −5.06 (24.7) | −8.49 (21.4) | −26.02 (11.1) | 1.78 |
- 2026 medians: |Δ15m| $3.55, |Δ60m| $7.30, |Δ180m| $13.35. The whole 3h12m unwind (−$36.25) sits at the **6.5th percentile** of 2026 180-minute changes: notable over 3 hours, invisible on a 15–60 minute view.
- **Answer to (a): no.** Within the first 15–60 minutes of either candidate ladder, no velocity, impulse or `G_Crash` metric was abnormal. The single abnormal impulse (Retail Sales) came 1.5–4h earlier and fully reversed. Whatever told the market to sell after 15:43 UTC was the fading of a geopolitical spike against a strong-dollar, 5%-yield backdrop, not a measurable shock.

### 1.4 Ladder reconstruction (exploratory, `scripts/ladder_1711.py`, `data/ladder_1711_output.txt`)
- **Method:** a chain of BUY baskets replayed on Dukascopy ticks under the clone's measured rules: entry at each M15 open, $3 steps for L2–5, $2 for L6, one add per M15 bar, exit at avg+0.6. It assumes the buy signal was on (price above the M15 EMA99 after the spike).
- **Result:** 18:00-server basket: 4 levels (3876.08 → 3864.18), closed 19:03:58. Then the 19:30 basket: **L1 3868.44 19:30, L2 19:45, L3 20:00, L4 20:40, L5 20:46, L6 3854.10 21:00**, reaching 9 levels by 22:00 and closing 22:30:42.
- Neither matches "6 levels inside 17:00–20:00" exactly. Dukascopy quotes ≠ RF quotes, and one trailing exit that didn't fill on RF would merge the two baskets (3876 → … → ~3858 ≈ "$22" and 6 levels).
- **Both versions:** a slow ladder of about 1 level per 15–40 minutes during an ordinary-speed grind.
- **To pin it down:** compare against BD's real deal list (RF history) for 17.11. Claude has that, and I didn't touch it.

---
## 2. Survey of protection mechanisms
### 2.1 Public evidence table
| Mechanism | What it does | Best public evidence | Evidence quality | Tag |
|---|---|---|---|---|
| ATR/velocity halt ("no new levels after a spike") | Pauses entries/levels when ATR or a fast move exceeds k×average | Vendor docs: Phoenix Apex "ATR Risk Stop" ATR14 vs 20-bar avg ×2.0 [vendor page]; Midas Grid model: direction after trend/impulse/breakout signals continued only **51.6%** (coin toss); realized vol of the last 60m correlates with the size of the next 15m move (r≈0.52) | Vendor docs: none. Midas: in-sample model, Dukascopy 1/2025–10/2026 | [U] / [S] |
| "No new level after N levels in T minutes" | Ladder-speed brake | GTSbot (Rundo et al. 2019, *Applied Sciences* 9(9):1796): disabling the x-/y-threshold spacing checks raised DD +25%/+18.3% and cut profit about 10–11% | In-sample ablation of their own system; no OOS | [S] |
| Hedge / lock | Opposite position freezes the floating loss | Midas: an automatic lock ladder removed blow-ups but turned income negative (−$33/month vs +$160/month); FlexHedgePro doc (rescue lock + recovery grid), no evidence | Midas in-sample [S]; vendor [U] | [S]/[U] |
| News filter | No baskets around NFP/CPI/FOMC | Midas: release hours ~2.4× wider ($29.55 vs $12.53 median range), but **only 1 of 26 modelled blow-ups** fell near a major release, no more than random control days. Academic: gold futures absorb macro news **within ~90 seconds** (Smales & Yang 2015, IRFA 41:292-302); positive US surprises push gold down (Elder, Miao & Ramchander 2012, JBF) | Peer-reviewed event studies [V abstract]; Midas [S] | [V]/[S] |
| Equity / basket stop | Closes the basket at X% loss | Midas: tight basket stops fired 6–15×/week, **95–98% of stopped baskets would have recovered**, and a 120-minute pause after a stop cut the worst day about 2.5×. MQL5 articles 22677/21833: design only (equity-based kill switch), no OOS | Midas in-sample [S]; MQL5 design [U] | [S]/[U] |
| Cap on orders / total lots | Fewer levels, lower total lots | Midas: 9 vs 11 orders → blow-ups 6 vs 10 over 22 months at $1,050 per 0.01; "the deposit per 0.01 lot is the strongest single lever" | In-sample model | [S] |
| ATR/volatility step | Step = f(ATR) | Midas: a step that widens on far orders cut blow-ups **6 → 3** over 22 months, "but sensitive to small changes". Many vendors use ATR steps with no evidence. Theory: intraday volatility is persistent and predictable (Andersen & Bollerslev 1997, JEF) | Model in-sample [S]; theory [V] | [S] |
| Grid reset / "cut and restart" | Close everything at −5–7% when ATR > 2 | axiscoretech AUD/CAD 15y: "ruin 100% → 6–17%". Numbers are **estimates**, with no OOS or trade list | Narrative estimate | [U] |
| Volatility targeting (portfolio level) | Scale exposure 1/σ | Harvey et al. 2018 (JPM): reduces left-tail events, Sharpe gains mainly in equities/credit, negligible in commodities/FX [V abstract]. Cederburg et al. 2020 (JFE): volatility-managed portfolios **don't beat** unmanaged ones out of sample for real-time investors [V abstract] | Peer-reviewed incl. OOS | [V] |
| Ruin theory | — | Taranto & Khan 2020 (IMFI): grid trading "will almost surely ruin an investment account in the long term", just slower than martingale | Theory + simulation | [V] |

- **Forex Factory / Reddit:** posts found (e.g. r/Forex "logic that doesn't suicide short when gold goes parabolic") are anecdotes with no trade lists [U]. Nothing there rises to OOS evidence.

### 2.2 What your clone has already tested (read-only from Benzaquen docs; I'm not re-proposing these)
- **`G_Crash` (15 M1 bars, move > 3×avg M1 range×√15, 2h pause, cap at L3):** round 2: 1/7 positive years. In BD_CLONE, 2022–3/2024 went **−47,517 vs −11,934** for the base. HANDOFF: "מזיק".
  - **My exploratory check explains why:** on Dukascopy M1, 01–19 UTC, ≥75 minutes after any data gap, `G_Crash` ×3 **fires on 77.4% of trading days 2018–2025, ~8.7 times/day**. ×4 fires on 39% and ×5 on 21%. It's a near-permanent brake that still **missed 17.11**.
- **bstop5/bstop8/bstop10:** 0/7, and it worsens every year (it realizes temporary drawdowns).
- **News alone; d24ntop already has a news pause (30 min before / 60 after).** 17.11's Retail Sales sat inside that pause, and the ladder came afterwards.
- **Hedge by depth, Donchian trend hedge (r23), gold-trend balancer (r74), intraday balancer ensemble (r76), spread regime (r90), 50-indicator TA gate (AUC 0.50–0.58), G_Context (EMA 20/50/200):** all failed.
- **v9 regime switch** (20-day ADR > 2% → wide settings): the leading candidate, at low confidence. **R1 below is the intraday, continuous cousin of v9**, so it should be judged against v9 rather than in isolation.

---
## 3. Exploratory computations (NOT pre-registered, NOT BD)
**Data:** free Dukascopy XAUUSD M1 bid, 1/2018–19/10/2026, from the GitHub mirror `kevingtlin/dukascopy_XAUUSD_1m_Data` (made with dukascopy-node). Plus Dukascopy datafeed ticks for 17.11 directly (no account). I didn't cross-check the mirror against direct Dukascopy on overlapping dates, because the mirror ends on 19.10.

**Model:** a simplified BD-like ladder (`scripts/bdlike_sim.py`). It does **not** model Overlap, swaps, Thursday/Friday off, the news pause or the 15%/14d floor. The spread is a constant 0.30. Intrabar ordering is adverse-first. **Its baseline loses in every variant, so absolute PnL is meaningless.** Only relative counts are informative, and even those need the real clone.

### 3.1 The $3 step against gold's volatility (`data/step_vs_vol_by_year.csv`) [V arith]
| Year | Median M15 range $ | $3 / median M15 range | Model L8+ baskets per 100 days |
|---|---|---|---|
| 2018 | 0.94 | 3.19 | 7.3 |
| 2019 | 1.02 | 2.94 | 6.9 |
| 2020 | 2.32 | 1.29 | 5.4 |
| 2021 | 1.73 | 1.73 | 4.7 |
| 2022 | 1.90 | 1.58 | 9.3 |
| 2023 | 1.66 | 1.81 | 5.4 |
| 2024 | 2.40 | 1.25 | 8.8 |
| 2025 | 4.45 | 0.67 | 12.7 |
| 2026* | 8.43 | 0.36 | 10.6 |

\*To 19.10.

In 2026 BD's fixed $3 step is about **one third of a typical M15 bar**, so in any drift the binding limit is `OneAddPerBar`, not price distance.

### 3.2 Does ladder speed predict depth? (`data/speed_vs_depth.csv`)
| Minutes L1 → L4 | n | P(reaches L8) |
|---|---|---|
| 45–60 (fastest possible) | 446 | 0.137 |
| 60–90 | 209 | 0.124 |
| 90–120 | 123 | 0.106 |
| 120–240 | 226 | 0.137 |
| >240 | 314 | 0.153 |

- Same picture in both halves (2018–22 and 2023–26), and by L6 speed quartile (0.40/0.37/0.35/0.46). **Speed doesn't add information; depth does** (P(L8) rises from 0.136 at L4 to 0.396 at L6, which is simply the martingale arithmetic). This matches Midas's 51.6% and your HYBRID_PLAN finding of "no continuation after news".
- My FREEZE(N,T) and WIDEN-after-fast-ladder screens (`data/rule_screen.csv`) gave small, inconsistent effects across dev/holdout and floor levels.

### 3.3 R1/R2 screen (`data/r1r2_screen.csv`)
Floor proxy F = loss in L1-lot×$ units at which a basket is cut.

| F | Variant | 2018–22 cuts | 2018–22 L8+ | 2023–26 cuts | 2023–26 L8+ | 2023–26 gross wins |
|---|---|---|---|---|---|---|
| 300 | baseline | 160 | 152 | 276 | 137 | 39,239 |
| 300 | R1 c=1.0 | 160 | 146 | 229 | 82 | 35,407 |
| 300 | **R1 c=1.5** | 162 | 116 | **202 (−27%)** | **47 (−66%)** | 31,214 (−20%) |
| 300 | R2 time-spacing | 152 | 95 | 258 | 58 | 38,825 |
| 300 | R1 1.5 + R2 | 156 | 77 | 195 | 25 | 31,189 |
| 150 | baseline | 307 | – | 468 | – | 36,632 |
| 150 | R1 c=1.5 | 295 | – | 364 (−22%) | – | 29,821 |

- **Read:** R1 bites only when the step is below σ (2023–26). It cuts the number of cuts by about a quarter and costs about 20% of gross wins in this crude model. **Against your pass gates (≥80% of base profit, ≤70% of base DD), that is borderline,** which is exactly why it should be pre-registered rather than adopted. R2 mostly trims depth with little effect on cuts.

---
## 4. Recommended pre-registrations for the clone (v7 d24ntop, RF set `bd_v7_d24ntop_robo_floor2022.set`)
Common rules:
- Everything else stays frozen: entries, lots, Overlap, the news pause, DayOffMask=24, the 15%/14d floor.
- The rule can only **block or delay** an add. It never opens, hedges or closes anything, so **no gate is loosened**.
- One primary parameter value. The sensitivity value is reported but **can't be selected**. No flip after the result.

### R1: volatility-floor step (primary)
- **Definition:** for every add from level k to k+1 (k ≥ 1): `dist_k = max(BD_dist_k, c × Ref5)`.
  - `BD_dist_k` is the clone's existing distance (Fix_Distance for L2–5, the dynamic distance from L6).
  - `Ref5` = the median, over the previous 5 completed server days, of each day's median M15 (high − low). It's computed on the tester's own symbol data, fixed at server-day start, with no look-ahead.
- **c = 1.5** (primary): chosen a priori as roughly the 2018–2023 ratio of $3 to the median M15 range (median 1.77, rounded down to stay conservative). It wasn't fitted to crash days or PnL. Sensitivity c = 1.0 is reported only.
- **What it does:** restores BD's 2018–23 step-to-σ geometry when gold is volatile. In calm regimes it is inert (max() keeps BD's step).
- **Rationale:** volatility persistence [V theory], Midas step-widening 6 → 3 blow-ups [S in-sample], v9 daily-ADR switch already the leading candidate [internal, low confidence], exploratory §3.3.
- **Pass (both periods, with your existing BD_CLONE gates):**
  - net profit ≥ 80% of the clone base;
  - **and** max equity DD (money) ≤ 70% of base;
  - **and** floor-cut days in holdout ≤ 70% of base;
  - **and** it doesn't lose to v9 on the same periods (otherwise it adds nothing).
- **Replay check:** on 17.11.2026 the deepest buy basket must have fewer levels than base (report it, but it isn't a gate; n=1).
- **Kill:** fails any gate in dev → KILL, no variants (no c sweep, no lookback sweep). Fails in holdout → KILL.
- **Split:** dev 2019–2022 (step ≥ σ, mostly inert there, so dev mainly checks "does no harm"), holdout 2023–10/2026 once. Also report 12/2025–10/2026 on EGlobal real ticks.

### R2: depth-dependent time spacing (secondary, only if there is budget for two)
- **Definition:** level k+1 for k ≥ 5 is allowed only if at least (k − 3) completed M15 bars have passed since that basket's last add: L6 needs 2 bars, L7 3, L8 4, … Levels 2–5 are unchanged (BD's measured one-add-per-bar).
- **Rationale:** in 2025–26 depth builds by time. GTSbot's time-spacing ablation [S in-sample]. GridPro "minimum interval between orders" [U vendor].
- **Exploratory:** it reduced L8+ baskets 137 → 58 but barely changed cuts. **Lower prior than R1.**
- **Pass/Kill:** same gates as R1, with no parameter alternatives. If R1 passes, the R1+R2 combination may be tested **only** as a separate pre-registration, not as a rescue.

### Explicitly NOT recommended (with reasons)
- **Velocity/ATR halts and "N levels in T minutes":** G_Crash already failed. 17.11 had no velocity signal. Speed doesn't predict depth (§3.2). The clone's ×3 trigger fires on about 77% of days.
- **News filter extensions:** already in d24ntop, and 17.11's ladder came after the pause. Events are absorbed within ~90 s [V].
- **Equity/basket stops and hedges/locks:** already failed internally, with consistent [S] evidence that they turn recoverable drawdowns into realized losses or negative income.
- **The honest structural alternative** (from r74/r76, restated): reduce BD's size per balance. Midas's "deposit per 0.01 lot" is the strongest lever [S]. That is a sizing decision for Nadav, not a rule.

---
## 5. Files
- `BD_CRASH_SURVEY.md` (this file) and `SOURCES.md`.
- `bdcrash_data_scripts.zip`:
  - `data/`: `XAUUSD_m1_2026-11-17.csv` (Dukascopy ticks → M1, UTC); `velocity_1711.csv`; `ladder_1711_output.txt`; `speed_vs_depth.csv`; `rule_screen.csv`; `r1r2_screen.csv`; `step_vs_vol_by_year.csv`; `velocity_rule_fire_days_2018_2025.csv`.
  - `scripts/`: `duka_dl.py`, `bi5_to_m1.py`, `ladder_1711.py`, `velocity_1711.py`, `bdlike_sim.py`, `bdlike_rules.py`, `bdlike_r1r2.py`.
- **Not shipped (size):** the raw tick bi5 files and the 219 MB M1 mirror. They can be re-downloaded with the scripts.
