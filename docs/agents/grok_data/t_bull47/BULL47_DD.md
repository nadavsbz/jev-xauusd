# BULL47_DD — Public-sources due diligence: "EA Bull Scalper" v4.7 and "Hedge Hog" (Ofer Dvir / MQL5 seller `oferdvir`)

Prepared by Grok for Claude (request 17.11.2026 18:45), 17.11.2026 ~19:10 Asia/Jerusalem.
Method: public pages only (curl / web fetch / web search / X public read API). No sign-up, no login, no purchase, no rental, no demo download, no contact with the seller.
Tags: **VERIFIED** = seen by me on a primary page (URL given); **[S]** = secondary source; **UNVERIFIED** = claim with no verifiable evidence.

## 0. Verdict (TL;DR)
- **No verifiable live track record exists in public** for Bull Scalper, Hedge Hog or any other product of this seller: MQL5 profile shows **0 signals / 0 subscribers**; no Myfxbook/FXBlue account found; no FTMO certificate published; all "live" evidence is seller-posted phone screenshots and seller videos. **VERIFIED** (absence, as of 17.11.2026).
- The **"~1%/day" claim has no public evidence**. The only public trace is the seller's own 17.11.2024 blog stating a *goal* of "1-2% a day" and admitting earlier "200-400% a day but the next day -50%". 1%/day compounds to ≈ ×12.3/yr (≈ +1,127%/yr on 252 trading days; ≈ +23%/month) vs. Claude's tester ~+7.8% over 1.5y (≈ 5%/yr ≈ 0.4%/month). The claim is ~2 orders of magnitude above the tester.
- Mechanics are **buy-only DCA averaging-down with optional martingale, trailing only in profit, stop loss optional/delayed and by default off in the seller's own setups** → classic negative-skew tail risk on index/gold crash days (exactly the BD crash-day profile we are trying to neutralize).
- **Recommendation: REJECT / PARK** (do not run, not even on demo, until real evidence exists). Minimum evidence to reopen: MQL5 signal (or investor access) on a real account, **≥3 months** of v4.7 forward and ideally **≥18 months** history on the same logic, passing our gate: honest ≥3.5%/month, age ≥1.5y, equity DD ≤25%, hard server-side SL on every position, no grid/martingale tail (max open lots bounded), and no loss on BD crash days.

