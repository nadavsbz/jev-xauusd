# t262 - ידע רחב: מט"ח, סחורות ומדדים ל-CFD ריטייל אחרי עלויות, בהחזקה של יום ומעלה (Grok, 15.11.2026)

## סיכום בעברית

**שלוש עובדות על RF שמכריעות כמעט כל רעיון.** כל המספרים מדף המפרט הציבורי של RF (ECN), שנמשך ב-15.11.2026, והם תואמים את `ecn_costs_20261030.csv`.
1. **הנכסים שאפשר לסחור בהם מעטים.**
   - מתכות: XAUUSD, ‏XAGUSD ו-XAUEUR בלבד.
   - אנרגיה: BRENT ו-WTI בלבד.
   - מדדים: DE40, ‏JP225, ‏US500, ‏USTECH ו-US30.
   - **אין** גז טבעי, חקלאות, נחושת או מתכות תעשייתיות.
   - לכן אסטרטגיות **חתך-רוחב** בסחורות ובמדדים, שבספרות הן החזקות ביותר, לא ישימות ב-RF. אין מספיק נכסים.
2. **ה-swap במדדים כמעט שווה לכל פרמיית המניות.**
   - לונג משלם ‎−8.6%/שנה (ארה"ב) או ‎−7.2%/שנה (DE40/JP225). שורט משלם ‎−1.8%/שנה.
   - כל מערכת לונג על מדד שמחזיקה ימים צריכה להרוויח את זה רק כדי להגיע לאפס.
3. **ה-swap במט"ח מפורסם וגלוי** (טבלה ציבורית ב-RF; אין צורך לנחש). יש swap חיובי בעיקר במבנה carry קלאסי:
   - **לונג** על מטבע תשואה מול JPY או CHF: ‏GBPJPY ‏+0.62, ‏AUDJPY ‏+0.55, ‏GBPCHF ‏+0.55, ‏USDCHF ‏+0.50, ‏USDJPY ‏+0.38, ‏EURCHF ‏+0.30 פיפס ליום.
   - **שורט** על EUR מול USD, AUD או GBP: ‏+0.19, ‏+0.30, ‏+0.12.
   - **הפער בין לונג לשורט** מרמז על markup של כ-1–2.5%/שנה לכל צד. ה-carry נטו שנשאר הוא כ-1–2%/שנה בלבד.
   - אין לי מחירי מט"ח עדכניים לנובמבר 2026, ולכן האחוזים השנתיים בטבלה הם הערכה.

**הרעיונות הכי טובים שעוד לא נבדקו אצלנו:**
1. **שילוב ה-carry בנפט מ-t261** (H1/H3). זה הכיוון המבוסס ביותר.
2. **FX carry סל צמדים עם swap חיובי ב-RF, עם מסנן משטר תנודתיות** (Menkhoff ואחרים 2012; Brunnermeier ואחרים 2008).
   - **חיסרון:** ה-carry ב-G10 כמעט נעלם אחרי 2008 (Fan ואחרים 2022).
   - **פתרון:** לבדוק רק עם מסנן VIX.
3. **FOMC במט"ח:** שורט USD ביום החלטת FOMC מתוזמנת (Mueller, Tahbaz-Salehi ו-Vedolin, ‏JF 2017).
   - העלויות במט"ח ב-RF זעירות (כ-0.5 נ"ב הלוך-חזור ב-EURUSD).
   - יש כ-8 אירועים בשנה.
   - שונה מסבב 35, שבדק את הסחף לפני FOMC במניות.
4. **FX value/PPP חתך-רוחב בין 8 מטבעות G10** (Menkhoff ואחרים 2017, שארפ כ-0.5).
   - איטי ומעט מסחר.
   - ה-swap האסימטרי של RF פוגע בו.
   - לא ידוע לי שיש OOS אחרי הפרסום.

