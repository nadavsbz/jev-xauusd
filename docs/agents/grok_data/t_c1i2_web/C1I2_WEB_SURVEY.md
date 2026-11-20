# C1I2_WEB_SURVEY: what others found about C1 (Catching Crypto Trends) and I2 (Beat the Market / noise area)
Prepared by Grok for Claude (request t_c1i2_web, 17.11.2026 20:20). Public web only: no sign-ups, logins, purchases, follows or subscriptions. Compiled 17.11.2026 ~21:05 (Asia/Jerusalem).
Tags: **[V]** VERIFIED = I read the primary source (paper PDF, the author's own repo/page, or the public stats page itself). **[S]** = secondary source, or a primary page I saw only through a search-index excerpt; numbers are as reported there. **[U]** = UNVERIFIED (claim not checked, or absence of evidence).
No numbers are invented. "(arith)" marks my own arithmetic. This does not duplicate the earlier `t_concretum/CONCRETUM_SURVEY.md` (sha 44b74cbf…4276); §2.3 there covers the I2 paper rules and Serpa in short form.

> **Nothing here changes the demo.** C1/I2 on demo stay exactly as they are unless Nadav decides otherwise. Every "improvement" below is a candidate for a pre-registered dev+holdout test only.

---
## 0. Bottom line (TL;DR)
1. **I2 on SPY/ES: post-publication decay is now confirmed by 5+ independent sources.** The pattern: a good first stretch after publication (May 2024 to Aug 2025), then a clearly negative regime from about Sep 2025 to Aug 2026 (Delgado: Sharpe −0.46, −8.1%) [S]. Brusco: SPY 2025 −4.9%, 2026 YTD (to Jul) −12.9%, the same on ES futures (corr 0.97) [V]. Strategy Autopsy: post-May-2024 Sharpe −0.05 gross / −0.71 net [S]. Bailey: pre-registered 20-month validation −0.051R/trade on MES [S]. Serpa: Sharpe 0.39 for 5/2024–3/2026 [V].
2. **I2 on Nasdaq is mixed but better than on SPY.** RipBacktest NQ, NY session only, 1 contract with no leverage: positive every year 2020–2026 including 2025 (+$22,410) and 2026 to Sep (+$34,256) [V page]. EdgeLab NQ 2010–2026: long side real (OOS Sharpe 0.68), **short side not robust** (IS −0.21) [V page]. Brusco's 2026 SPY/ES collapse does not appear there. Bailey: on MNQ all 54 settings were profitable in dev; the 20-month validation result was reported for MES [S]. Concretum's own FAQ: Nasdaq futures 2007–9/2024 Sharpe 1.23, MDD 26% [V].
3. **C1 has been flat since the paper's data ended (19.03.2025).** AlgoEdge recomputation on BTC (daily, 9 lookbacks, 25% vol target, 0.10% fees): Sharpe 0.05 from Apr 2025 to Oct 2026, worst loss −15%. 5y to 16.11.2026: 5.7%/y, Sharpe 0.49, MDD −15.3% [S/V page]. That fits a choppy BTC regime (ATH ~$125k Oct 2025, then −53% by Jun 2026, per that source) [S]. No independent OOS evidence that C1 is *broken*; it is "not earning".
4. **Our C1 is not the paper's C1.** Paper = **daily** closes, **9** lookbacks {5,10,20,30,60,90,150,250,360}, **long-only** main spec, 25%/σ(3m) capped at 200%, 20% rebalance threshold on vol-driven changes only, 10 bp cost [V]. Ours (per the brief) = H6 bars, 7 lookbacks (10–250), half long-only / half long-short. The paper's own L/S BTC Combo is weaker than long-only (Sharpe 1.31 vs 1.58, gross, 2015–3/2025) [V]. Any published benchmark therefore only loosely applies to our variant. Claude should confirm that lookbacks are in days (×4 H6 bars), not bars.
5. **Concretum stopped publishing I2 performance after Aug 2025.** The last public update is the BTM FAQ Q24 (paper version 22.09.2025): 2024 +32.2%, 2025 Jan–Aug +1.0% [V]. Nothing later was found [U]. There is no C1 performance update at all [U]. Concretum has moved on to paywalled variants (VIX-calibrated bands 07/2026, fast-alpha execution overlay 02/2026, BTC intraday momentum by session 16.11.2026).
6. **No live watchable account running C1 or I2 logic with ≥6 months was found.** The closest is Collective2 "ares" (intraday MNQ L/S, flat overnight, 75 months, 32.4%/y, MDD 14.1%; **rules undisclosed**, C2 marks it "hypothetical"; 2025 only +5.0%) [V page].

---
## 1. I2: independent replications and post-publication (OOS) evidence

### 1.1 Reference: what the paper and Concretum say [V]
- Paper: SSRN 4824172, Concretum PDF version 22.09.2025 (https://concretumgroup.com/wp-content/uploads/2026/02/Beat-the-Market.pdf). SPY 1-min May 2007–Apr 2024, 14-day noise area, 30-min checks, exit max(UB,VWAP)/min(LB,VWAP), 2%/day vol target, 4x cap, $0.0035/sh + $0.001/sh slippage. Result: total 1,985%, 19.6%/y, Sharpe 1.33, MDD 25%. [V]
- FAQ Q24 monthly table (post-publication): 2024 = **+32.2%**; 2025 Jan..Aug = −1.2, 7.6, −0.2, 4.3, −2.1, −2, −2, −2.9 → **YTD +1.0%**. Weak years in-sample: **2016 −12.8%, 2017 −6.9%**. [V]
- FAQ Q13 (futures, 2007–Sep 2024, same rules): **Nasdaq futures total 1,533%, CAGR 16.8%, vol 13.6%, Sharpe 1.23, MDD 26%, hit 43%**. S&P500 futures Sharpe 1.32, Russell 0.45, MidCap 0.80. 33 futures average Sharpe 0.60. [V]
- FAQ Q14: optimal lookback 90d (Sharpe 1.35→1.50), optimal multiplier 1.5 (→1.55); Concretum presents this as evidence against over-fitting. [V]
- FAQ Q15: I-Star impact model → Sharpe 1.17 vs 1.33. [V]
- FAQ Q22: VWAP-only trailing stop Sharpe 1.17 vs 1.35 for band+VWAP (2007–12/2024). [V]
- Zarattini LinkedIn (May 2025): a live sub-account trading "a similar intraday momentum strategy on SPY" for 6 months showed avg slippage −$0.005/sh and commission $0.012/sh (buy $0.004, sell $0.019) on ~$100M volume. YTD Apr 2025 +10.7%. https://www.linkedin.com/posts/carlozarattini_heres-the-latest-update-on-the-intraday-activity-7325909248368939008-i3CU [S]. Note: $0.012/sh commission is more than 3x the backtest's $0.0035 (arith).

### 1.2 Independent replications table
| # | Who / link | Data, instrument | Costs | In-sample | Post-publication / OOS | Tag |
|---|---|---|---|---|---|---|
| R1 | **Serpa 2026**, https://wato.it.com/papers/spy-intraday-momentum-oos-2026.pdf , code https://github.com/PazSheimy/spy-intraday-momentum-oos | IQFeed SPY 1-min | $0.0035 + $0.001/sh | 2015–4/2024 Sharpe 1.34, 19.8%/y, MDD 26.2% | **5/2024–3/2026: +9.4% total (SPY +29.5%), 4.8%/y, Sharpe 0.39, MDD 18.5%**; daily mean not ≠ 0 (p 0.59); hit ratio unchanged (45%), so the loss is in win size. Best regimes: 2008/2020/2022 high-vol; worst: low-vol / steady-trend (2016–17, 2025). Candidate explanations: 0DTE growth, crowding. | [V] |
| R2 | **Delgado, "Beat the Market Revisited"** SSRN 7323419 https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7323419 | TradeStation SPY 1-min 2000–8/2026 | as paper | Reproduces 1,989% / Sharpe 1.317 after matching the authors' Python code: **typical-price VWAP** and **VWAP confirmation at entry** | Reproduces Concretum FAQ (2024 +31.8% vs 32.2%; 2025 Jan–Aug +1.4% vs 1.0%). **5/2024–8/2025: +19.3%, Sharpe 1.06. 2/9/2025–14/8/2026: −8.1%, Sharpe −0.46.** Pooled 5/2024–8/2026 Sharpe 0.35. Searched 129 trials; final frozen spec Sharpe 1.274, MDD −14.8% (2000–2026), **PBO 38–41%** | [S] (abstract via index; SSRN timed out) |
| R3 | **Brusco** https://github.com/giovannibrusco/zarattini-2024-momentum-spy (CONCLUSIONS.md 07/2026) | Alpaca IEX SPY 2020-07→2026-07; IB ES 2024-05→2026-07 | $0.0035/sh; ES $0.85+$1.40 + 0.25 tick | SPY 2020–26 Sharpe 1.11, alpha 16.7%; 2020–24 Sharpe 1.4–2.0 each year; 2022 +25.8% | **SPY 2025 −4.9% (Sharpe −0.27); 2026 YTD −12.9% (Sharpe −1.91).** ES "final" 2024-05→2026-07 Sharpe −0.07; corr ES/SPY 0.97, so not a feed or cost artefact. Base exit (opposite band) beat final in 2024–26 (Sharpe ~0.7 vs ~0), flagged as **post-hoc**. Verdict: "not allocable today, not dead". | [V] |
| R4 | **Strategy Autopsy** (26.10.2026) https://strategy-autopsy.vercel.app/cases/noise-band-intraday-momentum/ | S&P 1-min 2008–10/2026, rechecked on SPY | 1.5 bp/RT (UK spread bet) | Pre-pub gross Sharpe 1.62; net 0.96 | **Post May 2024: gross −0.05, net −0.71 (−11%) vs index +48%.** ~6,000 trades/18y, so each extra bp of cost costs ~0.45 Sharpe. 1x leverage. | [S] |
| R5 | **Chris Bailey** (13.10.2026) https://cbailey.uk/trading/noise-area-intraday-momentum/ | Micro futures MNQ/MES/MYM/M2K, dev 2019–2024 | $1/side + 1 tick, worst-case fills, extra hard stop (1 daily σ) | Dev: 54/54 settings profitable on MNQ (+0.060R median) and MES (+0.047R); MYM mixed; **M2K 0/54**; family-wise p 0.005 | **One pre-registered look at 20 newer months: MES −0.051R/trade (284 trades), worse than a long-only control (+0.003R).** | [S] (WebFetch excerpt; page 403 to curl) |
| R6 | **RipBacktest NQ** (protocol frozen 11.10.2026) https://ripbacktest.com/posts/noise-area-breakout-nq/ | NinjaTrader NQ 1-min back-adjusted 2020–25.09.2026; 1 contract, **no vol sizing** | $15.76/RT | Dev 2020–23 t=2.82 (L/S), 2.98 (L-only) | **NY session L/S: +$231,557, 1,504 trades, +$153.96/trade net, PF 1.28, every year positive: 2024 +$44,017, 2025 +$22,410, 2026 (to Sep) +$34,256.** Long-only PF 1.43. **Asia and London sessions lose** (London L/S −$91k). ES same rule did not pass (dev t 1.91, losing holdout). Holdout was already used, so the author calls it a candidate; forward test runs from 12.10.2026. | [V] |
| R7 | **EdgeLab** (24.07.2026) https://edgelabtrading.com/blog/zarattini-intraday-momentum-nasdaq/ | Databento NQ 1-min 2010–2026, params locked 2010–17 | 0.01% RT | Long IS Sharpe 0.90, short **−0.21**, both 0.43 | OOS 2018–2026: long 0.68, short 1.22, both 1.39 (business-day Sharpe). Author: short side = "long-vol bet", profits in 2018/2022; **"soft patch since 2024 peak"** on the long side. | [V] |
| R8 | **Quantitativo** (16.01.2025) https://www.quantitativo.com/p/intraday-momentum-for-es-and-nq | Databento ES/NQ 2010–2025 | IBKR + fees + 0.25 tick/side | ES paper rules: 8.1%/y, Sharpe 0.91, MDD 24%; "flat 2010–2017". With lookback 90 + 3% vol/8x cap: ES Sharpe 1.25; **NQ 24.3%/y, Sharpe 1.67, MDD 24%** | No OOS; author says he is forward-testing (no results found [U]). The changes (90d, more leverage) were chosen in-sample. | [V] |
| R9 | **Chuk**, "Noise-band Intraday Momentum in Nasdaq-100 Futures" SSRN 7609644 | MNQ 2020–7/2026, 1 contract | stop slippage modelled | +$10.26/day net, daily Sharpe 1.14; stop slippage removes ~22% of edge | Paper-forward since 28.09.2026, no live contracts, no forward P&L published | [S] |
| R10 | Reddit r/Daytrading 1sd1zl3 https://www.reddit.com/r/Daytrading/comments/1sd1zl3/ | SPY 1-min 4/2022–4/2026 | "material" | +45.2% fixed size, 9.97%/y, Sharpe 1.14 vs SPY +54.8% → alpha ≈ −4%/y | — | [S] (index excerpt; reddit blocked) |
| R11 | Maróy SSRN 5095349 (01/2025) | QQQ, optimised | — | Claims Sharpe >3, >50%/y with VWAP / Ladder exits after **optimising all parameters** | **Brusco's frozen 27-variant re-test: the paper config wins in-sample; OOS 2024→ winner = control, Sharpe 0.16; walk-forward reselection 0.57 vs fixed 0.92.** | [S] claim / [V] re-test |
| R12 | Hunt Gather Trade newsletter https://newsletter.huntgathertrade.com/p/intraday-momentum-researched-based | QQQ, daily proxy 10/2014–10/2025 | — | Daily-bar proxy PF 1.26, Sharpe 1.13; criticises single-instrument over-fitting in Maróy | — | [S] |

**Read-across to our I2 (USTECH H1 CFD):**
- **Instrument:** Nasdaq evidence (R6/R7/R8, Q13) is more favourable than SPY/ES evidence (R1–R5). No public source shows NQ collapsing in 2025–26 like SPY/ES; R6 shows 2025 and 2026 positive [V]. EdgeLab's "soft patch since 2024 peak" refers to its long-only line [V].
- **Check interval:** we use H1, the paper 30 min. In Brusco's IS grid (2020-10→2023), final/14/60 had Sharpe 1.58 vs 1.73 for final/14/30 [V]. Bailey had all 54 dev settings (15/30/60 min) profitable on MNQ [S]. So H1 is not obviously harmful, but it is untested on 2025–26.
- **Session:** R6 shows the same rule **loses in Asia and London sessions** on NQ [V]. USTECH CFD trades almost 24h. Claude should verify that our I2 anchors the open at **09:30 ET** and trades only 09:30–16:00 ET, with σ built from RTH moves only [U for our code].
- **Short side:** EdgeLab says NQ shorts were negative 2010–17 [V]. The paper (Q5) says both legs contributed on SPY [V]. RipBacktest NQ shorts were positive 2020–26 (+$79,330) [V]. Mixed evidence.
- **Costs:** CFD spread/commission is the main risk. Autopsy: each extra bp/RT ≈ −0.45 Sharpe at ~330 trades/yr [S]. Concretum's own live commission was $0.012/sh vs $0.0035 assumed [S]. Our demo should log the effective spread per trade in bp.

---
## 2. C1: independent replications and post-publication evidence

### 2.1 Reference: what the paper says [V]
Paper: https://concretumgroup.com/wp-content/uploads/2026/02/Catching-Crypto-Trends.pdf (version 9 Apr 2025; SSRN 5209907).
- Data: CoinMarketCap, 21,616 coins, survivorship-free; BTC backtest 1.1.2015–19.3.2025. **Daily** close. [V]
- Signal per lookback n ∈ {5,10,20,30,60,90,150,250,360} days: enter long when Close = Donchian upper(n). Trailing stop = max(prev stop, Donchian mid(n)); the initial stop is the mid; exit when Close ≤ stop. [V]
- Size: w = min(0.25/σ_3m, 200%) × Pos; Combo = equal average of the 9 weights. [V]
- Costs: base tables are gross. Sensitivity at 10/25/50 bp; **20% rebalance threshold applied only to vol-driven changes** (signals always execute), which recovers ~100 bp/y at 50 bp cost. Later tables net of 10 bp. [V]
- BTC Combo (gross): CAGR 30%, vol 17%, **Sharpe 1.58**, Sortino 2.03, MDD 19%, alpha 14%, beta 0.17. Short lookbacks (5–30d) are best (Sharpe 1.55–1.66); 150d weakest (0.99). [V]
- Net 10 bp + threshold: BTC Sharpe 1.56, MDD 19%; ETH 1.51, MDD 15% (from Aug 2015). [V]
- Top-20 rotation, monthly: CAGR 18%, vol 9%, Sharpe 1.57, MDD 11%, alpha 10.8%. [V]
- **Long-short appendix (BTC, gross): Combo CAGR 27%, vol 18%, Sharpe 1.31, MDD 19%** vs long-only 1.58; L/S 5-asset portfolio net Sharpe 1.09 vs LO 1.44. The authors call L/S results "sensitive to modeling assumptions". [V]

### 2.2 Replications
| # | Who / link | Setup | Result | Post-paper (after 19.3.2025) | Tag |
|---|---|---|---|---|---|
| C-R1 | **AlgoEdge Research** issue 30.10.2026 https://algoedgeinsights.beehiiv.com/p/catching-crypto-trends-the-nine-model-strategy-that-cut-bitcoin-s-worst-crash-from-83-to-20 ; live page https://algoedgeresearch.com/live/crypto-trend | BTC+ETH, daily 00:00 UTC, 9 lookbacks, 25% vol target, 0.10% fees | BTC 12/2015–10/2026 Sharpe 1.45, MDD −20% (B&H 1.07/−83%); ETH 1.04/−16%. Average exposure ~21%, 25%/y vs 62% B&H. Each single lookback Sharpe 1.07–1.46. At 0.5%/trade cost Sharpe 1.27. Placebo (shuffled timing, 1000x) median Sharpe 0.75. ML add-on made it **worse**. | **Apr 2025–Oct 2026: Sharpe 0.05 ("flat"), worst loss −15%.** By period: 2015–21 Sharpe 1.96; 2022–3/2025 0.84. Live page (close 16.11.2026): in cash, 0/9 models long; last 5y 5.7%/y, Sharpe 0.49, MDD −15.3% | [S] article; [V] live-page stats as displayed (still a backtest extended daily, not a live account) |
| C-R2 | **Jaewon Jung / QuantMage** (23.04.2025) https://www.1nve.st/p/catching-crypto-trends | 5 horizons (20,40,60,90,150), GBTC/ETF, different exit (Ultimate Smoother) and **strategy-vol** sizing, SHV/IAU defensive leg | CAGR 31.5%, MDD 15.9%, Sharpe 1.4 (9y) | None. Rules picked "after some experimentation" (in-sample) | [V] (author page) |
| C-R3 | Quantpedia / QuantConnect implementation https://www.quantconnect.com/terminal/cache/embedded_backtest_c314ca2005a3645b28a2d77a133e4371.html | Top 5–20 coins, long-only, monthly EOM rebalance, liquidity exit rules omitted; start 2018-01-01; series to ~Aug 2026 | Stats not extracted from the embedded page | — | [U] numbers |
| C-R4 | "The Replicator" Delphic Alpha (24.03.2026) https://delphicalpha.substack.com/p/the-replicator-catching-crypto-trends | 67 coins | Paywalled | — | [U] |
| C-R5 | QuantifiedStrategies article (X post 15.09.2025) | summary | — | — | [S] |

No GitHub replication with post-2025 OOS and costs was found for C1 [U]. A reader comment on C-R2 (hydromod) says Turtle-style BTC trend "worked much better in early years and has settled down" [S, anecdotal].

---
## 3. Community criticism, failure regimes, and proposed improvements (with evidence grade)

### 3.1 I2 (noise area)
| Issue / proposal | Source | Evidence type | Grade |
|---|---|---|---|
| Fails in low-vol, range-bound or steady-uptrend regimes (2016–17, 2025); best in crises (2008, 2020, 2022) | Serpa [V]; Concretum table [V]; Brusco [V] | Observational, consistent across sources | Strong |
| Post-publication / crowding / 0DTE decay | Serpa [V], Autopsy [S] | Hypothesis; Delgado shows decay began ~Sep 2025, not at publication [S] | Unproven cause |
| Short side is a "long-vol bet", not robust on NQ | EdgeLab [V] | Split IS/OOS | Medium (single source; RipBacktest NQ shorts positive 2020–26) |
| Costs: ~0.45 Sharpe per extra bp/RT | Autopsy [S] | Sensitivity | Strong for CFD execution |
| Lookback 90d / multiplier 1.5 | Concretum FAQ Q14 [V], Quantitativo [V] | **In-sample only.** Brusco's frozen test shows 14d config wins; walk-forward selection destroys value | Curve-fit risk |
| Maróy exits (VWAP/Ladder), full optimisation → Sharpe >3 | Maróy [S] | Optimised in-sample; failed Brusco's frozen re-test [V] | Reject |
| Base exit (opposite band) instead of band+VWAP | Brusco [V] | Better 2024–26 on SPY and ES but **post-hoc** | Candidate for prereg only |
| Delgado filters: asymmetric short filter, RelVol sizing, vol overlays, persistence, profit lock, breakeven, trade caps, daily loss limit, VWAP dominance, regime overlays | Delgado [S] | 129-trial search, PBO 38–41%; frozen spec Sharpe 1.27 (whole period) | Weak; high over-fit probability |
| Fast-alpha execution overlay (wait for 1 opposite 5-min bar before entry/exit) | Concretum QuanTips #2, 02/2026 [V] https://concretumgroup.com/wp-content/uploads/2026/02/Improving-Performance-with-Fast-Alphas-A-Tactical-Overlay-for-Intraday-Trend-Trading.pdf | Applied to a **different** baseline (open ± ½ATR14 bands, 15-min checks; SPY 2007–1/2026 Sharpe ~0.87 → 0.99, +~200 bp CAGR); no holdout | Author in-sample |
| VIX-implied bands/sizing | Concretum 07/2026 [S] (paywalled) | Rules not public | [U] |
| Session matters (NY only on NQ) | RipBacktest [V]; Concretum BTC intraday 16.11.2026 (best session Sharpe 1.33 gross, others "a fraction") [S] | Cross-session test | Strong implementation point |
| SMA-trend filter for shorts (only short below 100/150/200 SMA) | Concretum FAQ Q21 [V] | Concretum: **sacrifices** profit | Reject |
| Multi-ETF/stock basket | Concretum Q12 (Sharpe >2 for a portfolio, 2018–8/2024) [V]; Quantitativo: "couldn't make it work for most stocks" [V] | Conflicting; selection bias risk | Weak |

### 3.2 C1 (crypto Donchian ensemble)
| Issue / proposal | Source | Grade |
|---|---|---|
| Choppy markets: flat Apr 2025–Oct 2026 | AlgoEdge [S] | Observational, OOS |
| Low return at 25% vol target (~21% average exposure) | AlgoEdge [S]; paper vol 17% [V] | Design property |
| Higher vol target (60%) → ~62%/y, MDD −42%, needs leverage on ~13% of days, borrow cost ignored | AlgoEdge [S] | Same Sharpe in-sample; leverage risk |
| Long-short weaker than long-only on BTC | Paper appendix [V] | Strong (authors' own) |
| Diversify across 10–20 coins (Sharpe ~1.5, MDD 11%) | Paper [V] | In-sample, survivorship-free; free data can't replicate honestly (AlgoEdge) [S] |
| 20% rebalance threshold on vol-only changes | Paper [V] | Cost-saving, low over-fit risk |
| ML overlay | AlgoEdge: made it worse [S] | Reject |
| Intraday bars (H6) instead of daily | No public test found [U] | Our deviation, untested publicly |

---
## 4. Live, watchable accounts (public pages only, ≥6 months)
| Account | Link | Age | Return / DD | Logic | Fit to C1/I2 | Tag |
|---|---|---|---|---|---|---|
| **ares** (Collective2) | https://collective2.com/details/131145247 | Since 12.09.2020 (75 months) | 32.4%/y compounded, MDD 14.1%, Sharpe 1.48, 781 trades, win 35.7%, avg 2.3 h. Years: 2021 +17.8, 2022 +76.4, 2023 +17.8, 2024 +70.1, **2025 +5.0**, 2026 YTD +14.6 | MNQ futures L/S, intraday, no overnight, always a stop, 1% risk/trade; **exact rules not public** | Closest public analogue to I2-on-Nasdaq (intraday NQ, flat EOD, low win rate/high payoff). The 2025 weakness matches the I2 regime. C2 labels it "hypothetical"; the page says 1,119 trades were placed in real brokerage accounts | [V] page stats; rules [U] |
| AlgoEdge "Catching Crypto Trends" | https://algoedgeresearch.com/live/crypto-trend | Daily since issue (10/2026), stance hash-chained | Backtest extended daily; 5y Sharpe 0.49 | Exact C1 (BTC/ETH) | A **signal tracker**, not a live account; useful as a free daily cross-check of our C1 stance (currently 0/9 long) | [V] page |
| RipBacktest NQ forward test | https://ripbacktest.com/posts/noise-area-breakout-nq/ | Since 12.10.2026 | — (too new) | Exact I2 on NQ, NY session | <6 months; worth re-checking in 2027 | [V] |
| Chuk MNQ paper-forward | https://www.justinchuktrading.com/trading-strategies | Since 28.09.2026 | No P&L published | I2 adaptation | <6 months; paper only | [S] |
| MQL5 "Nasdaq Intraday" (VOLQUIS) | https://www.mql5.com/en/signals/2387090 | 14 weeks | −0.11% | USTEC intraday M15, rules undisclosed | **Fails ≥6 months**; listed only because it showed up | [V] page |
| Eriksson "Bitcoin Core" | https://erikssonsystems.com/systems/bitcoin-core/ | Myfxbook live since 12/2025 (~9 months) | +13.9%, MDD 19.9% (vendor page) | BTCUSD multi-entry breakout, multiple timeframes | Not a daily Donchian ensemble; vendor-reported | [S] |
| Myfxbook "BTC Breakout EA" (MrThibo) | https://www.myfxbook.com/members/MrThibo/btc-breakout-ea/12194354 | 2026 only | +24.0%, DD 22.1%, avg trade 12 min, 81% win | BTC scalper | Not similar (scalper, <6 months) | [V] page |
No Darwinex/eToro/FXBlue/ZuluTrade account with documented C1- or I2-like rules was found [U, absence; Darwinex/FXBlue not exhaustively searched].

---
## 5. Does Concretum publish live performance or rule corrections?
- **I2:** yes, until **Aug 2025**. The FAQ Q24 monthly table is in the paper (versions 03.02.2025, then 22.09.2025) [V]. LinkedIn monthly posts appeared through at least Apr/May 2025 [S]. **No update after Aug 2025 found** [U, absence], i.e. nothing covering the Sep 2025–2026 weak regime that Delgado/Brusco document.
- **I2 rule clarifications:** Delgado says exact reproduction needs (a) **typical-price VWAP** and (b) **VWAP confirmation at entry**, both taken from the authors' published Python reference code [S]. Serpa notes the reference code dividend-adjusts the previous close used in the noise area [V]. The FAQ (Q1–Q25) covers code, data, lookbacks, VWAP-only stop and slippage [V]. **Action for Claude:** check that our I2 entry requires price beyond **both** the band and VWAP, and which VWAP price we use.
- **C1:** no performance update and no corrections found since the 9 Apr 2025 version [U]. Concretum's crypto work since then: a free Kraken minute-data tool (13.11.2026) and "Bitcoin Intraday Momentum" (16.11.2026, paywalled; best custom session 29.8%/y gross, Sharpe 1.33) [S].
- Concretum's newer paywalled intraday items (VIX bands 07/2026, intraday seasonality 08/2026, ETFs 08/2026) suggest they keep refining the family, not that they have endorsed the original as unchanged [S/interpretation].

---
## 6. Candidate improvements for **pre-registered** testing (dev + holdout). Nothing changes on demo without Nadav's decision.
Proposed protocol: freeze the spec and the list of variants before any run. Dev = data up to 31.12.2023 (I2) / 19.03.2025 (C1); holdout = afterwards, opened once. Apply a DSR/PBO-style penalty for the number of variants. Pass = holdout Sharpe ≥ 50% of dev **and** > 0 after realistic CFD costs.

**I2 (USTECH):**
1. **I2-A (implementation audit, not a variant):** RTH-only anchor (09:30 ET open, max/min(open, prev close)), σ from RTH minutes only, VWAP confirmation at entry, typical-price VWAP. Report the H1 vs 30-min effect. Evidence: R2/R6. *Low over-fit risk.*
2. **I2-B long-only vs L/S:** pre-register both; decide by dev. Evidence: EdgeLab (shorts negative IS) vs RipBacktest (shorts positive). *Medium.*
3. **I2-C base exit (opposite band) vs band+VWAP:** Brusco's post-hoc 2024–26 observation. Only valid if dev ≤2023 also supports it. *High over-fit risk, as Brusco warns.*
4. **I2-D cost stress:** effective spread from demo fills, plus +1/+2 bp per RT. Kill if net Sharpe < 0.5 at +1 bp. Evidence: Autopsy. *Essential.*
5. **I2-E fast-alpha execution delay** (one opposite M5 bar before entry/exit, with a max wait). Concretum in-sample on a different baseline only. *Medium.*
Rejected outright: Maróy-style full optimisation, walk-forward reselection, SMA short filter, lookback 90 / multiplier 1.5 (in-sample selected).

**C1 (BTC/ETH):**
1. **C1-A paper-faithful control:** daily bars, 9 lookbacks 5–360, long-only, 25%/σ3m cap 200%, 20% vol-only threshold, 10 bp. Run it side by side with our H6 / 7-lookback / half-L/S variant, to know whether our deviations add or cost. *Essential, low risk.*
2. **C1-B long-only vs our 50% L/S mix:** the paper says L/S is weaker on BTC. *Low risk.*
3. **C1-C 20% rebalance threshold** on vol-driven changes if not already used. *Low risk; cost-only.*
4. **C1-D higher vol target (e.g. 35–40%)** with leverage ≤1x: raises return; Sharpe unchanged in-sample. A sizing decision for Nadav, not an "edge" improvement.
5. **C1-E add 3–8 liquid coins** (paper's rotation, monthly, liquidity exits). Survivorship-free universe data is needed; otherwise biased.

**Decisions Nadav should make before real money (from this survey):**
- (a) Accept that **I2 has a documented ~12-month negative regime on SPY/ES (Sep 2025→Aug 2026)**. Nasdaq looks better but evidence is mixed. Either require a minimum forward period on demo (e.g. 6 months per Brusco's "frozen forward monitoring") or size I2 small.
- (b) Accept that **C1 at a 25% vol target earned ~0 for 18 months after publication**. It is a drawdown-control/crypto-exposure tool, not a 3–8%/month engine. Expected return at the paper's risk level is single-digit to ~25%/y in backtests (arith from the sources above).
- (c) Whether to run the paper-faithful C1 control (C1-A) alongside our variant on demo. That is a change, so it needs his OK.

---
## 7. Method notes / limits
- Reddit (old.reddit JSON) and SSRN abstract pages blocked or timed out from this box. Those items rely on search-index excerpts and are tagged [S].
- X search (public, via the X connector): little substantive discussion. The relevant items were @ConcretumR posts (13 and 16.11.2026, Kraken data / BTC intraday by session) and @quantitativo1 (16.01.2025, ES/NQ implementation). No critical threads with data found.
- YouTube / Elite Trader not covered in depth [U]. Matt Cullerton's "tokdocs" page says a viral TikTok misrepresented the noise band as a "survivor" from testing 50 papers [S, not opened].
