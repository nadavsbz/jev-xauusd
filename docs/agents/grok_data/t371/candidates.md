# t371 candidate triage (Grok -> Claude)
Written 24.11.2026 ~19:25 IST (Asia/Jerusalem, UTC+2). Read-only: public pages via WebSearch/WebFetch and plain unauthenticated curl of public MQL5 pages. No log-in, sign-up, follow, copy, subscribe or purchase. No browser. No MT5 terminal touched.
Tags: VERIFIED = read on the source page. OBSERVED = my arithmetic on VERIFIED numbers (shown). ASSUMED = my inference. UNKNOWN = not shown publicly.
Protocol: t363 event_claims_protocol.md was read read-only on Benzaquen. It covers event claims ("when X says Y, the market moves"). For track records I applied its spirit (fixed screen locked before pulling pages; no moving gates afterwards). No event claims came up in this round, so its n>=20 / random-day / confounder steps were not triggered.

## Method (locked before looking at any candidate page)
1. Crawled the public MQL5 Signals list pages (MT5 page1-52 + MT4 page1-60, orderby=rating, plus growth sort): **3,769 unique public signals** parsed (`list_parsed.csv`, raw HTML in `raw/list*`).
2. De-duped against **896 signal IDs** already present in earlier rounds' files on the box (`_prior_ids.txt`) and the closed families listed in the task.
3. Numeric pre-screen from list columns: weeks >= 78 (18 months), list max DD <= 25%, geometric monthly from MQL5 growth (MQL5 growth already neutralises deposits/withdrawals) >= 3%/month. Result: **74 pass numerically; 65 are prior/closed; 9 new.** Six of the 9 were below 3%/mo once computed from growth/weeks (Quasar 2392579 39%/90w, Bot Pulse 2272948 9%/104w, Vinh KWS 2309411 41%/106w, Daytrade Pro Live 1949810 81%/185w, Page One 2310235 27%/78w, VPX Candle Day 2378459 66%/79w = 2.83%/mo) [OBSERVED from list columns]. The rest were opened in full.
4. For every opened page: the monthly growth table, the W1 growth series and the stats block were parsed from the public HTML (`monthly.py`). Top-10 concentration is computed on **weeks** (daily series not public); MQL5's own "80% of growth achieved within N days" line is quoted when shown.
5. Off-MQL5: one Myfxbook/EdgeWatchFX lead (Apex DayTrader) found via WebSearch. Myfxbook, Darwinex, FXBlue, Zulu, Binance and OKX leaderboards were already mined in t202-t256 and were not re-crawled.

---

