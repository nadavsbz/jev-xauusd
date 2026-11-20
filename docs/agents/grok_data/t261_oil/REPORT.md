# t261 - נפט: מחקר עומק (Grok, 15.11.2026)

## סיכום בעברית

**שורה תחתונה:**
1. **למה מגמה עובדת בנפט יותר מבמתכות.** בנפט יש מלאי פיזי מוגבל וזעזועי היצע שנמשכים זמן רב (OPEC, שייל, מלחמות). זה יוצר משטרים מתמשכים של backwardation, מחסור במלאי ומחירים עולים, או של contango, עודף מלאי ומחירים יורדים. בספרות, מומנטום ו-backwardation בוחרים את אותן סחורות: אלה שהמלאי שלהן נמוך (Gorton, Hayashi ו-Rouwenhorst 2013). זהב, לעומת זאת, הוא נכס מוניטרי עם מלאי עילי עצום. העקום שלו כמעט תמיד ב-full carry, כלומר בריבית, ואין בו convenience yield. לכן אין לו "מנוע" פיזי למגמה, וזה מתאים לתוצאות שלנו: XAU ‏0.01–0.17, ‏XAG ‏‎−0.30–0.28, ונפט 0.46–0.60.
2. **ממצא מתודולוגי קריטי, לפני כל הרצה נוספת על נפט.** לפי הודעות של RoboForex, ה-CFD על BRENT ו-WTI מגולגל לחוזה הבא בכל פקיעה, ובחשבון האמיתי מתבצעת **התאמת יתרה** בגובה הפער בין החוזים. מכאן שתי השלכות:
   - **(א) בנתוני ה-H1 הגולמיים יש קפיצות גלגול** (סבב 29 כבר ציין "קפיצות של שני בבוקר"). הקפיצות האלה הן לא רווח או הפסד אמיתי. הן מזייפות אותות Donchian ואת ה-P&L. צריך לבנות סדרה מתואמת-גלגול (back-adjusted) ולחשב עליה גם את האותות וגם את ה-P&L. בלי זה, גם r29/r58 וגם בדיקת ה-holdout המתוכננת של C1 על נפט מזוהמות.
   - **(ב) בדמו, פוזיציות נסגרות בגלגול** (לפי הודעת RF מ-2016). כל בדיקה קדימה על דמו תיראה שונה מחשבון אמיתי.
   - **סטטוס:** VERIFIED מהודעות RF 2015–2016. צריך לוודא שזה עדיין המדיניות ב-2026.
3. **עלות ההחזקה ב-RF כבדה:** ‏swap ‎−6%/שנה על לונג ו-‎−3%/שנה על שורט (דף המפרט הציבורי, 15.11.2026, וגם `ecn_costs` מ-30.10). זה בנוסף ל-roll yield שעובר דרך התאמת היתרה. ב-10% תנודתיות, כלומר חשיפה של כ-0.3 מההון, זה ‎−1.8%/שנה על לונג קבוע. **יש הטיה מבנית לטובת השורט.**
4. **COT:** הספרות הכי חזקה (Kang, Rouwenhorst ו-Tang, ‏JF 2020) מראה ששינוי שבועי בפוזיציות הספקולנטים מנבא **היפוך** בשבועות שאחריו, כי הם צורכים נזילות. הממצא ההפוך: Singleton (‏2014) מצא המשכיות בשינוי של 13 שבועות, אבל רק סביב 2008. ‏Sanders ואחרים (2004) ו-Büyükşahin ו-Harris (‏2011) מצאו שהפוזיציות **הולכות אחרי** המחיר ולא מנבאות אותו. המסקנה: אם בודקים COT, בודקים היפוך על השינוי השבועי, לא המשכיות.
5. **עונתיות:** ‏Arendas ואחרים (2018) מצאו שמרץ, אפריל ואוגוסט חזקים ושאוקטובר ונובמבר חלשים (1983–2017). האפקט מובהק, אבל נבדק על סדרה רציפה לא מתואמת, ו-2018–2026 הוא OOS אמיתי. ‏OPEC: התגובה מתרכזת סביב יום ההכרזה ואינה עקבית. ‏Brent-WTI: הקו-אינטגרציה נשברה ב-2010–2015, ובזוג משלמים swap משני הצדדים (כ-‎−9%/שנה על הזוג). זה לא מומלץ.
6. **CTAs:** ‏CTAs משלבים lookbacks של 1, 3 ו-12 חודשים, ומכיילים כל נכס לתנודתיות יעד (Hurst, Ooi ו-Pedersen 2017). הם מגלגלים לפני הפקיעה ומחשבים אותות על סדרה מתואמת. רבים מהם משלבים מגמה עם carry, כלומר מבנה עקום.

