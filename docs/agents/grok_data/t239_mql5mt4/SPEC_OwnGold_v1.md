# SPEC_OwnGold_v1 — first in-house XAUUSD design for the RoboForex tick tester

Written: 2026-11-14, Asia/Jerusalem (IST, UTC+2).

This is a **design spec for our own EA**, not a clone of a vendor book. It is meant for Claude to implement and walk-forward on his machine (Dukascopy ticks + RoboForex ECN cost model). Work to produce this file was box-only; the Benzaquen machine was not touched.

Bars and cost conventions follow the house gate used on Happy / Kenni / TP TRADER (t230 / t233 / t239). They do not move after seeing a backtest.

---

## 0. Lessons from the books we decoded

These are the reasons the rule families below look the way they do.

1. **The binding fail is almost always net edge after realistic gold costs, not a missing “idea”.** Kenni’s pending-stop breakout had the healthiest *shape* we saw (hard SL, median hold **17.78 min**, top-10 36%, direction and timing both passed) and still printed only **7.65 bp** mean ECN net against a **10 bp** official bar, with closed TWR DD **27.89%**. TP TRADER’s gold book recosted to **+0.56 bp** mean (median **−3.84 bp**). Happy Gold captured a median **$0.35** in a **7-second** hold — a few tenths of a dollar, not 10 bp — and blew **35.4%** TWR DD once RF commission and Dukascopy gold width were applied.
2. **A pile-up of +1-pip winners is not an edge we can own.** Happy News winners had a median **+3 pips** but a 25th percentile pile-up at **+1 pip**, with a **5-second** median hold. That is a latency and fill-quality product. On gold, the same pattern (Happy Gold’s 7-second trail to +$0.35) died at RF costs. Our EA must not trade the first seconds of a spike and must not need a better fill than a public ECN tape.
3. **Return concentration is a frequent official fail, even when monthly return looks fine.** Gold Reaper / Limitless carried the “80% of growth in N days” banner; Solnce’s top-10 close-days were **53%** of log-TWR; VAJJ.5.4 cleared 3.57%/mo and 16% DD and still failed at **64.7%** top-10 (one month, October 2025, was +29%). A family that makes its year in ten sessions is not a passer, and we will not “fix” it by dropping the 50% bar.
4. **Grids, stop-ladders, and averaging hide the DD that the closed curve does not show.** The GR family, Happy Japanese (martingale), Kenni’s Medium Risk sibling (**60.85%** DD on a denser ladder), and TP TRADER’s 2020–2023 book (max **108** concurrent tickets, 44 on one symbol) all looked smoother on closed TWR than they were in stacked risk. Our hard rule is **one position, no add, no opposite hedge, no pending ladder**.
5. **Leverage-up can look like a new edge.** TP TRADER did ~15%/yr in 2020–2023 (honest **1.18%/mo**, DD **18%**) and then ~+150%/yr in 2024–2026. Median lots/balance in 2024 was **45×** the calm window; at constant 2020–2023 risk the later years fell back to ~**1%/mo**. We will not raise risk to manufacture 3%/mo. Sizing is fixed-fractional and frozen before the test.
6. **What actually looked healthy, when it appeared:** a **hard SL on every trade**; holds of **~15 minutes to a few hours** (Kenni 17.8 min, not 7 seconds); **breakout / momentum on gold**, two-sided so shock days can be shorts (Happy Gold was flat or green on 25 of 26 official crash dates, and **+$1,310 on 2026-01-30** when gold fell 9.9%); **no averaging down**; closed DD in a **teens-to-20%** band. We will keep that shape and refuse the parts that failed (sub-10 bp captures, stacking, news latency, risk ramps).
7. **A ≥10 bp net gold edge is hard, and we already know it.** At $4,000/oz, 10 bp is **$4.00/oz**. The official RF ECN round-trip used in t233 is **$0.31/oz** (~0.8 bp), so the 10 bp bar is about **13× cash RT**, not 5×. Kenni missed it by 2.35 bp with a real direction edge. This spec therefore prefers families whose **typical winner is a multiple of ATR or of a session range**, not a scalp, and it includes an explicit **kill-criterion** if none of them clear 10 bp out of sample. We will not lower the bar, add a second lot, or trade NFP.

