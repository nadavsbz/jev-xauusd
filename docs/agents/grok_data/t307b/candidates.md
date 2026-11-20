# t307b: מועמדים פחות מוכרים עם ראיה post-publication (Grok -> Claude)
תאריך: 20.11.2026 (שעון ישראל). מחבר: Grok Bot (המאסטרו). אין המלצת מסחר, ההחלטה של נדב.

## הקשר
- t307: #2 (Rebalancers SPY/IEF) נכשל ב-holdout (Sharpe 0.37, דעיכה מ-2023), ו-#3 (TOM) נכשל כבר ב-DEV. הלקח: אנומליות מדד מפורסמות ופשוטות דועכות.
- **אישוש עצמאי לכישלון #2 [OBSERVED]:** KruegerAlgorithms (2026) שחזרו את Harvey/Mazzoleni/Melone: ‎+6.95bp ליום ב-1990–2022 (t 2.85), אבל ב-holdout 2023–08.2026 רק ‎+3.17bp (t 0.60), וב-CFD אחרי עלויות ‎−13.9bp. זה תואם את מה ש-Claude מצא. https://kruegeralgorithms.com/en/research/forced-flows-second-round-pensions-cta-leveraged-etfs
- בבקשה הזו חיפשתי מנגנון מבני (flow כפוי, fixing, rebalancing של מדד, הנפקה), עם עדיפות ל-FX, זהב ונפט ב-ECN CFD ואחר כך ETF ב-Alpaca. לכל מועמד יש תשובה מפורשת לשאלה: האם עבד **אחרי** הפרסום?
- לא חוזר על אף אחד מ-12 המועמדים של t307. מועמד A1 קרוב ל-t307 #1 (Krohn et al., חלון Tokyo) אבל צר יותר (ימי gotobi בלבד); הקורלציה ל-#1 מצוינת שם.

## תגיות
- **VERIFIED** = נקרא בטקסט המקור (PDF שהורד ל-/workspace/t307b/src וחולץ ב-pdftotext).
- **OBSERVED** = מקור משני (בלוג מתרגל או מחקר עצמאי לא מבוקר, תקציר) שלא אומת מול טבלת המקור.
- **ASSUMED** = הערכה שלי. **UNKNOWN** = לא נמצא.
- **אזהרת מקור:** חלק גדול מהראיות שאחרי הפרסום מגיעות מבלוגים של מתרגלים (KruegerAlgorithms, Liquidity Hunters, Spectra Markets, Quantseeker, ohlcv.io, devpost). אף אחד מהם לא עבר ביקורת עמיתים. ל-KruegerAlgorithms יש מוצר מסחרי ב-MQL5 שמבוסס בדיוק על A1 ו-A2, כלומר ניגוד עניינים. לכן כל המספרים שלהם מתויגים OBSERVED בלבד.
- סינון חובה (לא רוכך): עלות תוך-יומית ≤0.02% לצד; swap ≤~5%/שנה; אין קורלציה ל-C1 (crypto trend H6) או ל-I2 (Nasdaq open intraday momentum); בלי grid או martingale; 1–3 עסקאות ביום לכל היותר; ראיה מאחרי 2010.

