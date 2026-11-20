# SPEC_HappyNews — clone specification for EA Happy News (Eightcap signal 1864588)

Written 2026-11-13, Asia/Jerusalem, from the t230 MQL5 history (`1864588.history.csv`, SHA `62eb00b2…`) and Dukascopy ticks. For Claude to build an MQL5 clone. This is an empirical recovery, not the vendor’s source. The vendor EA (Happy News v1.6.1, happyforex.de) is the faster path to a RoboForex ECN demo; a clone should be paper-checked against this history before any live use.

**Broker clock:** Europe/Athens (EET/EEST). Verified: pending placements sit a median **2 seconds** before official US 08:30 ET stamps (NFP-like, 72 matches).

**Account constraints:** ECN, raw spread, commission on notional (Eightcap charged ~$7/lot RT on GBPUSD; RoboForex ECN is 20/mio, cheaper). No swap needed for a 5-second median hold. Do not run on Pro / Pro-Cent. Do not copy the MQL5 signal.

---

## 1. Idea

Seconds before a scheduled high-impact release, place a **buy-stop and a sell-stop** on each selected major, a fixed 10 pips from mid, with a 16–20 pip SL and a 100 pip TP. After one side fills, cancel the other, and **immediately manage the SL**: winners are taken as a short-hold locked-in SL (median +3 pips in 5 seconds); losers take the original 16–20 pip SL. Untriggered pendings are deleted ~64 seconds after placement. No martingale, no grid, no overnight. Risk ~1% of balance per fill.

This is a volatility-capture straddle, “regardless of the outcome,” matching the vendor’s published description.

---

## 2. Inputs (empirical values; names follow the vendor changelog)

| Input | Recovered value | Evidence |
|---|---|---|
| `SetPendingSecondsBeforeNews` | **2** | Lead vs matched event: median 2s, mode 2s, 322 of 671 leads at 2s, 234 at 3s. Lead vs :00/:30 clock: median 2s. |
| `PendingDistanceFromPrice` | **10 pips** | 1,200 both-pending cancelled pairs: mode 10.0, median 10.35, p10 10.05, p90 11.65; 856 of 1,200 round to 10. A few 12–16 on wild pre-spikes. |
| Placement SL | **16–20 pips**, typically **18** | 2,400 placement SLs: median 17.9, modes 18 (932), 20 (790), 16 (438). Per-symbol slight variation; a single input of 18 with a 16–20 band covers it. |
| Placement TP | **100 pips, always** | 2,400 of 2,400 = 100.00 pips exactly. |
| `DeleteUntriggeredPendingsAfterNews` | **60 seconds** (observed cancel **63–65s**, median **64s**) | 2,400 cancels: median 64, p10 63, p90 65. The extra 3–4s is likely server/execution, not a 64-second input. |
| Opposite-pending delete | **On fill of one side** (vendor v1.5) | Structural: every pending row in the export is a *cancelled* one (3,668 cancelled = all Buy Stop + Sell Stop rows). Filled pendings appear only as Buy/Sell deals. 82–86 same-minute both-side fills (whipsaw) still occurred, net **+$4,356** — the delete is not instantaneous in a two-tick spike. |
| Post-fill SL modify | **Yes, always.** 100% of 1,697 exits are `[sl]`. Close price **equals** the SL column on every fill. | Winners: median **+3.0 pips**, mean +5.6, p25 +1.0, p75 +9.4, p90 +19.3, max +91.8 (almost the 100-pip TP, but still tagged `[sl]`). Hold median **5 seconds**. Losers (~14.6%): p05 **−17.9 pips**, i.e. the original placement SL. See §5. |
| Lot / risk | **1.0% of running balance** at the placement SL | At 18 pips: median risk 0.984%, mean 1.19%. Lots per $1,000 median: AUDUSD 0.050, EURUSD 0.060, GBPUSD 0.057, USDJPY 0.081 (JPY pip-value calibrated). Corr(lot, balance) = 0.945. No lot step-up after a loss beyond balance growth. |
| Symbols (this book) | **EURUSD, GBPUSD, USDJPY, AUDUSD** | Only these four. Suffix `.i` on Eightcap. |
| One position per symbol per event | Typical | Rare 2-leg same-second same-symbol (9 groups). Four symbols may fire on the same release. |
| Max spread filter | Not uniquely recovered | Vendor claims ECN-compatible. A 20-pip “do not place” cap would be consistent with a news EA but was not identified as a hard cut in this book. |
| Impact filter | **High**, plus a minority of Medium | Of 671 matched clusters: 585 high, 44 medium, 42 low (low matches are likely a better high-impact event a few minutes away, or a “speaks” residual). |