---

## 1. Hard requirements (the OwnGold v1 gate)

All of the following are official for this EA. A backtest “pass” means they all hold on the **held-out** window after costs, not only in-sample.

| # | Requirement | Official cut |
|---|---|---|
| 1 | Symbol | **XAUUSD only** (Dukascopy ticks for fills; M1/M15 for signals). |
| 2 | Hard SL | A numeric stop is in the market **on every live position**, set at or before fill. No hidden virtual SL. No widening the SL after entry. Tightening / trailing is allowed. |
| 3 | No averaging / grid / stacking | **Max 1 open position.** At most one working entry order (or a linked OCO pair that leaves only one fill). After a fill, cancel the other side immediately. No add-on, no scale-in, no hedge. |
| 4 | Median hold | **≥ 15 minutes** on closed trades (15 minutes to a few hours is the design band; a time-stop should make this natural, not a filter applied after the fact). |
| 5 | Net expectancy | Mean net **≥ 10 bp** per closed trade after official RF cost (below). Median net is reported; it does not replace the mean. |
| 6 | Honest monthly TWR | **≥ 3.0%** hunt floor; **≥ 3.5%** standing bar, computed as \((1+\mathrm{TWR}/100)^{1/\mathrm{months}}-1\), months = calendar span / 30.4375, cash-flow-adjusted. Use a constant starting equity (suggested $10,000) and no external deposits. |
| 7 | Equity / TWR DD | Peak-to-trough of the official recosted TWR (and of mark-to-market equity, which for one position is derivable) **≤ 25%**. |
| 8 | Concentration | Top-10 close-days share of log-TWR **< 50%**. |
| 9 | Crash days | Official 26 UTC dates in `results_t209/crash_G_ASIA_LONG.csv`. **Preferred / OwnGold hard cut:** daily TWR **≥ 0** on every one of those dates (flat is a pass; a loss is a fail). Also report the standing hunt stats (mean daily TWR ≥ −0.10%, non-loss rate ≥ 50%). A family that is structurally long-only into those shocks fails even if it is lucky. |
| 10 | Slippage stress | Recost at official RF cash RT **plus $0.10/oz per side** ($0.20/oz extra RT, total **$0.51/oz**). Mean net must still be **≥ 10 bp**, honest monthly still **≥ 3.5%**, TWR DD still **≤ 25%**. A stress fail is a fail. |
| 11 | Sizing | Fixed fractional **0.5% or 1.0% of equity** at the initial SL (grid below). No martingale, no “recovery” lot, no year-by-year risk ramp. |
| 12 | Sample | Held-out window should have enough closed trades for a 10 bp mean to mean something. Treat **< 150 OOS trades** as under-powered: a numeric pass is then *provisional* and needs a second held-out fold or a paper stretch, not a live go. |

**Official cost model (t233, do not freelance):**

- RF ECN cash round-trip **$0.31/oz** (commission + realistic spread) is the unstressed official path. Also publish the decomposition: 20/mio commission (~$0.08/oz RT on 100 oz) plus the tape’s fill-instant half-spread twice, if the tester already does that; the **$0.31** floor is used if the tape RT would be cheaper.
- One gold pip = **$0.10**. One bp = \(10^4 \times (\text{signed \$/oz net}) / \text{entry}\). At $4,000/oz, 10 bp = **$4.00/oz**.
- Fills: conservative bid/ask (buy at ask, sell at bid) on Dukascopy ticks, not mid. If a pending is triggered, fill at `max(stop, ask)` / `min(stop, bid)` as the tester already does for Kenni/Happy.
- Vendor-style P&L for the TWR path = net after those costs (and swap if a trade is held through 21:00 UTC; prefer **not** to hold rollover — see flatten rule).

