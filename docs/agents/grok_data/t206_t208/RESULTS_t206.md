# RESULTS_t206 — broad platform search, any style

Round t206. Authorization `[pt208u]`: Nadav did **not** ask for a grid-specific
search; grid is simply **not a reason to reject**. This round goes back to a
broad search for profitable systems of any type (trend, breakout, mean
reversion, grid, news, crypto, indices, commodities), with grids judged on the
same numbers as everything else.

Each name is judged alone (no portfolio mix). Public access only. Unique t206
files; t202–t205 were not overwritten. Accounts already in the t202–t205
shortlists were **skipped**, not re-litigated.

## Verdict

**No new public book passes all four filters** (verified real, ≥ 18 months
honest age, ≥ 3.5%/month on **Abs. Gain**, max **equity** DD ≤ 30%, top 3
months < 50% of dollar profit). The printed "Monthly" and MQL5 "Growth since
YEAR" figures continue to be unreliable: Gain vs Abs gaps, inflated Weeks vs
Started, and "80% of growth in N days" warnings take almost every 5%+-looking
name off the list.

The closest *new* honest long track is **SFE Impulse** (BTC+ETH, Started
22 Aug 2023, 38.7 months genuine, Abs **2.85%/month**, equity DD **7.88%**,
no concentration warning) — under the 3.5% bar, and currently −9.7% this
month. Two crypto/multi-asset books clear 3.5% Abs and 18 months and equity
DD, but both carry the MQL5 **80%-in-N-days** stamp (**Crypto Trading Pepper**,
**Techno Long Term**). A Brazilian WIN-futures book (**Portifolio IA XP**)
hits 7.6%/month honest Abs at 28% equity DD, but it is not a RoboForex
instrument and one trade is 35% of all profit.

**No cost-screen file, no PREREG, no backtest.** Nothing new is both inside
the filter and a decodable single rule. Already-failed families (gold S/R,
goldfade, London FX breakout, carry, BTC MR, NR7/ID at 5%/25% size, JLC news
1-min at size, AUDCAD_ENV_GRID_T205) were not retested.

For context only, not re-opened: **Carla Mt4** (4.65% Abs, 26.6% DD, 45 mo)
and **EdgeTrader** (4.01% Abs, 15.3% DD, ~26 mo, Gain = Abs) would still sit
on the right side of this looser 18-month / 3.5% / 30% DD filter. They were
in t202/t204/t205 and stay skipped. Carla's history is still private;
EdgeTrader had no published entry rule.

## Filter and search surface

- 3.5%/month compound for 18 months is Abs ≥ **85.7%**; for 24 months ≥ 129%;
  for 36 months ≥ 246%. Site "Monthly" is ignored when Abs is available.
- Honest age: Myfxbook first-trade / analytics years; MQL5 **Started**, not
  Weeks (the inflation issue is unchanged). Trading-days ÷ activity% is used
  only as a cross-check.
- Equity DD, not balance DD, is the 30% cap.
- Grid is allowed. It is still judged on Abs, equity DD, age, and concentration.

**Searched this round (beyond t202–t205 lists):**

| Surface | What was read | What came back |
|---|---|---|
| **Myfxbook** `/systems?drawValue=30&ageValue=547&accountType=2&lastTraded=30&size=40` (18 mo, DD≤30%, Real) **page 1 and page 2** | 40 + 24 names. Page 2 is already ≤ 3.41% printed monthly. | New hooks: BIGFISH ENR, Mtrader XM2, Wisdom EA, GOLD Copy, Advicefx, SMART MONEY, Elysium, W3, Max. After Abs: **all fetched names fail** (Wisdom Abs 9.5%, BIGFISH Abs 25%). |
| Same list, `?sort=absGain` | WebFetch returned the marketing shell, **no table** | Needs a browser. See § scrape. |
| **MQL5 Signals MT5** sorted by growth | Growth list + individual pages for RAZOR, Deux ex machina, Crypto Pepper, Gold Minion, Harmonizer, SFE Impulse, Techno Long Term, Portifolio IA XP; Started dates for OnlyUJ, GOLD HUAT | Weeks inflation is still the default. Genuine long Starts: Pepper (May 2022), SFE (Aug 2023). |
| **MQL5 MT4 list** | Not a separate clean table from this fetch (same catalogue shell) | Browser if a distinct MT4 sort exists. |
| **Myfxbook "most popular"** | Seagull, Beetle, FXStabilizer, AGI EA, Snail (−99.9%), The Money Tree | Popular ≠ Abs. Seagull / FXStabilizer / Beetle were already grid-rejected on *style* in t202; this round they would still need Abs and equity DD. Not re-fetched individually (known grid-popular names, not new). |
| **Forex Factory** | Public threads; no 18-month Trade Explorer book matching 3.5%/30% | The "Verified Profitable EA" thread is ~11.5 months. Trade Explorer is JS. |
| **TradingView** strategy authors | No live *broker-verified* 18-month 3.5% Abs book from a public fetch | Browser. Paper / strategy-tester curves are not "verified real." |
| **Bybit / Binance / Bitget** copy-trading leaderboards | Bybit official board is **7 / 30 / 90-day**, not 18-month ROI+MDD | URLs in § scrape. Crypto Pepper and SFE Impulse above are the long public crypto tracks we *could* verify on MQL5. |
| **Reddit r/algotrading** | 2025–2026 posts are week-scale gold scalps or ~8-month copy bots | No 18-month Myfxbook-verified 3.5% track. |
| **X** | Not a verifiable 18-month ledger by itself | Would need a linked Myfxbook/MQL5, which would already be in the lists above. |

