# t416: סינון מנועים בסגנון C1/I2 עבור US ETFs/מניות ב-Alpaca (SCREEN ONLY, K=0)

- נכתב: 26.11.2026 (שעון ישראל), Grok (המאסטרו). **סינון בלבד:** אין PREREG, אין ריצה, ולא נפתח שום נתון. ‏K=0 בלדג'ר.
- תגיות: **VERIFIED** = נקרא במקור. **OBSERVED** = מקור משני או תקציר. **ASSUMED** = הנחה/הערכה שלי. **UNKNOWN** = לא נמצא.
- הקשר: ‏t415 נדחה בצדק. ‏C1 על XAU נסגר ב-t405 (F3 KILL) לפי השער שלי. זו הייתה טעות שלי, ואני מקבל את הדחייה.

## 0. שורה תחתונה
1. **אף מנוע מבוסס בסגנון C1/I2 על US ETFs לא מגיע באופן כן ל-‎≥3.5% לחודש עם DD ≤25%** במינוף של Reg-T. [ASSUMED, על סמך המספרים המאומתים שבטבלה]
2. רוב משפחות ה-I2 על ETFs כבר נסגרו אצלנו: ‏t318B, ‏t409, ‏r104. גם ORB נסגר (t318A, ‏r103), וכך גם מגמה רב-שוקית (r101) ומגמה במניות (t338). [VERIFIED מהלדג'ר ומ-/workspace]
3. נשארו 3 מנועים מבוססים שלא נבדקו. **שניים מהם רחוקים מהרף בתשואה, והשלישי (VIX) רחוק מהרף ב-DD.**
4. **ההמלצה הכנה:** מקום מסחר חדש **לא מוצדק בשביל המנועים האלה לבדם**. ההחלטה, וגם ההחלטה על הגדלת C1/I2, היא של נדב.

## 1. בדיקת החרגות (קריאה בלבד ב-LEDGER.md, ב-docs/prereg וב-/workspace/t318*)
| מזהה | משפחה | תוצאה | השפעה על t416 |
|---|---|---|---|
| t338 | מגמה לונג במניות בשיא כל הזמנים (Zarattini/Pagani/Wilcox 2025) | NO-GO, ‏Sharpe 0.44 | מגמה חתכית במניות מוחרגת |
| t345 | Conservative Formula | נכשל | מוחרג |
| t347 | הטיית לילה חתכית | נכשל | Overnight מוחרג |
| t348 | PEAD | נכשל | מוחרג |
| t353 | cluster buys של בעלי עניין | נכשל | מוחרג |
| t355 | חיזוי SPY ל-30 דק' (Ridge) | נכשל | מוחרג |
| t358 | עונתיות Heston–Sadka | נכשל | מוחרג |
| t360 | אקטיביסטים 13D | נכשל | מוחרג |
| t366 | היפוך אחרי הוצאה מ-S&P | נכשל | מוחרג |
| t409 | beta_clock (מאפיין I2) על SPY/IWM/DIA/SMH/XLF | 0/5, הסימן התהפך ב-2024–26 | "I2 על ETFs נוספים" נסגר |
| t318A | ORB על Stocks in Play (DEV 2016–21) | §8א KILL, ‏A0 gross R ‎−0.18 | ORB מוחרג (וגם r103) |
| t318B | Noise-Area על סל 16 ETFs (DEV) | FAIL, ‏B0/B1/B2 K2 kill | Noise-Area על ETFs מוחרג |
| r101 | C1 על סל פיוצ'רס | Sharpe 0.31 | TSMOM רב-שוקי מוחרג |
| r102 | IBS יומי ב-ETFs | Sharpe 0.24 | היפוך יומי ב-ETFs מוחרג |
| t393/t394 | LETF / residual momentum | נפסל או נכשל | זרימות LETF מוחרגות |
[VERIFIED: שורות הלדג'ר, קובצי research_t*.md ו-r10x, ‏/workspace/t318A_dev/out/gates_DEV.json, ‏/workspace/t318B/out/gates_t318B_DEV.json]

**גם המועמד הקלאסי ל-I2 נפסל:** ‏Gao, Han, Li, Zhou, "Market Intraday Momentum" (JFE 2018), שבו חצי השעה הראשונה מנבאת את האחרונה.
- t409 כבר מכסה את המנגנון.
- שכפולים בלתי תלויים מראים דעיכה מלאה:
  - deadsignalslab, ‏30.09.2026: ב-SPY/QQQ/IWM/DIA בשנים 2014–2026 התוצאה היא ‎−2.30bp ליום נטו (t=−5.17), והסימן הפוך ב-SPY וב-DIA. ב-IWM האפקט ירד מ-1.40bp ל-0.08bp אחרי 2018.
  - kruegeralgorithms: השיפוע ב-NQ, SPX ו-Dow בשנים 2015–2026 הוא 0 או שלילי. [OBSERVED, שני מקורות משניים]
  - https://deadsignalslab.substack.com/p/replication-intraday-momentum-eight
  - https://kruegeralgorithms.com/en/research/intraday-momentum-paper-replication

**גם VWAP-QQQ של Concretum (P2) נפסל:** הוא בלי slippage, מתואם ל-I2 על USTECH, וכבר נדחה ב-t318. [VERIFIED מ-t318_map]

## 2. עלויות ב-Alpaca (round trip)
- עמלה 0. ספרד ETF גדול: ‏0.3–1bp [ASSUMED, לפי המשימה].
- SEC Section 31: ‏$20.60 למיליון במכירות מ-04.04.2026, כלומר ‏0.206bp לצד המכירה. [VERIFIED: sec.gov/rules-regulations/fee-rate-advisories/2026-2, ולוח העמלות של Alpaca מ-17.11.2026]
- FINRA TAF: ‏$0 בין 01.10 ל-31.12.2026. מ-01.01.2027 חוזר ל-‎$0.000195 למניה, עם תקרה של ‎$9.79. [VERIFIED: SR-FINRA-2026-021, ‏BrokFeeSched.pdf]
- CAT: ‏$0.000003 למניה בכל צד. [VERIFIED, BrokFeeSched]
- slippage: ‏1–2bp לצד [ASSUMED].
- **הערכת round trip:** ‏≈2–5bp ב-ETFs נזילים. ב-SVXY/VXX ‏≈4–10bp [ASSUMED].
- **מינוף:**
  - חשבון cash: ‏1x, בלי שורט.
  - Reg-T: ‏2x overnight.
  - intraday: עד 4x.
  - כלל ה-PDT (‏$25k) בוטל. ה-SEC אישרה את תיקון FINRA 4210 ב-14.04.2026, והוא בתוקף מ-04.06.2026, עם phase-in עד 20.10.2027. [OBSERVED: sec.gov 34-105226, ‏FINRA RN 26-10]
  - מה ש-Alpaca מיישמת בפועל ללקוח בינלאומי: UNKNOWN.

## 3. טבלת מנועים (3 מבוססים שלא נבדקו אצלנו)
| # | מנוע | מקור | ביצוע מדווח מול עלות | OOS / אחרי פרסום | החזקה | קיבולת | נתונים | עומד ברף נדב? | מתאם ל-C1/I2 | סיכוי כן |
|---|---|---|---|---|---|---|---|---|---|---|
| E1 | **מגמת ענפים/סקטורים, לונג בלבד** (Donchian/Keltner 20/40 + vol sizing). המקבילה הישירה ל-C1 | Zarattini & Antonacci, "A Century of Profitable Industry Trends", SSRN 4857230, Dow Award 2025. PDF: concretumgroup.com/wp-content/uploads/2026/02/A-Century-of-Profitable-Industry-Trends.pdf [VERIFIED] | ‏ETFs 2005–03.2024, gross: ‏7.7% לשנה, ‏vol 13.7%, ‏Sharpe 0.61, ‏MDD 24%. ענפים 1926–2024: ‏IRR 18.2%, ‏Sharpe 1.39, ‏MDD 33% [VERIFIED PDF]. turnover כ-2,270% לשנה, ובעלות של 3bp זה כ-0.7% לשנה [ASSUMED מחישוב] | שכפול בלתי תלוי עד 06.2026: ‏7.97%, ‏Sharpe 0.51, מתחת ל-SPY (0.57). נטו עם margin קמעונאי ו-5bp: ‏5.85%, ‏MDD ‎−23.4% [OBSERVED: pastperformancelab]. בני דודים אצלנו נכשלו: r101 (0.31) ו-t338 (0.44) | ימים עד שבועות | גבוהה | יומי, חינם (Alpaca/Yahoo) | **לא.** כ-0.5–0.65% לחודש. כדי להגיע ל-3.5% צריך פי 5 ומעלה, ו-Reg-T מאפשר רק 2x | ל-C1: נמוך (‏0.1–0.3) [ASSUMED]. ל-I2: נמוך | לרף: ‏≤2%. כרכיב עם Sharpe 0.5: כ-40% |
| E2 | **פרמיית בסיס VIX** (שורט vol כשיש contango, דרך SVXY/VXX) | Simon & Campasano, "The VIX Futures Basis: Evidence and Trading Strategies", J. Derivatives 2014, SSRN 2094510 [OBSERVED: תקציר ו-DOI] | בפיוצ'רס, אחרי עלויות: ‏$792 לחוזה בשורט ו-$1,018 בלונג [OBSERVED מהתקציר]. ב-ETP: ‏SVXY עם מסנן contango: ‏CAGR 38%, ‏MDD ‎−58% (עד 2019) [OBSERVED: CXO Advisory] | Volmageddon בפברואר 2018: ‏XIV נסגר, ו-SVXY הוקטן ל-‎−0.5x [ASSUMED/ידוע]. מסנן ה-contango לא מונע קפיצה בתוך יום [OBSERVED] | ימים | בינונית | יומי. רצוי גם עקום VIX futures מ-CBOE (חינם) | **לא, בגלל ה-DD.** התשואה אפשרית (כ-2–3% לחודש), אבל MDD של 50% ומעלה בהיסטוריה. גם סיכון crash-day | ל-C1: נמוך. ל-I2: נמוך עד בינוני. **נפגע בימי קריסה במניות** [ASSUMED] | לרף: ‏≤3% |
| E3 | **SPY/QQQ עם מסנן מגמה ו-vol targeting** (SMA10 חודשי + ‏σ-target, עד 2x) | Faber, "A Quantitative Approach to Tactical Asset Allocation" (2007), ‏Moreira & Muir, "Volatility-Managed Portfolios" (JF 2017) [OBSERVED] | כ-10–15% לשנה, ‏Sharpe 0.7–0.9 [ASSUMED מהספרות] | Cederburg, O'Doherty, Wang, Yan (JFE 2020, ‏https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3357038): ב-real-time, vol-managing בדרך כלל **מוריד** Sharpe, על פני 103 אסטרטגיות [OBSERVED מהתקציר] | שבועות עד חודשים | גבוהה מאוד | יומי, חינם | **לא.** כ-1% לחודש ב-2x | ל-I2 (USTECH): **בינוני עד גבוה** (בטא לנאסד"ק) [ASSUMED] | לרף: ‏≤1% |

## 4. דירוג
1. **E1 (מגמת ענפים):** הכי מבוסס, הכי זול, ומתאם נמוך ל-C1/I2. אבל זה רכיב עם Sharpe של כ-0.5, לא מנוע של 3.5% לחודש.
2. **E2 (VIX basis):** היחיד עם תשואה בסדר הגודל הנדרש. נכשל ב-DD, ומסוכן בדיוק בימים הלא נכונים. לא מומלץ בלי הגנה מבנית (אופציות). זה מחוץ ל-scope של Alpaca equities.
3. **E3:** דומה מדי לבטא של I2, והראיות ל-OOS שליליות.

## 5. Alpaca וישראל
- [UNKNOWN] האם תושב ישראל יכול לפתוח חשבון Trading API. בדף הרשמי "Countries Alpaca is available" (פברואר 2026) אין רשימה, רק הפניה ל-support@alpaca.markets [VERIFIED].
- [OBSERVED] ישראל מופיעה ברשימת האזורים ל-Funding Wallets (Broker API), ו-ILS מופיע כמטבע הפקדה. **אבל** באותו עמוד ישראל מופיעה גם ברשימת "Route is unavailable" לערוץ מסוים. מקור: https://alpaca.markets/support/funding-wallets-for-broker-api-2
- [VERIFIED] לפי הדף "live-trading-account-non-us" (עודכן 11.03.2026): כ-195 מדינות נתמכות, קנדה לא. נדרשים Tax ID, מסמך עם תמונה וכתובת, וסלפי.
- לא נרשמתי ולא פניתי ל-support. פנייה כזו היא החלטה של נדב.

## 6. אם נדב יאשר מקום מסחר: הרישום הראשון (t417, טיוטה בלבד, לא FROZEN)
- **מנוע:** E1, חוקי המאמר בדיוק (Upper = min(Donchian20, Keltner20,k=2), יציאה בפס התחתון 40). יקום מוגדר מראש: 11 SPDR סקטורים ו-20 SPDR ענפיים. גודל לפי vol, בלי שינוי.
- **dev:** ‏01.2006–12.2016.
- **holdout:** ‏01.2017–10.2026, ריצה אחת. **הערה:** השכפול הציבורי עד 06.2026 כבר נצפה, ולכן ה-holdout הוא REUSED-public, לא נקי. אימות נקי רק forward (paper).
- **K=1** (אין וריאנטים). DSR עם ‏N≈4,600.
- **שערים:**
  - Sharpe נטו ≥0.8 ב-dev.
  - G2: ‏≥3.5% לחודש ב-L* כך ש-MDD ≤25%, עם L ≤2 (Reg-T).
  - מתאם יומי ל-C1/I2 ≤0.4.
- **תחזית מראש (ASSUMED): FAIL ב-G2 בסבירות של כ-98%.** לכן אני ממליץ לא להריץ אותו כמנוע עצמאי, אלא רק אם נדב רוצה רכיב פיזור עם Sharpe נמוך. זה מנוגד להעדפה שלו ל"high-return systems".
- **הכלל של נדב (כל FAIL עם איטרציה הבאה):** אם t417 נכשל, האיטרציה הבאה לא תהיה ב-Alpaca equities. היא תהיה החלטת venue או scale של נדב.

## 7. הסכמה
- ההחלטה בין הגדלת C1/I2 בתוך DD ≤25% לבין venue חדש היא של נדב. היא כרוכה בכסף ובהרשמה. **אני מסכים.**
