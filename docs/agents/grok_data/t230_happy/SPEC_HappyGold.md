# SPEC_HappyGold — clone specification for EA Happy Gold Eightcap (signal 1862128)

Written 2026-11-13, Asia/Jerusalem, from the t230 MQL5 history (`1862128.history.csv`, SHA `265ce6ad…`), Dukascopy XAU M1 and ticks. Empirical recovery of the **scalp** settings only.

**This book is a NO-GO for a RoboForex live or demo-as-a-path-to-live run** after the official tick recost (honest 9.59%/month but TWR DD **35.4%**). The SPEC is still written so the rules are not lost, and so a demo used only to *measure RF gold spreads* has a target. **Never use the GridNews settings** of the same product (signal 1714611, equity DD 88.83%).

**Broker clock:** Europe/Athens, same as Happy News (same seller, same Eightcap book family). Deposit stamp 2023-02-09 00:54:02.

---

## 1. Idea

A **one-position XAUUSD breakout scalp**. Pending buy-stop and/or sell-stop are parked at **ZigZag / swing extremes** (not a 10-pip news straddle), mostly at the 06:00 broker open, and live until 15:00 or 22:00. SL is a hard **$2.56**, TP a hard **$10.00**. After a fill, the SL is moved into profit and the trade is usually done in **7 seconds**, capturing a median **$0.35**. Max one open trade. Risk 2% of balance (sometimes 4%).

This matches the vendor’s published scalp: “hard SL −24 pips, max 1 open trade, ZigZag extremes, dynamic TP, max 20 pips spread.” Under their gold-pip convention (1 pip = $0.10), 24 pips = $2.40, close to the recovered **$2.56**; 100 “points” at $0.10 would be $10, which is exactly the TP. “Dynamic TP” is not what this book does at placement — placement TP is a constant $10 — but almost every exit is a *modified SL*, so the effective take-profit is dynamic and tight.

---

## 2. Recovered rules

| Rule | Value | Evidence |
|---|---|---|
| Symbol | **XAUUSD only** | 749 of 749 fills. Suffix `.i`. |
| Max open trades | **1** | Max concurrent same-symbol = 1, max same-side = 1, averaging-down pairs = 0, same-second groups = 0. |
| Placement time | **06:00:00 or 06:00:01** primary (716 of 1,239 cancelled pendings). Refreshes through the day (09:00, 15:00, 21:30, …). Seconds 0–2. | Cancel times: **22:00** (646) or **15:00** (201). Mean lifetime 9.3 hours, median 9.0. This is a session window, not a 64-second news cancel. |
| Entry type | **Pending buy-stop / sell-stop at a swing extreme** | Distance from Dukascopy mid at the placement minute: median **$36.50**, mean $57, p75 $67, max $1,091. Signed distance is almost always positive (stop is on the breakout side). Only 39 of 1,200 placement seconds have *both* sides at once — often one side, the ZigZag direction. |
| Placement SL | **$2.56 exactly** (256 points at $0.01; 25.6 “gold pips” at $0.10) | 1,071 of 1,239 at 256, 168 at 254. Min $2.54, max $2.56. |
| Placement TP | **$10.00 exactly** (1,000 points) | 1,239 of 1,239. |
| Post-fill | SL moved into profit. **745 `[sl]`, 4 `[tp]`.** Close = SL on the `[sl]` exits. | Median capture **+$0.35** (35 points), mean $0.63, p10 $0, p90 $2.09. Median hold **7 seconds**, mean 138s. The 4 TP hits are the $10 target. Losers take the $2.56 original SL (−256 points). |
| Lot | **2% of balance** at the $2.56 SL (a second mode at **4%**) | Lots per $1,000: median 0.0785, 25th 0.078, 75th 0.163, max 0.250. Risk at $2.56: median 2.01%, 75th 4.16%. Corr(lot, balance) = **0.997**. Zero step-up after a loss. `lots = (0.02 * Balance) / (2.56 * 100)` for the 2% mode, times 2 for the 4% mode. |
| Spread filter | Vendor: “max 20 pips.” | Not a hard cut we could recover. At $0.10/pip that is a $2.00 width; Dukascopy width at actual *fills* had median $0.42 and a tail to $6.53. |
| News | **Not the engine** | Fill hours span 06–21, peak 15–16 (London/NY). A minority of 15:30 placements exist. Crash-day and large-down-day P&L is green or flat, not a news-straddle pattern. |