---

## 2. Shared engine (all families)

Implement once; families only change the signal that places the stop.

**Position and orders**

- State: `FLAT | PENDING_OCO | IN_TRADE`.
- While `IN_TRADE`, no new entry signal is acted on.
- A fill on one side cancels the sibling stop immediately.
- SL is a real stop order. Initial SL is never moved away from the market. Optional trail: only after price has travelled at least `trail_arm_R` times the initial SL, then trail by `trail_atr` × ATR.
- Flatten to cash at the family’s time-stop, and in any case **before 20:45 UTC** on weekdays (no 21:00 UTC rollover by default; `allow_rollover=false`). Friday: flatten at **16:00 America/New_York**.

**Sizing**

```
lots = clip( (risk_frac * equity) / (sl_dollars * 100), min_lot=0.01, lot_step=0.01 )
```

`sl_dollars` is the initial SL distance in $/oz. Sweep `risk_frac ∈ {0.005, 0.01}`. Official published path uses **0.01** if both pass, else the one that holds DD ≤ 25%. If even 0.005 fails DD while the 10 bp mean holds, the family is a **risk fail**, not a “use 0.1%” rescue in v1.

**Filters (apply to every family unless a row says otherwise)**

1. **Session window (Europe/London and America/New_York, DST-aware).** No new entries in the Asia thin session (22:00–07:00 London) and no new entries in the last 30 minutes before the flatten clock.
2. **Spread cap.** Do not place or leave a pending if the current bid–ask width **> $0.40** (4 gold pips). Cancel if width exceeds this while still pending.
3. **News blackout.** Using `/workspace/algotrade/data/us_macro_calendar_2015_2026.csv` (or the same event set Claude already uses): **no new entry** from `T − news_pre` to `T + news_post` around high-impact USD events: NFP, CPI (and core), FOMC statement / rate / presser, GDP, PCE, Unemployment Claims, employment revisions, and named-chair testimony. Default `news_pre=60 min`, `news_post=30 min`; sweep 30/60 and 60/60. If a position is already open when the window starts, **leave it** (do not flatten into the print — that is a latency trade). The point of the blackout is to not *enter* the spike.
4. **ATR regime.** ATR(14) on M15, in $/oz. Trade only if `atr_min_mult * ATR_median_20d ≤ ATR_now ≤ atr_max_mult * ATR_median_20d`. Defaults: `atr_min_mult=0.7`, `atr_max_mult=2.5` (skip both dead and riot regimes). Sweep as in each family.
5. **Minimum SL vs the 10 bp bar.** If the initial SL would be **< $2.00**, skip the trade. A $2 stop needs a very high win rate to average +$4 net after $0.31 costs. We would rather miss the trade.

**Reporting (every run, in-sample and OOS, unstressed and +1 pip/side)**

Honest %/mo, TWR and equity DD, top-10 log-TWR share, mean and median net bp, median hold, trade count, win rate, PF, max concurrent (must be 1), crash-day table on the 26 official dates, lots/equity over time (must not trend up except through compounding of the fixed fraction). Direction-vs-random and timing-vs-random, N=2,000, are **descriptive** for v1 and cannot rescue a failed cost or DD bar; run them on a passer or a near miss.

---

## 3. Rule family A — session opening-range breakout (**build this first**)

This is the recommended first build. It is the closest *clean* cousin of the only healthy shape we actually measured (Kenni’s pending-stop breakout), with the ladder, the sub-10 bp tightness, and the DD overshoot stripped out. It is two-sided, so crash days can be short. The opening range gives a natural, testable structure and a hold measured in tens of minutes to a few hours, not seconds. A **minimum range filter** is there specifically to protect the 10 bp bar: we do not take breakouts of ranges too small to pay RF costs at a reasonable R-multiple.