**הרעיונות שלא ישימים או שכבר נבדקו:**
- מומנטום ו-carry חתך-רוחב בסחורות: אין מספיק נכסים.
- סבב בין מדינות במדדים: בפועל יש רק 3 מדינות.
- vol-managed על מדד לונג: ה-swap של ‎−8.6% והראיות ל-OOS שליליות (Cederburg ואחרים 2020).
- מומנטום במט"ח לפי סדרת זמן: סבב 10 נכשל.
- ממוצע חוזר בצמדים צולבים: סבב 43.
- FOMC במניות: סבב 35.
- תחילת חודש ב-US500: סבב 59.
- יום לפני חג: סבב 36.
- פקיעת אופציות: סבב 37.
- מגמה על מדדים: סקאן 1 F3 וסבב 3.
- יחס USTECH/US30: סבב 40.
- סוף חודש במט"ח: סבב 19.
- Gotobi: סבב 9.

---

## English detail

### 0. RF facts used throughout (public spec page, ECN tab, fetched 15.11.2026)
- **Instruments:**
  - FX: 28 G10 pairs (AUD, CAD, CHF, EUR, GBP, JPY, NZD, USD).
  - Metals: XAGUSD, XAUUSD, XAUEUR.
  - Indices & Energies: .DE40Cash, .JP225Cash, .US500Cash, .USTECHCash, .US30Cash, BRENT, WTI.
  - Also crypto and about 50 US stocks.
  - **No natural gas, agriculture, copper/industrial metals, platinum or palladium** appear on ECN or Prime. Copper's absence matches Claude's r58 finding.
- **FX costs:**
  - Average spread 0.1-1.6 pips plus commission 20 per million per side (0.2 bp/side).
  - EURUSD round trip is about 0.1 pip spread + 0.4 bp commission, about 0.5 bp.
  - Crosses run about 1-3 bp round trip.
- **Index costs:** average spread 0.2-5.5 points plus 5 per million per side.
- **Swaps:**
  - Indices: long -8.6 %/yr (US) and -7.2 %/yr (DE40/JP225); short -1.8 %/yr.
  - Oil: long -6 %/yr; short -3 %/yr.
  - Gold: long -60 / short +19 points per lot per day. At $3975 that is about -5.5 %/yr long and **+1.7 %/yr short**.
  - Silver: long -1.3 / short +0.16 pips per day.
- **Implied markups:**
  - Indices: long = -(r + m) and short = r - m give r ≈ 3.4 %, m ≈ 5.2 %/yr per side. This is a rough inference.
  - Oil: no financing is economically needed on a futures-based CFD, so the oil swap is pure markup.

**FX swap table.** Pips per day are from the RF ECN page on 15.11.2026. %/yr uses **assumed** price levels I picked as indicative; signs and relative sizes are robust, but levels should be recomputed with live prices.

| Pair | Long pips/day | Short pips/day | Assumed px | Long %/yr | Short %/yr | Long+short (≈ -2× markup) |
|---|---|---|---|---|---|---|
| USDCHF | +0.50 | -1.30 | ~0.80 | +2.28% | -5.93% | -3.65% |
| AUDJPY | +0.55 | -1.40 | ~99 | +2.03% | -5.16% | -3.13% |
| GBPCHF | +0.55 | -1.85 | ~1.06 | +1.89% | -6.37% | -4.48% |
| AUDCHF | +0.25 | -1.00 | ~0.53 | +1.72% | -6.89% | -5.17% |
| NZDCHF | +0.20 | -0.65 | ~0.46 | +1.59% | -5.16% | -3.57% |
| CADCHF | +0.20 | -0.65 | ~0.58 | +1.26% | -4.09% | -2.83% |
| EURCHF | +0.30 | -1.00 | ~0.92 | +1.19% | -3.97% | -2.78% |
| GBPJPY | +0.62 | -2.85 | ~200 | +1.13% | -5.20% | -4.07% |
| USDJPY | +0.38 | -2.10 | ~150 | +0.92% | -5.11% | -4.19% |
| NZDJPY | +0.15 | -0.90 | ~87 | +0.63% | -3.78% | -3.15% |
| AUDCAD | +0.15 | -0.90 | ~0.91 | +0.60% | -3.61% | -3.01% |
| GBPCAD | +0.22 | -1.56 | ~1.84 | +0.44% | -3.09% | -2.66% |
| USDCAD | +0.15 | -1.00 | ~1.38 | +0.40% | -2.64% | -2.25% |
| EURUSD | -0.98 | **+0.19** | ~1.15 | -3.11% | +0.60% | -2.51% |
| EURAUD | -1.40 | **+0.30** | ~1.75 | -2.92% | +0.63% | -2.29% |
| EURGBP | -0.75 | **+0.12** | ~0.865 | -3.16% | +0.51% | -2.66% |
| AUDUSD | -0.10 | -0.30 | ~0.66 | negative both | | |
| GBPUSD | -0.37 | -0.30 | ~1.33 | negative both | | |

