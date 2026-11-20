# RESULTS t253 — CopyFX full-universe public-stats screen

**Verdict: one public-stats passer, not yet a clone candidate.**  
The only listed book that clears the frozen age / honest-TWR / DD / concentration / floating-loss / closed-family / BD-crash bars is **TycheCerf** (`aaap/47104691`). The sibling rule cannot be fully applied (the card has no `company_client_id`). There is still no public CopyFX trade list, and a read-only MQL5 name search found no signal twin, so the 4–5 pip / median-hold / hard-SL replicability gate was not run.

As-of: **2026-11-14**, Asia/Jerusalem.  
PREREG (hashed **2026-11-14 22:03 IST**, before any universe P&L / monthly / curve-DD / top-10 / crash-day computation): `PREREG_t253.md`, SHA-256 `f287f55cf02052847da754c11494a454ccaf45a9d1de55f18be2804d14968303`.

Read-only throughout. No CopyFX or MQL5 sign-up, follow, copy, or subscribe. Fresh card series were pulled the same evening (~22:07–22:10 IST). 623 × 5 endpoint files, **0 errors**.

---

## 1. Coverage versus t224 / t226 / t232

| Round | What was actually listed | What was curved |
|---|---|---|
| t224 | Discovered the public `POST https://roboforex.com/api/copy/*` surface (no login). Method paper, not a full census. | Selected cards only. |
| t226 | Token `getRating` crawl. **1,353** unique keys. The write-up treated `match` as required (≥3 characters). | Priority long-book subset. |
| t232 | Re-screened that **1,353**-book inventory at the 1.5-year bar (as-of 2026-11-13). **21** books had listing age ≥1.5y, card monthly ≥3%, and card `dd_max` ≥ −30%, and were fully curved. **No CopyFX passer.** (The only numeric 1.5y “pass” that round was an MQL5 card, Kenni, closed by a sibling with DD 60.85%.) | Those 21. |
| **t253 (this round)** | `match` omitted; `period` 0; platforms `mt4+mt5+rst`; `limit` 500; walk `offset` until `more=false`. Coverage pass with `deal_count` and `subscriber_count` sorts as well as `profit_percent`. All three sorts returned the **same** 5,022 keys (no extras). | Every age-eligible book with card `dd_max` > −25%, plus all same-client siblings of any age. |

**Listed universe on 2026-11-14: 5,022 unique `source_id/login` keys.**

Versus the t226 inventory of 1,353:

- 1,320 keys in both
- **3,702 new** listed books
- 33 t226 keys gone from the public rating

Age-eligible (registration on or before **2025-05-14**): **1,340** (MT4 1,122, MT5 196, RST 22). Of those, **972 were not in t226**. Two t226 age-eligible keys have since left the rating.

t232’s 21 curved books are a subset of the old inventory. **TycheCerf and all three near-misses below are new versus t226 and t232** — they were never in the 1,353-key token crawl, so t232 could not have screened them.

Prefix counts on the 5,022: `bbba` 1,399, `bbbc` 598, `bbbb` 458, then the `aaa*` prefixes (largest `aaay` 224 … `aaah` 54) and `ccca` 50 (RST). Platforms: MT4 2,517, MT5 2,455, RST 50.

---

## 2. Screen funnel

Bars (frozen in the PREREG): age ≥ 18 months; honest cash-flow TWR monthly ≥ 3% (flag ≥ 3.5%); max of TWR-curve DD, `getDdMax`, and worst equity−balance gap ≤ 25%; top-10 days < 50% of log-TWR, with residual monthly still ≥ 3%; share of days with ≥ 2% floating loss < 30% to pass (30–50% flag / near-miss at best; ≥ 50% fail, SARUJA-like); no sibling of the same `company_client_id` with DD > 40%; not in a closed family (list now includes SARUJA); no BD crash-day daily TWR ≤ −25% (26 dates; a day ≤ −10% is a flag only). Leverage-ups (balance jumps ≥ 15%) are flags, then checked against that day’s TWR so a winning day is not mistaken for a deposit.

**Card-`dd_max` pre-filter (stated in the PREREG):** 904 of the 1,340 age-eligible books already have card `dd_max` ≤ −25% (706 ≤ −40%). Card `dd_max` understates curve DD except in rare cases (S1). A curve cannot help those 904 pass, so they were tallied as DD fails without a full official series. This is slightly narrower than “pull every age-eligible book” and is consistent with t232 practice.

436 age-eligible books had card `dd_max` > −25%. 30 of those have a headline (card-yield) monthly ≥ 3%; 24 ≥ 3.5%. The fetch set was those 436 plus their same-client siblings of any age = **623** books (86 of the siblings are younger than 18 months). 161 of the 436 have **no** `company_client_id`, so the sibling rule is incomplete for them.

