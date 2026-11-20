# CONCRETUM SURVEY — ORB replications, Concretum/Zarattini papers, point-in-time earnings calendars
Prepared by Grok for Claude (request 17.11.2026 16:50). Public web only: no sign-ups, no purchases, no logins.
Compiled 17.11.2026 (Asia/Jerusalem). Tags: **[V]** = VERIFIED (I read it in the cited primary source or ran the public endpoint myself). **[S]** = secondary source, stated as that source reports it. **[U]** = UNVERIFIED.
No numbers here are invented. Where a number is my own arithmetic it is marked "(arith)".

---
## 0. Ground truth: what the paper actually specifies (SSRN 4729284)
Source PDF (public mirror, Univ. St.Gallen): https://alexandria.unisg.ch/server/api/core/bitstreams/3c2989c4-688d-4d78-8a71-f02690990d51/content ; SSRN: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284 (revised 29 Apr 2025)
- Data: CRSP for the survivorship-free universe (delisted names included, e.g. TWTR), **IQFeed** intraday, **unadjusted** for splits/dividends; period 2016-01-01..2023-12-31; MATLAB. [V]
- Filters: opening price > $5; 14-day average volume ≥ 1,000,000 sh; 14-day ATR > $0.50. [V]
- Direction: first 5-min bar (9:30–9:35) bullish → long only, via a buy-stop at the 5-min high; bearish → short only, via a sell-stop at the 5-min low; doji → no trade. [V]
- Stop: 10% of ATR14 from the **executed entry price**. Exit at 16:00 if not stopped. No profit target in this paper (the 10R target belongs to the QQQ paper SSRN 4416622). [V]
- Sizing: 1% of capital lost if the stop is hit; **max leverage 4x** ("in accordance with FINRA brokers"); footnote: the leverage cap means some trades risk less than 1%. [V] How the 4x is shared across 20 simultaneous names is NOT specified. [V: absent from the text]
- Stocks in Play: RelVol = OR volume today / mean OR volume of the previous 14 days; RelVol ≥ 1.0; trade the top 20 by RelVol. [V]
- Costs: **commission $0.0035/sh only (IBKR Pro Tiered entry level). No slippage is modelled.** Start NAV $25,000. [V]
- Results (Table 2/3) [V]:
  | Strategy | Total | IRR | Vol | Sharpe | Hit | MDD | Alpha | Beta |
  |---|---|---|---|---|---|---|---|---|
  | ORB Base (all filtered stocks) | 29% | 3.2% | 6.6% | 0.48 | 41.4% | 13% | 3.3% | 0.01 |
  | 5m ORB + RelVol (top 20) | 1,637% | 41.6% | 14.8% | 2.81 | 48.4% | 12% | 35.8% | 0.00 |
  | 15m ORB + RelVol | 272% | 17.4% | 12.2% | 1.43 | 44.7% | 11% | 16.9% | −0.01 |
  | 30m ORB + RelVol | 21% | 2.3% | 11.1% | 0.21 | 42.4% | 35% | 2.8% | 0.01 |
  | 60m ORB + RelVol | 39% | 4.1% | 10.2% | 0.40 | 42.3% | 21% | 4.4% | 0.01 |
  | COMBO (equal-weight 5/15/30/60) | 234% | 15.8% | 7.9% | 1.99 | 47.3% | 7% | 15.0% | 0.00 |
  | S&P 500 | 198% | 14.2% | 18.3% | 0.78 | 54.9% | 34% | 0 | 1.00 |
- Edge per trade: avg PnL −0.02R when RelVol < 1, **+0.08R when RelVol > 1**, 0.38R at RelVol > 30x (net of commission; Fig. 4). [V]
- **Cost arithmetic (arith):** R = 0.10×ATR ≥ $0.05/sh (ATR floor $0.50). Claude's $0.02/side means $0.04/sh round trip = **0.8R at ATR $0.50, 0.4R at ATR $1, 0.2R at ATR $2, 0.08R at ATR $5**. Against a published mean of about 0.08R (RelVol>1 bucket; the top-20 bucket's mean is not tabulated), a flat 2¢/side probably wipes out the edge on low-ATR names. The result depends heavily on the ATR mix of the names actually selected. I recommend modelling slippage as a fraction of R or ATR (or in bps plus a spread proxy) next to the flat ¢/share.