**ההשערות המוגדרות מראש** (פירוט מלא בסעיף 6 באנגלית):
- **H1, תזמון carry לפי מלאי (לא מגמה, ‏dev ‏+ holdout רגילים):** מלאי הנפט המסחרי בארה"ב (EIA ‏WCESTUS1) מול ממוצע 5 השנים לאותו שבוע. כשיש גירעון: לונג. כשיש עודף: שורט. על WTI ו-BRENT בסיכון שווה, ‏10% תנודתיות.
- **H2, ‏COT היפוך (לא מגמה):** ‏z של השינוי השבועי ב-Managed Money net כאחוז מ-OI. כש-z ≥ ‎+1.5: שורט WTI ל-10 ימי מסחר. כש-z ≤ ‎−1.5: לונג.
- **H3, מגמה מסוננת במלאי (נשען על מגמה, ולכן הכרעה על holdout 2023–2026 בלבד):** ‏C1 בדיוק כמו ב-r29/r58, רק בכיוון שמסכים עם סימן המלאי.
- **רזרבה H4:** העונתיות של Arendas, אסטרטגיה A. הכלל פורסם ב-2018, ולכן כל הנתונים שלנו הם OOS.
- **תנאי מקדים P0 לכל השערה:** סדרה מתואמת-גלגול ו-P&L שכולל את התאמת הגלגול.

---

## English detail

### 0. Scope, sources and verification status
- **What I read:**
  - SCAN_PLAN rounds 1-59: `D:\Claude\jev\docs\SCAN_PLAN.md`, read-only.
  - Claude's t261/t262 request: `claude_outbox.md` ~l.609-628.
  - RF cost snapshot: `data/derived/ecn_costs_20261030.csv`.
  - RF public contract-specification page, fetched 15.11.2026.
- **Citation status:**
  - Every citation below was checked against a publisher, SSRN, NBER or RePEc page or the PDF itself during this session, except where marked **[unverified]**.
  - Where I quote a number, its source is given. Figures I could not open myself are flagged.
- **Notation:** "OOS" = evidence on data after the original paper's sample or after its publication.

### 1. RF facts that drive everything (oil)
| Item | Value | Source |
|---|---|---|
| Symbols | `BRENT`, `WTI` ("Spot ... Crude Oil", 1 lot = 1000 bbl, leverage 1:20) | RF spec page (ECN tab), 15.11.2026 |
| ECN avg spread | 1.70 pips = $0.017, about 1.6-1.7 bp at $100-113 | RF spec page |
| ECN commission | 50 per million per side, i.e. 0.5 bp/side | RF spec page |
| Measured cost (Claude) | about 3.3 bp/side intraday; RT 7.5 bp used in r57 | SCAN_PLAN r57/r59 |
| Swap | long **-6.0 %/yr**, short **-3.0 %/yr** (mode 5 = annual % of price) | RF spec page, matches `ecn_costs_20261030.csv` |
| Contract roll | At each futures expiry the CFD rolls to the next contract. Trading closes 20:00 server time, and **real accounts get a balance adjustment equal to the old/new contract price difference**. **Demo positions are closed** at the last price. | RF notices 15.12.2015 and 28.01.2016 (roboforex.com/about/company/news/show/708-... and /727-...). **Current (2026) policy not re-verified.** |

**Implications:**
1. **Roll gaps in the raw price series.**
   - The true P&L of a held RF oil CFD is the *futures excess return* (it includes roll yield, because the balance adjustment cancels the price gap) **minus the swap**.
   - The raw MT5 price series still contains roll gaps. A backtest on raw bars therefore books phantom P&L at every roll, and Donchian channels see phantom breakouts.
   - Direction of the bias: in backwardation the next contract is cheaper, so the raw series gaps down. The raw backtest then charges longs a loss that the real account would have credited, and does the reverse for shorts. In contango it is the opposite.
   - So raw-bar backtests **understate trend-with-carry positions and overstate trend-against-carry positions**.
   - r29/r58 did not correct for this; r29 even flags the Monday jumps. The holdout test approved at 12:35 ("C1 on WTI+BRENT, decided on holdout only") **should be run on a roll-adjusted series, declared in the prereg.**
2. **The swap is a pure markup.**
   - A futures position needs no financing, so the RF swap is not compensation for anything.
   - At 10 % vol targeting (oil vol about 30-40 %, so notional about 0.25-0.35x equity), the drag is about -1.5 to -2.1 %/yr when long and -0.75 to -1.05 %/yr when short.
   - **This creates a structural short tilt.** A long-only oil strategy must earn more than 6 %/yr of notional just to break even on carry.
3. **Demo forward tests will not match real accounts,** because demo positions are force-closed at each roll (if that 2016 policy still applies).