Of the 904 card-DD rejects, 103 were still fetched as siblings of a potential book and classified on their curves. The remaining 803 unfetched aged books are `fail_card_dd` (801) plus two unfetched closed-family name hits.

Classification of all **1,340** age-eligible listed books:

| Class | n |
|---|---|
| `fail_card_dd` (unfetched; card already ≤ −25%) | 801 |
| `fail` (fetched, hard bar) | 528 |
| `closed_family` (fetched) | 5 |
| `closed_family_unfetched` | 2 |
| `near_miss` | 3 |
| `passer` | **1** |
| Fetched aged (check) | 537 (= 623 − 86 young sibs) |

Fail-tag counts among fetched classifications (a book can carry more than one tag): concentration 534, monthly 486, curve/getDdMax/gap DD 247, sibling DD 189, hold-loser ≥ 50% 39, closed family 5, BD crash-day ≤ −25% 3. (The two unfetched SARUJA-name books add two more `closed_family` tags in the all-aged tally, total 7.)

Closed-family hits this round: EdgeTrader (`aaac/7247505` Phoenix, `aaaq/73020704` EdgeTrader Prime), Solnce (`aaaq/73023319`), CAZADOR (`aaav/24201152`), S1 (`aaay/35058148`), and two unfetched name hits on **GlobalTraders88** (`aaak/38038627` “Saruja EUR Pairs”, `bbba/37163052` “Saruja EA Trade”). Official SARUJA cards `aaaa/21596244` and `aaab/22749275` are younger than 18 months, so they are not in the aged funnel; they remain closed from t251.

---

## 3. Passer — TycheCerf (`aaap/47104691`)

Card: https://roboforex.com/copy-trading/rating/aaap/47104691/

| Field | Live public card + official series, 2026-11-14 |
|---|---|
| Name / strategy | TycheCerf / **TycheCerf_cent** |
| Platform | MT4 ProCent (`group` `my-cent-U`), USD, **is_cent true**, leverage **1:2000** |
| Fee / offer | **10%** of profit, weekly (`period` 604800, scheme 1). Offer only since **2026-09-27** (the book itself is older). |
| Min equity / copiers | $100 / **6** |
| `company_client_id` | **None** — sibling rule **cannot be fully applied**. Only one listed book matches the name TycheCerf / Cerf. |
| Registration | 2023-12-19 (curve starts 2024-01-18 at balance $10.35) |
| Official start used for age | **2023-12-19** (earlier of registration and curve) |
| Age | **34.86 months** — pass (≥ 18) |
| All-time official TWR | **+1,956.24%** (profit $195.81, end balance $206.34, ATH 2026-11-10 at the same TWR) |
| Honest monthly | **+9.06%** — clears the 3.5% standing bar |
| Stricter DD | **−19.37%** (`getDdMax` 2024-02-15). Curve peak-to-trough **−15.28%**. Worst equity gap **−19.28%** on 2025-01-10 (equity $42.12 vs balance $52.18). |
| Top-10 share of log-TWR | **39.74%** — pass. Residual TWR **+505.65%** → residual monthly **+5.30%** (still ≥ 3%). |
| Floating-loss days (≥ 2%) | **8.84%** of 362 equity days — low (well under 30%). |
| BD crash days (26 dates) | 9 overlaps; worst **2026-08-27 −0.15%**. 2026-10-12 was **+5.28%**. No ≤ −10% flag. |
| Deals / symbols | **341** closed deals: EURUSD **319**, GBPUSD 20, BTCUSD 2. Card description: “scalping & intradaya”. |
| Avg profit / deal | **$0.57** (API `profit_usd` / `deal_count`; already in USD on a cent book — **not** a pip or bp figure). ≈ 9.8 deals/month. |

**Leverage-ups.** The automatic ≥15% balance-step flag fires once, on 2024-01-24 ($11.76 → $13.62, **+15.82%**). That day’s official TWR is **+15.77%** (unexplained +0.04 pp). It is a winning day already inside the top-10, not a deposit. A later 2026-10-15 step (+12.78% balance vs +9.58% TWR, unexplained +3.19 pp) is a possible modest cash-in, not a size jump. Several large TWR days coincide with a flatter balance path (withdrawals and/or equity vs balance). No material leverage-up is visible from the daily official series.

**Caveats that keep this a public-stats passer, not a live or clone candidate:**