### 3.1 Idea

Once per chosen session, measure the high/low of the first `N` minutes. Place a buy-stop above that high and a sell-stop below that low. The first fill is the trade; the other side is cancelled. SL is a hard ATR- or range-multiple beyond the far side or beyond the breakout. TP is a range or ATR multiple, or a trail after 1R. Flatten at session end.

### 3.2 Exact rules

**Sessions (DST-aware; define both, sweep which are enabled):**

| Session | Range window | Trade window (pendings may fill) | Flatten |
|---|---|---|---|
| London | 08:00–08:00+`N` **Europe/London** | From range end until 16:30 London | 16:30 London |
| New York | 08:30–08:30+`N` **America/New_York** (or 13:30 London if `N` starts at London 13:30 — use NY local) | From range end until 16:00 NY | 16:00 NY |

If both sessions are on, they are **separate** one-trade opportunities. Still max one position *globally*: if London is still open at NY range end, **do not** arm NY. No stacking across sessions.

**Range.** Let `H`, `L` be the highest high and lowest low of M1 bars that **close** inside the range window (include the opening print). `R = H − L`.

**Skip the session if:**

- `R < r_min_atr * ATR(14, M15)` or `R > r_max_atr * ATR(14, M15)`, or
- `R < $r_min_abs` (absolute floor), or
- a news blackout overlaps the range window or the first `arm_delay` minutes after it, or
- spread cap fails.

**Entry.** At range end + `arm_delay` seconds (default 0; sweep 0 and 60 to avoid the print that *sets* the range):

- Buy stop at `H + buffer`, sell stop at `L − buffer`.
- `buffer ∈ {0, 0.10 × ATR_M15, $0.20}`.

**Stop loss (hard, set with the pending or on fill, same price).** Sweep two definitions; do not mix in one run:

- **A1 (range SL):** SL for a long is `L − buffer`; for a short is `H + buffer`. Optionally cap at `sl_atr_cap * ATR` if the range is huge.
- **A2 (ATR SL):** SL is `k_atr * ATR(14, M15)` from the **entry**, in the adverse direction.

If the resulting `sl_dollars < $2.00`, skip.

**Take profit / trail.** Sweep one of:

- **Fixed:** `TP = m_r * R` from entry (or `m_atr * ATR` if using A2).
- **Trail:** no fixed TP; arm a trail after `trail_arm_R` (default 1.0) × initial SL, trail by `0.5 × ATR(14, M15)` from the favourable extreme (or a chandelier of `trail_atr * ATR`).

**Time stop.** Close at the session flatten clock if still open. That is the primary hold control. Do not add a “minimum 15-minute” hold filter that blocks a stop-out; the *median* should clear 15 minutes because we are not trailing in the first seconds and not targeting $0.35.

**One fill per session.** If neither stop hits by flatten, cancel both.

### 3.3 Parameter grid (family A)

Keep the Cartesian product manageable. Suggested official v1 grid (~a few hundred runs, not tens of thousands):

| Parameter | Sweep |
|---|---|
| `sessions` | `{London}`, `{NY}`, `{London, NY}` |
| `N` minutes | `{15, 30, 60}` |
| `r_min_atr`, `r_max_atr` | `(0.25, 1.5)`, `(0.35, 2.0)`, `(0.50, 2.5)` |
| `r_min_abs` | `{$1.50, $3.00}` |
| `buffer` | `{0, $0.20}` (drop the ATR buffer in v1 if the grid is tight; add it in a refinement only if a near miss exists) |
| SL mode | `A1` or `A2` with `k_atr ∈ {0.75, 1.0, 1.5, 2.0}` |
| TP mode | `m_r ∈ {1.0, 1.5, 2.0}` **or** trail with `trail_arm_R ∈ {1.0}` and `trail_atr ∈ {0.5, 1.0}` |
| `news_pre`, `news_post` | `(60, 30)` default; `(60, 60)` as one sensitivity |
| `risk_frac` | `{0.005, 0.01}` — run **after** a structure pass on a unit-lot / 1% path, not as a signal parameter |

