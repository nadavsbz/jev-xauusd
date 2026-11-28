# t307 — מועמדי אסטרטגיה עם בסיס מחקרי (Grok -> Claude)
תאריך: 20.11.2026 (שעון ישראל). מחבר: Grok Bot (המאסטרו). אין המלצת מסחר, ההחלטה של נדב.

## מתודולוגיה ותגיות
- כל מספר מתויג: **VERIFIED** = נקרא בטקסט המקור עצמו (PDF/עמוד המאמר שהורד ונקרא ב-pdftotext); **OBSERVED** = מופיע במקור משני (Quantpedia/CXO/תקציר מנוע חיפוש) ולא אומת בטבלת המקור; **ASSUMED** = הערכה שלי; **UNKNOWN** = לא נמצא.
- כל המספרים בטבלאות המקור הם **לפני עלויות** אלא אם נכתב אחרת.
- סינון חובה (pre-registered, לא רוכך): עלות תוך-יומית ≤0.02% לצד; swap ≤~5% לשנה; מכשירים EGlobal/RoboForex ECN (FX, זהב, מדדים, crypto CFD) או Alpaca (מניות/ETF ארה"ב); לא crypto trend ולא Nasdaq open momentum; בלי martingale/grid; עד 1–3 עסקאות ביום; ראיה מחוץ למדגם או שחזור עצמאי אחרי 2010.
- חישוב עזר לעלות (ASSUMED): round-trip ב-0.02% לצד = 4bp. אסטרטגיה שהתשואה הממוצעת שלה לעסקה נמוכה מ-~4bp נכשלת בסינון העלות, אלא אם מסננים לימים חזקים.
- C1 = crypto trend H6; I2 = Nasdaq intraday momentum (Concretum/Zarattini).

## טבלת סיכום
| # | מועמד | מקור | נכס | ציון | סינון |
|---|---|---|---|---|---|
| 1 | FX Fix Reversal (Tokyo/ECB/London) | Krohn, Mueller, Whelan, JF 2024 | EURUSD/GBPUSD/USDJPY וכו' (ECN) | **4** | עובר בתנאי שעלות ECN ≤~0.5bp לצד (לבדוק) |
| 2 | Front-running Rebalancers (SPY vs IEF) | Harvey, Mazzoleni, Melone, NBER/SSRN 2025 | SPY/IEF (Alpaca) | **4** | עובר |
| 3 | Turn-of-the-Month / Dash for Cash | McConnell & Xu FAJ 2008; Etula et al. RFS 2020 | US500 CFD / SPY | **3** | עובר (swap: להעדיף SPY ב-Alpaca) |
| 4 | Multi-asset Time-Series Momentum (ללא crypto) | Moskowitz, Ooi, Pedersen JFE 2012; Hurst, Ooi, Pedersen JPM 2017 | ETF ב-Alpaca (SPY, EFA, GLD, TLT, UUP, DBC...) | **3** | עובר דרך ETF; ב-CFD swap עלול לעבור 5% |
| 5 | EURUSD Time-of-Day (domestic-hours depreciation) | Breedon & Ranaldo, JMCB 2013 | EURUSD (ECN) | **3** | עלות גבולית; ראיה רק עד 2007 |
| 6 | Market Intraday Momentum (last 30 min) | Gao, Han, Li, Zhou JFE 2018; Baltussen, Da, Lammers, Martens JFE 2021 | US500 / SPY | **2** | עלות גבולית-נכשלת; קורלציה ל-I2 |
| 7 | Pre-FOMC Announcement Drift | Lucca & Moench JF 2015 | US500 / SPY | **2** | ראיה: נעלם אחרי 2015 |
| 8 | Macro Announcement Days | Savor & Wilson JFQA 2013 | SPY | **2** | אין ראיה אחרי 2009 |
| 9 | FX Carry | Koijen, Moskowitz, Pedersen, Vrugt JFE 2018 | FX (ECN) | **2** | swap/מבנה עלויות CFD; סיכון crash |
| 10 | Pairs Trading (distance) | Gatev, Goetzmann, Rouwenhorst RFS 2006; Do & Faff FAJ 2010 | מניות (Alpaca) | **2** | דעיכה מתועדת; הרבה עסקאות |
| 11 | Overnight Drift (ES 2:00–3:00 ET) | Boyarchenko, Larsen, Whelan RFS 2023 | US500 CFD | **1** | נכשל בעלות (לפי המחברים) |
| 12 | FOMC Cycle (even weeks) | Cieslak, Morse, Vissing-Jorgensen JF 2019 | SPY | **1** | נכשל: היפוך 2017–2021 |

## המלצה: 3–4 לבדיקה (בסדר עדיפות)
1. **#1 FX Fix Reversal** — הכי מגוון מול C1/I2 (FX, תוך-יומי, מבני/inventory). מנגנון מוסבר, מאמר JF עדכני, מדגם כולל 2010–2019. הסיכון: המחברים מצאו שללקוח (liquidity demander) בשוק client התשואה אחרי עלויות שלילית (2006–2019). השאלה המרכזית ל-DEV היא אם עלות ECN אמיתית (spread+commission) קטנה מספיק.
2. **#2 Front-running Rebalancers** — Sharpe מעל 1 גם נטו לפי המחברים, מדגם 1997–2023, נכסים זולים (SPY/IEF ב-Alpaca), סקיו חיובי. סיכון: פורסם ב-2025, ולכן ה-holdout שלנו הוא בעצם post-publication.
3. **#3 Turn-of-the-Month / Dash for Cash** — הכי פשוט ליישום ולבדיקה. ידוע מאוד ולכן סיכון דעיכה גבוה, אבל Etula et al. נותנים מנגנון (settlement) שמאפשר כלל מעודכן: להזיז את החלון לפי T+1 מ-05.2024.
4. **#4 TSMOM על ETF** (או #5 כתוספת זולה ל-#1 על אותם נתוני Dukascopy) — TSMOM מגוון מ-I2 ובחלקו מ-C1, אבל ביצועי trend בשנות ה-2010 חלשים (ASSUMED/UNKNOWN). #5 זול לבדיקה יחד עם #1.

---

## 1. FX Fix Reversal — ציון 4
1. **מקור:** Krohn, I., Mueller, P., Whelan, P. (2024). "Foreign Exchange Fixings and Returns around the Clock". *Journal of Finance* 79(1):541–578. https://doi.org/10.1111/jofi.13306 ; גרסה פתוחה: https://wrap.warwick.ac.uk/id/eprint/177333/ ; SSRN 3521370.
2. **כללים (מהמאמר, זמני ET):** חלונות: pre-T 17:00–20:55 (Tokyo fix 9:55 Tokyo; ב-EST נגמר 19:55), post-T 20:55–2:00, pre-E 2:00–8:15 (ECB fix 14:15 CET; **הוזז ל-16:00 CET ביולי 2016**), E-L 8:15–11:00 (לא נסחר), post-L 11:00–17:00 (London fix 16:00 London). אסטרטגיה: **long USD לפני fix** (pre-T, pre-E) ו-**short USD אחרי fix** (post-T, post-L). Tokyo = −Δs(pre-T) + Δs(post-T); Europe = −Δs(pre-E) + Δs(post-L) [VERIFIED]. גודל פוזיציה: חשיפה שווה למטבע / dollar portfolio. timeframe: M5–H1. ליישום שלנו (ASSUMED): להתחיל ב-EURUSD ו-GBPUSD בחלון Europe בלבד (2 עסקאות ביום), כניסה ב-17:00 ET בעייתית בגלל rollover, אז להתחיל ב-17:30.
3. **ביצועים (לפני עלויות):** מדגם 01.1999–12.2019, G9 [VERIFIED]. תשואה שנתית בחלון Europe: EUR 15.6%, GBP 12.4%, CHF 12%; בחלון Tokyo 6.2% (CHF) עד 14.2% (NZD) [VERIFIED]. סטיית תקן שנתית "generally below 8%" [VERIFIED]. 1$ ב-EUR בחלון Europe צמח ל-26.9$ עד סוף 2019 [VERIFIED]. Sharpe: UNKNOWN (לא חישבתי מהטבלה). MDD: UNKNOWN. אחרי עלויות ללקוח (Table X, 2006–2019): שלילי [VERIFIED, ניסוח המחברים: "reversal returns turn negative once transaction costs are taken into account"].
4. **נתונים:** Dukascopy tick/M1 (EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD) + spread אמיתי מ-RoboForex ECN/EGlobal.
5. **קורלציה:** C1 ≈ 0, I2 ≈ 0 [ASSUMED]: נכס, שעות ומנגנון שונים.
6. **דעיכה:** בינונית. פורסם ב-2020 ב-SSRN וב-2024 ב-JF; התבנית מבנית (ביקוש ל-USD ב-fix), אבל יש סיכון שזמן ה-ECB fix ישתנה. אין לנו מדגם post-publication, אז 2020–2026 הוא OOS אמיתי.
7. **ציון 4:** פיזור מצוין ומנגנון חזק. ההוראה מהמחברים שעלויות מוחקות את הרווח ללקוח היא הסיבה שזה לא 5. gate מוצע: תשואה נטו לעסקה > עלות ECN מדודה ×2.

## 2. Front-running Rebalancers (SPY vs IEF) — ציון 4
1. **מקור:** Harvey, C.R., Mazzoleni, M.G., Melone, A. (2025, rev. 01.2026). "The Unintended Consequences of Rebalancing". NBER WP 33554 / SSRN 5122748. https://www.nber.org/papers/w33554
2. **כללים [VERIFIED מבחינת המבנה]:** סימולציה של תיק 60/40 (S&P 500 / 10Y T-note). **Threshold signal** = סטיית משקל המניות מ-60% בתיק שמאוזן מחדש כשהסטייה ≥ δ (כויל סביב 2pp); **Calendar signal** = סטיית המשקל בתיק שמאוזן בכל יום מסחר אחרון בחודש. משקל האסטרטגיה = ממוצע של (−Threshold/1.5%) ושל Calendar מותאם: sign(−Calendar) בשבוע האחרון בחודש, sign(Calendar_{−4}) ביום העסקים הראשון בחודש, ו-0 בשאר הימים. תשואה = (R_SP500 − R_10Y) × w. עדכון יומי, החזקה עד היום הבא. ליישום: SPY מול IEF ב-Alpaca, עסקה אחת ביום לכל היותר.
3. **ביצועים:** 10.09.1997–17.03.2023: תשואה עודפת 10.20% לשנה, vol 9.17%, Sharpe 1.11, skew 5.23 [VERIFIED, Table 6]. Sharpe נטו מעלויות "close to 1" [VERIFIED]. Sharpe בלי 09.2008–03.2009 ו-03.2020: 0.90 [VERIFIED]. MDD: UNKNOWN.
4. **נתונים:** Yahoo/Alpaca יומי ל-SPY, IEF (או ES/ZN). צריך close-to-close.
5. **קורלציה:** C1 ≈ 0; I2 נמוכה, ~0.1 [ASSUMED]. האסטרטגיה בין-נכסית ויומית, ולא מומנטום תוך-יומי.
6. **דעיכה:** גבוהה-בינונית. פורסם 2025 והמחברים עצמם מציינים front-running. הרווח מרוכז בתקופות משבר (skew 5.23), כך שתקופה רגועה עלולה להיראות כ-FAIL.
7. **ציון 4:** כללים מפורשים, Sharpe נטו ~1, נכסים זולים. מוריד: מדגם post-publication קצר, ותלות במשברים.

## 3. Turn-of-the-Month / Dash for Cash — ציון 3
1. **מקור:** McConnell, J.J., Xu, W. (2008). "Equity Returns at the Turn of the Month". *FAJ* 64(2). https://docs.lib.purdue.edu/ciberwp/43/ ; Etula, E., Rinne, K., Suominen, M., Vaittinen, L. (2020). "Dash for Cash: Monthly Market Impact of Institutional Liquidity Needs". *RFS* 33(1):75–111. https://www.aalto.fi/sites/default/files/2021-03/dashforcashpaper_final_complete.pdf
2. **כללים:** בסיס (McConnell-Xu): long מדד מ-close של יום T−2 (כדי להחזיק את יום −1) עד close של היום ה-3 בחודש החדש; אחרת flat. גרסת Etula: long מ-T−3 עד T+3 (T = יום מסחר אחרון), כשאופציונלית short/flat מ-T−8 עד T−4. הלוגיקה תלויה ב-settlement: המאמר נכתב תחת T+3, וב-09.2017 עבר ל-T+2 [VERIFIED שהמאמר מציין את המעבר], ומ-05.2024 ל-T+1 [ASSUMED/ידע כללי]. לכן כלל מקדים: להזיז את החלון יום אחד קדימה לכל קיצור settlement. גודל: 100% חשיפה, 1–2 עסקאות בחודש.
3. **ביצועים:** McConnell-Xu: 1987–2005, כל התשואה העודפת בחלון של 4 ימים [VERIFIED, תקציר]; תשואה יומית value-weighted 0.14% בחלון לעומת −0.01% בשאר הימים [OBSERVED, CXO]. Quantpedia: 7.2% לשנה, vol 6.9%, Sharpe 1.04, MDD −20.79% (1926–2005, הערכה שלהם) [OBSERVED]. Etula: CRSP VW מאז 1995: −17bp ב-T−8..T−4 ו-+77bp ב-T−3..T+3; abnormal +48bp ב-T−3..T+3 [VERIFIED].
4. **נתונים:** Yahoo SPY יומי (1993+), Dukascopy US500.
5. **קורלציה:** C1 נמוכה, ~0.1; I2 נמוכה, ~0.1 [ASSUMED]: חשיפת beta למניות רק כ-20% מהזמן.
6. **דעיכה:** גבוהה. האפקט ידוע מאז 1988 ו-Quantpedia מזהירה שאפקטים קלנדריים "vanish or rotate". ראיה אחרי 2010 במאמרים שקראתי: חלקית בלבד (אות ה-Calendar של Harvey 2025 עד 2023). חייב בדיקה עצמאית על 2010–2026.
7. **ציון 3:** פשוט, זול, מנגנון סביר. מוריד: ידוע מאוד, beta long-only, בלי ראיה post-2010 נקייה בידיים שלי.

## 4. Multi-asset Time-Series Momentum (ללא crypto) — ציון 3
1. **מקור:** Moskowitz, T.J., Ooi, Y.H., Pedersen, L.H. (2012). "Time Series Momentum". *JFE* 104:228–250. https://pages.stern.nyu.edu/~lpederse/papers/TimeSeriesMomentum.pdf ; Hurst, B., Ooi, Y.H., Pedersen, L.H. (2017). "A Century of Evidence on Trend-Following Investing". *JPM* Fall 2017. https://www.aqr.com/-/media/AQR/Documents/Insights/Journal-Article/AQR-JPM-Fall-2017.pdf
2. **כללים:** לכל נכס: סימן התשואה העודפת ב-12 חודשים (Hurst: שילוב 1/3/12 חודשים) → long/short; גודל לפי volatility targeting (40% לנכס ב-MOP; תיק 10% vol ב-Hurst); איזון חודשי. timeframe: D1/חודשי. ליישום שלנו (ASSUMED): ETF ב-Alpaca (SPY, EFA, EEM, TLT, IEF, GLD, DBC, UUP/FXE/FXY), long/flat כשאין short זול, איזון חודשי.
3. **ביצועים:** MOP: תיק מגוון עם Sharpe "greater than one" (1985–2009) [VERIFIED, טקסט]. Hurst: 1880–2016; drawdowns "up to 25%" [VERIFIED]; 7.3% לשנה נטו מעלויות ומ-2/20, vol 9.7%, Sharpe נטו 0.76 [OBSERVED, הנתונים נמצאים בתמונת Exhibit 1 ולא בטקסט שחולץ].
4. **נתונים:** Yahoo/Alpaca יומי ל-ETF; Dukascopy ל-FX/זהב.
5. **קורלציה:** C1 בינונית, ~0.2–0.4 (אותו style, נכסים אחרים, בעיקר במשברים); I2 נמוכה, ~0.1 [ASSUMED].
6. **דעיכה:** בינונית-גבוהה. ביצועי trend ב-2010–2019 נחשבים חלשים [ASSUMED, לא אומת במקור שקראתי]. אזהרת swap: ב-CFD של מדדים/זהב swap long עלול לעבור 5% לשנה [ASSUMED], ולכן רק דרך ETF.
7. **ציון 3:** ראיה ארוכה וחזקה מאוד, אבל חפיפת style עם C1 ודעיכה בעשור האחרון.

## 5. EURUSD Time-of-Day — ציון 3
1. **מקור:** Breedon, F., Ranaldo, A. (2013). "Intraday Patterns in FX Returns and Order Flow". *JMCB* 45(5):953–965. גרסה פתוחה (SNB WP 2011-04): https://www.snb.ch/public/asset/en/www-snb-ch/publications/research/working-papers/2011/working_paper_2011_04/publications0_en/working_paper_2011_04.n.pdf
2. **כללים [VERIFIED]:** מטבע נוטה להיחלש בשעות המסחר המקומיות שלו. שעות (Table 1): Europe 07:00–15:00 מקומי, US 08:00–16:00 NY. EURUSD: **short EUR בשעות הבוקר האירופיות** ו-**long EUR בשעות ארה"ב** (open-to-close / open-to-open), בלי התאמות חגים. 2 עסקאות ביום. timeframe: H1.
3. **ביצועים:** 1997–2007, EBS bid/ask: Sharpe 1.3 (short בבוקר) ו-0.9 (long אחה"צ) **אחרי עלויות** [VERIFIED]. במטבעות אחרים: "most ... not profitable when trading costs are included" [VERIFIED]. תשואה שנתית ו-MDD: UNKNOWN.
4. **נתונים:** Dukascopy EURUSD M1/tick.
5. **קורלציה:** C1 ≈ 0, I2 ≈ 0 [ASSUMED]. מול #1 קורלציה חיובית צפויה [ASSUMED].
6. **דעיכה:** גבוהה. המדגם נגמר ב-2007, כלומר אין ראיה אחרי 2010 במאמר. Krohn et al. 2024 (עד 2019) מראים תבנית תוך-יומית קרובה ב-USD, שזה שחזור חלקי ולא זהה. 2010–2026 הוא OOS מלא.
7. **ציון 3:** זול לבדיקה יחד עם #1. נכשל בקריטריון הראיה עד שנבדוק בעצמנו OOS (זה בדיוק ה-holdout).

## 6. Market Intraday Momentum (last 30 min) — ציון 2
1. **מקור:** Gao, L., Han, Y., Li, S.Z., Zhou, G. (2018). "Market Intraday Momentum". *JFE* 129:394–414. https://doi.org/10.1016/j.jfineco.2018.05.009 ; Baltussen, G., Da, Z., Lammers, S., Martens, M. (2021). "Hedging Demand and Market Intraday Momentum". *JFE* 142:377–403. https://academicweb.nd.edu/~zda/intramom.pdf
2. **כללים [VERIFIED]:** בתחילת חצי השעה האחרונה (15:30 ET): long אם r1 (close אתמול → 10:00) > 0, אחרת short; סגירה ב-close. גרסת Baltussen: האות = תשואה מ-close אתמול עד 30 דקות לפני הסגירה (rROD). עסקה אחת ביום.
3. **ביצועים (לפני עלויות):** Gao (SPY 1993–2013): 6.67% לשנה, std 6.19%, Sharpe 1.08 [VERIFIED]. Baltussen (חוזי מדדים 12.1974–05.2020): η(rROD) 6.86% לשנה, std 3.96%, Sharpe 1.73; η(rONFH) Sharpe 1.07 [VERIFIED]. עלויות לא נכללו ("we do not consider transaction costs") [VERIFIED]. MDD: UNKNOWN.
4. **נתונים:** Alpaca/Polygon SPY M1; Dukascopy US500.
5. **קורלציה:** C1 ≈ 0; **I2 בינונית, ~0.3–0.5** [ASSUMED]: אותה משפחה (intraday momentum במדדי ארה"ב), בסוף היום במקום בפתיחה.
6. **דעיכה:** בינונית.
7. **ציון 2:** חישוב: 6.86%/252 ≈ 2.7bp לעסקה, פחות מ-round-trip של 4bp, כך שנכשל בסינון העלות בגרסה הבסיסית [ASSUMED, חישוב שלי]. אפשר לנסות רק עם פילטר |r| גדול / ימי vol גבוהה, ועם קורלציה ל-I2.

## 7. Pre-FOMC Announcement Drift — ציון 2
1. **מקור:** Lucca, D.O., Moench, E. (2015). "The Pre-FOMC Announcement Drift". *JF* 70(1). NY Fed SR 512: https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr512.pdf ; דעיכה: Kurov, Wolfe, Gilbert (2021) "The disappearing pre-FOMC announcement drift", *FRL* 40. https://pmc.ncbi.nlm.nih.gov/articles/PMC7525326/
2. **כללים [VERIFIED]:** long SPX ב-14:00 ET ביום שלפני הודעת FOMC מתוכננת, יציאה ב-14:00 ביום ההודעה (15 דקות לפני 14:15); cash בשאר הימים. 8 עסקאות בשנה.
3. **ביצועים:** 09.1994–03.2011: ממוצע 49bp (0.488) לאירוע, Sharpe שנתי 1.14 [VERIFIED]. אחרי הפרסום (Kurov et al.): 2011–2015 עם מסיבת עיתונאים 44.5bp; 2016–2019 9.2bp, שלא שונה מימים רגילים [VERIFIED].
4. **נתונים:** Alpaca/Dukascopy US500 M5 + לוח FOMC.
5. **קורלציה:** C1 ≈ 0, I2 נמוכה [ASSUMED].
6. **דעיכה:** **מתועדת: נעלם אחרי 2015**.
7. **ציון 2:** עלות זניחה ומעט עסקאות, אבל הראיה post-2015 שלילית. מתאים לכל היותר כ-overlay.

## 8. Macro Announcement Days — ציון 2
1. **מקור:** Savor, P., Wilson, M. (2013). "How Much Do Investors Care About Macroeconomic Risk? Evidence from Scheduled Economic Announcements". *JFQA* 48(2):343–375. https://repository.upenn.edu/server/api/core/bitstreams/80bbba5b-87be-4a72-84aa-d1ced5dd0b62/content
2. **כללים:** long מדד close-to-close בימי פרסום מתוכננים של CPI/PPI, Employment ו-FOMC; flat בשאר הימים.
3. **ביצועים:** 1958–2009: 11.4bp בימי הודעה לעומת 1.1bp בימים אחרים; Sharpe גבוה פי 10 [VERIFIED]. Sharpe/MDD לאסטרטגיה: UNKNOWN. ביקורת: Ernst, Gilbert & Hrdlicka (2019), בחירת סוגי הודעות ex post [OBSERVED, מצוטט ב-Knox & Vissing-Jorgensen 2026].
4. **נתונים:** Yahoo SPY + לוח BLS/FOMC.
5. **קורלציה:** C1 ≈ 0; I2 נמוכה-בינונית (ימי הודעה = ימי vol) [ASSUMED].
6. **דעיכה:** גבוהה, אין ראיה אחרי 2009 בידיים שלי.
7. **ציון 2.**

## 9. FX Carry — ציון 2
1. **מקור:** Koijen, R., Moskowitz, T., Pedersen, L.H., Vrugt, E. (2018). "Carry". *JFE* 127(2). https://pages.stern.nyu.edu/~lpederse/papers/Carry.pdf
2. **כללים:** דירוג מטבעות G10 לפי carry (הפרש ריבית / forward discount), long לגבוהים ו-short לנמוכים, משקלים לפי דירוג, איזון חודשי.
3. **ביצועים:** carry בכל סוג נכס עם Sharpe 0.6–0.9, ותיק רב-נכסי עם Sharpe 1.5 [VERIFIED, טקסט]; מטבעות 11.1983–02.2011 [VERIFIED]. Sharpe ספציפי ל-FX: UNKNOWN (לא חולץ מהטבלה).
4. **נתונים:** Dukascopy + ריביות (FRED) + טבלת swap אמיתית מהברוקר.
5. **קורלציה:** C1 נמוכה-בינונית (risk-on) [ASSUMED]; I2 נמוכה [ASSUMED].
6. **דעיכה:** גבוהה; carry crash 2008 מתועד בספרות (Brunnermeier, Nagel, Pedersen 2008).
7. **ציון 2:** ב-CFD ה-swap הוא התשואה עצמה פחות markup של הברוקר, ולכן לא עומד ברוח סינון ה-swap. מדגם עד 2011.

## 10. Pairs Trading (distance method) — ציון 2
1. **מקור:** Gatev, E., Goetzmann, W., Rouwenhorst, K.G. (2006). "Pairs Trading: Performance of a Relative-Value Arbitrage Rule". *RFS* 19(3). WP: https://www.nber.org/system/files/working_papers/w7032/w7032.pdf ; Do, B., Faff, R. (2010). "Does Simple Pairs Trading Still Work?" *FAJ* 66(4).
2. **כללים:** formation של 12 חודשים: זוגות לפי מינימום SSD של מחירים מנורמלים; trading של 6 חודשים: פתיחה כשהפער > 2σ [VERIFIED], סגירה בהתכנסות.
3. **ביצועים:** "about 12 percent" לשנה excess לתיקי top-pairs (WP 1962–1997) [VERIFIED]. Do & Faff: top-20 0.86% לחודש (1962–1988) → 0.37% (1989–2002) → 0.24% (2003–2009) [OBSERVED, תקציר].
4. **נתונים:** Alpaca יומי (מניות S&P 500).
5. **קורלציה:** ≈ 0 לשניהם [ASSUMED].
6. **דעיכה:** **מתועדת**.
7. **ציון 2:** דעיכה, הרבה עסקאות ו-short borrow.

## 11. Overnight Drift (ES 2:00–3:00 ET) — ציון 1 (נכשל בעלות)
1. **מקור:** Boyarchenko, N., Larsen, L.C., Whelan, P. (2023). "The Overnight Drift". *RFS* 36(9):3502–3547. NY Fed SR 917: https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf
2. **כללים:** long S&P 500 futures 2:00–3:00 ET (פתיחת אירופה).
3. **ביצועים:** 1998–2020: 3.7% לשנה (1.48bp ליום); Sharpe 1.1 לפני עלויות ו-**−0.5 אחרי bid-ask**; חלון 1:30–3:30: 1.3 לפני ו-0.3 אחרי [VERIFIED].
4. **נתונים:** Dukascopy US500.
5. **קורלציה:** נמוכה [ASSUMED].
6. **דעיכה:** UNKNOWN.
7. **ציון 1:** 1.48bp < 4bp, נכשל בסינון העלות לפי המחברים עצמם. שווה בדיקה רק בגרסה מותנית (אחרי selloff ביום הקודם; המאמר מראה reversal אסימטרי), כרעיון ולא כמועמד.

## 12. FOMC Cycle (even weeks) — ציון 1 (נכשל בראיה)
1. **מקור:** Cieslak, A., Morse, A., Vissing-Jorgensen, A. (2019). "Stock Returns over the FOMC Cycle". *JF* 74(5):2201–2248. https://www.stern.nyu.edu/sites/default/files/assets/documents/cycle_paper_cieslak_morse_vissingjorgensen.pdf ; עדכון: Knox & Vissing-Jorgensen (2026) FEDS 2026-023. https://www.federalreserve.gov/econres/feds/files/2026023pap.pdf
2. **כללים:** long מניות בשבועות 0, 2, 4, 6 של מחזור FOMC (שבוע 0 מתחיל יום לפני ההודעה); flat בשבועות האי-זוגיים.
3. **ביצועים:** 1994–2016: התשואה העודפת ליום גבוהה ב-13.6bp בשבוע 0 וב-10bp בשבועות 2/4/6, ביחס לשאר הימים [VERIFIED, טיוטה 10.2015]. **2017–2021: מחזור הפוך מובהק** [VERIFIED, Knox & Vissing-Jorgensen 2026].
4. **נתונים:** Yahoo SPY.
5. **קורלציה:** נמוכה [ASSUMED].
6. **דעיכה:** **מתועדת: היפוך**.
7. **ציון 1.**

---
## הערות integrity
- לא הומצאו מספרים. כל מה שמסומן VERIFIED נקרא ב-PDF שהורד ל-/workspace/t307/src (טקסט חולץ ב-pdftotext).
- מאמרים מאחורי paywall (JF/JFE/RFS בגרסה סופית) לא נרכשו. נעשה שימוש בגרסאות פתוחות (SSRN/NBER/WRAP/NY Fed/מחברים), ולכן מספרים בגרסה הסופית עשויים להיות שונים מעט.
- r/algotrading לא שימש כראיה.
- אין המלצת מסחר, ההחלטה של נדב.