**P0, prerequisite for any oil hypothesis below (also for the C1-oil holdout):**
- **Roll dates:**
  - Identify each RF roll from the RF schedule on the spec page if it is still published.
  - Otherwise, use the first bar after a 20:00 server-time close on a weekday near expiry, where |gap| is much larger than typical.
  - WTI: CL last trade is about 3 business days before the 25th of the month. Brent: ICE expiry is the last business day of the second month preceding delivery. RF rolls a few days earlier.
- **Back-adjustment:** build a back-adjusted (difference-adjusted) series by removing each roll gap.
- **P&L:** P&L = adjusted price change - spread/commission - swap per calendar night.
- **Report:** the number of rolls found per year (WTI should be about 12) and the median absolute gap in bp. **Do not look at strategy returns while doing this.**

### 2. Why trend works in oil more than in metals
1. **Storage economics and the convenience yield.**
   - *Source:* Fama & French (1987), "Commodity Futures Prices: Some Evidence on Forecast Power, Premiums, and the Theory of Storage", *Journal of Business* 60(1), 55-73. This is the theory of storage (Kaldor, Working, Brennan), tested on futures data.
   - *Finding:* the basis of metals behaves mostly like an interest rate (full carry), while the basis of storable-but-scarce commodities varies strongly with inventories.
   - *Applied to oil:* oil inventories are bounded by tank and Cushing capacity, and supply responds slowly. Shocks therefore persist as long backwardation regimes (scarcity, rising prices) or long contango regimes (glut, falling prices).
   - *Applied to gold:* gold's above-ground stock is many decades of mine supply, so its curve sits at roughly full carry and there is no physical "trend engine".
2. **Momentum and backwardation pick the same commodities, the low-inventory ones.**
   - *Source:* Gorton, Hayashi & Rouwenhorst (2013), "The Fundamentals of Commodity Futures Returns", *Review of Finance* 17(1), 35-105 (NBER w13249).
   - *Finding:* low inventories predict backwardation and higher risk premia; momentum and basis strategies earn excess returns largely because they select low-inventory commodities; position data (COT) does not predict premia.
   - *Why it matters here:* this is the cleanest academic statement of why oil trend and oil carry are linked.
3. **Long-run evidence on backwardation versus contango.**
   - *Source:* Levine, Ooi, Richardson & Sasseville (2018), "Commodities for the Long Run", *Financial Analysts Journal* 74(2), 55-68 (NBER w22793; AQR data set public).
   - *Finding (1877-2015):* index returns averaged about 7.7 %/yr in backwardation versus about 2 %/yr in contango, driven by carry. Spot returns alone were higher in contango, which is mean reversion.
   - *OOS:* the sample is long (back to 1877), but there is no post-2015 OOS in the paper.
4. **Spot versus term premia.**
   - *Source:* Szymanowska, de Roon, Nijman & van den Goorbergh (2014), "An Anatomy of Commodity Futures Risk Premia", *Journal of Finance* 69(1), 453-482.
   - *Finding:* sorting on basis, momentum and other characteristics produces spot premia of 5-14 %/yr and term premia of 1-3 %/yr, and a high-minus-low basis factor explains the spot premia.
   - *For a single front-month CFD:* the relevant part is the spot premium.
5. **Roll yield is what separates long-run commodity returns.**
   - *Sources:* Erb & Harvey (2006), "The Strategic and Tactical Value of Commodity Futures", *FAJ* 62(2), 69-97; Gorton & Rouwenhorst (2006), "Facts and Fantasies about Commodity Futures", *FAJ* 62(2), 47-68.
   - *OOS for G&R:* Bhardwaj, Gorton & Rouwenhorst (2015), "Facts and Fantasies about Commodity Futures Ten Years Later", NBER w21243. Over 2005-2014 the EW commodity premium was 3.67 %/yr versus 5.23 % in-sample (not significantly different), and **the high-basis minus low-basis spread kept working out of sample (about 10.4 %/yr)**. This is real post-publication OOS for the basis/carry effect.
6. **Supply shocks are persistent and of different types.**
   - *Sources:* Kilian (2009), "Not All Oil Price Shocks Are Alike", *American Economic Review* 99(3), 1053-1069; Hamilton (2009), "Causes and Consequences of the Oil Shock of 2007-08", *Brookings Papers on Economic Activity* (Spring), 215-261.
   - *Applied:* demand-driven and supply-driven shocks have different persistence. OPEC regime changes (Nov 2014, Mar 2020) and shale cycles create multi-month moves, the environment a Donchian or TSMOM rule profits from.