**Pattern:**
- Positive swap = long the higher-yielder against the funding currencies JPY and CHF, and short EUR against USD, AUD and GBP. This is the classic G10 carry book.
- The long+short sum implies a markup of about 1.1-2.6 %/yr **per side**. The net carry a retail CFD trader keeps is therefore about 0.4-2.3 %/yr on notional, versus the full interest differential in academic studies. At 10 % vol that is about 0.1-0.2 Sharpe from carry alone.
- **The rest must come from spot behaviour (the forward-premium puzzle).**
- Swaps change with central-bank rates; this is a snapshot.

### 1. FX
**1.1 Carry (G10)**
- **Sources:**
  - Lustig, Roussanov & Verdelhan (2011), "Common Risk Factors in Currency Markets", *Review of Financial Studies* 24(11), 3731-3777.
  - Menkhoff, Sarno, Schmeling & Schrimpf (2012a), "Carry Trades and Global Foreign Exchange Volatility", *Journal of Finance* 67(2), 681-718: carry losses coincide with spikes in global FX volatility.
  - Brunnermeier, Nagel & Pedersen (2008), "Carry Trades and Currency Crashes", *NBER Macroeconomics Annual* 23, 313-347: crash risk rises with carry crowding and falls with lower VIX.
  - Burnside, Eichenbaum, Kleshchelski & Rebelo (2011), "Do Peso Problems Explain the Returns to the Carry Trade?", *RFS* 24(3), 853-891.
  - Daniel, Hodrick & Lu (2017), "The Carry Trade: Risks and Drawdowns", *Critical Finance Review* 6(2), 211-262.
  - Koijen, Moskowitz, Pedersen & Vrugt (2018), "Carry", *JFE* 127(2), 197-225: currency carry Sharpe 0.61 (current carry).
  - Lustig, Roussanov & Verdelhan (2014), "Countercyclical Currency Risk Premia", *JFE* 111(3), 527-553: "dollar carry", i.e. long all foreign currencies versus USD when the average foreign rate exceeds the US rate.
- **Post-publication / OOS:**
  - **Weak.** Fan, Paseka, Qi & Zhang (2022), "Currency Carry Trade: The Decline in Performance after the 2008 Global Financial Crisis", *Journal of International Financial Markets, Institutions & Money* 76, 101460, documents the decline and attributes it to the disappearance of downside-risk compensation.
  - A Bloomberg research note ("Currency investment insights: alternative risk premia benchmarks", about 2020) reportedly shows G10 carry at about 5.7 %/yr (Sharpe 0.65) in 2000-2009 versus about 0.6 %/yr (Sharpe 0.08) in Dec-2009 to May-2020. **[figures seen only in a search summary; I opened the PDF but could not confirm them in the extracted text]**
  - The August 2024 yen-carry unwind is a recent crash example (general knowledge; no paper cited).