---
## 1. Independent replications of the ORB "Stocks in Play" paper
| # | Who / where | Data | Universe | Costs / slippage | Reported result | Post-2023? | Tag |
|---|---|---|---|---|---|---|---|
| 1 | **QuantConnect, Derek Melchin (research post 18444)** https://www.quantconnect.com/research/18444/opening-range-breakout-for-stocks-in-play/ | QC US equities (minute) | Top 1,000 by dollar volume, price > $5 (point-in-time QC fundamentals universe), ATR > $0.50, RelVol > 1, top 20 | Post does not state fees or slippage (QC default model, details [U]). Sizing: 1% risk / 20 names, **capped at 1/20 of equity per name (about 1x gross, not 4x)** | **2016 only: Sharpe 2.396, beta −0.042** (SPY Sharpe 0.836). Optimisation over OR 5–25 min × universe 500–1500: 17/25 combos beat SPY's Sharpe. ATR filter $0–2 all beat the benchmark; an ATR>1% of price variant gave Sharpe 2.237 | No | [V] |
| 2 | **QC comments**: Yuri Lopukhov (Python/C# ports), Jack Pizza, Lars Klawitter, Angus Li (same page) | QC | as #1 | — | Angus Li: "backtest doesn't look good for other years". Jack Pizza: returns "painfully low", **collapses in dot-com**, ~10% DD in COVID, >$50 price filter hurts. Klawitter: 1–2 min OR and 2,000-name universe better (2020–22, paper trading). Yuri: **minute-resolution artifact, the stop-loss is placed on the NEXT minute after the entry fill** (live it would sit at the fill second), so backtests ≠ live. Python ATR warm-up bug (ATR 3x too small) | — | [V] (qualitative quotes) |
| 3 | **Reddit r/algotrading, OP of thread 1hezqql** (Dec 2024) https://www.reddit.com/r/algotrading/comments/1hezqql/ | QC (Melchin code) | as #1 | not stated [U] | Ran **2016 → "present day" (Dec 2024)**: Sharpe ~1.4, max DD 8.1%, beta 0.03, PSR 100%, **net 176% total**, **win rate 17%**, lagged in post-COVID rallies | Partly (includes 2024 up to Dec) | [S] |
| 4 | **Petr Podhajsky (LinkedIn)** https://www.linkedin.com/posts/petr-podhajsky_systematictrading-daytrading-backtesting-activity-7378799325260259328-qSR_ | not stated | **Russell 3000** | "realistic slippage" (value not given) | "Equity curve looked solid (even w/ fees)… once I applied realistic slippage → edge disappeared." No numbers | [U] | [S] |
| 5 | **Quant for Free (quant4free.com)** https://quant4free.com/analysis/stocks-in-play-relvol-orb/ | **Alpaca SIP 5-min** | **PROXY: fixed 20 liquid mega-caps** (not a full scanner) | 1.0 bp spread + 0.5 bp slip, fees 0 | Paper-like default (RelVol ≥1, 0.10 ATR, top 5, L/S): 9,065 trades, win 9.6%, **−100%**. Best of 24 Optuna trials: OOS 2023-06-30..2026-09-18: −72.95%, DSR 0 | Yes, but proxy universe → not a valid test of the paper | [S] |
| 6 | **MK27MK/orb_paper_reproduction** (GitHub) https://github.com/MK27MK/orb_paper_reproduction | [U] | Base strategy only | [U] | "Work in progress… Stocks in Play refinement is not implemented yet" | — | [S] |
| 7 | **pderer/orb_strategy** (GitHub) https://github.com/pderer/orb_strategy | **Yahoo 5-min** (recent dates only) | current symbol list (rreichel3/US-Stock-Symbols), **survivorship-biased** | none stated | No aggregate results published | — | [S] |
| 8 | JittoJoseph/Hummingbird-Project (GitHub) https://github.com/JittoJoseph/Hummingbird-Project | Upstox | NSE India port | — | No results; just restates the paper | — | [S] |
| 9 | Jocimar Lopes, MQL5 article 23226 (cited by quant4free as rule lock) | MT5 | [U] | [U] | [U] | [U] | [U] |
| 10 | CXO Advisory summary https://www.cxoadvisory.com/individual-investing/intraday-trading-of-overactive-stocks-via-opening-range-breakout/ | — | — | — | Summary only; notes commission-only costs | — | [S] |
| 11 | aistocktradingbots.com review (23.10.2026) https://aistocktradingbots.com/blog/orb-strategy/ | — | — | — | Says the QC post "does not state fees or slippage"; no new backtest | — | [S] |

**Author follow-up:** Carlo Zarattini (LinkedIn, ~Feb 2025) says the **QQQ/TQQQ** 5-min ORB edge "remains robust and in line with historical performance" (TQQQ, stop 7.5% ATR14, EOD exit). That is a self-report on the single-ETF paper, not on Stocks in Play: https://www.linkedin.com/posts/carlozarattini_glad-to-see-that-nearly-two-years-after-activity-7298045436207005696-5mr- [S]. Concretum also published Python code for the QQQ ORB paper (Polygon.io): https://www.linkedin.com/posts/carlozarattini_backtesting-the-opening-range-breakout-orb-activity-7305637543012675585-ZVhw [S]
**I found no public full-universe, survivorship-free replication with explicit slippage covering 2024–2026.** [V: none in searches]

### Consensus
1. The rule set is reproducible in shape (QC: 2016 Sharpe 2.4 vs paper 2.81 for 2016–23). Over longer QC runs it decays to Sharpe ~1.4 with a total return far below the paper (176% vs 1,637%). Part of that is QC's ~1x gross cap vs the paper's 4x [S/arith].
2. **Every source that added realistic slippage reports that the edge disappears** (Podhajsky; quant4free on a proxy). The paper itself has **zero slippage**. [S]
3. Win rate 10–20% in replications vs 48.4% in the paper. That is a material, unexplained gap, possibly from stop-fill modelling or bar resolution [S/U].

### Pitfalls (check list for r103)
- **Survivorship:** the paper uses CRSP with delistings. Current-symbol lists (pderer) are biased. Alpaca must include delisted symbols and you must build the universe point-in-time. [V]
- **Unadjusted prices:** the paper uses unadjusted intraday data. The $5 / $0.50 ATR / 1M-volume filters on split-adjusted data shift the universe. [V]
- **Look-ahead in RelVol:** the numerator must be the 9:30–9:35 volume only, known at 9:35, with no entry before 9:35:00. The denominator is the prior 14 days only. Universe filters (ATR14, ADV14) must use data through t−1. "Opening price > $5" uses the 9:30 open. [V paper definitions] Whether the opening-auction print is inside the first 5-min bar differs by feed: SIP vs IQFeed handling is [U]. RelVol is very sensitive to it, so test with and without the auction print.
- **Stop-fill realism:** (a) entry is a stop order at the OR extreme. Gaps or fast moves through it mean fills at the bar open or worse, not at the level (quant4free uses bar open on gap-through). (b) The stop-loss is tiny (0.1 ATR) and is often hit in the same 1-min bar as the entry. With 1-min bars you cannot tell the order of events, so assume the worst case: entry and stop in the same bar = stopped. (c) QC's next-minute stop placement flatters results. [V/S]
- **Leverage cap:** 1% risk at a 0.1 ATR stop gives notional = 10%×equity/(ATR/price). For ATR/price = 3% that is 333% per name (arith), so the 4x cap binds almost always with 20 names. The allocation rule (first-come-first-served by trigger time? pro-rata?) is unspecified, so pre-register one. QC uses 1/20 equity per name. [V/arith]
- **Short side:** borrow availability/HTB fees on in-play small caps, plus the SSR (Rule 201) uptick restriction after a −10% day, block many shorts in reality. Neither is modelled anywhere. [U]
- **Costs:** model the spread at the open (wide on in-play names) plus slippage per side as a fraction of R. Run the commission-only paper case as a sanity check only.

---
## 2. Other Concretum / Zarattini papers needing US stock/ETF data
Index of papers: https://concretumgroup.com/papers/ [V]. SSRN direct PDF download was blocked from the box; I used Concretum-hosted PDFs (https://concretumgroup.com/wp-content/uploads/2026/02/<Title>.pdf) and public mirrors.

### 2.1 ORB COMBO (5/15/30/60 min), same paper (SSRN 4729284)
Same rules as §0, with RelVol computed over the first n minutes vs the 14-day mean of the same window. COMBO = equal-weight of the four n-minute portfolios. 2016–2023, commission $0.0035, no slippage. COMBO: Sharpe 1.99, IRR 15.8%, MDD 7%. The 30m and 60m versions are weak (Sharpe 0.21/0.40). [V] The COMBO's Sharpe rests on the 5m and 15m legs, so it is the same cost exposure with a diluted edge.

### 2.2 "Can Day Trading Really Be Profitable?" (QQQ/TQQQ ORB), SSRN 4416622
PDF: https://concretumgroup.com/wp-content/uploads/2026/02/Can-Day-Trading-Really-Be-Profitable.pdf [V]
- Data: QQQ/TQQQ 1-min, 2016-01-01..2023-02-17.
- Entry at the **open of the 2nd 5-min bar** in the direction of the 1st bar (doji = no trade). Stop at the 1st bar's opposite extreme. **Target 10R or EOD.** Risk 1%/trade, 4x max leverage, **commission $0.0005/sh, no slippage**, $25k. [V]
- QQQ: 675% total, Sharpe 1.12 (as printed in the text; secondary sites quote 1.13/1.19 [S]), ann. return 31%, alpha 33%, 1,795 trades. TQQQ: 1,484% total. [V]
- A secondary site reports an independent QQQ replication breaking even at ~2¢/share slippage, with profits concentrated in 2022: https://theorbstrategy.com/blog/orb-strategy-win-rate-and-backtesting-basics/ [S, original replication not located → U]

### 2.3 "Beat the Market: An Effective Intraday Momentum Strategy for SPY" (noise area), SSRN 4824172
PDF: https://concretumgroup.com/wp-content/uploads/2026/02/Beat-the-Market.pdf ; mirror https://alexandria.unisg.ch/server/api/core/bitstreams/a99aba00-f967-49b3-aceb-f544dc386e0b/content [V]
- Data: SPY 1-min from IQFeed, May 2007..Apr 2024.
- σ(HH:MM) = mean over the last 14 days of |Close(HH:MM)/Open(9:30) − 1|.
- UpperBound = max(Open_t, Close_{t−1}) × (1+σ); LowerBound = min(Open_t, Close_{t−1}) × (1−σ). (A volatility multiplier VM variant exists.)
- Decisions **only at HH:00 and HH:30** (first possible at 10:00). Long above UB, short below LB.
- Exit: trailing stop = **max(UB, VWAP)** for longs, **min(LB, VWAP)** for shorts, checked on semi-hours. Reverse on the opposite band. Flat at 16:00.
- Sizing: shares = AUM_{t−1}/Open × min(4, 2% / σ_SPY,t) (daily vol target 2%, 14-day daily vol [S for the 14-day window: orbitalaip/github summaries]), 4x cap.
- Costs: **$0.0035/sh commission + $0.001/sh slippage** (they measured ~$0.001 mean / $0.0005 median slippage on >1,000 live IBKR market orders in Apr 2024). [V]
- Results: base 100% exposure + current band + VWAP: Sharpe 1.24, 9.7%/y. With dynamic sizing: **total 1,985%, 19.6%/y, vol 14.3%, Sharpe 1.33, MDD 25%**, beta −0.07. [V]
- Paper FAQ: "works on other ETFs/stocks", with a diversified portfolio Sharpe > 2 (2018–Aug 2024, chart only). On 33 futures 2007–Sep 2024: average Sharpe 0.60, portfolio 1.65. [V, no tables for the ETFs]
- **Independent OOS (Sheimy Paz Serpa, 2026):** https://wato.it.com/papers/spy-intraday-momentum-oos-2026.pdf ; SSRN 7290621. IQFeed 1-min. In-sample replication 2015–Apr 2024: Sharpe 1.34, 19.8%/y (matches). **OOS May 2024..Mar 2026: total +9.4% vs SPY +29.5%, 4.8%/y, Sharpe 0.39, MDD 18.5%.** The decline is statistically significant. Same costs ($0.0035 + $0.001). [V] Larry Swedroe's commentary (paywalled): https://larryswedroe.substack.com/p/when-beat-the-market-meets-the-real [S]
- Data need: 1-min SPY (or other ETFs). Alpaca SIP is fine.

### 2.4 "Intraday Momentum for ETFs" = Concretum article "Where To Trade Intraday Trends" (19.08.2026)
https://concretumgroup.com/where-to-trade-intraday-trends/ ; https://concretumgroup.substack.com/p/where-to-trade-intraday-trends
- 49 ETFs, ~2 decades; base model = "a volatility breakout strategy that we usually deploy" (bands). **Full rules are paywalled ($80 PDF / Substack)**, so I did not buy them. [V that it is paywalled]
- Public teaser: walk-forward ranking by recent strategy performance; concentrating on the **4–6 best ETFs**; top-4 portfolio **Sharpe ≈1.2, CAGR 12%, MDD 13%** (from https://concretumgroup.com/articles/). [S]
- Related premium (paywalled, rules unknown [U]): "Improving the ORB Strategy on SPY", "Can VIX Improve Intraday Trend Following?", "The Intraday Seasonality of Market Trends" (07.08.2026 teaser: last hour historically ~60% of daily trend profits, "significant shift" recently [S]), "Intraday Trend Following With 0DTE Options", "Following the Trend… With ETFs!".
- A reconstructable approximation: run the §2.3 noise-area rules on each of N liquid ETFs and pick the top-k by trailing strategy Sharpe (lookback to pre-register). Treat this as our own variant, not their rules.

### 2.5 "VWAP: The Holy Grail for Day Trading Systems", SSRN 4631351
PDF (public mirror): https://www.projectnoir.eu/code/Volume_Weighted_Average_Price_VWAP_Holy_Grail.pdf [V]
- QQQ/TQQQ 1-min, 2018-01-02..2023-09-28. Long when price is above session VWAP, short when below (1-min candle closes vs VWAP, reverse on cross, flat EOD; exact first-bar timing per secondary sources [S]).
- **Commission $0.0005/sh**; slippage discussed but not deducted [V: §3.4].
- QQQ: $25k → $192,656 (**671%**), **Sharpe 2.1**, MDD 9.4%. TQQQ: 8,242%, ~116%/y. [V]
- Independent tests report the edge collapses with realistic spread/slippage and after Sep 2023: https://quant4free.com/analysis/session-vwap-bias/ , https://guanalyser.com/test-bench/vwap-trading-strategy/ [S, not opened → U]

### 2.6 "Does Trend-Following Still Work on Stocks?" (Zarattini, Pagani, Wilcox), SSRN 5084316
PDF: https://concretumgroup.com/wp-content/uploads/2026/02/Does-Trend-Following-Still-Work-on-Stocks.pdf [V]
- Data: **Norgate** survivorship-free daily data, all liquid US stocks 1950–Oct 2024 (trade study); portfolio 1991–2024.
- Trade study: eligible if close > $10 (unadjusted) and 42-day average dollar volume > $1M (CPI-deflated). **Entry: close ≥ all-time-high adjusted close → buy next open.** **Trailing stop = ATH × (1 − 10×ATR42/Close)**, never lowered. Exit next open when close < stop. Cost 0.50% per round turn. [V]
- Portfolio: Russell 3000 members, price > $10, ADV$42 > $1M. Weight = (30%/σ42,ann) × 1/max(200, N_holdings). Gross leverage cap 200% (proportional rescale). MOO orders. Daily rebalance. [V]
- Results: theoretical (no costs) **CAGR 15.02%, vol 14.93%, Sharpe 0.85, MDD 31.75%, alpha 6.19%** (the SSRN abstract version says CAGR 15.19% through Nov 2024 [S]). With costs (IBKR $0.0035/sh, min $0.35, sells ×2 plus SEC fees; I-Star impact a1=708, a2=0.55, a3=0.71; borrow = 2×rf, min 100 bp): **$100k → CAGR 2.45%, Sharpe 0.06**; $1M → 9.01%/0.49; $10M → 12.53%/0.70. [V]
- With "Turnover Control" (skip small rebalances, spread trades over days, skip trades whose commission exceeds a notional threshold): $100k → **CAGR 12.97%, Sharpe 0.75, MDD 32.97%**; $1M → 13.40%/0.75. [V] **The exact turnover-control thresholds are NOT public** ("contact us"). [V]
- Data need: survivorship-free daily OHLC with delistings, Russell 3000 membership (point-in-time), split/dividend-adjusted and unadjusted closes.

### 2.7 "A Century of Profitable Industry Trends" (Zarattini, Antonacci), SSRN 4857230, 2025 Dow Award
PDF: https://concretumgroup.com/wp-content/uploads/2026/02/A-Century-of-Profitable-Industry-Trends.pdf [V]
- Data: Ken French 48 industries, 1926–2024. ETF test: **31 SPDR sector/industry ETFs** (Yahoo daily), 2005–Mar 2024.
- Entry (long only): close ≥ UpperBand_{t−1}, where UpperBand = min(Donchian20 high, Keltner(20, k=2)). Keltner uses EMA20 ± 1.4×k×mean|ΔP| (their adaptation). [V]
- Exit: trailing stop = max(prev stop, LowerBand), LowerBand = max(Donchian40 low, Keltner(40,2) lower). [V]
- Sizing: per-asset daily vol target 1.5%/N using 14-day vol. Gross cap 200%. Daily rebalance (close prices only). [V]
- Results: industries 1926–2024 **18.2%/y, vol 12.6%, Sharpe 1.39** (no costs). **ETFs 2005–2024 with $0.0035/sh: IRR 7.7%, Sharpe 0.61, MDD 24%** vs SPY 10.0%/0.59/55%. [V]
- Data need: daily ETF OHLC (free).

### 2.8 "The Volatility Edge: A Dual Approach for VIX ETNs" (Zarattini, Aziz, Mele), SSRN 5316487
PDF: https://concretumgroup.com/wp-content/uploads/2026/02/The-Volatility-Edge.pdf [V]
- eRV30 = std of the last 10 daily SPY returns × √252 × 100; eVRP = VIX − eRV30; term structure = VIX vs VIX3M. Signal computed 15 min before the close, MOC execution, **5 bp per trade**, 2% rebalance threshold, VIXY/SVXY. [V] Allocation table per the secondary summary: eVRP>0 & VIX<VIX3M → short vol at VIX/100; eVRP≤0 & VIX<VIX3M → 0.5×; eVRP≤0 & VIX>VIX3M → long vol; else cash [S].
- Result 2008–May 2025: **CAGR 16.3%, Sharpe 1.00, Sortino 1.67**, ~15% SPX correlation. [V/S]
- QC implementation: https://www.quantconnect.com/research/21143/harvesting-the-volatility-risk-premium-with-a-dual-vix-signal/ [S]
- **Note:** our own t_vixts (VIX/VIX3M) was KILLED at dev on 17.11, so this overlaps a dead line. Re-test only if the eVRP leg adds something distinct.

### 2.9 Others (lower priority / not stock-intraday)
- **QuanTip: Improving Performance with Fast Alphas** (16.02.2026): 5-min SPY 2007–2026, a short-horizon mean-reversion signal used as an execution overlay on intraday trend. Raises net CAGR/Sharpe (numbers not public on the index page [U]). https://concretumgroup.com/papers/
- **QuanTips: GTAA updated + IBKR implementation** (19.06.2026), Faber GTAA through 2025 with tranching. ETF daily data. [V listing; rules = Faber's 10-month SMA, standard]
- **The Tranching Dilemma** (14.11.2025): US equity momentum 1991–2024, rebalance timing luck up to ~350 bp/y. [V listing]
- **ChatGPT in Systematic Investing** (30.10.2025): S&P 500 momentum plus LLM news scoring. Needs news data. [V listing]
- **The Power of Price Action Reading** (28.06.2024): discretionary trader overlay, so it cannot be replicated mechanically. [V listing]
- **Catching Crypto Trends** (08.04.2025): Donchian ensembles on crypto. Not US stock data. [V listing]
- **NextVoL volatility targeting** (21.04.2026). [V listing]

---
## 3. Free point-in-time earnings calendar sources (pre-earnings premium study)
Key concept: event studies need the **actual** announcement timestamp (EDGAR gives it). A *tradable* pre-earnings strategy needs the date **as known in advance**. Free sources give actual dates only, so you must proxy expectation (e.g., same-quarter-last-year date, or only trade inside N days if the date was confirmed). The historical confirmation timestamp is not available for free (vendors such as Wall Street Horizon sell it [U]).

| Source | Coverage | Point-in-time? | Access | Limitations / look-ahead | Tag |
|---|---|---|---|---|---|
| **SEC EDGAR submissions JSON** `https://data.sec.gov/submissions/CIK##########.json` | All EDGAR filers; Item 2.02 exists since 2004-08-23 (Item 12 from 2003 before that) | **Yes for actual release time**: `acceptanceDateTime` (ISO with Z), `filingDate`, `reportDate`, `items` (e.g. "2.02,9.01"). Older filings are in paged `files` (e.g. Apple: 1994–2015 in -001.json) | **No signup**. Declared User-Agent header required; ≤10 req/s. Bulk nightly `submissions.zip` (https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | Acceptance time is an UPPER BOUND (press release often hits the wire minutes earlier). Some firms furnish 2.02 late or not at all (e.g. results only in 10-Q). CIK→ticker mapping must be point-in-time; tickers get recycled. Includes delisted filers (survivorship-safe) | [V: I queried AAPL live: fields present, 8-K 2.02 rows with acceptance 20:30–21:30Z] |
| **EDGAR full-text search** (efts.sec.gov/LATEST/search-index?q=...&forms=8-K) | 2001+ | same as above | No signup | Rate limits; better to filter submissions by `items` | [S/U for exact coverage] |
| **Quant500 `sp500_earnings_announcements.csv`** https://quant500.com/data | **2003-04-25 → 2026-11-17, 65,670 announcements, 808 companies** (S&P 500 incl. past members) | Derived from EDGAR 8-K 2.02/Item 12, with `time_et`, `session`, `date_uncertain`, `time_convention` flags | **No account, CSV, CC0** | S&P 500 only. The time is flagged PROVISIONAL (EDGAR processing latency). Membership list as of their build [U] | [V page] |
| **FinzData/sec-earnings-release-dates** (Hugging Face) https://huggingface.co/datasets/FinzData/sec-earnings-release-dates | **229,885 releases, 2004-08 → 2026-11**, all US filers | 8-K 2.02 `accepted_et` in NY time plus `timing` (before_open/during/after_close), `report_date`, accession | Parquet download (`hf://datasets/...`), no signup for the sample (they call it a "free sample"; whether it is complete is [U]) | Same EDGAR caveats; ticker field is the current ticker (point-in-time mapping [U]) | [V page] |
| **Nasdaq calendar API** `https://api.nasdaq.com/api/calendar/earnings?date=YYYY-MM-DD` | I tested 2014-01-28 and 2020-07-28: returns rows (166 on 2020-07-28) | Gives the **actual** report date plus EPS, consensus, surprise. **The `marketCap` field is CURRENT (look-ahead):** AMD showed $827B on 2020-07-28. `time` is often "time-not-supplied" | No signup, unofficial (browser UA needed), per-day calls | Unofficial/ToS; delisted-name coverage [U]; the consensus is the final pre-report value, not an as-of-date value [U] | [V: live test] |
| **Alpha Vantage `EARNINGS`** `query?function=EARNINGS&symbol=X` | Quarterly history (start year varies by name [U]) | `reportedDate`, `reportTime` (pre/post), reported vs estimated EPS, surprise. Actual dates | **Free signup** (API key), **25 req/day** | Per-symbol, slow for a full universe; delisted symbols [U]; `EARNINGS_CALENDAR` is forward-looking only (3/6/12 months) | [S] (OpenBB code + AV docs via search) |
| **Yahoo** (`finance.yahoo.com/calendar/earnings?day=`; yfinance `get_earnings_dates(limit=)`) | Several years per ticker [U] | Actual dates plus EPS estimate/actual | No signup, unofficial scraping | Rate-limited/blocked often; no delisted names; time zone quirks [U] | [U] |
| **Zacks earnings calendar** | [U] | [U] | Web, unofficial | ToS; no bulk history | [U] |
| **Kaggle "NASDAQ Earnings Calendar (Auto-Updating)"** https://www.kaggle.com/datasets/anthonypm/nasdaq-earnings-calendar-auto-updating | Rolling **next 10 business days only** (version history might accumulate snapshots [U]) | Forward-looking snapshot (this is PIT expected-date data if old versions are kept) | Kaggle (free account to download) | Not a history unless you collect versions | [V page] |
| **GitHub s-kerin/finance_calendars** https://github.com/s-kerin/finance_calendars | wrapper over the Nasdaq API | as Nasdaq | pip | as Nasdaq | [S] |
| FirstRate Data earnings (2000+) https://firstratedata.com/fundamental-data/earnings/ | 2000+ | [U] | **Paid** (excluded) | — | [S] |

**Recommendation for §3:** use EDGAR 8-K Item 2.02 (via the submissions bulk zip, or the FinzData parquet as a fast start, cross-checked against Quant500 for the S&P 500) as the canonical **actual-event** timestamp, with session = before_open/after_close mapped to the reaction day. For the *pre-earnings premium* entry (e.g., buy t−5 … sell t−1), define the "expected date" without look-ahead. Two options: (a) prior-year same-fiscal-quarter announcement date ± tolerance, only trading if the actual date falls within ±3 trading days (report the drop-out rate), or (b) treat the event as known when it is ≥ X days away, which assumes firms confirm dates ~2+ weeks ahead [U]. Use Nasdaq API rows only for EPS/surprise. Never use its marketCap.

---
## 4. Recommendations for r103 (ORB Stocks-in-Play replication on Alpaca 1-min SIP, 2016+)
1. **Pre-register two cost regimes in R units, not just ¢:** C0 = paper (commission $0.0035 only, sanity reproduction). C1 = $0.0035 + $0.02/side. C2 = $0.0035 + $0.04/side. Also report the **average ATR/price and the R-distribution of selected names**, so the reader sees the slippage/R ratio (at ATR $0.50, 2¢/side = 0.8R round trip).
2. **Fill model:** entry stop fills at max(level, bar open if gapped) plus slippage. If the entry and the 0.1-ATR stop both fall in the same 1-min bar, count it as STOPPED (worst case). Optionally report a "same-bar optimistic" variant to bound the result. The stop is active from the entry second (not the next bar).
3. **RelVol:** compute it from 1-min bars 9:30–9:34 inclusive (5 bars), with entries only from 9:35:00. Run a sensitivity check including/excluding the opening-auction print if Alpaca exposes it via trades (condition codes) [U]. 14-day denominators exclude today.
4. **Universe:** point-in-time, including delisted names. Unadjusted prices for the $5/ATR/ADV filters (as in the paper). Exclude ETFs/ADRs? The paper doesn't say, so pre-register (default: common stock only [U]).
5. **Leverage:** paper = 4x gross with 1% risk per name; allocation order unspecified. Pre-register: process triggers in time order, then cap at 4x gross. Also report a QC-style 1x-gross variant (1/20 equity per name) for comparability with the QC/Reddit numbers.
6. **Holdout:** dev 2016–2021, holdout 2022–2025/26. The interesting question is whether 2024–2026 holds; no public source answers that.
7. **Shorts:** flag the share of PnL from shorts and from names with a −10% day (SSR-affected) as an execution-risk diagnostic.
8. **Kill criteria (suggested):** if C1 Sharpe < 1.0 or the holdout Sharpe < 50% of dev, mark it NOT TRADEABLE for retail. That matches the public evidence (all slippage-aware tests failed).
9. **Better next candidates:** the noise-area SPY (§2.3) is cheap to test but has a documented OOS decay (Sharpe 0.39 for 5/2024–3/2026), so test it only as a portfolio of ETFs (§2.4 approximation). The trend-following stocks (§2.6) are robust in a 1991–2024 backtest but need the unpublished turnover control (at $100k without it, Sharpe 0.06). Industry/ETF trend (§2.7) is simple and free-data, with a modest Sharpe of 0.61 on ETFs.