---

## 3. Event universe

1,012 straddle clusters. 671 (66%) matched to a public calendar event inside a 10-minute window; those 671 hold **$98,099 of $104,448** (94% of P&L). 341 unmatched hold $6,349, many after the ForexFactory snapshot ends on 2025-04-07, or at AUD 04:30 / GBP 09:00–11:30 broker times. A clone should use a live ForexFactory (or equivalent) calendar, not a closed snapshot.

**Families by book net $** (names collapsed across FF / US / MT5 labels; one cluster = one event window):

| Family | Clusters | Fills | Net $ | Clone? |
|---|---|---|---|---|
| USD NFP block (NFP, Nonfarm, Unemployment Rate, Average Hourly Earnings — same 08:30 ET print) | 76 | 237 | **43,848** | **Yes, primary** |
| USD CPI (headline, core, n.s.a.) | 36 | 161 | **30,767** | **Yes, primary** |
| USD PMI / ISM (manufacturing, services, prices paid, flash, S&P Global) | 88 | 263 | 6,908 | Yes |
| USD Claims (Initial Jobless Claims / CLAIMS, weekly Thursday) | 104 | 185 | 4,706 | Yes |
| USD PPI | 28 | 90 | 3,171 | Yes |
| USD JOLTS | 22 | 59 | 2,839 | Yes |
| USD rate / FOMC / Fed decision | 31 | 64 | 2,274 | Yes |
| USD Retail Sales (headline + core) | 27 | 80 | 1,753 | Yes |
| GBP / EUR flash Manufacturing PMI | 21+24 | 19+25 | 894+702 | Yes |
| AUD Employment, AUD/GBP/EUR CPI, GBP Retail, some rate speeches | small | small | a few hundred | Optional |
| USD Confidence (Michigan, CB), USD PCE, USD GDP | 44+20+19 | — | **−438, −444, −1,041** | **Optional, off by default.** These three families are net negative in this sample. |
| Unmatched residual | 341 | 254 | 6,349 | Calendar-coverage issue, not a third engine |

Optional vendor filters to implement as inputs, on/off: “include speaks” (a few Lagarde / Bailey / Fed-member clusters exist, tiny $), “forecast ≠ previous.” The latter was not uniquely identified.

Currencies traded follow the pair: USD events fire all four majors; GBP events fire GBPUSD (and sometimes others); AUD events fire AUDUSD at 04:30 broker (00:30 UTC / 11:30 AEDT-ish); EUR flash PMIs fire EURUSD.

---

## 4. Placement algorithm (clone)

For each upcoming calendar event `E` at official time `T` (converted to broker time):

1. If `E` is not in the enabled family list, skip.
2. At `T − 2 seconds`, for each enabled symbol whose currency is affected:
   - Read mid `M` (or bid/ask mid). If a max-spread input is set and `(ask−bid) > cap`, skip this symbol.
   - Place **Buy Stop** at `M + 10 pips`, SL = entry − `SL_pips`, TP = entry + 100 pips.
   - Place **Sell Stop** at `M − 10 pips`, SL = entry + `SL_pips`, TP = entry − 100 pips.
   - Lots: `lots = (0.01 * Balance) / (SL_pips * pip_value_per_lot)`, rounded to the broker’s lot step (0.01). Pip value in account currency. This reproduces the 0.050–0.081 lots/$1,000 table.