**ZigZag parameters (depth, deviation, backstep) were not uniquely recovered.** A clone must either (a) take them from the vendor EA’s scalp preset, or (b) fit a ZigZag so that the pending price equals the prior confirmed extreme, at 06:00, on this history (cancelled pending prices are in `pend_gold.csv`). The distance-to-mid distribution (median $36.50, heavy tail) is the target, not a 10-pip offset.

---

## 3. Session algorithm (clone sketch)

1. At 06:00:00 broker (and on a refresh schedule at 15:00 if flat): compute the current ZigZag last high and last low on XAUUSD (timeframe to be fitted; M15 or M5 is the usual family).
2. If spread < cap and no position is open:
   - Buy Stop at the last confirmed high (possibly + a small buffer), SL = entry − $2.56, TP = entry + $10.00.
   - and/or Sell Stop at the last confirmed low, SL = entry + $2.56, TP = entry − $10.00.
   - Lots from the 2% (or 4%) formula. One pending side is typical; both is allowed if they cannot both be inside the market.
3. Cancel leftover pendings at 15:00 and at 22:00.
4. On fill: delete any remaining pending; do not open a second position. Move SL as in §2 (lock a few dimes of profit within seconds; optional short trail). Max hold is in practice minutes; a time-stop of 15–30 minutes would cover the p99 without changing the median.
5. Friday / rollover: this scalp almost never holds a 21:00 UTC night (swap on the book is −$12 total in 3.7 years). Flatten before rollover if still open.

---

## 4. Crash-day behaviour (required for any gold clone)

Official BD 26 dates (2026-04-21 … 2026-10-12): **15 up, 1 down (2026-10-12 −$1,715, −2.00%), 10 flat**. Mean daily return +0.80%, non-loss 96.2%. Sum +$9,176. On the 20 worst XAU close-to-close days of 2023-02–2026-10: **12 up, 0 down, 8 flat**, including **+$1,310 on 2026-01-30** (gold −9.9%). A clone that is long-only, or that grids, will **not** reproduce this. The sell-stop side is doing the work on crash days.

---

## 5. Why RoboForex fails the gate (do not “fix” this by retuning)

- Eightcap charged **$0 commission**; RF ECN 20/mio is about **$16 RT per lot**, −$13,668 on the history.
- Dukascopy bid–ask at the fill second: median **$0.42**, enough to flip 183 winning book trades into official losses.
- Official path: $60,302, 9.59%/month, WR 54%, PF 2.44, **TWR DD 35.4%**. 18 of 46 official months are negative. **90% of official profit is 2026** (large lots after compounding). Stress at $0.50/side blows the path through zero.
- Direction and timing still pass: the edge is real on the original broker, not at RF costs.

A RoboForex demo is only useful as a **spread measurement**, not as a path to a live copy, unless those measurements show fill-instant widths near the published 5-point ECN average rather than the $0.42 Dukascopy median we saw at this book’s fill times.

---

## 6. Worked numbers

Pending example (2026-11-11, cancelled): Buy Stop 7.33 lots at 4,066.90, SL 4,064.34 (**$2.56**), TP 4,076.90 (**$10.00**), placed 15:00:01, cancelled 22:00:00.

Fill example, same day: Sell 7.33 lots at 16:37:22 at 4,013.67, SL moved to 4,011.14 (**$2.53 in the money**), closed 4 seconds later at that SL, book **+$1,854.49**. Per ounce: 1,854.49 / (7.33 × 100) = **$2.53**, matching the moved SL. Balance was about $93,400; 7.33 / 93.4 × 1,000 = **0.0785 lots per $1,000**, the 2% risk mode (2% × 93,400 / (2.56 × 100) = 7.30 lots).

SHA-256 of this file: see `SPEC_HappyGold.md.sha256`.