7. **Trend in general (cross-asset).**
   - *Sources:* Moskowitz, Ooi & Pedersen (2012), "Time Series Momentum", *Journal of Financial Economics* 104(2), 228-250; Hurst, Ooi & Pedersen (2017), "A Century of Evidence on Trend-Following Investing", *Journal of Portfolio Management* 44(1), 15-29.
   - *HOP details:* 67 markets including 29 commodities, 1880-2016, an EW mix of 1/3/12-month signals with 10 % vol targeting. Trend was profitable in every decade and did best in **low-correlation environments**.
   - *Post-publication OOS:*
     - Positive: Babu, Levine, Ooi, Pedersen & Stamelos (2020), "Trends Everywhere", *Journal of Investment Management* 18(1), extends to more assets and later data.
     - Negative: Huang, Li, Wang & Zhou (2020), "Time-Series Momentum: Is It There?", *JFE* 135(3), 774-794, finds asset-by-asset predictability weak and says the TSMOM portfolio profit is close to a "historical mean" strategy.
     - Negative: Kim, Tse & Wald (2016), "Time Series Momentum and Volatility Scaling", *Journal of Financial Markets* 30, 103-124, find most of the TSMOM alpha comes from vol scaling, and performance is weaker after 2009.
   - **Net: trend is a real but modest and noisy premium; do not expect Sharpe >0.8 on 2 assets.**
8. **Momentum in commodities, cross-section and behavioral.**
   - *Sources:* Miffre & Rallis (2007), "Momentum Strategies in Commodity Futures Markets", *Journal of Banking & Finance* 31(6), 1863-1886; Bianchi, Drew & Fan (2016), "Commodities Momentum: A Behavioral Perspective", *JBF* 72, 133-150; Fuertes, Miffre & Rallis (2010), "Tactical Allocation in Commodity Futures Markets: Combining Momentum and Term Structure Signals", *JBF* 34(10), 2530-2548.
   - *FMR 2010:* the double sort (momentum plus roll-return) earned about 21 %/yr abnormal return, 23.55 % gross and 22.88 % net for the best variant (Quantpedia summary of their Table 6). It survived White Reality Check/SPA over 55 rules and an extension to Nov-2008. This is cross-sectional over about 27-37 commodities, **not reproducible with 2 assets**, but the **agreement of trend and carry** is the transferable idea.

**Oil features that predict *when* trend works (from the above):**
- **(a) Trend and carry agree:** backwardation plus uptrend, or contango plus downtrend (FMR 2010; GHR 2013; Levine et al. 2018).
- **(b) Inventory deviation from normal:** same mechanism as (a), observable weekly from EIA.
- **(c) Low cross-asset correlation regimes** (HOP 2017); a portfolio-level property.
- **(d) Large supply-regime breaks:** not forecastable ex ante.
- **Not supported:** COT "crowding" as a trend-timing tool. Practitioner lore only; I found no peer-reviewed support **[unverified]**.

### 3. Oil-specific signals, days-to-weeks holds
**3.1 COT (CFTC disaggregated, NYMEX WTI)**
- **Kang, Rouwenhorst & Tang (2020),** "A Tale of Two Premiums: The Role of Hedgers and Speculators in Commodity Futures Markets", *Journal of Finance* 75(1), 377-417 (SSRN 2449315).
  - *Data:* 26 commodities, 1994-2014, with a DCOT robustness check.
  - *Finding:* **weekly** position changes: commodities heavily bought by speculators (non-commercials) **underperform** in the following weeks, and those bought by hedgers outperform. Speculators consume liquidity; hedgers provide it. Hedging pressure (the long-run level) has the Keynesian positive sign only after this short-run component is removed.
  - *Caveats:* the paper's tests are mainly **cross-sectional**. **Time-series evidence for a single market (WTI) is not established there.** Post-publication OOS: none found.
- **Singleton (2014),** "Investor Flows and the 2008 Boom/Bust in Oil Prices", *Management Science* 60(2), 300-318.
  - *Finding:* the 13-week change in **managed-money spread positions** (and index-investor flows) predicted **higher** subsequent oil futures excess returns, i.e. continuation.
  - *Caveats:* the sample centres on 2006-2010. The author himself suggests part of the effect may be front-running the index roll.
- **Sanders, Boris & Manfredo (2004),** "Hedgers, Funds, and Small Speculators in the Energy Futures Markets: An Analysis of the CFTC's Commitments of Traders Reports", *Energy Economics* 26(3), 425-445.
  - *Finding:* net positions do **not** generally lead returns. They move contemporaneously, with funds buying as prices rise.
- **Büyükşahin & Harris (2011),** "Do Speculators Drive Crude Oil Futures Prices?", *Energy Journal* 32(2), 167-202.
  - *Finding (Granger tests):* **prices lead positions**. Hedge funds behave like trend followers.