3. If one pending fills: **delete the opposite pending immediately**. Modify the filled position’s SL as in §5.
4. At `T + 60 seconds` (or 64s after placement): delete any still-untriggered pending from this event.
5. Do not stack a second straddle on the same symbol while one from this event is open. Other symbols may be open together (four-symbol NFP is normal).

---

## 5. Post-fill SL modify (the residual uncertainty)

This is the only rule that is **empirical, not a single clean input**. Facts that a clone must reproduce:

- 100% of exits are at the SL (`[sl]`), and `close == SL` exactly on every deal.
- Median hold **5 seconds**, p90 82 seconds.
- Winning P&L (85%): median **+3 pips**, a pile-up at **+1 pip** (25th percentile), a long right tail (p90 +19, max +92).
- Losing P&L: the original 16–20 pip SL, hit when the fill never goes into profit.

**Candidate rule, to be fitted on ticks against this history, not treated as final:**

- After fill, if price moves `+1 pip` in favor, jump SL to lock `+1` to `+3` pips (breakeven-plus). Optionally trail behind a fast extreme (the right tail of +10 to +20 pips in a few seconds on NFP is a trail or a delayed lock at a further extreme, not a 100-pip TP).
- If price never goes +1 pip in favor, the original 18-pip SL stands.
- There is **no** evidence of a time-stop other than this fast SL management. There is **no** evidence they wait for the 100-pip TP (only the extreme tail approaches it, and even those closes are tagged `[sl]`).

A first clone can implement “lock +3 pips as soon as +3 is seen, else original SL,” and then fit a short trail on the Happy News tick windows in `results_t230/market/ticks_*.pkl`. The vendor EA already contains the exact modify (changelog v1.5: “modify SL/TP after the pending fills”).

---

## 6. Worked example — 2026-09-04 12:30 UTC (US Average Hourly Earnings / NFP block)

Broker 15:29:58, UTC 12:29:58, event 12:30:00 UTC, lead 2 seconds. Four fills, book net **+$6,170.18** (the book’s single best day).

| Symbol | Side | Lots | Book entry → exit (hold) | Book pips | Book net $ | Dukascopy mid pips | RF conservative BA pips | Entry width (Dukas) | Eightcap entry slip vs mid |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | Sell | 5.20 | 1.16169 → 1.15944 (2s) | +22.5 | +1,133.60 | 33.2 | 30.7 | 3.3 | +8.5 adverse |
| AUDUSD | Sell | 4.36 | 0.72001 → 0.71825 (3s) | +17.6 | +736.84 | 28.5 | 27.2 | 1.1 | +8.6 |
| USDJPY | Buy | 7.36 | 156.134 → 156.677 (3s) | +54.3 | +2,499.26 | 64.6 | 60.5 | 5.2 | +7.4 |
| GBPUSD | Sell | 4.96 | 1.35216 → 1.34846 (9s) | +37.0 | +1,800.48 | 47.0 | 47.0 | 1.7 | +9.5 |

Opposite buy-stops were cancelled ~10 seconds after placement (export close times 15:30:08–09). Book captures *less* than Dukascopy mid and *less* than conservative bid/ask — Eightcap already paid 7–9 pips of entry slip. A clone on RoboForex ECN should assume similar or slightly better fills, not mid-price.

Lots at this date (balance ~$99k): 5.20–7.36, consistent with 1% risk at ~18 pips given each pip value.

---

## 7. Risk, cost, and what a clone will not automatically get

- Gate (RESULTS_t230_happy.md): official RoboForex path **12.87%/month, TWR DD 11.86%**, top-10 remaining 12.09%, direction p=0.0005. Stress at 2 pips/side half-spread: return still 12.23%, **DD 28.67%**. A clone that fills like Dukascopy on ECN is a pass; a clone that pays 2 pips/side at every release is not a 25% DD product.
- The 2-second lead requires a fast calendar and a co-located or VPS-close terminal. If placement is late, both stops can fill (whipsaw) or neither.
- Replicability from the visible trades is **high** except for the exact trail in §5.

SHA-256 of this file: see `SPEC_HappyNews.md.sha256`.