**Freeze before the OOS read:** pick at most **two** candidate rows from the *dev* window (see §6) using the official gates applied to dev (10 bp, hold, DD, top-10, crash). Only those two are evaluated on the held-out years. No grid search on 2024–2026.

**Why this family can clear 10 bp (and how it can fail).** A 30-minute London range of, say, $4–8 with `m_r=1.5` gives a designed winner of $6–12/oz (15–30 bp at $4,000) before costs, which is the right *order of magnitude*. It fails if most “winners” are stopped to a tiny trail, if the range filter is so loose that R is a couple of dimes, or if both sides get chopped in a two-sided open (win rate too low at 1:1). The skip rules exist to avoid that chop.

---

## 4. Rule family B — volatility-contraction breakout (NR / inside bar)

Build second, only if A is implemented and reported. Same shared engine.

### 4.1 Idea

Trade the first breakout after a short, quiet bar (NR-style or inside bar) during London or New York, not during Asia. The entry is a pending stop at the contraction bar’s extreme. SL is the other side of that bar (or a small ATR pad). This should also produce holds of tens of minutes and winners measured in ATR, not ticks.

### 4.2 Exact rules

**Signal timeframe:** M15 (default) and M30 as a second grid value.

**Contraction, at bar close, only if the bar’s close time is inside 08:00–16:00 Europe/London or 08:30–15:30 America/New_York:**

- **B1, NR(L):** this bar’s range = min of the prior `L` completed ranges, `L ∈ {5, 7, 10}`.
- **B2, inside bar:** this bar’s high ≤ prior high and low ≥ prior low.

Skip if the contraction range `C < $1.00` or `C < 0.25 * ATR(14)` (cannot pay costs) or `C > 1.0 * ATR(14)` (not actually quiet).

**Entry.** Buy stop at `high + buffer`, sell stop at `low − buffer`, `buffer ∈ {0, $0.20}`. OCO, one fill. Pendings expire at the earlier of `expiry_bars` closes (`{2, 4, 8}` on the signal TF) or the session flatten clock (16:30 London / 16:00 NY).

**SL.** Other side of the contraction bar, minus/plus `buffer`. If that distance is `< $2.00`, skip. If it is `> sl_atr_cap * ATR(14)` (`sl_atr_cap ∈ {1.5, 2.0}`), skip (expansion already happened).

**TP.** `m * C` with `m ∈ {1.5, 2.0, 3.0}`, or the same ATR trail as family A (`trail_arm_R=1`, `trail_atr ∈ {0.5, 1.0}`).

**Time stop.** Session flatten, same as A.

**Filters.** Shared news, spread, ATR-regime, max-1, no-rollover rules.

### 4.3 Grid (family B)

`TF ∈ {M15, M30}`; contraction `{NR5, NR7, NR10, inside}`; `m ∈ {1.5, 2.0, 3.0}` or trail; `expiry_bars ∈ {4, 8}`; `buffer ∈ {0, $0.20}`; `risk_frac ∈ {0.005, 0.01}`. Same two-candidate freeze before OOS.

Failure mode to watch: too many signals, small `C`, mean net a few bp. If the distribution of `C` is tight, kill the family rather than tightening the trail.

---

## 5. Rule family C — impulse then pullback continuation

Build third. This is the family most likely to *improve entry price* (the Kenni/TP pattern of buying the breakout print is what made average net thin). It is also easier to curve-fit, so the walk-forward freeze is mandatory.

### 5.1 Idea

In London or NY, wait for a strong impulse bar or burst (`impulse ≥ p * ATR`). Then wait for a retracement of fraction `r` of that impulse (or back to EMA(20) on M15). Enter with a **stop in the impulse direction** when price resumes (break of the pullback extreme). SL goes beyond the pullback extreme. TP is a measured move or a trail. If the pullback eats the whole impulse, the setup is dead.

