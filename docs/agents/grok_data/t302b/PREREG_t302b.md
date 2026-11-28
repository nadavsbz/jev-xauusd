# PREREG t302b — full t239/t241 gate on six MQL5 history exports

Written and hashed: 2026-11-20 10:33 Asia/Jerusalem (IST, UTC+2).

**Hashed before any P&L, monthly TWR, direction-vs-random, random-timing, top-10-days, RF recost, crash-day, Gold-Reaper overlap, lot-vs-balance, stacking, or floating-DD computation on these six files.** A structural peek only (column names, Type / Direction / Comment tokens, row counts, symbol and volume tokens, date-span endpoints, presence or absence of S/L and T/P, thousands-separators, Balance/Credit row counts and comment tokens and cash-row signs, and file SHA-256) was used to design the parsers and to freeze official starts from first-live-trade endpoints. Reconciliation targets are frozen from the t302 public-page cache (logged-out MQL5 signal pages and listing, as of 19.11.2026), not from ticket sums. No sums, win-rates, monthly tables, or per-trade averages were computed before this hash.

Requester: Claude, `claude_outbox.md` entry **19.11.2026 22:35** (“t302 התקבל. המשך: export ושער, ו-t301 קודם”): export 2391620, 2385553, 2394167, 2373216, then 2031876 and 2389887; run the t239/t241 gate with a new PREREG before the run; TycheCerf stays aside until there is a client_id or tickets. The six CSVs are already on the box at `/workspace/t302/exports/<id>_history.csv`.

Unique t302b names. No overwrite of t218–t302. Read-only on Benzaquen except copying this round’s PREREG/RESULTS/CSVs into `docs/agents/grok_data/t302b/` and an append-only Hebrew note in `docs/agents/grok_inbox.md`. Do not touch terminals, `accounts.json`, `C:\MT5_JEV_*`, or live accounts. Never print passwords, logins or account numbers. No costs, no settings changes, no deletions except this agent’s own temp files.

---

## Scope (frozen)

Six MQL5 history exports, two layouts.

**Layout A — standard closed-trade / order export** (same as t239/t241), semicolon-separated, broker time, newest-first:

`Time;Type;Volume;Symbol;Price;S/L;T/P;Time;Price;Commission;Swap;Profit;Comment`

Used by: 2385553, 2394167, 2373216, 2031876.

**Layout B — MT5 deal export** (no second Time, no S/L or T/P columns):

`Time;Symbol;Type;Direction;Volume;Price;Commission;Swap;Profit;Comment`

`Direction` is `In` / `Out` (entry / exit). Used by: 2391620, 2389887.

Thousands-separators appear as spaces in some price and cash fields (same as t230/t239/t241). Vendor P&L for a closed trade is **profit + commission + swap** (t230/t233/t239/t241 convention).

As-of date for honest monthly: **2026-11-20**. Months = (as-of − official start) / 30.4375. Honest monthly = \((1 + \mathrm{TWR}/100)^{1/\mathrm{months}} - 1\).

---

## Files (structural, frozen)