- **Background papers:**
  - Bessembinder (1992), "Systematic Risk, Hedging Pressure, and Risk Premiums in Futures Markets", *Review of Financial Studies* 5(4), 637-667.
  - de Roon, Nijman & Veld (2000), "Hedging Pressure Effects in Futures Markets", *Journal of Finance* 55(3), 1437-1456.
  - Basu & Miffre (2013), "Capturing the Risk Premium of Commodity Futures: The Role of Hedging Pressure", *JBF* 37(7), 2652-2664: hedging-pressure sorts are long-short and cross-sectional.
  - Hong & Yogo (2012), "What Does Futures Market Interest Tell Us about the Macroeconomy and Asset Prices?", *JFE* 105(3), 473-490: growth in **aggregate** open interest predicts commodity returns.
  - Fattouh, Kilian & Mahadeva (2013), "The Role of Speculation in Oil Markets: What Have We Learned So Far?", *Energy Journal* 34(3), 7-33: a survey that finds little evidence speculators drove oil prices.
- **Answer to Claude's question:**
  - *Direction:* the best-identified evidence says **reversal** after large *weekly changes* in speculator (MM) net positions; positions themselves follow trend.
  - *Metric:* weekly change in MM net as % of OI, standardised (z-score over a trailing window).
  - *Avoid:* *levels* (net %OI) as a contrarian signal. The level contains long-run hedging pressure, which has the opposite sign (KRT 2020).
  - *Continuation (Singleton):* specific to 2006-10 and to spread positions; do not use it as the primary sign.
- **Release timing:** positions are as of Tuesday and released Friday 15:30 ET, so trade at the next open after release.

**3.2 Term structure / Brent-WTI**
- **Curve slope** is the best-supported predictor (basis/carry: GHR 2013; KMPV 2018; BGR 2015 OOS).
  - *Koijen, Moskowitz, Pedersen & Vrugt (2018),* "Carry", *JFE* 127(2), 197-225: commodity carry Sharpe 0.50 (current carry) and 0.64 (carry averaged over months 1-12).
  - *Boons & Porras Prado (2019),* "Basis-Momentum", *Journal of Finance* 74(1), 239-279: basis-momentum (first-nearby momentum minus second-nearby momentum) beats basis and momentum in time series and cross-section. Post-publication OOS: not found **[unverified]**.
  - *Paschke, Prokopczuk & Wese Simen (2020),* "Curve Momentum", *JBF* 113, 105718 **[cited from memory; not re-opened this session]**.
- **Data problem:**
  - EIA's free NYMEX futures-price table (RCLC1-4) **stops after 5 April 2024** (EIA page checked 15.11.2026), so it covers dev but not the whole holdout.
  - RF's own roll gaps give one slope observation per month (gap / price at each roll). That proxy is usable through 2026.
  - Weekly **inventories** (below) are the best always-available proxy for the slope, per GHR 2013.
- **Brent-WTI spread:** cointegration broke in 2010-2015 (Cushing glut, US export ban) and returned after the 2015 export liberalisation.
  - *Sources:* Büyükşahin, Lee, Moser & Robe (2013), "Physical Markets, Paper Markets and the WTI-Brent Spread", *Energy Journal* 34(3); Liu (2018), *OPEC Energy Review*.
  - *On RF:* a long/short pair pays **both** swaps (about -6 % and -3 %, i.e. about -9 %/yr of one-leg notional), and the spread's % volatility relative to notional is small. **Not recommended.**

**3.3 Seasonality**
- **Arendas, Tkacova & Bukoven (2018),** "Seasonal Patterns in Oil Prices and Their Implications for Investors", *Journal of International Studies* 11(2), 180-192.
  - *Data:* Stooq monthly Brent/WTI futures, 1983-2017.
  - *Findings:* March, April and August are strong; October and November are weak.
  - *Feb-Sep versus Oct-Jan:* WTI monthly mean +1.66 % versus -1.45 % (t-test p = 0.0016). Mar-Apr versus May-Feb: +3.40 % versus +0.07 % (p = 0.008). Their table, WTI.
  - *Caveats:* (i) Stooq continuous series are likely **not roll-adjusted**, so roll gaps contaminate monthly returns; (ii) 2009-2017 subperiod results are weaker for Brent.
  - *OOS:* **2018-2026 is entirely post-publication OOS.**
- **Quayyoum, Khan, Shah, Simonetti & Matarazzo (2020),** "Seasonality in Crude Oil Returns", *Soft Computing* 24(18), 13547-13556: also reports month effects. Details not re-checked.
- **Suenaga & Smith (2011),** "Volatility Dynamics and Seasonality in Energy Prices: Implications for Crack-Spread Price Risk", *Energy Journal* 32(3): seasonality is strong in **products** (gasoline, heating oil) and weak in crude. Futures curves already price in predictable seasonality.
- **Driving season, hurricanes, refinery maintenance:** these show up mainly in product cracks and inventories, not reliably in crude futures returns. I found no peer-reviewed tradable crude "hurricane" effect **[none found]**.