- **RF applicability:** only the positive-swap legs above. RF keeps 1-2.5 %/yr per side, which removes roughly half or more of the academic carry.
- **Overlap with our rounds:** none (r10 was FX trend, r43 FX mean reversion).
- **Untested idea C-FX1:**
  - *Rule:* hold an equal-risk basket long GBPJPY, AUDJPY, USDJPY, GBPCHF, USDCHF, **only when** VIX (CBOE, public) is below its trailing 252-day median at the previous close; otherwise flat.
  - *Signal and costs:* daily signal; RF swap per night; cost on each switch.
  - *Expectation:* a crash-filtered carry in the spirit of Menkhoff (2012a) and BNP (2008).
  - *Concentration risk:* about 5/8 of the risk is "short JPY/CHF". It is effectively one bet; report that honestly.
  - *Period:* dev 2015-2022, holdout 2023-2026.
  - *Prior odds:* low, about 10 %, because post-2008 G10 carry is weak and RF takes a large markup.

**1.2 Value / PPP**
- **Sources:**
  - Menkhoff, Sarno, Schmeling & Schrimpf (2017), "Currency Value", *RFS* 30(2), 416-441: long cheap / short expensive by real exchange rate gives Sharpe about 0.5, and about 0.8-0.9 when adjusted for productivity, export quality, net foreign assets and output gap. The information is distinct from carry and momentum.
  - Asness, Moskowitz & Pedersen (2013), "Value and Momentum Everywhere", *JF* 68(3), 929-985: FX value and momentum are negatively correlated.
  - Rogoff (1996), "The Purchasing Power Parity Puzzle", *Journal of Economic Literature* 34(2), 647-668: PPP deviations have a half-life of about 3-5 years, so the signal is slow.
- **OOS after publication:** not found **[unverified]**.
- **RF applicability:** feasible on 8 G10 currencies with monthly rebalancing. CPI or REER data come from OECD/BIS (public).
  - Holds last months, so the asymmetric RF swap matters a lot: a short in a high-yielder costs about 3-7 %/yr.
  - Only 8 currencies means low breadth; expect Sharpe well below 0.5.
- **Overlap:** none.
- **Priority:** medium-low.

**1.3 Cross-sectional currency momentum**
- **Sources:**
  - Menkhoff, Sarno, Schmeling & Schrimpf (2012b), "Currency Momentum Strategies", *JFE* 106(3), 660-684: up to about 10 %/yr (1976-2010); transaction costs cut 30-50 %; profits concentrate in minor and EM currencies.
  - AMP (2013).