## C1. ICM30 — https://www.mql5.com/en/signals/2400112 (Oeyvind Borgsoe / Relevant Trading, MT4, ICMarketsSC-Live24)
- Age: 208 weeks, monthly table starts Nov 2022 [VERIFIED]. **But the signal was registered on 2026.11.16 ("Started 2026.11.16 14:08")**, and the history before that is imported. The risk block states that the monitoring period is **6 days 3 hours** [VERIFIED]. So the live-monitored part is 8 days.
- Return: growth 1,813.70%, initial deposit 20.00 USD, deposits 0, withdrawals 0 [VERIFIED]. Geometric monthly from the monthly table: all 49 months 6.21%/mo; **last 24 months 2.99%/mo; last 12 months 1.53%/mo** [OBSERVED]. The headline comes from a 20 USD start: Nov 2022–Mar 2023 = +13.9/+37.3/+26.1/+22.1/+14.7% [VERIFIED table]. ASSUMED: minimum-lot granularity on a 20 USD balance inflates early % returns.
- Worst month: **Aug 2026 −13.46%** [VERIFIED]. Both sibling signals by the same author were hit in the same month (Balanced Blend 1724716 −5.85%, Balanced Blend 2 2229611 −5.55%) [VERIFIED], so ASSUMED: shared EA components.
- DD: balance max 73.28 USD = 17.39% [VERIFIED]. Equity DD shown is 4.95% [VERIFIED], but it covers only the 6-day monitoring window, so **historical equity/floating DD is UNKNOWN**.
- Instruments: EURUSD 1,137 deals, USDCAD 1,079, plus a few other FX [VERIFIED]. Cost class A (FX majors well under 2 bp/side) [ASSUMED from typical ECN spreads]. Swap: UNKNOWN (5-hour average hold, so it carries some overnights).
- Grid/martingale evidence: concurrent positions UNKNOWN (trade list needs log-in). Win rate 82.81%, avg win 0.37 vs avg loss −0.84 USD, best trade 11.84 vs worst −48.24 USD, max consecutive loss −73.28 USD in 2 trades (= the whole 17.39% DD) [VERIFIED]. ASSUMED: the profile fits a basket, averaging or wide-stop mean-reversion book; it cannot be excluded without the trade list. Max deposit load 4.40% [VERIFIED, 6-day window only]. Long 75.28% [VERIFIED].
- Cost hurdle: net points = (62,273 − 17,940) / 2,269 = **~1.95 pips per trade** [OBSERVED], below the RoboForex hurdle of 4–5 pips per trade. Not replicable at our cost even if the rule were known.
- Concentration: no "80% within N days" warning shown [VERIFIED]. Top-10 weeks = 36.1% of log growth [OBSERVED, weekly proxy]. Daily top-10: UNKNOWN.
- Hold: average 5 hours [VERIFIED]. Median: UNKNOWN. Hard SL: UNKNOWN.
- **Verdict: NO-GO.** Honest recent return is below the bar (1.53%/mo over 12 months, 2.99% over 24 months), there is no live-monitored equity history (8 days), the edge is ~2 pips per trade (below our 4–5 pip cost), and the loss profile is asymmetric (grid or averaging not excluded). Siblings: Balanced Blend Of EAs 1724716 = 2.38%/mo over 68 months, last 12 months 0.88%, equity DD 36.01% [VERIFIED/OBSERVED] → NO-GO. Balanced Blend 2 2229611 = 1.80%/mo, last 12 months 1.28% [OBSERVED] → NO-GO.