| Signal | File | SHA-256 | Physical lines (incl. header) | Layout | Structural Type counts (not P&L) | Notes |
|---|---|---|---|---|---|---|
| Van PM, [2391620](https://www.mql5.com/en/signals/2391620), Mira Hardani, PrimeCodex-MT5 | `2391620_history.csv` | `8ea7bff7b77868ac27801d0dbab704b00d0722827dbf61fde0a3a6579c919812` | 4,308 (4,307 data) | B deals | Buy 2,106 (In 1,064 / Out 1,042), Sell 2,094 (In 1,043 / Out 1,051), Balance 106, Credit 1 | Symbols on Buy/Sell: AUDCAD.std 1,779, XAUUSD.std 1,188, EURUSD.std 895, plus NZDCAD.std, USDCAD.std, GBPUSD.std and other FX. All 4,307 comments empty. No S/L or T/P columns. Deal-time span 2024.10.23 09:55:18 … 2026.11.06 15:47:17. Cash-time span 2024.10.21 07:37:17 … 2026.10.26 19:31:59. Cash signs: Balance − 53, 0 26, + 27; Credit 0 1; all cash comments empty. Thousands-spaces in 1,197 rows. Volumes (Buy/Sell) 19 distinct; top 0.30 / 0.60 / 0.15 / 0.90. In/Out counts are not equal, so open inventory and/or partials are expected. |
| EU Zone Arsenal, [2385553](https://www.mql5.com/en/signals/2385553), FortunePrimeGlobal-Live, account currency **EUR** | `2385553_history.csv` | `010150a76e829cc28ac6902c5aca606537935a3935d1f410f0feba60e2d4b3ba` | 1,149 (1,148 data) | A standard | Buy 510, Sell 437, Buy Limit 127, Sell Limit 66, Sell Stop 5, Buy Stop 2, Balance 1 | Closed Buy/Sell symbols: GBPUSD-E 298, EURJPY-E 268, EURUSD-E 213, plus EURAUD, EURGBP, EURCHF, EURNZD and others (947 closed, matches the page trade count). Open-time span 2024.12.02 16:25:56 … 2026.11.11 12:05:16. Close-time span 2024.12.02 22:15:04 … 2026.11.11 12:37:38. On closed Buy/Sell: S/L non-zero 172 / empty 775; T/P non-zero 494 / empty 453. Comments: cancelled 200 (all 200 pendings), [tp] 251, [sl] 3, empty 658, plus a few `to #` / `from #` partials, and one Deposit. Cash: one Balance + with comment Deposit, at 2024.11.28 10:05:10. Thousands-spaces in 3 rows. |
| Gold EA Stop Loss No Martingale, [2394167](https://www.mql5.com/en/signals/2394167), Ajaya Pokhrel, ICMarketsSC-Live18 | `2394167_history.csv` | `2a4c997bd085fc03af68d65de4a86c08c63addf539fe312af8b25de1b1a738c8` | 1,217 (1,216 data) | A standard | Buy 394, Sell 422, Buy Stop 220, Sell Stop 156, Balance 24 | Closed Buy/Sell symbols: XAUUSD 687, GBPCAD 58, USDJPY 55, plus small GBPUSD/EURUSD/USDCHF/GBPJPY/USDCAD/NZDUSD (816 closed, matches the page). Open-time span 2024.08.12 16:30:10 … 2026.11.11 10:00:00. Close-time span 2024.08.12 16:31:57 … 2026.11.19 10:00:00. On closed Buy/Sell: S/L non-zero 815 / empty 1; T/P non-zero 760 / empty 56. Comments: cancelled 376 (all 376 pendings), [sl] 546, [tp] 163, empty 129, two `to #`. Cash: Balance − 14 and + 10, all comments empty, 2024.08.10 11:07:00 … 2026.10.04 06:33:01. Thousands-spaces in 1,064 rows. |
| Stable Sky, [2373216](https://www.mql5.com/en/signals/2373216), Yi Fan Liu, RallyvilleMarkets-Live | `2373216_history.csv` | `b52ee3d507b8a1998991731c83ec4c1544f3256e19f480022344a810225303ce` | 516 (515 data) | A standard | Buy 231, Sell 282, Buy Limit 1, Balance 1 | Closed Buy/Sell symbols: NZDCAD 249, AUDNZD 133, AUDCAD 131 (513 closed, matches the page). This is the AUDCAD/NZDCAD/AUDNZD trio flagged in t302 as the same pattern as rejected grid families. Open-time span 2024.04.19 17:06:00 … 2026.09.09 01:35:26. Close-time span 2024.04.22 04:57:00 … 2026.09.10 07:54:19. On closed Buy/Sell: S/L non-zero 345 / empty 168; T/P non-zero 442 / empty 71. Comments: empty 420, [tp] 93, cancelled 1, Deposit 1. Cash: one Balance + Deposit at 2024.04.19 03:06:24. Thousands-spaces in 2 rows. File activity ends 2026-09-10 (t302 already noted inactivity since 09.2026). 70 distinct volumes. |
| Blue Agressive CFDs Fiat FIC04, [2031876](https://www.mql5.com/en/signals/2031876), Fabio Aparecido De Almeida, InfinoxLimited-Live04 | `2031876_history.csv` | `b5f84931149c3b9f64954e554cd0104ff2a793b329099b248948ab05d3603458` | 18,210 (18,209 data) | A standard | Buy 2,274, Sell 2,030, Buy Stop 6,993, Sell Stop 6,911, Balance 1 | Closed Buy/Sell symbols: XAUUSD 1,323, USDJPY.i 1,109, EURUSD.i 828, EURGBP 416, GBPUSD 409, plus EURUSD 82, USDJPY 82 and a handful of others (4,304 closed, matches the page). Open-time span 2022.11.30 02:03:09 … 2026.11.12 18:12:19. Close-time span 2022.11.30 02:03:31 … 2026.11.18 11:09:27. On closed Buy/Sell: S/L non-zero 3,386 / empty 918; T/P non-zero 3,480 / empty 824. Comments: cancelled 13,904 (all 13,904 pendings), [sl] 2,422, [tp] 109, empty 1,774. Cash: one Balance + with empty comment at 2022.11.08 16:27:53. Thousands-spaces in 5,206 rows. 752 distinct volumes. Cancelled-pending / fill ratio is structurally very high. |
| Soft Chili, [2389887](https://www.mql5.com/en/signals/2389887), Donna Citra Setiadi, HandalSemesta-Server | `2389887_history.csv` | `9882a30110d652aa91b97ea0012e650ef93873296ae3ea4b6268f1ead2f8fb37` | 485 (484 data) | B deals | Buy 242 (In 206 / Out 36), Sell 241 (In 36 / Out 205), Balance 1 | Symbol XAUUSD only (483 deals). Comments: empty 242, `[tp …]` 212, `[sl …]` 29, Deposit 1. No S/L or T/P columns; stop/target prices appear only in some Out comments. Deal-time span 2024.11.05 19:04:00 … 2026.11.18 14:49:00. Cash: one Balance + Deposit at 2024.11.05 09:57:04. Thousands-spaces in 484 rows. Single volume 0.10 on all Buy/Sell. In/Out counts (Buy In 206 vs Sell Out 205; Sell In 36 vs Buy Out 36) are consistent with FIFO close-by-opposite-type, plus one leftover open In. |

---

## Deal-file parser (Layout B, frozen before P&L)

1. Parse fields with space-thousands stripped. Sort deals oldest-first.
2. Per symbol, maintain a FIFO book of open lots:
   - `Buy In` opens or adds a long; `Sell In` opens or adds a short.
   - `Sell Out` closes long lots FIFO; `Buy Out` closes short lots FIFO.
   - `InOut` / `Out By` (if present): close then open the remainder.
   - Partial closes: consume the Out volume from the front of the FIFO; allocate the Out row’s profit, commission and swap to that close; allocate any commission recorded on the matching In pro-rata by lots.
3. A closed trade’s vendor P&L = allocated profit + commission + swap. Open time / open price / lots / side come from the In; close time / close price / comment come from the Out.
4. Unmatched Ins at end of file are open inventory (not in closed TWR). Unmatched Outs are flagged and excluded from official TWR.
5. Hard SL is not visible from a missing column. A comment `[sl <price>]` counts as a visible stop for that close only. `[tp …]` alone does not.

Layout A is parsed exactly as t239/t241 (`Time` / `Time.1` as open/close). Symbol suffixes `.std`, `-E`, `.i`, trailing `.` are stripped for `sym_norm` (XAU*, FX majors/crosses). Contract size is inferred after this hash from Profit vs signed price move × volume, and commission scaling follows t241 `infer_lot_scale`.

---

## Official starts (frozen before P&L)

Same rule as t239/t241: **first live Buy/Sell (or first deal) in the file is official.** The page “Started” stamp is a listing-age sensitivity and cannot change the official start. The MQL5 weeks clock is reported as a sensitivity.

As-of **2026-11-20**. Live age ≥ 18 months means official start on or before **2025-05-21**. 3 years preferred: on or before **2023-11-20**.

| id | Official start (first live trade/deal) | Months at as-of | Weeks clock (page) | Page “Started” (listing lag) | First cash in file |
|---|---|---|---|---|---|
| 2391620 | **2024-10-23** | 24.90 | 107 weeks (~24.61 mo, implied ~2024-11-01) | 2026.09.16 16:16:30 | 2024-10-21 |
| 2385553 | **2024-12-02** | 23.59 | 102 weeks (~23.46 mo, implied ~2024-12-06) | 2026.08.07 09:01:17 | 2024-11-28 |
| 2394167 | **2024-08-12** | 27.27 | 119 weeks (~27.37 mo, implied ~2024-08-09) | 2026.10.04 03:42:03 | 2024-08-10 |
| 2373216 | **2024-04-19** | 31.05 | 125 weeks (~28.75 mo, implied ~2024-06-28) | 2026.05.12 06:03:29 | 2024-04-19 |
| 2031876 | **2022-11-30** | 47.67 | 208 weeks (~47.84 mo, implied ~2022-11-25) | 2023.08.02 23:38:12 | 2022-11-08 |
| 2389887 | **2024-11-05** | 24.48 | 107 weeks (~24.61 mo, implied ~2024-11-01) | 2026.09.05 03:24:43 | 2024-11-05 |

All six official starts are on or before 2025-05-21 (age bar expected to pass; this does not pre-judge TWR, DD, or replicability). Only 2031876 is past the 3-year preferred date. Listing stamps would fail 18 months for five of the six and cannot be used.

---

## Page reconciliation targets (frozen from t302 cache, 19.11.2026)

Not computed from the tickets. Currency is USD except 2385553 (EUR).

| id | Growth | Profit | Equity | Balance | Initial | Deposits | Withdrawals | Trades | Eq DD | Bal DD | Page weeks |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2391620 | 173.75% | 67,896.18 USD | 80,009.98 | 82,403.14 | 50,037.00 | 401.81 | 35,931.85 | 2,093 | 6.05% | 9.95% | 107 |
| 2385553 | 123.59% | 16,066.74 EUR | 26,723.91 | 29,066.74 | 13,000.00 | 0.00 | 0.00 | 947 | 12.82% | 8.55% | 102 |
| 2394167 | 167.64% | 1,524.18 USD | 1,312.03 | 1,312.03 | 1,088.64 | 2,353.41 | 3,654.20 | 816 | 8.96% | 23.36% | 119 |
| 2373216 | 194.28% | 19,427.88 USD | 27,770.28 | 29,427.88 | 10,000.00 | 0.00 | 0.00 | 513 | 14.41% | 3.63% | 125 |
| 2031876 | 321.01% | 64,216.37 USD | 84,326.35 | 84,220.66 | 20,004.29 | 0.00 | 0.00 | 4,304 | 2.84% | 14.44% | 208 |
| 2389887 | 196.27% | 19,626.82 USD | 29,693.72 | 29,626.82 | 10,000.00 | 0.00 | 0.00 | 242 | 9.02% | 19.35% | 107 |

Siblings already scored in t302 (none over 40%): 2391620 sibling 2391627 DD 6%; 2385553 Australian Arsenal 2385551 DD 10%; 2394167 ids 2394142 DD 22% and 2397478 DD 4%; 2031876 FIC08Milion 2031922 DD 8%; 2373216 and 2389887 none listed. A missing page is not a pass; no new sibling crawl is required unless a local cache already has one.

TycheCerf (CopyFX) is **out of scope**.

---

## House bars (official GO — all must hold)

These are Nadav’s standing bars and the t302 / 22:35 brief, not the tighter 3.5%/5-min standing line from t241. The t241 3.5% monthly and 5-minute hold are reported as sensitivities and **cannot ease** a fail, nor can they tighten an official GO on this round.

A book is an official **GO** only if all of the following hold on the official-start clock:

1. **Live age ≥ 18 months** (official start on or before 2025-05-21). 3 years preferred (on or before 2023-11-20), not required.
2. **Honest monthly TWR ≥ 3.0%.** Deposit/withdrawal-adjusted time-weighted return, rebuilt from the file (closed vendor P&L + cash flows), not vendor “Growth” and not profit/(initial+deposits). Those two are reported as checks, especially on 2391620 and 2394167 (large cash flows).
3. **Equity / TWR-curve peak-to-trough DD ≤ 25%.** Official DD is the vendor-P&L TWR path. If a floating/intra-trade equity path is derivable (mark-to-market of overlapping positions), it is also reported; a floating DD >25% fails even if closed DD is inside the cap. If floating DD is not derivable (missing ticks on some symbols/years), say so and do not invent it. For gold-only or gold-majority risk, use the same Dukascopy XAU mid as t239/t241 when coverage exists. Official DD is max(closed TWR DD, floating DD if derivable). Page equity/balance DD are checks only.
4. **Top-10 close-days share of log-TWR < 50%.** Official is calendar days of closes, not weeks. The t302 top-10 *weeks* figures are flags only and are not a substitute.
5. **No sibling** (same vendor / strategy / author) with published or measured DD > 40%. Use the t302 sibling notes above; do not reopen a closed family.
6. **Not Gold-Reaper / Limitless family** (de-dup below). Also compare the six books to each other and, for gold tapes, to earlier gold candidates already on the box (GR, Limitless, t230 Happy Gold, t231 Cazador gold if a local tape exists). Official close line: **>20%** unique `(open-minute, side)` events (gold) or `(symbol, open-minute, side)` (FX).
7. **Grid / stacking / averaging-down.** Measure max concurrent (book and same-symbol), same-side opens within 1 and 5 minutes, averaging-down count, opposite hedges, cancelled-pending / fill ratio, and lot escalation after losses. Official **FAIL** if both (a) max concurrent same-symbol ≥ 5 and (b) averaging-down count ≥ 20, or if after a losing close the next same-symbol same-side lot is ≥ 1.5× the prior lot on ≥ 20% of such sequences with at least 10 such sequences. Otherwise report as a flag, not an auto-fail. An unbounded grid cannot be a clean GO even if the numeric bars clear.
8. **Replicability** (next section) must pass, including the +1 pip/side stress and hard SL.

Closed-family rule: a numeric pass does not reopen Gold Reaper, Profalgo, Solnce/Kuropatkin, Happy, SARUJA, EdgeTrader, CAZADOR, S1, Kenni, Harmonizer, Black Dragon, Bull/Ofer, LazyPro, NoPain/NoStress. A unique-event match >20% against any of those tapes is official NO-GO.

---

## Replicability gate (official)

On closed trades, after RF recost (t239/t241 method):

- **Gold ≥ 10 bp** average ECN-recosted net per trade. **FX ≥ 5 pips** average net official (majors and crosses). **4 pips is a sensitivity and cannot ease the official bar.**
- **Median hold ≥ 15 minutes** (this brief and S4 of t302). The t241 5-minute line is a sensitivity only and cannot ease a fail.
- **Hard SL:** official PASS if ≥ 80% of closed trades have a visible non-zero S/L price on the ticket (S/L column). For Layout B (no column), a comment `[sl <price>]` counts for that trade only; `[tp …]` alone does not. Below 80%, or no visible stops, is a **FAIL** (hard SL unconfirmed or scarce). Report the exact coverage.
- **+1 pip / side** slippage stress: gold $0.10/oz/side; FX 1 pip/side in the symbol’s pip size. A book that fails the stress is a fail on replicability even if the unstressed average clears.

RF recost (frozen, t239/t241):

- **Gold (XAU*):** ECN cash round-trip $0.31/oz (`CASH_RT_ECN`). Also report Pro $0.24/oz as a sensitivity. File swap is kept on the recosted path as in t241.
- **FX:** cash RT = published ECN commission + a conservative spread. Spreads (pips RT) as t241, extended for symbols in this round: EURUSD 0.8, GBPUSD 1.0, USDJPY 0.8, AUDUSD 1.0, USDCHF 1.2, EURJPY 1.2, EURAUD 1.5, EURCAD 1.5, USDCAD 1.2, EURGBP 1.2, EURCHF 1.2, NZDUSD 1.2, AUDCAD 1.5, AUDCHF 1.5, CADCHF 1.5, AUDNZD 1.5, NZDCAD 1.5, EURNZD 1.5, GBPCAD 1.5, GBPNZD 1.5, GBPAUD 1.5, GBPCHF 1.5, GBPJPY 1.5, CHFJPY 1.5, CADJPY 1.5, NZDCHF 1.5, NZDJPY 1.5, USDMXN 2.0, other FX 1.5. Plus commission of $7/lot/side ($14/lot RT, scaled by inferred contract) if the file commission is zero or rebate-like; if the file already has a non-zero commission, use the file commission and add only the spread. State which rule was applied per book. 2385553 is recosted in **EUR** via the profit-identity pip value.
- Pip sizes: XXXJPY 0.01; XAU 0.10; other FX 0.0001 (USDMXN 0.0001).
- 1 gold pip = $0.10. 1 bp = \(10^4 \times (\text{signed \$/oz net}) / \text{entry}\).

Report average net in bp (gold) and in pips (FX), median hold, hard-SL coverage, and the stressed average, overall and by symbol group.

---

## Direction vs random and timing vs random

N = **2,000** permutations, seed **302302** (direction/side) and **302301** (timing). Official only if a book otherwise looks like a GO (run on all six anyway; they cannot rescue a failed house bar).

- **Direction vs random:** shuffle sides, keep entry/exit times and prices, compare mean recosted net to the real mean.
- **Timing vs random:** for gold, same t239 method on Dukascopy XAU mid (`/workspace/algotrade/data/xauusd_m1_bid_dukascopy_2015_2026.csv.gz` and the 2022–2026 ask file), ±4 hour window, keep hold and side. For FX-only books, run the same test only if a local M1 mid for that symbol already exists on the box; otherwise state **not run / no local FX M1** and do not download a new tape. Direction does not need a mid tape.

A one-sided p-value and the percentile of the real mean in the null are reported. Descriptive if the house gate already failed.

---

## Crash-day check (BD / gold crash dates)

Official dates: the 26 UTC dates in `results_t209/crash_G_ASIA_LONG.csv` (same list as t239/t241). Applies to each book’s **XAU** closed-trade TWR (and to the full-book daily TWR if gold is the majority of risk — official for 2394167 and 2389887; also report for 2391620 and 2031876). Pass bar (descriptive if other bars already fail; official if the book is otherwise a GO): mean daily TWR on crash dates ≥ **−0.10%** and non-loss rate ≥ **50%**. Books with no gold trades (2385553, 2373216 expected) get a full-book daily TWR table on those dates as a descriptive; it is not a fail by itself.

Broker clocks: try offsets 0, ±1, ±2, ±3 hours against UTC; official offset is the default **UTC+2** used for the rest of that book’s UTC work (do not pick the kindest offset after seeing crash-day P&L). State the offset-search as a sensitivity only.

---

## Gold Reaper / Limitless / earlier-candidate de-dup (official)

Compare each book’s closed XAU trades to:

- `/workspace/goldreaper_history.csv` and `/workspace/research_new_component/myfxbook/goldreaper_history.csv`,
- `/workspace/t218_bundle/lim_hist_all.tsv`,
- t230 Happy Gold `results_t230/1862128.history.csv` if present,
- any other local gold candidate tapes already on the box under `results_t218*`, `results_t230/`, `results_t231/`, `results_t239/`, `results_t241/`.

A **match** is a same-side XAU fill whose open time is within 2 minutes and open price within $1 (after zone alignment), or a distinctive comment such as `The Gold Reaper_`. Official close line: **>20%** unique `(open-minute, side)` events. Try offsets 0, ±1, ±2, ±3 hours; official offset is the one that maximises unique-event overlap, stated in the results. Also de-dup the six t302b books against each other. A few coincidental same-minute gold prints are not a close. FX books are compared among themselves on `(symbol, open-minute, side)` with a 3-pip (30-pip JPY) price tolerance, as in t241.

---

## Special focus (frozen before seeing the numbers)

1. **2391620 Van PM:** large withdrawals ($35,931.85 vs $50,037 initial). Does the page Growth 173.75% / 4.18%/mo survive cash-flow TWR? Reconcile 106 Balance + 1 Credit rows to the page cash. t302 flagged 0 trades/week now; last deal endpoint is 2026-11-06. AUDCAD is the largest symbol: report its mean net pips separately (cost is borderline). Layout B pairing quality (unmatched Ins/Outs, open inventory vs page Equity 80,009.98 vs Balance 82,403.14) must be stated. Hard SL is structurally invisible (empty comments, no S/L column) and is expected to fail the 80% bar unless a stop appears in a way the structural peek missed — do not invent one.
2. **2385553 EU Zone Arsenal:** t302 suspected hold-losers / a basket (0 negative months, average loss 1.76× average win, 50-win streak, equity DD above balance DD). Report median hold, swap/year estimate, max concurrent, averaging-down, and how often losers are held longer than winners. Account is EUR. Structurally S/L is empty on 775/947 closed trades — hard-SL coverage will be scored, not assumed.
3. **2394167 Gold EA SL:** page bal DD 23.36% is close to the 25% cap; Oct 2026 was a bad month on the public curve. Closed vs floating DD, top-10 *days*, and gold mean net bp after $0.31/oz and +1 pip/side are the questions that decide it. Structurally S/L is present on 815/816 closed trades.
4. **2373216 Stable Sky:** the cross trio and inactivity since 2026-09-10. Is it an uncapped grid under the H4 rule above? Equity DD 14.41% vs balance DD 3.63% on the page already suggests held floating risk. No new trades after 2026-09-10 in the file: age still counts from official start, but say that the last 2+ months are flat.
5. **2031876 Blue Agressive FIC04:** t302 near-miss (last-12m +1.2%, top-10 weeks 82%). Official top-10 *days* and last-12-month honest TWR from the file may fail even if lifetime ≥ 3%. 13,904 cancelled pendings vs 4,304 fills must be reported. Mixed gold + FX recost.
6. **2389887 Soft Chili:** gold-only, Layout B, t302 negative skew (average loss 5.2× average win). Top-10 days, hard SL (structurally only 29 `[sl …]` comments on Outs), and whether the mean gold net clears 10 bp after RF and stress.

A GO still requires every house bar and the replicability gate. No trading recommendation; the decision is Nadav’s.

---

## Outputs (frozen)

- `/workspace/t302b/PREREG_t302b.md` plus SHA-256, hashed before new P&L.
- `/workspace/t302b/RESULTS_t302b.md` and `t302b_results.json`, plus SHA-256.
- Copies of the six CSVs, the PREREG and the RESULTS (md+json) to `D:\Claude\jev\docs\agents\grok_data\t302b\`.
- An append-only Hebrew summary in `docs/agents/grok_inbox.md` with the PREREG and RESULTS sha256. Do not duplicate if a t302b gate result was already appended in the last hour.
- GO / NO-GO per book with key numbers (age, official start, honest %/mo, closed and floating DD, top-10 day share, avg net bp/pips, median hold, hard-SL coverage, GR unique-event match, crash-day, RF recost, +1 pip/side stress, grid/stacking flags, reconciliation vs the page).
- `SPEC_<name>.md` only on official GO.

The bars in this file do not move: 3.0%/month official (3.5% is a t241 sensitivity only), 25% DD, 18-month age (start on or before 2025-05-21), 50% top-10 log-TWR days, 40% sibling DD, gold 10 bp average net, FX 5 pips average net (4 pips sensitivity only), 15-minute median hold, 80% hard-SL coverage, 20% GR/family unique-event match, the official +1 pip/side stress, and the grid rule in bar 7.