## טבלת סיכום
| # | מועמד | מקור עיקרי | נכס | ראיה post-publication | ציון |
|---|---|---|---|---|---|
| A1 | Gotobi / Tokyo-fix USDJPY | Ito & Yamada 2017 (NBER w22820); Bessho, Sugimoto, Suzuki 2023 (arXiv 2301.13204) | USDJPY (ECN) | **כן, חלקית** [OBSERVED]: Krueger, ticks אמיתיים 04.2023–06.2026, ‎+4.5bp לעסקה, t 2.7 | **4** |
| A2 | Index Event Day: short FTSE 100 לתוך ה-closing auction | KruegerAlgorithms 2026 (מתרגל); מנגנון: Mase 2007 | UK100 CFD | **כן** [OBSERVED]: holdout 2023–06.2026, ‎+11.5bp נטו, t 3.9, 27 ימים | **3** |
| A3 | FOMC-day short USD | Mueller, Tahbaz-Salehi, Vedolin, JF 2017 | סל G10 מול USD (ECN) | **כנראה כן, לא מבודד** [OBSERVED]: Quantseeker 1992–2025 | **3** |
| A4 | End-of-Month Treasury (index extension) | Hartley & Schwarz 2019 (SSRN 3440417) | TLT/IEF (Alpaca) | **מעורב** [OBSERVED]: חיובי ב-futures מ-2010; holdout של TLT ב-10.2024–10.2026 שלילי (Sharpe −0.26) | **3** |
| A5 | Month-end equity-hedge flow ל-4pm fix | Melvin & Prins, JFM 2015 | EUR/GBP/AUD/CAD מול USD | **לא, דעך** [OBSERVED]: Donnelly 2022, Krueger, YuRa | **2** |
| A6 | Treasury Auction Cycle | Lou, Yan, Zhang, RFS 2013 | IEF/TLT (Alpaca) | **דעך** [VERIFIED]: Fleming, Liu, Nguyen, NY Fed 2026: נחלש בבירור ב-2015–2024 | **2** |
| A7 | EIA crude inventory intraday momentum | Wen, Indriawan, Lien, Xu, Energy J. 2023; Alturki & Kurov, JFM 2022 | WTI CFD | **לא** [OBSERVED]: Krueger 2015–2022, שני הכיוונים מפסידים | **1** |
| A8 | Gold overnight vs day / reopen drift | Blose, Gondhalekar, Kort, JEF 2018 | XAUUSD | **לא** [OBSERVED]: Liquidity Hunters 2022–2026; ה-reopen drift הוא בעיקר carry, ש-swap מוחק | **1** |

**המלצה (top 3 לבדיקה):** A1 Gotobi, A2 FTSE event day, A3 FOMC-USD. A4 רביעי, כתוספת זולה על נתוני Yahoo.
**שורה תחתונה כנה:** כל המועמדים שעוברים (A1–A4) קטנים. המתרגלים עצמם מעריכים את A2 בכ-0.8%/שנה על ה-notional ואת A1 ב-3–5bp לעסקה. אלה אבני בניין עם קורלציה נמוכה ולא מנוע של "עשרות אחוזים בחודש". **בזהב ובנפט לא מצאתי מועמד מבני שעבר post-publication:** כל הנתיבים שבדקתי (fix, overnight, EIA, roll, BCOM) מתועדים כדעיכה או כחוסר edge.

---

## A1. Gotobi / Tokyo-fix USDJPY — ציון 4
1. **מקור:** Ito, T., Yamada, M. (2016/2017). "Puzzles in the Tokyo Fixing in the Forex Market: Order Imbalances and Biased Pricing by Banks". NBER WP 22820 (גרסת כתב עת 2017, JIMF [OBSERVED]). https://www.nber.org/system/files/working_papers/w22820/w22820.pdf ; Bessho, H., Sugimoto, T., Suzuki, T. (2023). "Forex Trading Strategy That Might Be Executed Due to the Popularity of Gotobi Anomaly". arXiv 2301.13204. https://arxiv.org/abs/2301.13204
2. **מנגנון [VERIFIED]:** יבואנים יפנים משלמים ב-USD לפי ה-TTM שנקבע ב-9:55 JST. הביקוש מתרכז בימי gotobi (5, 10, 15, 20, 25, 30) ובסוף החודש. הבנקים קונים USD מראש (cover), ולכן USDJPY עולה לקראת 9:55 ויורד מיד אחריו. Ito-Yamada: order imbalance עקבי לטובת USD, ומחיר "hump-shaped" שמתהפך אחרי ה-fix. מדגם 05.01.2006–31.12.2013, ו-dummy של "5th and 10th days" מובהק בכל המפרטים.
3. **כללים:**
   - (a) **Bessho et al. [VERIFIED]:** בימי gotobi, long USDJPY ב-3:00 JST ויציאה ב-9:55 JST. 2018–2020, נתוני EBS, אחרי spread: N=185, PF=1.46, W=0.60. בימים שאינם gotobi אותו כלל נותן PF=0.51.
   - (b) **ההיפוך [VERIFIED]:** short מ-9:55 עד 12:00 JST בימי gotobi שבהם ה"אנומליה התרחשה" (עלייה לפני ה-fix, מידע שזמין ב-9:55): N=113, PF=2.09, W=0.57.
   - (c) **גרסת Krueger ל-forward test [OBSERVED]:** בימי gotobi, long לתוך ה-fix ואחר כך short עד "late morning". בסוף החודש short מה-fix עד late morning. בחגים יפניים שחלים באמצע השבוע short בבוקר עד שעת ה-fix. הזמנים המדויקים לא פורסמו (נשמרו ב-SHA).
   - **הצעת PREREG שלנו [ASSUMED]:** כניסה ב-7:55 JST (22:55 UTC, אחרי ה-rollover, כך שאין swap) ויציאה בדיוק ב-9:55:00 JST. Krueger: דקה אחת איחור מורידה את התוצאה מ-‎+4.5 ל-‎+1.9bp [OBSERVED]. היפוך אופציונלי מ-9:55 עד 11:00 JST. גודל: סיכון קבוע של 0.25–0.5% מה-equity לעסקה, עם stop. timeframe: M1/tick.