## C2. ORDER FLOW System — https://www.mql5.com/en/signals/2348377 (Alikhan Yakhyaev, MT4, RoboForex-ECN-3)
- Age: 86 weeks [VERIFIED]. "Started 2025.12.11" means part of the history is imported; the monthly table starts Apr 2025 [VERIFIED].
- Return: growth 379.16% [VERIFIED]. Initial deposit 8.81 USD, deposits 174.55, withdrawals 10.00 [VERIFIED]. Geometric monthly 9.65% over all months, but **Apr–Jun 2025 = +43.1/+79.6/+31.7%** on a few-dollar balance; last 12 months 2.42%/mo [OBSERVED].
- Concentration: **"80% of growth achieved within 7 days. This comprises 1.17% of days"** [VERIFIED]. Top-10 weeks ≈ 100% of log growth [OBSERVED] → FAIL.
- DD: balance max 22.02 USD = 25.11%, relative balance 9.96%, equity 3.87% [VERIFIED].
- Instruments: GBPUSD 635 deals, EURUSD 94, USDJPY 45, XAUUSD 17, plus other crosses [VERIFIED]. Cost class A/B.
- Style: "Trading is fully manual; EA used only for position sizing"; author says SL on every trade and no averaging/martingale [VERIFIED as author's claim; not checked against trades]. Algo trading 88% [VERIFIED; contradicts "fully manual", UNKNOWN why]. Average hold 22 minutes [VERIFIED]; median UNKNOWN.
- Cost hurdle: ~1.9 pips net per trade (31,313 − 14,905 points / 866 trades) [OBSERVED, mixed symbols so rough] → below 4–5 pips.
- **Verdict: NO-GO** on concentration (80% of growth in 7 days), growth inflated by a tiny base, discretionary trading and a thin per-trade edge.

## C3. AlphaEdge Smart — https://www.mql5.com/en/signals/2361276 (Martin Stibor, "Founder at EdgeTraders", MT4, RoboForex)
- Age: 98 weeks [VERIFIED]. Growth 153.80%, no deposits or withdrawals [VERIFIED]. 4.13%/mo over all months, 5.08% over the last 12 months [OBSERVED].
- DD: balance relative 15.32%, max 9.53%; equity 3.55% [VERIFIED]. XAUUSD 678 of 679 deals [VERIFIED]. SL+TP on every trade, no grid/martingale (author claim) [VERIFIED as claim]. Average hold 2 hours [VERIFIED].
- Concentration: **"80% of growth achieved within 23 days (3.35% of days)"** [VERIFIED]. Top-10 weeks 58.7% [OBSERVED] → FAIL.
- **Closed family:** the numbers (15.3% DD, ~4%/mo, ~26 months) and the "EdgeTraders" affiliation match the EdgeTrader record closed in t206/t212 [OBSERVED match with RESULTS_t206.md line 37; ASSUMED same account]. A sibling, CapitalEdge Signals 2361187, is already among the prior IDs.
- **Verdict: NO-GO** (closed EdgeTrader family, and top-10 concentration over 50%).

## Other checks this round (all NO-GO)
| ID / source | Key facts | Reason |
|---|---|---|
| Expert Pro 2313981 | growth 81.70%, deposits 952 / withdrawals 1,289, balance max DD 30.45%, equity 20.07%, algo 0%, "80% of growth within 19 days", top-10 weeks 75.7% [VERIFIED/OBSERVED] | DD > 25%, concentrated, manual |
| US500 AndyCFD 2364634 | description: "uses a smart martingale strategy"; reviewer: "lack of S/L" [VERIFIED] | martingale, no SL |
| Bitcoin Scalper BTC 2294444 | 104% / 95 weeks, "80% within 11 days", last 12 months 0.27%/mo, BTCUSD only [VERIFIED/OBSERVED] | concentrated, BTC cost class > 2 bp |
| Apex DayTrader EA (Myfxbook RobotTraderKing/apex-ea/11111499) | Myfxbook gain +69.00%, **monthly 2.01%**, DD 18.98%, avg trade length 1 day [VERIFIED via search snippet]. EdgeWatchFX (built by the same developer) shows 10.6% equity DD, Pepperstone, since 10.09.2024 [VERIFIED vendor page]. "Apex H1 V2 @ ICMarkets" +215.8%, age UNKNOWN | below 3%/mo on the main ~2-year account. H1 V2 cannot be judged (age UNKNOWN); the vendor page blocks curl and Myfxbook was not bypassed |

## Young-signal pre-screen (52–77 weeks; not eligible yet; context for the next direction)
Of the 31 young public signals with ≥3.5%/mo and list DD ≤ 20%, I opened 10 [VERIFIED page stats, OBSERVED ratios]:
- Concentrated (MQL5 "80% within N days" ≤ 24 days and/or top-10 weeks > 50%): VSA 2393860, Luxor 2358121, Kefren 2369741, NebulaEA 2332163, Ingham 2360292, Five Strategy 2333519.
- Hold time under 15 minutes: NKHC 69 2380306 (5 min; equity DD 16.4% against balance DD 4.0%), CCC 2378209 (7 min, manual).
- Possible averaging (equity DD much larger than balance DD on one cross): Stable Return Portfolio 2366514 (EURCAD only; equity DD 12.1% vs balance DD 5.5%; worst month +3.41%) [ASSUMED grid-like]. AlgoTradeInvest 1 2396976 has "grid" in its description [VERIFIED].
- **None is a clean forward-watch candidate today.**

## Bottom line
**0 of the checked candidates pass triage.** Three full triages (C1–C3) plus 4 others, all NO-GO. MQL5 at list level is now essentially exhausted: all 3,769 public signals were parsed, and the 74 numeric passers are prior, closed or failed here. No PREREG for a trading rule was written, because no candidate passed (honest). The next-direction PREREG (search protocol, PROPOSED) is in `PREREG_t371_PROPOSED.md`.