**3.4 OPEC days**
- **Sources:**
  - Lin & Tamvakis (2010), "OPEC Announcements and Their Effects on Crude Oil Prices", *Energy Policy* 38(2), 1010-1016.
  - Demirer & Kutan (2010), "The Behavior of Crude Oil Spot and Futures Prices around OPEC and SPR Announcements: An Event Study Perspective", *Energy Economics* 32(6), 1467-1476 **[pages from memory]**.
  - Loutia, Mellios & Andriosopoulos (2016), "Do OPEC Announcements Influence Oil Prices?", *Energy Policy* 90, 262-272.
- **Consensus:** effects concentrate around the announcement, are asymmetric (cuts and status-quo matter more), and vary by period. OPEC influence is weaker when unconventional supply is viable (post-shale).
- **Verdict:** no stable multi-day drift to exploit. **Not proposed.**

**3.5 Inventories versus the 5-year average**
- **Background:** the EIA Weekly Petroleum Status Report (WCESTUS1 = U.S. commercial crude stocks ex-SPR) is public, weekly, 1982 to present. GHR 2013 is the theory: low stocks lead to backwardation and higher premia. Industry convention is to compare against the 5-year average for the same week.
- **Announcement-surprise effects are intraday:**
  - Halova Wolfe, Kurov & Kucher (2014), "Noisy Inventory Announcements and Energy Prices", *Journal of Futures Markets* 34(10), doi 10.1002/fut.21633.
  - Our r57 (EIA intraday momentum) found zero.
  - The **level** (deviation from normal) as a slow carry proxy is a different, untested signal; see H1/H3.

**3.6 Crack spread**
- **Girma & Paulson (1999),** "Risk Arbitrage Opportunities in Petroleum Futures Spreads", *Journal of Futures Markets* 19(8), 931-955: 3:2:1 and 1:1 cracks are stationary, and ±1.75-2.5 sd mean-reversion trades were profitable historically.
- **RF applicability:** RF has no gasoline or heating-oil CFDs, so this is **not tradable**. As a predictor of crude itself it is not established.

**3.7 USD link**
- **Source:** Fratzscher, Schneider & Van Robays (2014), "Oil Prices, Exchange Rates and Asset Prices", ECB Working Paper 1689.
- **Finding:** the oil-USD correlation turned negative in the 2000s and is time-varying. It is a contemporaneous risk link, not a predictive signal.
- **Not proposed.**

### 4. How CTAs trade oil differently
- **Signals:** a blend of horizons, about 1-12 months (HOP 2017 uses an EW 1/3/12-month mix). Moving-average crossovers and TSMOM are near-equivalent: Levine & Pedersen (2016), "Which Trend Is Your Friend?", *FAJ* 72(3), 51-66.
- **Risk:**
  - Per-instrument volatility targeting using 1-3-month EWMA vol, then portfolio-level vol targeting with sector caps (energy is usually one sector).
  - Harvey, Hoyle, Korgaonkar, Rattray, Sargaison & Van Hemert (2018), "The Impact of Volatility Targeting", *JPM* 45(1), 14-33: vol targeting improves Sharpe for equities and credit but **is negligible for commodities**. Its benefit there is left-tail reduction.
  - Baltas & Kosowski (2020), "Demystifying Time-Series Momentum Strategies: Volatility Estimators, Trading Rules and Pairwise Correlations", in *Market Momentum: Theory and Practice* (Wiley), ch. 3: efficient range-based vol estimators and correlation-aware sizing reduce turnover.
- **Roll:**
  - CTAs roll ahead of first notice and expiry, often before the index roll window (the "Goldman roll" is around business days 5-9). They compute signals on **back-adjusted continuous series**.
  - Some hold deferred contracts (e.g., December) to cut roll costs and front-end noise, and some choose the curve point with the best carry. This is practitioner knowledge, widely described; I found no single peer-reviewed source **[unverified as a citation]**.
- **Carry overlay:** many large managers combine trend with carry and term structure (KMPV 2018; FMR 2010).
- **What we should copy:** (i) back-adjusted series; (ii) multi-horizon signal and vol targeting (C1 already does this); (iii) a carry/inventory condition.

### 5. Answer on "C1 on WTI+BRENT, decided on holdout only"
I agree with the 12:35 conditions in grok_inbox, and add two more:
- **(a) Roll-adjusted data (P0) is mandatory and must be declared.** Without it the holdout result is not interpretable.
- **(b) Shared holdout with H3.** If H3 below is also run on the same holdout, both prereg files must state it. H3 counts as a pass only if it passes its own gates **and** beats plain C1-oil on the holdout by at least 0.2 Sharpe. Otherwise the simpler plain C1-oil wins (or nothing does).