## Candidate table (new names only)

Ages as of 12 Nov 2026, Asia/Jerusalem (UTC+2). Abs %/mo is compound on
profit / deposits (or Abs. Gain), not Growth and not site Monthly.

| Name | Link | Honest Abs %/mo | Honest months | Equity DD | Concentration | Style | Verdict |
|---|---|---|---|---|---|---|---|
| **SFE Impulse** | [2049326](https://www.mql5.com/en/signals/2049326) product [104102](https://www.mql5.com/en/market/product/104102) | **2.85%** (€1,963 / €1,000, deposits €0; Growth 256% is a bit higher because of €1,150 withdrawals) | **38.7**, Started **22 Aug 2023** = Weeks 167 (match, VERIFIED) | **7.88%** (balance 27.95%) | No 80%-in-N-days warning | BTCUSD 439 + ETHUSD 541, hold **6h**, WR 58%, PF 1.37, avg win €12.91 ≈ avg loss €12.97 (SL-like, **not** a grid), 100% algo, activity 10%, leverage **1:30**, 9 trades/week. Author SmartForexExpert / Joel Juanpere. Currently **−9.70%/month**. Reviews: needs Saturday crypto; weak in low-volatility June 2024 | **Closest new honest book. FAIL 3.5%.** Not a PREREG: under the bar, and BTC mean-reversion was already failed as a family; this looks more like a selective impulse/breakout, but the live Abs is 2.85% and fading. Product page did not resolve to a numeric rule via WebFetch (Market catalogue shell). |
| **Crypto Trading Pepper** | [1521998](https://www.mql5.com/en/signals/1521998) | **~5.66%** ($96,962 / $5,000, deposits $0; Growth 2,157% close to Abs 1,939%) | **54**, Started **11 May 2022** = Weeks 236 (match, VERIFIED) | **7.73%** (balance 46.97%) | **FAIL: 80% of growth in 16 days** (0.97% of 1,651 days) | BTCUSD 1,650 + ETHUSD 467, hold 21h, WR 47%, PF 1.18, best +$4,981 / worst −$1,924, deposit load 100%, 97% algo. Valeriia Mishchenko (valerytrading.com). Currently **−13.94%/month**, annual forecast −100% | **FAIL concentration.** Return and age and equity DD would otherwise pass. Not a stable 5.7% machine. |
| **Techno Long Term** | [2307342](https://www.mql5.com/en/signals/2307342) | ~10.5% over 18 mo (profit €2,035 / €401) | Started **5 May 2025 (18.2 mo)**; Weeks 114 and a 794-day lifetime are a bit longer | 13.77% (bal 38.63%) | **FAIL: 80% in 17 days** (plus a 6-day warning on listing day) | Multi-strategy, author "no martingale / no grid / SL on every trade": XAUUSD 1,457 (ATR SL, breakout component **added Apr 2026**), US30, USTEC, BTC, US500, hold 57 min, WR 69%, PF 1.22. New EA added Feb 2026; holiday pause Dec 2025; several mid-stream risk cuts. Currently −5.34%/month | **FAIL concentration**, and the rule is **not frozen** (components added during the live window). 4,869 trades, not one decodeable entry. |
| **Portifolio IA XP** | [2283635](https://www.mql5.com/en/signals/2283635) | **7.61%** (Growth = Abs, deposits 0, withdrawals 0, +394%) | **21.8**, Started **18 Jan 2025** ≈ Weeks 106 | **28.02%** (bal 47.42%) | Monthly UNKNOWN; **one trade = 35% of lifetime profit** | B3 **WIN** mini-Ibovespa futures (WINJ/M/V/Q/G/Z), leverage **1:1**, hold 1h, WR 49%, PF 1.16, 1,804 trades, XP MT5. "IA" portfolio, 98% algo | Hits return, age, and (tightly) equity DD, but **not an RF CFD** and not a simple rule. Do not backtest on Dukascopy FX. |
| **BIGFISH ENR** | [11548224](https://www.myfxbook.com/members/ophili/bigfish-enr/11548224) | **Abs +25.32% vs Gain +530%** ≈ 0.9–1.3%/mo | Analytics years 2024–2026; streaks from mid-2025 | 25.75% | UNKNOWN (year tabs not expanded). This Year +84.90% Gain, −155 pp vs last year | **AUDCAD averaging** (Best Symbol AUDCAD in every session), 2d hold, WR ~79%/70%, avg win 27 vs loss 60 pips, Z **−11.72**, basket-like losing closes in 1–7 seconds, 641 trades, PF 1.74, INFINOX 1:500 MT4. Author ophili / Trendkings, Nigeria. Many sibling books at 32–67% DD | **FAIL Abs.** Grid is allowed; 1%/month is not the target. Same AUDCAD-basket shape as Carla/NoPain, much worse honest return. |
| **Wisdom EA (Axi Select)** | [10998658](https://www.myfxbook.com/members/eaforexcenterII/wisdom-ea-axi-select/10998658) | **Abs +9.52%** ($1,755 / $18,433 dep.) | ~26–38 mo | 28.75% | This Year +119% Gain is not Abs | Multi-symbol automated, Sydney/EURCHF-heavy, also USOIL and gold, hold 4h44, WR 82–85%, PF 1.43, Z −8.16, commissions −$1,319, Interest −$100, 777 trades, Axi 1:100 MT4. Already called out as deposit-distorted in t202 | **FAIL Abs.** |
| **RAZOR EA** | [2300694](https://www.mql5.com/en/signals/2300694) | 1.15%/mo if the 206 weeks were real; 5.9% if only the 9.5 mo since Started | **Started 29 Jan 2026**; Weeks 206 is the t202 inflation pattern | 15.26% | — | NZDCAD 783, AUDCAD 550, AUDNZD 454, 2d, WR 74%, PF 1.98. Reviewer: "Fair grid system." 94% algo | **FAIL age and/or Abs.** Grid OK; numbers are not. |
| **Deux ex machina** | [2271402](https://www.mql5.com/en/signals/2271402) | **1.23%/mo** over 24 mo (Abs 34% on €21,170 deposits; Growth 6,559% is withdrawal-distorted) | Started 15 Nov 2024 (24 mo); author claims 2021; trading-days 556 / 27.68% ≈ 5.5 y | **25.99%** | — | AUDCAD 1,095 + AUDNZD + NZDCAD + US30 + gold. Reviews: no SL, "adding" on AUDCAD, strategy changes, long quiet periods. Monthly growth **1.96%** | **FAIL Abs.** Equity DD would pass. |
| **Harmonizer High Risk** | [2394758](https://www.mql5.com/en/signals/2394758) | 0.8%/mo over ~25 mo of possible loaded history (Abs 22%) | **Started 8 Oct 2026**; Weeks 109 inflated | 6.75% (balance maximal 31.32%) | — | Author on the page: **"This strategy uses grid!"** AUDCAD + NZDCAD only, 3d hold, WR 66%, PF 1.94, 100% algo, High Risk preset of Harmonizer EA | **FAIL Abs / age.** |
| **Gold Minion** | [2351061](https://www.mql5.com/en/signals/2351061) | 2.76%/mo over 36 mo, or 9.8% over 10.5 mo | Started 30 Dec 2025; Weeks 158 inflated | 7.51% | t202 already put it in the 80%-in-N-days class | XAUUSD only, 11h, WR 57%, PF 1.73, 94% algo, many "no trading for 6 days" warnings | **FAIL age and/or return.** |
| **GOLD Copy Trading** | [ScalperAiAlgo](https://www.myfxbook.com/members/ScalperAiAlgo) | sibling Abs 41% vs Gain 122% | Member joined **21 Jun 2025 (~5 mo)** | 24–33% | — | Gold, 8k+ trades on a short book, Z −22, bio "No DRAWDOWNS!" is false | **FAIL 18 months.** |
| OnlyUJ, GOLD HUAT | [2245675](https://www.mql5.com/en/signals/2245675), [2376856](https://www.mql5.com/en/signals/2376856) | not fully Abs-audited | Started **25 Jul 2024 (15.5 mo)** and **7 Jun 2026** | — | — | — | **FAIL 18 months.** |
| Mtrader XM2, Advicefxrobot, SMART MONEY, Elysium #4, W3 S2 R, Max | page-1 hooks, monthly 3.4–7.2% printed | Abs **UNKNOWN** | in the 18-mo list | ≤30% printed | Max yearly +115%; W3 yearly 0% | Mtrader's public profile is full of **Mtrader grid4** siblings, including −86%/94% DD. IDs not in the profile fetch | Not promoted until Abs is read. Browser URLs below. |

## Decodes (top new books)

**SFE Impulse.** Live book is a selective BTC+ETH system, 6-hour average hold,
roughly even dollar wins and losses, 58% WR, 10% time-in-market, 1:30 leverage
(low). That is the opposite of a grid: losses are taken, activity is sparse,
and the account never needed high leverage to post 2.85%/month. The MQL5
product (104102, SmartForexExpert) did not yield a numeric entry/stop rule
from the public Market fetch (the URL opened the general catalogue). Reviews
say it does well in high-volatility regimes and poorly in quiet ones — a
breakout/impulse story, ASSUMED, not VERIFIED as a freezeable rule. Current
month −9.7%. **Not cost-screened or pre-registered:** it is under the 3.5%
filter, and a BTC family was already failed at high-return size. RF crypto
swap and spread would have to be charged if this were ever tested; that work
is not started here.

**Crypto Trading Pepper.** Same two symbols, longer hold (21h), lower WR
(47%), thin PF (1.18), 4.5-year genuine age, huge dollar P&L on a $5k seed
with **no further deposits** (honest compounding). The MQL5 stamp "80% of
growth in 16 days" means the lifetime 5.66%/month is not a repeatable monthly
edge — it is a short explosive window plus a long grind, and the book is now
−14% this month. Mechanic not published as a single entry rule (author has a
suite of EAs). **FAIL concentration;** no PREREG.

**Techno Long Term.** Explicit public mechanic *family*: several rule-based
EAs in parallel, hard SL, no grid, gold ATR stops, an XAUUSD breakout leg
that was **added in April 2026**, a second EA added in February 2026, holiday
off-switch in December 2025. That is a changing portfolio, not a frozen
spec. The 80%-in-17-days warning and the mid-stream changes are enough to
stop a t206 PREREG even if concentration were forgiven.

**BIGFISH ENR / RAZOR / Deux ex / Harmonizer.** These are the AUDCAD–NZDCAD
averaging family (Harmonizer's author says "grid" in so many words; RAZOR's
reviewer says "fair grid"; BIGFISH basket-closes in seconds on AUDCAD;
Deux ex reviews describe adding on AUDCAD with no SL). Grid is allowed
this round. Their **honest Abs is 0.8–1.3%/month** after deposits, at 15–26%
equity DD — the same disappointing Abs we already measured on the long
ToTheMoon/NoPain track (~2.3%) and on AUDCAD_ENV_GRID_T205 (~2% only on a
zombie path). No new decode, no new backtest.

**Portifolio IA XP.** Intraday B3 WIN futures, 1:1, 49% WR, PF 1.16, one
outlier win at 35% of lifetime profit. No RF mapping, no Dukascopy WIN tape
on the box, no PREREG.

## Cost screen and backtest

**None.** The frozen method is cost-screen → hashed PREREG → P&L only when a
rule is inside the filter and decodable. That gate was not met. No
`COST_PRESCREEN_*t206*`, no `PREREG_*t206*`, no `code/backtest_t206*`, no
`results_t206/`.

A qualitative RF note, not a screen: SFE Impulse and Crypto Pepper trade
BTC/ETH with 6–21h holds, so RF crypto **swap and commission** would be
material on a real test, and Saturday-session reviews already flag broker
differences. BIGFISH/Harmonizer-style AUDCAD baskets pay the same short-swap
tax computed in t205 (a 3-day Wednesday-inclusive short ≈ 37% of a 12-pip
win). None of that was turned into a ratio, because none of those names was
advanced.

## URLs that need a browser scrape (public, no login unless noted)

These are the holes WebFetch could not fill. A logged-in scrape is marked.

1. **Myfxbook sort by Abs. Gain, by profit, and by age**, pages 1–5, same
   18-month / DD≤30% / Real filter:
   `https://www.myfxbook.com/systems?drawValue=30&ageValue=547&accountType=2&lastTraded=30&size=40`
   — `?sort=absGain` returned no table to WebFetch. Page 2 of the default
   (Gain) sort is already under 3.5% printed monthly, so a *Gain* page 3–5
   is unlikely to add a 3.5% Abs name; an **Abs-gain sort** still might.
2. **Monthly Analytics year tabs** (top-3 month share) for: BIGFISH ENR
   `…/11548224?tab=monthly`, Wisdom `…/10998658?tab=monthly`, and any Abs
   pass that appears after a sort change.
3. **Account IDs / Abs. Gain** not present on profile-level fetches:
   Mtrader XM2 (`https://www.myfxbook.com/members/iminwarn`),
   Advicefxrobot (`https://www.myfxbook.com/members/Advicefxnet`),
   SMART MONEY INVESTMENTS (`https://www.myfxbook.com/members/claudioca`),
   Elysium #4 (`https://www.myfxbook.com/members/guanchuan3153`),
   W3 S2 R (`https://www.myfxbook.com/members/withhumble`),
   Max (`https://www.myfxbook.com/members/Maxioo`),
   GOLD Copy Trading 336% book under `https://www.myfxbook.com/members/ScalperAiAlgo`.
4. **MQL5 trade lists** — "please log in" (VERIFIED). Needed only if a
   name first passes Abs/age/DD/concentration on the public summary.
5. **SFE Impulse product** `https://www.mql5.com/en/market/product/104102`
   — WebFetch opened the Market catalogue, not the EA's parameter text.
6. **Bybit / Binance / Bitget 18-month lead-trader ROI+MDD:**
   `https://www.bybit.com/en/promo/global/copy-trading-traders`,
   `https://www.bybit.com/en/leaderboard/`,
   Binance and Bitget copy-trading leaderboards (JS). Official Bybit help
   documents 7/30/90-day windows only; an 18-month column may not exist.
7. **ZuluTrade, eToro Popular Investors, cTrader Copy** — same JS / login
   walls as t202 (`https://www.zulutrade.com/zuluranking`,
   `https://www.etoro.com/discover/people/stats`,
   `https://app.ctrader.com/copy`).
8. **Forex Factory Trade Explorer** and **TradingView** live-verified
   strategy pages — JS; no 18-month 3.5% Abs book appeared in public
   HTML this round.
9. **Myfxbook last-200 / full history** for any future Abs pass — often
   truncated or private without a session.

## Files

| File | SHA-256 | Bytes |
|---|---|---|
| `shortlist_t206.md` | `e4fcd8b910dfda501cf3d9a8f7137c527ad8db3544f81f15e1eedd1d2e0af56c` | 7,316 |
| `RESULTS_t206.md` | this file | |

No other t206 artefacts.

## Bottom line

Opening the search back up to every style, and loosening age to 18 months
while raising the Abs bar to 3.5% and capping equity DD at 30% with a 50%
top-3 rule, **did not produce a new buildable system**. Printed 5–8%/month
Myfxbook names (BIGFISH, Wisdom, Harmonizer, RAZOR, Deux ex) are Gain
theatre: honest Abs is about **1%/month** on AUDCAD-style grids, or a
9-month-old signal with inflated Weeks. The honest long crypto book that
is *not* concentration-tainted (SFE Impulse) runs at **2.85%/month**. The
honest long crypto book that *does* clear 3.5% (Pepper) made 80% of its
growth in 16 days and is losing this month. **No MQL5, no deploy, no
second parameter search.** A browser pass on the Abs-gain sort and on the
unfetched Myfxbook IDs in § scrape is the only remaining public stone;
it is not expected to overturn the Abs arithmetic already in hand.