1. Missing `company_client_id` — a same-operator book with DD > 40% would not be linkable by the published field.
2. Cent account, tiny absolute dollars (start ~$10, now $206), 1:2000 leverage, copy offer only ~7 weeks old, 6 subscribers.
3. No public tickets (same finding as t252: the logged-out card has Overview + Stats only; undocumented trade endpoints 404/405). Replicability — FX majors 4–5 pip net, median hold ≥ 5–15 min, hard SL — **cannot be scored**.
4. Average $0.57/deal cannot be converted to pips without lots and prices. “Scalping” in the blurb plus a 1:2000 cent book is a reason to wait for tickets, not a reason to loosen the bar.

**MQL5 name search (read-only, no login):** no public user or signal named TycheCerf. `https://www.mql5.com/en/users/TycheCerf` returns 404. Site-restricted search and the public MQL5 search page returned no signal, author, or product under that name. `tychique1998` is an unrelated MQL5 profile with no signals and is not a twin. **No MQL5 ticket export path** is available via the approved read-only `maestro_nb2026` session for this book.

---

## 4. Near-misses (ranked by honest monthly)

Near-miss, as frozen in the PREREG: age-eligible, honest monthly ≥ 3%, and only one or two *narrow* fails (DD 25–35%, top-10 50–70%, floating 30–50%, sibling DD 40–50%, residual monthly just under 3%). Three books qualify. None is a passer.

### 4.1 JMao / Lucky Cat — `aaap/47131749`

https://roboforex.com/copy-trading/rating/aaap/47131749/

MT4, leverage 1:1000, fee 25% weekly, 44 copiers, `company_client_id` **28899**. Age **18.30 months** (reg 2025-05-06). Official TWR **+456.03%** → honest monthly **+9.83%** (clears 3.5%). Stricter DD **−23.12%** (curve; `getDdMax` only −10.96%; equity gap a mild −2.35%). Top-10 **48.67%** (just inside the bar); residual monthly **+4.93%**. Floating-loss share **1.21%** (330 days). 1,714 deals, **XAUUSD only**. Avg profit **$0.27**/deal. Balance $556.46, profit $456.17.