### 6. Pre-specified hypotheses (for Claude's prereg; one run each)
**Common to all:**
- **Instruments:** RF `WTI` and `BRENT` CFDs.
- **P&L:** on the P0 roll-adjusted series, minus spread and commission at Claude's measured RF cost (3.3 bp/side or the measured median at execution hour, whichever is higher), minus RF swap of -6 %/yr long and -3 %/yr short per calendar night at 2026 rates. Report a zero-swap line for 2015-2021 descriptively only.
- **Sizing:** each asset at 10 % annualised vol (60-day EWMA of daily adjusted returns, lagged one day); portfolio = equal risk.
- **Holdout:** 2023-01-01 to the last full month, run once.
- **Reporting:** correlation with C1 and I2 is always reported (daily, 2020-2026).

**H1: Inventory-carry timing (not trend; normal dev → holdout)**
- *Source logic:* GHR 2013; Levine et al. 2018; BGR 2015 OOS basis effect.
- *Data:* EIA weekly WCESTUS1 (thousand bbl), 1982 to present.
- *Signal:* D_t = (S_t - A_t) / A_t, where A_t = mean of S for the same ISO week in the 5 preceding calendar years (weeks 52/53 mapped to 52).
- *Position:* long both assets if D_t < 0, short both if D_t > 0. Signal updates only on release weeks.
- *Execution:* first RF H1 bar at or after release + 1h (release is Wed 10:30 ET, Thu in holiday weeks). Use the actual release calendar; never use a value before its release time.
- *Dev period:* earliest RF oil history (expected ≥2015) to 2022-12-31.
- *Dev gates (all):*
  - net Sharpe ≥ 0.6;
  - ≥ 60 % of calendar years positive;
  - maxDD ≤ 25 %;
  - |corr| ≤ 0.3 with C1 and I2;
  - |corr| ≤ 0.5 with the plain C1-oil (r29 signal on adjusted data). Above 0.5 it is the same bet and should be dropped.
- *Holdout gates:* Sharpe ≥ 0.4, ≥ 3/4 years positive (2026 counted if ≥ 6 months), maxDD ≤ 25 %.
- *Kill:* any dev gate fails → kill, no variants (no dead-band, no Cushing-only, no other window).
- *Expected trades:* few sign flips per year, so cost is small and swap dominates. Prior odds of passing about 15 %.

**H2: COT speculator-flow reversal (not trend; normal dev → holdout)**
- *Source logic:* Kang, Rouwenhorst & Tang 2020; contrary prior: Singleton 2014.
- *Data:* CFTC disaggregated futures-only, NYMEX "CRUDE OIL, LIGHT SWEET" (WTI), 2010-2026 (Claude has it).
- *Signal:*
  - x_t = Δ(MM_long - MM_short) / OI_t (weekly change, as of Tuesday).
  - z_t = x_t / sd(x over the previous 156 weeks, excluding t). Require ≥ 104 weeks of history.
- *Rule:*
  - If z_t ≥ +1.5, **short** WTI. If z_t ≤ -1.5, **long** WTI.
  - Entry at the first RF bar after Friday 15:30 ET release + 1h, in practice the Monday open (server time).
  - Exit at the close of the 10th trading day.
  - One position at a time; signals during an open trade are ignored.
  - BRENT gets the same trades, reported **descriptively only**.
- *Dev period:* 2012-01 (after the 104-week warm-up) to 2022-12.
  - If RF WTI history starts later, prices before the RF start come from EIA RCLC1/RCLC2 roll-adjusted daily settlements. Declare this in the prereg.
- *Dev gates:*
  - n ≥ 50;
  - mean net per trade > 0 with t ≥ 2.0;
  - annualised strategy Sharpe (daily, flat days = 0) ≥ 0.5;
  - ≥ 60 % of years positive;
  - |corr| ≤ 0.3 with C1, I2 and C1-oil.
- *Holdout gates:* mean net > 0, Sharpe ≥ 0.3, n ≥ 12.
- *Kill:* fail, **or** dev shows the opposite sign (continuation, t ≤ -2). Do **not** flip the rule after seeing it. No other thresholds or holds.
- *Expected:* about 6-8 events per year. The effect size for a single market is unknown (KRT is cross-sectional). Prior odds about 10-15 %.

**H3: Oil trend conditioned on inventory carry (leans on oil trend → decided on HOLDOUT ONLY)**
- *Source logic:* FMR 2010 (trend and carry agree); GHR 2013. The selection of oil came from our dev (r29/r58) and is declared openly.
- *Rule:*
  - Compute C1's Donchian ensemble exactly as in r29/r58 (same lookbacks {10,20,30,60,90,150,250} on H6, same lag, same long/short half-structure), on P0-adjusted data.
  - Keep C1's position only if its sign agrees with H1's inventory sign: long allowed if D_t < 0, short allowed if D_t > 0. Otherwise flat.
  - WTI+BRENT equal risk; one basket.