## 1. Product facts — EA Bull Scalper (MT5) — https://www.mql5.com/en/market/product/116071
| Item | Value | Tag |
|---|---|---|
| Price | Buy 45 USD; Rent 1 month 32 USD | VERIFIED (product page) |
| Published | 18 September 2024 | VERIFIED |
| Current version / updated | 4.7 / 17 November 2026 | VERIFIED |
| Demo downloads | 84 | VERIFIED |
| "Activations: 20" | This is the **number of activations allowed per purchase** (installations per licence), **not a count of buyers/users** — correct the earlier reading "20 activations" | VERIFIED value; meaning [S] (MQL5 forum: https://www.mql5.com/en/forum/60012 , https://www.mql5.com/en/forum/353866) |
| Reviews | 1 — from a **[Deleted]** user, 2024.11.19 09:46, no text; seller replied 12:46 | VERIFIED |
| Comments | 7 — **all 7 by the seller** (2024.11.27 → 2025.12.05): phone screenshots ("Real account", "my private account"), FTMO set files (ftmo10kbtc.set, ftmo10k100.set, ftmo_nasdaq.set) and tester report images | VERIFIED https://www.mql5.com/en/market/product/116071/comments |
| Seller self-description | "the whole point in this scalping strategy is to accept some drawdown and let the ea open position when the trend also goes against so the ea will open DCA positions" | VERIFIED (overview) |
| Positioning | buy-only; trailing stop applied only once a position is in profit | VERIFIED (overview) |

### 1.1 Version history (What's new tab) — https://www.mql5.com/en/market/product/116071/updates (VERIFIED)
| Version | Date | Note (seller text, abridged) |
|---|---|---|
| 1.7 | 2024.09.22 | opening positions after trailing detected |
| 2.0 | 2024.11.04 | $ risk mgmt "for funded trading set to max day loss", cooldown |
| 2.20 | 2024.11.17 | position opening mgmt |
| 2.30 | 2024.11.20 | position tracking |
| 2.31 | 2024.12.01 | on-chart P&L; "position opening double outcome with more safety measures" |
| 2.32 | 2024.12.09 | cosmetic |
| 3.0 | 2025.02.17 | new trailing model; "fix for all brokers risk loss feature" |
| 3.1 | 2025.02.17 | retracement % input |
| 3.3 | 2025.02.21 | avoid top position placing |
| 3.4 | 2025.02.23 | position management |
| 3.5 | 2025.02.24 | error cooldown (not enough money → retry later) |
| 3.51 | 2025.02.24 | patch correction |
| 3.61 | 2025.03.12 | reduced printing |
| 3.71 | 2025.04.22 | "AI trading scalper module" |
| 3.72 | 2025.06.03 | trailing sensitivity multiplier |
| 3.73 | 2025.06.19 | on-chart line where next DCA position opens |
| 3.74 | 2025.06.25 | position spacing multiplier |
| 4.0 | 2025.07.20 | **"Martingale option added"**, **"delayed position stop loss added!"** |
| 4.1 | 2025.09.08 | trailing start line; improved AI calc |
| 4.2 | 2025.11.02 | **"Martingale Improved"** |
| 4.3 | 2025.12.10 | swing swap calculation |
| 4.7 | 2026.11.17 | "Better models / Profit lock / Burst extreme hi frequency trading" |

Cadence: **22 releases in ~26 months** (avg ≈ 1 per 5 weeks), with bursts (6 releases 17–24 Feb 2025; 4 in June 2025), then an **~11-month gap** (2025.12.10 → 2026.11.17) and a jump 4.3 → 4.7 released *today*. Any track record before today is on a different logic version; v4.7 has **zero days** of public forward history. VERIFIED (dates); interpretation is mine.

## 2. Hedge Hog (MT5) — https://www.mql5.com/en/market/product/154007
| Item | Value | Tag |
|---|---|---|
| Price | 55 USD | VERIFIED (seller list / product) |
| Published / version | 30 October 2025 / 1.4 (updated 2 November 2025) | VERIFIED |
| Demo downloads / activations-per-licence | 75 / 15 | VERIFIED |
| Reviews / comments | none | VERIFIED |
| Versions | 1.3 (2025.11.02) "position and martingale fix, risk loss fixed"; 1.4 (2025.11.02) "Position management fix" | VERIFIED https://www.mql5.com/en/market/product/154007/updates |
| Description | "Built on the foundation of ... EA Bull Scalper v4, it extends **buy-side grid trading** with limited hedging"; "Lot Progression: Supports incremental sizing for scaled entries, with aggressive modes"; risk controls "max drawdown limits (e.g., 5%), per-position risk caps (e.g., 6000 points)"; aimed at Nasdaq | VERIFIED |
| Seller blog launch post (3 Nov 2025) | "I just started playing around with my new Expert Advisor ... Hedge Hog EA" — i.e. no track record at launch | VERIFIED (profile feed https://www.mql5.com/en/users/oferdvir) |
| Live account / signal | none found | VERIFIED (absence) |

## 3. Seller profile — https://www.mql5.com/en/users/oferdvir
- Name "Ofer Dvir", "Sound Engineer at Germany", country Israel, rating 2581; **"2 years experience", 14 products, 25 demo versions, 0 jobs (freelance), 0 signals, 0 subscribers**. VERIFIED.
- **Registered at MQL5.community 2023.01.26**. VERIFIED (profile page 4 feed).
- Links: Facebook page "Bull Trading Society" (https://www.facebook.com/people/Bull-Trading-Society/61573385519457/) — not fetched (login wall); X @dvir_ofer; YouTube @oferdvir3558; free Udemy course "Mastering automatic trading" (includes a free LE version of Bull Scalper) [S] (https://comidoc.com/udemy/mastering-automatic-trading).
- **Products (14)** — all VERIFIED from product pages (demo DL / published / version / reviews / comments):
  - EA Bull Scalper MT5 116071 — 84 / 2024-09-18 / 4.7 / 1 / 7
  - EA Bear Scalper MT5 123680 — 50 / 2024-09-23 / 4.0 / 1 / 10 (35 USD; "Limited time 35$ for 100copies then ... retail price of 225$")
  - Bull EA Scalper MT4 126941 — 22 / 2024-11-19 / 4.0 / 1 / 3 (30 USD; "Special for 24Hours will be back to 125$ soon!!")
  - Bear EA Scalper MT4 127430 — 11 / 2024-11-28 / 4.0 / 1 / 3 (85 USD; "Limited time for 45$ then i go to the retail price of 299$"; description lists default `MaxDrawdownPercent = 100.0` and `Risk = 6000` points "Hidden stop loss")
  - Slalom Scalper 133991 — 31 / 2025-03-10 / 2.0 / 0 / 5 ("Smart Recovery", reverses after SL)
  - Fibonacci Scalper Bullish 134332 — 31 / 2025-03-16 / 1.5 / 0 / 10
  - Slalom Scalper pro (MT4) 136375 — 9 / 2025-04-17 / 2.0 / 1 / 3
  - Fibonacci Scalper Pro Seller 138378 — 19 / 2025-05-09 / 1.4 / 0 / 3
  - Gap Rider 153142 — 25 / 2025-10-20 / 1.0 / 0 / 2 ("just drop it on any test even corona crushes :)")
  - Hedge Hog 154007 — 75 / 2025-10-30 / 1.4 / 0 / 0
  - Free: Chart historical archeology viewer 128104, Summorai 143883, Summorai mt4 148190, Trailer 159803 (free "reduced version" of Bull Scalper, 2025-12-27)
- No removed products or old signals are visible publicly (cannot see deleted items without login) — UNVERIFIED either way.
- 2026 activity on MQL5 feed: roulette-tracker app (2026.05.11, 2026.05.27), stage-plot Mac app (2026.02.20); no trading results posted in 2026 before v4.7. X account @dvir_ofer (created 2023-07-04, 9 followers) has since July 2026 posted almost only roulette-app promotion; last Bull Scalper posts 2026-01-14/22/28 (images/video links only). VERIFIED (X public API, MQL5 feed).

## 4. Public traces of live accounts / performance claims
| Source | What exists | Tag |
|---|---|---|
| MQL5 Signals | Profile shows 0 signals; none found under seller name | VERIFIED (absence) |
| Myfxbook / FXBlue | Nothing found (web search; Myfxbook direct member URL 403) | VERIFIED-absence via search only (search coverage limited) |
| FTMO / prop | Seller video 2025-06-03 (https://www.youtube.com/watch?v=qN1EDudvqxI, transcript fetched): he is running **the free FTMO trial** (80k demo), day 2 at ~82k, 5 lots/position, up to 20 DCA positions, "**I am not using any stop-losses like the risk management. I don't like it**", says he will "open a signal connected to the FTMO" — **no such signal exists**. Profile posts: 2025-06-11 "day 2 of the FTMO 80,000$ challenge ... if you use the Signal"; 2025-06-27 "Bull v3.74 ... just passed 4 different FTMO challenges (Swing account) each in around 5-10 days"; 2025-07-03 "FTMO challenge will be finished soon"; 2025-10-24 "Another happy EA Bull Scalper [user] just sent me that he passed a Challenge". **No certificate, no account link, no outcome posted.** A free trial is a demo. | Posts VERIFIED; claims UNVERIFIED |
| MQL5 comments | 2024-11-27..2025-01-22 phone screenshots labelled "Real account"/"my private account"; no account number, broker statement or link | VERIFIED (exist); content UNVERIFIED |
| YouTube | ozbDJ4bg4Fc "Bull Scalper v3: Professional MT5 Expert Advisor" (transcript = feature tour + tester/visual demo; describes "complex DCA plus strategy", max-risk-in-points as SL, "close all position on Max draw down is a risky powerful tool"); yE3GF4ku36Q "Using EA trading scalping robot Bull Bear metatrader5" (2024-09-23, 213 views, "which i use for my day trading account"); 2pKf87DWO1k short (title only: "EA Bull scalper and Fibonacci scalper + a free bot"); 2025-12-25 profile post "EA Bull scalper 2025 10000 to 30000 forex scalping" (video, no account) | VERIFIED (metadata/transcript); no verifiable account shown |
| X @dvir_ofer | Nov 2024 "will try to post every day the P&L"; posts are images/promotions only; 2025 promo posts tag #the5er #FundedTrader | VERIFIED (exist); P&L UNVERIFIED |
| Telegram | 2025-06-10 blog says "join the channel I update there almost every day" (likely an MQL5 channel); no public Telegram channel found | UNVERIFIED |
| Facebook | Page "Bull Trading Society" exists (link on profile); content behind login wall, not read | UNVERIFIED |
| Reddit / Forex Factory | No mentions found (Reddit API 403; web search returned nothing relevant) | VERIFIED-absence via search only |
| Hebrew sources | Search for "עופר דביר" + trading/robot returned only MQL5 pages; no Hebrew reviews/mentions found | VERIFIED-absence via search only |

## 5. Independent user reviews / mentions
- Only third-party voices found: MQL5 review by a **[Deleted]** account (no text) on 116071; on Bear Scalper 123680 two users (René, Dec 2024; Kevin, Oct 2025) **asking for set files** — no results reported. VERIFIED. No independent positive or negative performance reports anywhere public.

## 6. The "≈1% per day" claim
- Source of current claim: Ofer → Nadav privately (per Claude). No public post states "1%/day" for v4.7. UNVERIFIED.
- Only public related text: blog "Ea scalping strategy", 17 Nov 2024 (https://www.mql5.com/en/blogs/post/759899): "**my profit goal is 1-2% a day** i find it a stable goal ... **before that i was making 200-400% a day but the next day -50%** and so on"; same post: new positions are "**not limited to the max number of ea positioned opened by ea only limited by the account free margin**". VERIFIED [S-level: via search snippet; direct fetch returned HTTP 503 rate-limit at time of check].
- Arithmetic: 1.01^21 ≈ 1.232 (+23%/month); 1.01^252 ≈ 12.27 (+1,127%/yr); 1.01^365 ≈ 37.8. Claude's tester for v4.3: +7.8% / 1.5y ≈ +5.1%/yr ≈ +0.42%/month. A "1%/day" EA that returns 0.4%/month in a real-tick test is either (a) running far larger lot/martingale settings than tested (→ much larger tail), or (b) the claim is a short-window cherry pick.

## 7. Red flags (each with evidence)
1. **No verifiable track record** after ~26 months on sale: 0 signals, no Myfxbook/FXBlue, no FTMO certificate; only screenshots. (VERIFIED absence)
2. **Refused investor access** to a live account despite repeated requests (per Nadav/Claude; not public) — combined with flag 1 this is disqualifying under our rules.
3. **Buy-only DCA averaging-down** by design ("accept some drawdown and let the ea open position when the trend also goes against"), **grid** (Hedge Hog: "buy-side grid trading"), **martingale option since 4.0, "improved" in 4.2**, Hedge Hog "lot progression ... aggressive modes". (VERIFIED) → profits come from many small trailing wins; losses come in rare large clusters (index gap-down/crash day, gold flush). Tester PF 5.5 with DD 4.3% is typical of such systems until the tail event; it is not evidence of safety.
4. **Stop loss is optional/"delayed"** ("delayed position stop loss", "give positions time before applying position SL"); "maximum risky positions allowed (positions without SL in profit)"; seller on video: "I am not using any stop-losses"; Bear default `MaxDrawdownPercent = 100.0`; "Risk = 6000 Max risk in points ... Hidden stop loss". (VERIFIED) → no hard server-side SL = fails our gate.
5. **Frequent, bursty version changes** (22 releases; 6 in one week; jump 4.3→4.7 today). Any history is not on v4.7. (VERIFIED)
6. **Marketing patterns**: fake-urgency prices ("Special for 24Hours will be back to 125$", "retail price of 299$" while selling at 35–85 USD for 1–2 years), requests for 5-star reviews, "get 1000x what you paid", "just drop it on any test even corona crushes". (VERIFIED)
7. **Seller's own words on performance variance**: "200-400% a day but the next day -50%". (VERIFIED via search snippet)
8. **Low adoption**: 84 demo downloads in 26 months; 1 review (deleted user); all comments by seller. (VERIFIED)
9. Seller's public activity in 2026 shifted to roulette/casino app promotion (MQL5 feed + X). Context only, not evidence about the EA. (VERIFIED)

## 8. What evidence would be required to reopen
- An **MQL5 Signal** (preferred, real account, broker-verified) or **investor (read-only) access** to a real account running **v4.7 unchanged for ≥3 months**, with full closed-trade history export; and ideally the same logic family live **≥18 months**.
- Our gate on that record: honest return ≥3.5%/month after costs; **equity** max DD ≤25% (not balance DD); age ≥1.5y; hard server-side SL on every position; bounded max open lots (no martingale/grid tail); profits not concentrated in a few days; **no loss on BD crash days** (check the account on the BD crash-date list).
- Plus: the exact .set used on the account, and a real-tick tester run of v4.7 with that .set over ≥5y including 2020-03, 2022 and the 2025/2026 crash days, reporting max simultaneous positions/lots and worst-day loss.

## 9. Raw evidence on box
`/workspace/claude_bridge/out_20261117/t_bull47/raw/` — fetched HTML/text of product, updates, comments pages (116071, 154007, other products), seller profile pages 1–4, seller list, blogs 762902/760240/763491/761032/764240, YouTube metadata.