### 5.2 Exact rules

**Signal TF:** M15.

**Impulse.** A completed M15 bar (or a sequence of at most 3 bars) whose close-to-close move in one direction is `≥ p * ATR(14, M15)`, `p ∈ {1.0, 1.5, 2.0}`, with the close in the impulse direction (close in the top or bottom third of the bar). Only during 08:00–16:00 London or 08:30–15:30 NY.

**Pullback window.** From the impulse close, wait up to `wait_bars ∈ {4, 8, 12}` M15 bars. A valid pullback retraces `r ∈ {0.38, 0.50, 0.62}` of the impulse range (high–low of the impulse burst) without closing beyond the impulse start (the origin). Optionally also accept a touch of EMA(20, M15) as a valid pullback if it occurs inside the same window (one on/off flag, default off in v1 to limit degrees of freedom).

**Invalidation.** If price closes beyond the impulse origin before entry, cancel. If the window expires with no pullback, cancel.

**Entry.** After a valid pullback, place a stop at the pullback extreme in the impulse direction (high of the pullback for a long continuation, low for a short) + `buffer ∈ {0, $0.20}`. The stop expires at the session flatten or after `expiry_bars=4` M15 bars.

**SL.** Beyond the opposite extreme of the pullback, `buffer` past it. Skip if SL `< $2.00` or `> 2.0 * ATR(14)`.

**TP.** Measured move: `m ∈ {1.0, 1.5}` times the **impulse range**, from entry; or the family-A trail.

**Filters.** Shared rules. Particularly important: **news blackout** — do not arm a continuation stop into NFP/FOMC.

### 5.3 Grid (family C)

`p ∈ {1.0, 1.5, 2.0}`; `r ∈ {0.38, 0.50, 0.62}`; `wait_bars ∈ {8, 12}`; `m ∈ {1.0, 1.5}` or trail; `buffer ∈ {0, $0.20}`; `risk_frac ∈ {0.005, 0.01}`. Freeze two dev candidates before OOS.

Failure mode to watch: overfitting the pullback fraction, and late entries that turn a 10 bp idea into a 2 bp chase. If OOS mean net collapses while IS looks excellent, this family is dead for v1.

---

## 6. Walk-forward and out-of-sample plan

**Data.** Dukascopy XAUUSD ticks for fills (same tape as t230/t233), M1/M15 bars derived from that tape for signals. UTC index. If tick coverage for a day is missing, **skip the day**; do not fill from mid. M1 bid from 2015 and M1 ask from 2022 are already on the box; the tester on Claude’s machine should use the fullest tick history he already has. State the first and last tick used in the report.

**Splits (frozen now, not after seeing 2026):**

| Role | Dates (inclusive, UTC) | Purpose |
|---|---|---|
| Warm-up | 2018-10-01 … 2018-12-31 | ATR, median ATR, EMAs. No trades counted. |
| **Dev / in-sample** | **2019-01-01 … 2023-12-31** | Grid search. Includes 2020 COVID gold move and 2022. Pick at most two rows per family. |
| **Held-out A (official OOS)** | **2024-01-01 … 2026-11-13** | Official pass/fail. Includes 2026-01-30 (−9.9% gold) and the official BD crash list that falls in 2026. **No parameter change after looking at this window.** |
| Sensitivity fold (not for picking) | Train 2019–2021, test 2022–2023, then apply the *same* row to held-out A | Stability check. A family that only works in 2024–2026 gold trend is not a pass even if official OOS is green — report it and fail the “regime gift” test (see below). |

**Selection on dev, in this order, all required:**