- *Dev:* reported descriptively only. **No pass/fail on dev.**
- *Holdout gates (all):*
  - Sharpe ≥ 0.5;
  - ≥ 3/4 years positive;
  - |corr| ≤ 0.3 with C1 and I2;
  - maxDD ≤ 25 %;
  - net per trade ≥ 5× RT cost;
  - **and** holdout Sharpe ≥ plain C1-oil holdout Sharpe + 0.2.
- *Kill:* any fail closes the "oil trend" family together with the plain C1-oil holdout test. No retries.

**H4 (reserve, only if Claude wants a fully post-publication test): Arendas et al. Strategy A**
- *Rule:* long WTI+BRENT (equal risk) from the first trading day of February to the last trading day of September; flat October-January.
- *Status:* the rule was frozen by a 2018 publication, so dev 2018-2022 and holdout 2023-2026 are both post-publication.
- *Gates:* the usual dev gates (Sharpe ≥ 0.6, ≥ 60 % of years), then holdout once.
- *Note:* long-only means paying the -6 %/yr swap for 8 months a year, about -4 %/yr of notional (about -1.2 %/yr at 10 % vol).

### 7. What NOT to do (already tested or unsupported)
- Intraday oil: r57 EIA found zero, and the spread is 3.3 bp/side.
- Brent-WTI pairs: regime-dependent, and double swap.
- OPEC event drift.
- Crack spreads: not tradable at RF.
- COT continuation as the primary sign.
- Re-running the commodity basket with metals: r58 and r38 already did.

### 8. Source list (full citations)
Bessembinder 1992 RFS 5(4):637-667 · Bhardwaj, Gorton & Rouwenhorst 2015 NBER w21243 · Bianchi, Drew & Fan 2016 JBF 72:133-150 · Boons & Porras Prado 2019 JF 74(1):239-279 · Büyükşahin & Harris 2011 Energy J 32(2):167-202 · Büyükşahin, Lee, Moser & Robe 2013 Energy J 34(3) · Demirer & Kutan 2010 Energy Econ 32(6) · de Roon, Nijman & Veld 2000 JF 55(3):1437-1456 · Erb & Harvey 2006 FAJ 62(2):69-97 · Fama & French 1987 J Business 60(1):55-73 · Fattouh, Kilian & Mahadeva 2013 Energy J 34(3):7-33 · Fratzscher, Schneider & Van Robays 2014 ECB WP 1689 · Fuertes, Miffre & Rallis 2010 JBF 34(10):2530-2548 · Girma & Paulson 1999 JFM 19(8):931-955 · Gorton & Rouwenhorst 2006 FAJ 62(2):47-68 · Gorton, Hayashi & Rouwenhorst 2013 RoF 17(1):35-105 · Halova Wolfe, Kurov & Kucher 2014 JFM 34(10) doi 10.1002/fut.21633 · Hamilton 2009 BPEA Spring:215-261 · Harvey et al. 2018 JPM 45(1):14-33 · Hong & Yogo 2012 JFE 105(3):473-490 · Huang, Li, Wang & Zhou 2020 JFE 135(3):774-794 · Hurst, Ooi & Pedersen 2017 JPM 44(1):15-29 · Babu et al. 2020 JOIM 18(1) · Kang, Rouwenhorst & Tang 2020 JF 75(1):377-417 · Kilian 2009 AER 99(3):1053-1069 · Kim, Tse & Wald 2016 JFinMkts 30:103-124 · Koijen, Moskowitz, Pedersen & Vrugt 2018 JFE 127(2):197-225 · Levine & Pedersen 2016 FAJ 72(3):51-66 · Levine, Ooi, Richardson & Sasseville 2018 FAJ 74(2):55-68 · Lin & Tamvakis 2010 Energy Policy 38(2):1010-1016 · Loutia, Mellios & Andriosopoulos 2016 Energy Policy 90:262-272 · Miffre & Rallis 2007 JBF 31(6):1863-1886 · Moskowitz, Ooi & Pedersen 2012 JFE 104(2):228-250 · Quayyoum et al. 2020 Soft Computing 24(18):13547-13556 · Sanders, Boris & Manfredo 2004 Energy Econ 26(3):425-445 · Singleton 2014 Mgmt Sci 60(2):300-318 · Suenaga & Smith 2011 Energy J 32(3) · Szymanowska et al. 2014 JF 69(1):453-482 · Arendas, Tkacova & Bukoven 2018 J Intl Studies 11(2):180-192 · Baltas & Kosowski 2020, Market Momentum (Wiley) ch. 3 · RoboForex contract specifications page (fetched 15.11.2026) and RF rollover notices 15.12.2015 and 28.01.2016 · EIA NYMEX futures price table (pet_pri_fut_s1_d; note: no data after 5.4.2024).