**Narrow fail: sibling DD.** Same client, `aaao/46158149` JMao / “Lucky Cat MT4” (https://roboforex.com/copy-trading/rating/aaao/46158149/), registered 2026-05-06, card `dd_max` only **−13.13%**, but official **curve DD −41.41%**. That is inside the 40–50% near-miss band and **fails the sibling bar**. Two younger siblings exist (`bbbb/77059111` Yen Hunter, `bbbc/52033802` Gold Hunter) with modest card DD; they do not change the family result.

**Flag:** BD 2026-04-23 daily TWR **−13.7%** (≤ −10%, not a −25% fail). `getDdMax` trough is the same date.

**MQL5 name search:** a public signal **Lucky Cat** / **Lucky Cat MT5** is published by Jian Tu (`tenh`), XAUUSD, $39/month — [Lucky Cat MT5](https://www.mql5.com/en/signals/2359404) (started 2026-02-14, 772 gold trades) and an MT4 “Lucky Cat” on the same author page. Deal counts and start dates do **not** match the CopyFX book (1,714 deals from 2025-05-06) or the “Lucky Cat MT4” sibling (919 deals from 2026-05-06). This is a **name-alike, not a confirmed twin** of client 28899. Even if a later approved export confirmed the same operator, the CopyFX sibling curve DD of −41.41% would still fail the family bar.

### 4.2 Diamondhill / Diamondhill — `aaac/72170338`

https://roboforex.com/copy-trading/rating/aaac/72170338/

MT4, leverage 1:500, fee 20%, 42 copiers, `company_client_id` **39585** (no listed sibling). Age **18.27 months** (reg 2025-05-07). Official TWR **+425.33%** → honest monthly **+9.51%** (clears 3.5%). Stricter DD **−17.37%** (curve; `getDdMax` −13.18% and equity gap −11.04% on 2025-06-10). Floating-loss share **6.82%**. 810 deals: XAUUSD 641, GBPUSD 136, BTCUSD 2. Avg profit **$3.98**/deal. Balance $3,896.94, profit $3,227.05. Worst BD overlap 2026-04-23 **−4.62%**. Three ≥15% balance steps (flag only).

**Narrow fail: concentration.** Top-10 share **61.75%** (inside the 50–70% near-miss band). Residual TWR still **+88.60%** → residual monthly **+3.53%** (the residual itself would clear 3.5%). That is why this is a near-miss rather than a hard fail: growth is lumpy, but it is not a two-day book.

**MQL5 name search:** no public signal or user named Diamondhill. Third-party commentary has linked the CopyFX name to a gold EA also used on “Short Stop Is Law” (Kuropatkin, already a concentration + sibling fail in this universe). That is not a ticket-export path.

### 4.3 VolantFX / VolantFX Dynamic — `bbbb/7770061`

https://roboforex.com/copy-trading/rating/bbbb/7770061/

MT5, leverage 1:500, fee 20%, 1 copier, `company_client_id` **5098** (no listed sibling). Age **39.20 months** (reg 2023-08-09). Official TWR **+240.08%** → honest monthly **+3.17%** (clears 3%, **does not** clear the 3.5% standing flag). Stricter DD **−22.24%** (`getDdMax` 2024-10-17; curve −18.43%; equity gap −19.01% on 2023-11-28). Top-10 share **45.30%** (under 50%). Floating-loss share **9.94%** of 905 days. **40,832** deals, mostly EURUSD 34,114, then GBPUSD 2,158, GBPCAD 1,474, XAUUSD 1,202, and smaller FX. Avg profit **$0.51**/deal. Balance $30,835.39, profit $20,630.10. Worst BD overlap 2026-06-05 **−2.62%**. Four ≥15% balance steps (flag).

**Narrow fail: residual monthly.** Removing the top-10 days leaves residual TWR **+95.27%** → residual monthly **+1.72%**, under the 3% residual bar. High deal count looks more inspectable than most CopyFX books, but without tickets we cannot tell whether the EURUSD mass is a seconds/latency scalp (Happy-class) or a hold-able edge.

**MQL5 name search:** no public signal or product named VolantFX or “VolantFX Dynamic”.

---

## 5. What this changes versus prior rounds

- The listed CopyFX universe is **about 3.7× larger** than the t226 token census (5,022 vs 1,353). Omitting `match` and paginating until `more=false` is the complete public method; t226’s “match required” note is incomplete as of 2026-11-14.
- After a full age + honest-TWR + curve-DD + concentration + floating + sibling + closed-family + BD screen, the public rating still yields **only one** stats-level passer, and that passer is a small MT4 cent book with no client id and no tickets.
- TycheCerf, JMao/Lucky Cat, Diamondhill, and VolantFX were all **invisible** to t226/t232. Finding them is new work, not a re-score of the old 21.
- Books that t232 already curved (Intraday gold, Bollinger AI, MaxForexShark, CAZADOR, Solnce, EdgeTrader Prime, Kuropatkin, Wallstreet gold, etc.) **still fail**, for the same structural reasons (curve DD, concentration, siblings, closed families). No prior fail was reversed.
- SARUJA remains closed (t251/t252). The hold-loser floating-share test, added after SARUJA, rejected 39 aged books at the ≥50% line; the one passer is at 8.8%.
- Replicability is unchanged as a bottleneck: CopyFX still does not publish a priced trade list when logged out. An MQL5 twin would have been the practical export path; none exists for the passer.

Next useful step for TycheCerf, if Nadav wants to go further, is **not** a CopyFX follow. It is either (a) wait for a confirmed public trade list / MQL5 twin, or (b) a separately approved, read-only inspection of something that actually publishes tickets. Until then this is a public-stats lead, not a system for the portfolio.

---

## 6. Method notes and artifacts

Honest monthly = `(1 + TWR/100)^(1/months) − 1` with `months = (as-of − official start) / 30.4375`. Daily simple return `r_i = (y_i − y_{i−1}) / (100 + y_{i−1})` on the official `profit_percent` series. Curve DD is min(index / running peak − 1) on `index = 1 + y/100`. Stricter DD is the worst of that curve, `getDdMax` (percent/100), and the worst same-day `(equity/balance − 1)`.

Endpoints (confirmed in t251/t252, used again here): `POST /getRating`, `/ratingCard/getAccountStats`, `/ratingCard/getDdMax`, `/account/chart/profit_percent`, `/account/chart/balance_equity`, `/account/chart/symbols`. Base `https://roboforex.com/api/copy`. No `my.roboforex.com` (login wall). No register / partner / “copy now”.

PREREG was not altered after the hash.

Artifacts under `results_t253/`:

- `PREREG_t253.md` and `.sha256`
- `inventory_listed.json`, `universe_listed.json` (charts stripped)
- `raw/rating/getRating_{sort}_off{N}.json`
- `raw/cards/{source}_{login}_{stats,profit_percent,ddmax,balance_equity,symbols}.json` (623 × 5, `fetch_errors.json` empty)
- `classified_aged.json`, `passers_nearmiss.json`, `gate_results.json`
- `aged_keys.json`, `potential_keys.json`, `fetch_keys_priority.json`

This file: `RESULTS_t253_copyfx_universe.md`. SHA-256 is written next to it after the hash is computed.