1. Max 1 position and a hard SL on every trade (implementation invariant).
2. Median hold ≥ 15 min.
3. Mean net ≥ 10 bp after $0.31/oz (dev window).
4. TWR DD ≤ 25%, top-10 < 50%, crash-day hard cut on whatever subset of the 26 dates falls inside 2019–2023 (the rest are OOS).
5. Among rows that clear 1–4, prefer the **higher mean net bp**, then the lower DD, then the lower top-10 share. Do not prefer higher monthly return from a higher `risk_frac`.

Then run **only those frozen rows** on held-out A, at both cost levels ($0.31 and $0.51). Official go/no-go is held-out A.

**Regime-gift check (required, cannot be the official pass by itself).** On the frozen row, report 2019–2023 test-fold and 2024–2026 separately. If held-out A clears 10 bp and 3.5%/mo but the 2022–2023 fold is near zero or negative after costs, label it **REGIME GIFT** and treat v1 as a **NO-GO** (same lesson as TP TRADER’s 2024–2026 leverage-up, even though here the “gift” would be a bull-gold sample, not lot size). We need the edge in more than one gold regime.

---

## 7. Kill-criterion (read this before loosening anything)

A ≥10 bp net gold edge was not sitting in the books we decoded, including the one book (Kenni) that already looked like a one-position breakout with a 15-minute hold. So:

- If **no family** produces a frozen row that clears the official OOS gate in §1 (10 bp mean, stress 10 bp, hold, DD, top-10, crash, 3.0/3.5% monthly), **stop**. Write a short fail table (best mean bp, why each family missed). That is a successful research outcome, not a reason to “finish the EA anyway.”
- **Do not**, in v1, in response to a miss: lower the 10 bp bar to 5× cash RT (~3–4 bp); allow a second position or a stop ladder; shorten the median-hold floor below 15 minutes; add a news-straddle or sub-minute trail; raise `risk_frac` above 1% to hit 3%/mo; or search the grid on 2024–2026.
- A **near miss** is defined narrowly: OOS mean net **8–10 bp**, all other hard bars green, stress mean **≥ 8 bp**. At most **one** refinement pass on a single family (for example, add the ATR buffer, or switch A1 to A2) with the *same* date splits, then a new OOS read. If that still misses 10 bp, kill v1.
- v2, if needed, would be a **slower** design (H1/H4 swing, multi-day hold, still one position and a hard SL), not a tighter scalp. Do not start v2 in the same breath as a v1 fail; report first.

---

## 8. Suggested build order for Claude

1. Shared engine: one-position state machine, RF $0.31 / $0.51 recost, news blackout, flatten rules, official report block (§1 and §2).
2. **Family A only**, full grid on 2019–2023, freeze ≤2 rows, official run on 2024–2026. This is the first backtest we want to read.
3. Family B if A is implemented and the engine report is trusted (even if A itself is a fail — B is a different entry, not a retune of A).
4. Family C last, with the overfitting warning in §5.3 taken seriously.
5. Stop at the kill-criterion rather than iterating into a curve-fit.

---

## 9. First family to build (one paragraph, also in the hand-off)

**Build family A, session opening-range breakout, first.** Arm one OCO pair at the high/low of the first 15/30/60 minutes of London and/or New York, take only the first fill, hard SL = the far side of the range or `k*ATR(14, M15)`, TP = 1.0–2.0× the range or an ATR trail armed at 1R, flatten at the session close, never more than one position, skip ranges that are too tight to pay $0.31/oz or that overlap a high-impact USD event. Sweep the §3.3 grid on 2019–2023, freeze at most two rows, and judge them on 2024–2026 with the §1 gate (10 bp mean after RF ECN, 15-minute median hold, 3.5%/mo, 25% DD, top-10 < 50%, no loss on the official BD crash dates, +1 pip/side stress). If that official OOS read does not clear 10 bp, do not loosen the rule — move to family B or stop under §7.

---

SHA-256 of this file is written next to it after the text is frozen (`SPEC_OwnGold_v1.md.sha256`).