4. **ביצועים מדווחים:**
   - Bessho: PF 1.46 ו-W 0.60 (2018–2020) [VERIFIED]. Sharpe, CAGR ו-MDD: UNKNOWN (מוצגים בגרפים בלבד).
   - Krueger [OBSERVED]: ב-search 2015–2022 gotobi n 573, ‎+3.35bp נטו (1.6 pips RT), t 3.0; סוף חודש n 96, ‎+4.35bp, t 4.9. Spread חציוני ב-9:55 על ticks אמיתיים: 0.3 pips.
5. **post-publication:** **כן, חלקית.**
   - Ito-Yamada פורסם ב-2016/17 ו-Bessho ב-2023. Krueger, על ticks אמיתיים מ-04.2023 עד 06.2026: gotobi n 225, ‎+4.5bp, t 2.7; סוף חודש n 38, ‎+5.1bp, t 1.8. forward מ-06.06.2026: gotobi n 22, ‎+5.3bp [OBSERVED].
   - אזהרות: אחרי תיקון גלובלי על 19 מועמדים q=0.13, כלומר עבר מקומית ולא גלובלית. כלל סוף החודש תלוי בכמה חודשים בודדים (בלי חמשת הטובים t 0.6) [OBSERVED].
6. **נתונים:** Dukascopy USDJPY tick/M1. לוח חגים יפני (Cabinet Office) ולוח gotobi (כשה-5/10/... נופל בסופ"ש או בחג, התשלום זז ליום העסקים הקודם [ASSUMED, לאמת]).
7. **קורלציה:** C1 ≈ 0; I2 ≈ 0 [ASSUMED]. **מול t307 #1 (Krohn, חלון Tokyo): חיובית, ~0.3–0.5 [ASSUMED]**, כי זה תת-קבוצה של אותו flow. מומלץ לבדוק אותו כ-overlay/filter ל-#1 ולא כאסטרטגיה בלתי תלויה.
8. **דעיכה:** נמוכה-בינונית. המנגנון הוא מנהג עסקי (Goto-barai) ו-cover של בנקים, ולא arbitrage פיננסי. סיכונים: התערבויות MoF; גודל ה-edge (3–5bp) קרוב לעלות; תלות בתזמון לשנייה.
9. **ציון 4:** הראיה הכי טובה שמצאתי למנגנון מבני ב-FX, עם OOS post-publication על ticks. מוריד: edge קטן, מקור ה-post-pub הוא מתרגל עם מוצר מסחרי, וחפיפה ל-#1.

## A2. Index Event Day: short FTSE 100 לתוך ה-closing auction — ציון 3
1. **מקור:** KruegerAlgorithms (29.09.2026, addendum 06.10.2026). "Index Event Days: the FTSE Falls Into the Auction Print, and It Held Out of Sample". https://kruegeralgorithms.com/en/research/index-rebalancing-closing-auction . מנגנון אקדמי: Mase (2007). "The Impact of Changes in the FTSE 100 Index". *Financial Review* (doi 10.1111/j.1540-6288.2007.00179.x) (price pressure והיפוך סביב שינויי הרכב) [OBSERVED, תקציר]; Comerton-Forde & Aramian, SSRN 6745718 (closing auction ב-LSE: imbalance גבוה בימי rebalancing) [OBSERVED, תקציר].
2. **מנגנון:** קרנות פסיביות חייבות לבצע את שינוי ההרכב ב-closing auction שלפני ה-effective date. המניות שיוצאות נמכרות לתוך ה-print, והמניות שנכנסות עוד לא במדד, ולכן המדד נלחץ כלפי מטה [OBSERVED].
3. **כללים [OBSERVED]:**
   - ימי אירוע: יום ה-closing auction שלפני ה-effective date של ה-review הרבעוני של FTSE 100 ו-STOXX (יום שישי השלישי במרץ, יוני, ספטמבר ודצמבר), ושל ה-MSCI reviews (לפי הודעות MSCI).
   - כניסה: short UK100 בשעה האחרונה של המסחר. כניסה 15–60 דקות לפני ה-close נתנה ‎+9.9 עד ‎+12.3bp ב-holdout.
   - יציאה: **אחרי ה-auction print** (~16:35 לונדון). יציאה דקה לפני ה-close נותנת רק ‎+4.0bp.
   - תדירות: ~8 עסקאות בשנה. גודל: אחיד; Krueger לא פרסמו את פרמטרי הביצוע שלהם.
4. **ביצועים [OBSERVED]:** עלות 1.5 נקודות RT. Search 2015–2022: n 63, ‎+8.3bp נטו, t 2.3, 8/8 שנים חיוביות. **Holdout 01.2023–06.2026: n 27, ‎+11.5bp, t 3.9**, 81% ימים חיוביים, 4/4 שנים. Ticks אמיתיים: ‎+11.9bp. ימי placebo: ‎+0.05bp. q=0.002 על 59 מבחני holdout. Krueger מעריכים "בערך 0.8% לשנה על ה-notional". Sharpe, CAGR ו-MDD: UNKNOWN.
5. **post-publication:** הממצא פורסם ב-09.2026, אז ה-holdout שלהם הוא OOS של המחקר עצמו ולא post-publication אמיתי. ה-post-pub היחיד: שני ימי אירוע עם ticks אחרי סוף ה-holdout, ‎−8.7 ו-‎+13.3bp [OBSERVED]. **אזהרה:** "תאום" באוסטרליה (AUS200) היה חזק יותר ב-search (‎+12.6bp) ונכשל ב-holdout (‎−3.5bp) [OBSERVED]. ראיות ה-index effect האקדמיות הן לפני 2010 ומראות דעיכה של אפקט ההכללה. Krueger גם מצאו "S&P 500 additions: no edge".
6. **נתונים:** Dukascopy UK100 (GBR.IDX) M1, ולוח תאריכים מהודעות FTSE Russell ו-MSCI. **צריך לבדוק שה-UK100 CFD של EGlobal/RoboForex משקף את ה-auction print** (Krueger: CFD של broker שלהם כן) [UNKNOWN אצלנו]. אירועי forward קרובים: MSCI ב-30.11.2026, FTSE/STOXX ב-18.12.2026 [OBSERVED].
7. **קורלציה:** C1 ≈ 0; I2 ≈ 0–0.05 [ASSUMED]: מדד אחר, סוף יום, 8 ימים בשנה.
8. **דעיכה:** בינונית. המנגנון בעל קיבולת (טריליונים פסיביים), אבל ה-print נסחר על ידי arbitrageurs מתוחכמים, n קטן, ושני ימים ב-2026 נושאים 30% מהסכום.
9. **ציון 3:** OOS נקי ב-holdout עם ticks, מנגנון ברור. מוריד: מקור יחיד ולא אקדמי עם ניגוד עניינים, n=27, תשואה שנתית זעירה, ושאלת הביצוע ב-print אצל ה-broker שלנו.

## A3. FOMC-day short USD — ציון 3
1. **מקור:** Mueller, P., Tahbaz-Salehi, A., Vedolin, A. (2017). "Exchange Rates and Monetary Policy Uncertainty". *JF* 72(3):1213–1252. https://doi.org/10.1111/jofi.12499 ; גרסה פתוחה (2014): https://paoloporchia.github.io/download/2014_10_18_PolicyUncertainty_MainFile.pdf
2. **מנגנון [VERIFIED]:** פרמיה על אי-ודאות במדיניות המוניטרית אצל מתווכים מוגבלי סיכון. התשואה פרושה על כל יום ההודעה, לפני ההודעה ואחריה.
3. **כללים:**
   - **[VERIFIED, מבנה]:** portfolio DOL = ממוצע 5 תיקים ממוינים לפי interest differential, long מטבעות מול USD, ביום הודעת FOMC המתוזמנת (8 בשנה). גרסה משופרת: רק מטבעות עם differential חיובי מול USD (pf5).
   - **ליישום [ASSUMED]:** long שווה-משקל EURUSD, GBPUSD, AUDUSD, NZDUSD, USDCAD (הפוך), USDCHF (הפוך), USDJPY (הפוך) מ-17:00 ET של היום שלפני ההודעה עד 17:00 ET ביום ההודעה. חציית rollover אחת, 8 פעמים בשנה, כך שה-swap זניח. timeframe D1/H1.
4. **ביצועים [VERIFIED, גרסת 2014, Table 2–3, 01.1994–01.2011]:**
   - DOL בימי FOMC: ‎9.64bp ליום (t 2.31), Sharpe 0.559 (מותאם ל-8 ימים בשנה). בימים אחרים: ‎0.52bp, Sharpe 0.219.
   - pf5 (high-rate): ‎14.44bp, Sharpe 0.627. Developed בלבד: DOL ‎10.45bp, Sharpe 0.459.
   - בגרסת JF הסופית (1994–2013): Sharpe 0.51 ו-0.93 לגרסה המשופרת [OBSERVED, מצוטט ב-Parity; לא קראתי את הגרסה הסופית, paywall].
   - CAGR ו-MDD: UNKNOWN. **הכל לפני עלויות.**
5. **post-publication:** **כנראה כן, אבל לא מבודד.** Quantseeker (12.2025, נתוני 01.1992–12.2025): כל מטבעות G10 התחזקו מול USD בימי FOMC בממוצע, והאפקט הוא "כמעט כולו פוסט-2000". אין פיצול נפרד לתקופה שאחרי 2014–2017 [OBSERVED]. אין מבחן OOS שעבר ביקורת עמיתים [OBSERVED, Parity]. **מסקנה: התקופה 2014–2026 היא OOS שאנחנו צריכים להריץ בעצמנו.** בנוסף, Krueger מצאו בתוך היום "macro events FOMC: no edge", אבל על מדדים ולא על FX.
6. **נתונים:** Dukascopy FX M1/H1, לוח FOMC (federalreserve.gov).
7. **קורלציה:** C1 ~0.1; I2 ~0.1–0.2 [ASSUMED]. ימי FOMC נוטים ל-risk-on, ו-I2 עשוי להיות long באותם ימים.
8. **דעיכה:** בינונית. מנגנון של פרמיית סיכון ולא של flow, ולכן פחות רגיש ל-arbitrage, אבל n=8 בשנה ותלוי במחזור הריבית (חזק יותר בהקלות).
9. **ציון 3:** מאמר JF, נכסים זולים, 8 עסקאות בשנה וראיה עד 2025. מוריד: Sharpe ~0.5, n קטן, ואין OOS שפורסם בנפרד.

## A4. End-of-Month Treasury (index extension) — ציון 3
1. **מקור:** Hartley, J., Schwarz, K. (2019). "Predictable End-of-Month Treasury Returns". SSRN 3440417. https://www.kristaschwarz.com/EOM.pdf
2. **מנגנון [VERIFIED]:** מדדי האג"ח (Bloomberg Treasury) מאוזנים ביום המסחר האחרון בחודש ומוסיפים ניירות חדשים, ולכן ה-duration מתארך. חברות ביטוח, ובמיוחד ביטוח חיים, הן "large net buyers... on benchmark index rebalancing dates".
3. **כללים:** long ב-Treasury coupon ב-3 ימי המסחר האחרונים בחודש, יציאה ב-close של היום האחרון. ליישום [ASSUMED]: TLT או IEF ב-Alpaca, קנייה ב-close של T−3 ומכירה ב-close של יום המסחר האחרון. 12 סבבים בשנה, אפס swap.
4. **ביצועים [VERIFIED]:** 1990–2018: ה-10-year ב-3 הימים האחרונים נותן ‎0.25% לחודש (≈3% לשנה) excess, ו-Sharpe "around 1". ה-futures הארוכים ביותר נותנים מעל 3% לשנה. **"The estimates in the final period, from 2015-2018 are smaller... but they remain significant"**. MDD: UNKNOWN.
5. **post-publication (מעורב):**
   - ohlcv.io: ב-Treasury futures מ-06.2010, בשלושת ימי המסחר האחרונים בחודש ZN ‎+5.2bp ליום (t 4.1) ו-ZF ‎+3.8bp (t 4.7) [OBSERVED].
   - devpost "Treasury Hunt" (10.2026): TLT, 3 ימים, נטו 2bp לצד, 31.07.2002–30.09.2024: 4.0% לשנה, vol 5.1%, Sharpe 0.78, MDD ‎−12.4%. **holdout 01.10.2024–02.10.2026: Sharpe ‎−0.26** [OBSERVED].
   - שני המקורות של מתרגלים חופפים בחלקם לתקופת המאמר. ה-post-pub הנקי היחיד (24 חודשים) שלילי.
6. **נתונים:** Yahoo TLT, IEF (2002+), ^IRX ל-cash.
7. **קורלציה:** C1 ≈ 0; I2 ≈ 0 עד −0.1 [ASSUMED]. **הערה:** קשור קלנדרית ל-t307 #3 (TOM, נכשל ב-DEV), אבל זה נכס אחר ומנגנון אחר (index extension ולא settlement).
8. **דעיכה:** בינונית-גבוהה. המחברים עצמם מזהירים מהיחלשות אחרי 2015, ו-holdout שלילי. מנגד, עליית החלק הפסיבי מחזקת את המנגנון לפי המחברים.
9. **ציון 3:** מנגנון מתועד עם כמויות, זול לבדוק (Yahoo יומי, שעה של עבודה). מוריד: post-pub שלילי בשנתיים האחרונות ו-beta לאג"ח.

## A5. Month-end equity-hedge flow ל-4pm fix — ציון 2
1. **מקור:** Melvin, M., Prins, J. (2015). "Equity hedging and exchange rates at the London 4p.m. fix". *JFM* 22:50–72. גרסה פתוחה (ECB 2013): https://www.ecb.europa.eu/events/pdf/conferences/131216/Third_FX_Workshop_MELVIN_PRINS_Equity%20hedging%20and%20exchange%20rates%20Nov%202013.pdf
2. **כללים:**
   - **[VERIFIED, מנגנון]:** ביום העסקים האחרון בחודש, מנהלי קרנות מתאימים hedge לפי שינוי השווי, ולכן מטבע שהמניות שלו עלו נמכר לקראת 16:00 לונדון.
   - **כלל מתרגל [OBSERVED, Donnelly/Spectra 2022]:** אם S&P 500 עלה ביותר מ-2.5% בחודש, למכור USD ב-7:00 NY ולצאת ב-11:00 NY (ה-fix). אם ירד ביותר מ-2.5%, לקנות USD. ב-USDJPY הסימן הפוך.
3. **ביצועים [VERIFIED]:** 04.2004–12.2012: עליית מניות של 10% → פיחות של 14bp בשעה שלפני ה-fix. ביום סוף חודש 72% מהתנועה מתהפך עד הצהריים למחרת. Sharpe, CAGR ו-MDD: UNKNOWN.
4. **post-publication:** **לא, דעך.**
   - Donnelly (Spectra, 07.2022): ה-hit rate עמד על 60–70% מ-2005, אבל המודל "has passed its expiry date", כי ה-hedgers מפזרים את ה-flow על כמה ימים או עוברים ל-VWAP של 24–48 שעות. ייתכן חריג ב-USDJPY ההפוך [OBSERVED].
   - YuRa (2017–2022): 4 מתוך 48 הגדרות רווחיות [OBSERVED].
   - Krueger: סל month-end אחרי ה-fix ‎−2.5bp ברוטו, בכיוון הלא נכון [OBSERVED].
   - Wang et al. (MPRA 112909): ה-hedging מפוזר לאורך החודש [OBSERVED].
5. **נתונים:** Dukascopy, Yahoo ^GSPC. **קורלציה:** C1 ≈ 0; I2 ~0.1 [ASSUMED]. **דעיכה:** מתועדת.
6. **ציון 2:** מנגנון קלאסי שדעך. שווה בדיקה רק כ-PREREG צר על USDJPY ההפוך.

## A6. Treasury Auction Cycle — ציון 2
1. **מקור:** Lou, D., Yan, H., Zhang, J. (2013). "Anticipated and Repeated Shocks in Liquid Markets". *RFS* 26(8):1891–1912. post-pub: Fleming, M., Liu, W., Nguyen, G. (2026). "Intraday Price Pressure and Order Flow Around U.S. Treasury Auctions". NY Fed SR 1188. https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1188.pdf
2. **כללים [OBSERVED, ohlcv.io שמצטט את LYZ]:** short ב-2Y מול תיק duration-matched ב-10 הימים שלפני כל מכרז, והיפוך ב-10 הימים שאחריו. ליישום: IEF/TLT מול SHY ב-Alpaca לפי לוח המכרזים של Treasury.
3. **ביצועים:** LYZ 1980–06.2008: Sharpe 1.08, ו-1.44 ב-1998–2008 [OBSERVED].
4. **post-publication:** **דעך** [VERIFIED, Fleming et al. 2026]:
   - האפקט התוך-יומי עומד על 0.7–1.2bp בתשואה וירד ב-0.75bp בין 2007–2014 ל-2015–2024.
   - האפקט של 10 ימים "most pronounced during 2007–2014 and weakens markedly in 2015–2024".
   - ohlcv.io (futures מ-2010): ZT +4.0bp gap (t 2.8), אבל מעורבב עם אפקט סוף החודש (A4) [OBSERVED].
5. **נתונים:** Yahoo IEF/TLT/SHY, TreasuryDirect auction calendar. **קורלציה:** C1 ≈ 0; I2 ≈ 0 [ASSUMED]. **דעיכה:** מתועדת (קרנות השקעה קונות ישירות במכרז).
6. **ציון 2:** דעיכה מתועדת בידי הפדרל ריזרב עצמו, וחפיפה עם A4.

## A7. EIA crude inventory intraday momentum (WTI) — ציון 1
1. **מקור:** Wen, Z., Indriawan, I., Lien, D., Xu, Y. (2023). "Intraday Return Predictability in the Crude Oil Market: The Role of EIA Inventory Announcements". *Energy Journal* 44(4). https://doi.org/10.5547/01956574.44.4.zwen (paywall, תקציר בלבד); Alturki, S., Kurov, A. (2022). "Market inefficiencies surrounding energy announcements". *JFM* 42(1):172–188. SSRN 3747330.
2. **כללים [VERIFIED, תקציר Wen et al.]:** ביום EIA (רביעי 10:30 ET), התשואה בחצי השעה השלישית מנבאת חיובית את התשואה בחצי השעה האחרונה, ולכן נכנסים בכיוון שלה לחצי השעה האחרונה. מספרים: UNKNOWN (paywall).
3. **post-publication:** **לא** [OBSERVED]: Krueger (PREREG 21.10.2026, 2015–2022, 331 דוחות, WTI CFD): ללכת עם הכיוון אחרי 5 דקות נותן ‎−19.27bp נטו (t −1.57), וגם reversal מפסיד. ברוטו ‎−2.6 עד ‎−2.9bp, ועלות של ~11.8bp RT. (זה בדק תגובה ראשונית ולא בדיוק את כלל "חצי שעה 3 → אחרונה".)
4. **עלות:** WTI CFD ~0.06 USD RT ≈ 8–12bp, **נכשל בסינון של 0.02% לצד** [ASSUMED/OBSERVED].
5. **נתונים:** Dukascopy LIGHT.CMDUSD M1, לוח EIA. **קורלציה:** C1 ≈ 0; I2 ~0.1–0.2 (intraday momentum style) [ASSUMED]. **דעיכה:** UNKNOWN/גבוהה.
6. **ציון 1:** נכשל בעלות, ואין OOS חיובי.

## A8. Gold overnight vs day / reopen drift — ציון 1
1. **מקור:** Blose, L.E., Gondhalekar, V., Kort, A. (2018). "Overnight versus day returns in gold and gold related assets". *JEF* 42(3):526–549; Blose & Gondhalekar (2014), *Applied Economics Letters*.
2. **ממצא מקורי [VERIFIED, תקציר]:** COMEX gold 1985–2012: תשואת הלילה חיובית מובהקת ותשואת היום שלילית, "economically important even with transaction costs". התקציר של 2014 עצמו מציין: "The asymmetry has weakened substantially over the years".
3. **כללים:** long בלילה (17:00 עד 8:20 NY) ו-flat או short בסשן NY. וריאנט: long ב-16:30/16:55 עד 19:00 NY (reopen).
4. **post-publication:** **לא** [OBSERVED, Liquidity Hunters 10.2026, Dukascopy 2022–2026]:
   - סשן NY ‎+0.8bp, לא שונה מהלילה. short על סשן NY: ‎−4.6%/שנה. long overnight + short day: Sharpe 0.34, MDD ‎−36.2%.
   - ה-reopen drift (‎+3.3bp, t 3.9) הוא בחלקו carry roll: ב-CFD עם swap של 1.5bp ללילה נשאר 1.2%/שנה, Sharpe 0.26.
   - Krueger: חלונות LBMA/COMEX/Shanghai ≤1.4bp ברוטו מול ~3bp עלות [OBSERVED].
   - Morgan Stanley (FIA 2026): שנה אחת שבה כמעט כל רווחי הזהב נרשמו מחוץ ל-pit hours. זה רגים ולא כלל [OBSERVED].
5. **נתונים:** Dukascopy XAUUSD M1. **קורלציה:** C1 ~0.1; I2 ≈ 0 [ASSUMED]. **דעיכה:** מתועדת.
6. **ציון 1:** מכוסה כאן כי זהב בעדיפות ראשונה. התשובה הכנה: לא נמצא edge זמני-מבני בזהב שעבר post-publication. **הקשר ל-BD:** הממצא של Liquidity Hunters שהסשן של 9:00 NY הוא בעל ה-range הגדול ביותר (‎$21.45 חציון ב-2025–2026 לעומת ‎$8.70 ב-2022–2024) רלוונטי לניהול סיכון של BD ולא לאסטרטגיה חדשה [OBSERVED].

---
## נספח: נבדקו ונדחו (לא לבדוק)
| רעיון | מקור | למה נדחה |
|---|---|---|
| Front-running Goldman/GSCI roll (נפט) | Mou 2011 (SSRN 1716841); Dubois & Maréchal 2021; Irwin, Sanders, Yan (AEPP 2022) | **[VERIFIED]** Dubois-Maréchal: ה-front-run "does not generate abnormal profits... after (reasonable) transaction costs". Irwin et al.: "Spread impacts disappear in the post-financialization period (2012-2019)". בנוסף צריך calendar spread, שאי אפשר לבצע ב-CFD |
| BCOM/GSCI January rebalancing (זהב) | event study 2006–2021, 289 rebalancings | אין השפעה מובהקת על המחיר [OBSERVED, תקציר] |
| LBMA gold fix / London 4pm fix daily | Krueger fixings study 2026 | London fix ‎+0.69bp ברוטו מול 1.15bp עלות; זהב ≤1.4bp מול 3bp [OBSERVED] |
| Vol-control funds sell into close | Krueger 2026 | שלילי אחרי ימי ירידה ואפס אחרי ימי עלייה [OBSERVED] |
| Leveraged-ETF rebalancing (סוף יום) | survey "The market impact of leveraged ETFs", QFE 2024 (doi 10.3934/QFE.2024031) | ההשפעה הכלכלית על המחיר "insignificant" [OBSERVED, תקציר]; קורלציה אפשרית ל-I2/last-30-min (t307 #6) |
| First trading day of quarter, S&P last hour | Krueger 2026 | n 13 ב-holdout (‎+15bp, t 2.26) קטן מדי; מדד ארה"ב, קרוב ל-I2 [OBSERVED] |

## הצעת סדר עבודה ל-Claude (PREREG, לא מחייב)
1. **A1 Gotobi** על אותם נתוני Dukascopy USDJPY שכבר נטענו ל-#1 Krohn. לבדוק אותו גם כ-filter על חלון Tokyo של #1. DEV 2015–2021, holdout מ-2022. gate: נטו > 2× spread מדוד ב-ECN.
2. **A3 FOMC-USD**: DEV 2000–2013 (תקופת המאמר), holdout 2014–2026 (post-publication אמיתי).
3. **A2 FTSE event day**: לאמת תאריכים מ-FTSE Russell ו-MSCI. ה-holdout 2023–2026 כבר "נצרך" על ידי Krueger, ולכן אצלנו רק forward (30.11.2026 ו-18.12.2026).
4. **A4 TLT EOM**: מבחן יומי של שעה על Yahoo. holdout 2019–2026 (אחרי המאמר).
- כל הבדיקות נספרות ב-Holm/DSR הכלל-חברתי.

## הערות integrity
- לא הומצאו מספרים. VERIFIED = נקרא ב-PDF שב-/workspace/t307b/src (gotobi_arxiv, ito_yamada, mtv, melvin_prins, hartley_schwarz, fleming_nyfed, dubois_marechal, irwin), או בתקציר המקור (Blose; Wen et al.).
- גרסאות סופיות ב-JF/JFM/RFS/Energy J. מאחורי paywall לא נרכשו. השתמשתי בגרסאות פתוחות, ולכן המספרים עשויים להיות שונים מעט מהגרסה הסופית.
- r/algotrading לא שימש.
- אין המלצת מסחר, ההחלטה של נדב.