- **RF applicability:** poor. RF has no EM currencies, and G10-only momentum is much weaker (qualitative claim from the paper's discussion of developed-market subsamples **[number not re-checked]**).
- **Overlap:** r10 (time-series trend on FX) failed at -0.86. Cross-sectional is different, but the same caveat applies.
- **Priority:** low.

**1.4 Central-bank events**
- **Equities:** Lucca & Moench (2015), "The Pre-FOMC Announcement Drift", *Journal of Finance* 70(1), 329-371. We tested it in r35 (Sharpe 0.79, inconsistent; the literature notes weakening after 2015).
- **FX:**
  - *Source:* Mueller, Tahbaz-Salehi & Vedolin (2017), "Exchange Rates and Monetary Policy Uncertainty", *Journal of Finance* 72(3), 1213-1252.
  - *Finding:* short USD / long other currencies earns significantly higher excess returns on **scheduled FOMC days**. The effect is larger for high interest-rate-differential currencies, increases with monetary-policy uncertainty, and is strongest in easing cycles. It has pre- and post-announcement components.
  - *Post-publication OOS:* not found **[unverified]**.
- **RF applicability:** good on cost (0.5-3 bp round trip), and swap is roughly irrelevant for one or two nights.
  - Only about 8 events per year, so dev 2015-2022 gives n ≈ 64. Low power; require t ≥ 2.
- **Untested idea C-FX2:**
  - *Rule:* on each scheduled FOMC decision day, go long the EW basket {EURUSD, GBPUSD, AUDUSD, NZDUSD} and short {USDJPY, USDCHF, USDCAD}, i.e. short USD against all 7.
  - *Entry and exit:* enter at 00:00 ET of the FOMC day; exit at 00:00 ET of the next day.
  - *Data:* Claude's `mt5_calendar_usd.csv` starts 12.2018 (from r35). For 2015-2018, use the Fed's public FOMC calendar.
  - *Gates:* the usual ones, plus t ≥ 2.0 given the small n.
  - *Prior odds:* about 15 %.

**1.5 Already tested (do not repeat):** r9 Gotobi, r10 FX trend, r19 month-end, r27 WM-fix reversal, r33 Asia-range breakout, r43 cross-pair mean reversion.

### 2. Commodities
**2.1 Cross-sectional momentum, carry, basis and basis-momentum**
- **Sources:**
  - Miffre & Rallis (2007), *JBF* 31(6), 1863-1886.
  - Fuertes, Miffre & Rallis (2010), *JBF* 34(10), 2530-2548: about 21 %/yr for momentum × term structure.
  - Szymanowska et al. (2014), *JF* 69(1), 453-482.
  - Koijen et al. (2018): commodity carry Sharpe 0.50 / 0.64.
  - Boons & Porras Prado (2019), *JF* 74(1), 239-279.
  - Bakshi, Gao & Rossi (2019), "Understanding the Sources of Risk Underlying the Cross Section of Commodity Returns", *Management Science* 65(2), 619-641: carry is linked to global equity-volatility risk.
- **OOS:** Bhardwaj, Gorton & Rouwenhorst (2015, NBER w21243). The basis (carry) spread held about 10.4 %/yr in 2005-2014, after Gorton & Rouwenhorst (2006). Real OOS.
- **RF applicability: not applicable.** RF ECN offers 5 commodity CFDs (two golds, silver, two crude grades). Cross-sectional sorts need 20+ markets.
- **The only transferable piece** is time-series carry on oil, i.e. t261 H1/H3.

**2.2 Gold and silver specifics**
- **Swap:** shorting gold **earns** about +1.7 %/yr and longs pay about 5.5 %/yr. That is a cost tilt, not a signal.
- **Already tested:** gold trend (r6, r58), session effects (r7), the PM fix (r26), ORB/NR7 (r4, r34), weekly breakout (r56), silver trend (r38). **The family is exhausted on RF.**

**2.3 Agriculture, natural gas, industrial metals:** not available at RF (verified on the spec page). Out of scope.

**2.4 Commodity-currency links (idea only)**
- **Sources:**
  - Chen, Rogoff & Rossi (2010), "Can Exchange Rates Forecast Commodity Prices?", *Quarterly Journal of Economics* 125(3), 1145-1194: commodity-currency exchange rates forecast commodity price **indices** out of sample, at quarterly horizons.
  - Ferraro, Rogoff & Rossi (2015), "Can Oil Prices Forecast Exchange Rates?", *Journal of International Money and Finance* 54, 116-141: the oil-CAD link holds at daily frequency and is mostly contemporaneous.
- **RF applicability:** USDCAD versus WTI is possible, but the predictive evidence is at index level and at horizons that do not map cleanly. Low priority, and **not proposed** as a hypothesis.

### 3. Indices
**3.1 Cross-country momentum / rotation**
- **Sources:**
  - Asness, Liew & Stevens (1997), "Parallels Between the Cross-Sectional Predictability of Stock and Country Returns", *Journal of Portfolio Management* 23(3), 79-87 **[pages from memory]**.
  - Bhojraj & Swaminathan (2006), "Macromomentum: Returns Predictability in International Equity Indices", *Journal of Business* 79(1), 429-451: one-year momentum followed by about two years of reversal.
  - AMP (2013): country index value and momentum.
- **RF applicability: not applicable.** RF has US500, USTECH and US30 (one country, ρ ≈ 0.9) plus DE40 and JP225, i.e. effectively 3 markets. **Overlap:** r40 (USTECH/US30 ratio trend) failed.

**3.2 Volatility-managed / vol-targeted index exposure**
- **Sources:**
  - Moreira & Muir (2017), "Volatility-Managed Portfolios", *Journal of Finance* 72(4), 1611-1644.
  - Harvey et al. (2018), *JPM* 45(1), 14-33: improves Sharpe for equities via the leverage effect.
  - Cederburg, O'Doherty, Wang & Yan (2020), "On the Performance of Volatility-Managed Portfolios", *JFE* 138(1), 95-117: **real-time OOS mostly fails**; across 103 strategies the managed versions underperform in most cases.
- **RF applicability: poor.**
  - The long index swap is -8.6 %/yr (US) or -7.2 %/yr. Against an equity premium of about 5-7 %/yr (and dividend treatment on RF cash-index CFDs unknown **[unverified]**), long multi-day index exposure has roughly zero or negative expected carry-adjusted return before any timing skill.
  - Shorts are cheap (-1.8 %), but the short side has negative premium.
- **Overlap:** r3 (short-only trend), r8/8b (overnight premium without swap), scan-1 F3 (C1 on DE40/JP225), r59 TOM.

**3.3 Macro timing (yield curve, credit spreads, valuation)**
- **Sources:**
  - Welch & Goyal (2008), "A Comprehensive Look at the Empirical Performance of Equity Premium Prediction", *RFS* 21(4), 1455-1508: most predictors fail OOS.
  - Campbell & Thompson (2008), "Predicting Excess Stock Returns Out of Sample: Can Anything Beat the Historical Average?", *RFS* 21(4), 1509-1531: small positive OOS R² with sign restrictions.
  - Estrella & Mishkin (1998), "Predicting U.S. Recessions: Financial Variables as Leading Indicators", *Review of Economics and Statistics* 80(1), 45-61: the curve predicts recessions, but equity timing from it is poor and slow.
  - Gilchrist & Zakrajšek (2012), "Credit Spreads and Business Cycle Fluctuations", *American Economic Review* 102(4), 1692-1720: the excess bond premium predicts activity.
- **RF applicability: poor.** Few signals (months to years), long-flat exposure pays an -8.6 % swap, and the OOS record is weak. **Not proposed.**

**3.4 Simple trend / 10-month SMA (Faber)**
- **Source:** Faber (2007), "A Quantitative Approach to Tactical Asset Allocation", *Journal of Wealth Management* 9(4), 69-79, updated 2013.
- **OOS:** the 2013 update reports lower volatility and drawdown out of sample, but the 2009-2012 annual returns lagged buy-and-hold in several years. Faber's own table.
- **RF:** the swap kills the long side. **Overlap:** C1 on indices (scan 1) and r3.

**3.5 Oil → equities**
- **Source:** Driesprong, Jacobsen & Maat (2008), "Striking Oil: Another Puzzle?", *Journal of Financial Economics* 89(2), 307-327: oil-price increases predict lower next-month stock returns.
- **OOS:** mixed. Later studies report instability and a sign change around 2008 in the US (e.g., the Capital Spectator note; various Energy Economics papers). **Not proposed.**

### 4. Ranking of untested ideas for RF (hold ≥ 1 day, after costs)
| # | Idea | Evidence strength | Post-pub OOS | RF fit (symbols, cost, swap) | Overlap | Recommendation |
|---|---|---|---|---|---|---|
| 1 | Oil inventory-carry timing (t261 H1) | strong theory (GHR 2013; BGR 2015 OOS for basis) | yes, for basis cross-section | WTI/BRENT; low turnover; swap -6/-3 | new | **run first (prereg)** |
| 2 | Oil trend × inventory filter (t261 H3) | FMR 2010 | partial | as above; holdout-only | extends r29/r58 | run with the plain C1-oil holdout, shared-holdout rule |
| 3 | COT MM-flow reversal on WTI (t261 H2) | KRT 2020 (cross-section) | none found | WTI; about 7 trades/yr; 2-week swap | new | run |
| 4 | FOMC-day short-USD basket (C-FX2) | Mueller et al. 2017 | none found | 7 pairs, about 0.5-3 bp RT, swap negligible | new (r35 was equities) | run, small n |
| 5 | VIX-filtered G10 carry (C-FX1) | LRV 2011, Menkhoff 2012a, BNP 2008 | **negative** post-2008 | positive-swap legs only; RF keeps 1-2.5 %/yr per side | new | optional, low prior |
| 6 | FX value (PPP/REER), 8 currencies | Menkhoff 2017 | none found | slow; asymmetric swap hurts | new | low priority |
| - | Commodity cross-section, country rotation, vol-managed index, macro timing, cross-sectional FX momentum | strong to medium in the literature | mixed | **not feasible / swap-killed at RF** | partly r10, r40 | skip |

### 5. Methodological notes for Claude
- **Swap regime:** applying 2026 swaps to 2015-2021 overstates costs, because rates were near zero then (r56 note). Keep 2026 swaps as the decision basis, which is conservative, and add a zero-swap or rate-adjusted line descriptively.
- **Oil roll gaps:** for any oil test, use roll-adjusted series (t261 P0).
- **Demo forward tests:** for oil on demo, positions may be force-closed at each roll (RF notice 2016).
- **Positive-swap FX trades:** the table is a snapshot. Swaps change with rate cycles, so the "positive" set in 2015-2021 (near-zero rates) was different. Use historical swap estimates (rate differential minus the inferred 1-2.5 % markup) or keep 2026 values as an approximation, and say which.

### 6. Source list (full citations)
Asness, Liew & Stevens 1997 JPM 23(3) · Asness, Moskowitz & Pedersen 2013 JF 68(3):929-985 · Bakshi, Gao & Rossi 2019 Mgmt Sci 65(2):619-641 · Bhardwaj, Gorton & Rouwenhorst 2015 NBER w21243 · Bhojraj & Swaminathan 2006 J Business 79(1):429-451 · Boons & Porras Prado 2019 JF 74(1):239-279 · Brunnermeier, Nagel & Pedersen 2008 NBER Macro Annual 23:313-347 · Burnside, Eichenbaum, Kleshchelski & Rebelo 2011 RFS 24(3):853-891 · Campbell & Thompson 2008 RFS 21(4):1509-1531 · Cederburg, O'Doherty, Wang & Yan 2020 JFE 138(1):95-117 · Chen, Rogoff & Rossi 2010 QJE 125(3):1145-1194 · Daniel, Hodrick & Lu 2017 CFR 6(2):211-262 · Driesprong, Jacobsen & Maat 2008 JFE 89(2):307-327 · Estrella & Mishkin 1998 REStat 80(1):45-61 · Faber 2007 J Wealth Mgmt 9(4):69-79 · Fan, Paseka, Qi & Zhang 2022 JIFMIM 76:101460 · Ferraro, Rogoff & Rossi 2015 JIMF 54:116-141 · Fuertes, Miffre & Rallis 2010 JBF 34(10):2530-2548 · Gilchrist & Zakrajšek 2012 AER 102(4):1692-1720 · Harvey et al. 2018 JPM 45(1):14-33 · Koijen, Moskowitz, Pedersen & Vrugt 2018 JFE 127(2):197-225 · Lucca & Moench 2015 JF 70(1):329-371 · Lustig, Roussanov & Verdelhan 2011 RFS 24(11):3731-3777; 2014 JFE 111(3):527-553 · Menkhoff, Sarno, Schmeling & Schrimpf 2012a JF 67(2):681-718; 2012b JFE 106(3):660-684; 2017 RFS 30(2):416-441 · Miffre & Rallis 2007 JBF 31(6):1863-1886 · Moreira & Muir 2017 JF 72(4):1611-1644 · Mueller, Tahbaz-Salehi & Vedolin 2017 JF 72(3):1213-1252 · Rogoff 1996 JEL 34(2):647-668 · Szymanowska et al. 2014 JF 69(1):453-482 · Welch & Goyal 2008 RFS 21(4):1455-1508 · RoboForex contract specifications (public page, fetched 15.11.2026) · Claude's `ecn_costs_20261030.csv` (matches the page).
