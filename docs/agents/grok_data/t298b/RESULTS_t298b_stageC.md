# RESULTS t298b, שלב C: קבוצת הטלגרם של Ramil (TopTargetForex). Grok, 19.11.2026
**מקור:** איסוף לקריאה בלבד מהסשן של נדב.
- הבסיס: /workspace/algotrade/telegram (‏12,985 הודעות, 27.10.2025–26.10.2026).
- **רענון read-only היום:** ‏468 הודעות חדשות, 27.10–19.11.2026 (GetHistory בלבד; לא נשלח, לא הוגב, לא הצטרפנו, לא שונה כלום) → tg/refresh_messages.jsonl.
**מגבלה:** הדיון של החברים לפני 6.4.2026 כוסה רק חלקית (מגבלת batch). לפני כן נאספו רק הודעות של רמיל ומסמכים.
**ציטוטים:** t298b_stageC_quotes.csv (‏52 ציטוטים: תאריך UTC, כינוי, נושא, סוג כלל). בלי מזהים ובלי פרטים אישיים מעבר לכינוי.

## 1. קבצי הגדרות וגרסאות
- 117 קבצי ‎.set ב-set_files_summary.csv.
- **הסטים הרשמיים של רמיל ל-BD (‏14.1.2026):** ‏M5, ‏2/3 ספרות, ‏MT4/MT5, ‏Lot 0.01, ‏Autolot false, ‏Martin 1.4, ‏MaxLot 5, ‏20/20 עסקאות, ‏Distance 800/8000, ‏Stoch=true. מיועדים ל-50k סנט ל-0.01, ‏Buy בלבד בטרנד.
- **CasperIT** (פורסמו ע"י רמיל, 13.2.2026): ‏Safe/Hybrid/Aggressive 50k. מכפיל 1.25/1.35/1.5, ‏MaxLot 1/1.5/2, ‏6/8/10 עסקאות, ‏Autolot true.
- **Lars:** ‏v1 (22.8.2025) ו-v2 (6.9.2025), צילום בלבד: ‏0.05 ל-‏$7.5k, ‏1.35, ‏MaxLot 2, ‏10/10, ‏TP 200, ‏Trail 600/100, שעות 2–21. אין לו עדכוני ביצועים על BD אחרי 10.2025, וגם לא מ-7–9.2026.
- **11.2026:** רמיל: "now i use ea at both trade direction full auto" (‏12.11). הקבוצה נפתחה מחדש ב-11.11 אחרי נעילה. אין סט חדש.

## 2. כללי ניהול: מכני מול שיקול דעת
### מכני (אפשר לנסח ככלל ולבדוק)
| # | כלל | מקור (ציטוט מתוארך) |
|---|---|---|
| M1 | **לוט לפי הון:** אוטומטי בזהב 0.01 ל-50k סנט (‏$500), או 30k ללא פחות מזה. חצי-ידני 0.01 ל-$1k–2k. במדריך: ‏$3k/$5k/$10k | ‏@ForexMechanicEA ‏2025-12-04, ‏2026-01-20, ‏2026-06-17 |
| M2 | מכפיל 1.3–1.5, ‏Autolot false | ‏@ForexMechanicEA ‏2026-08-26 + מדריך |
| M3 | **כיוון אחד בלבד בזהב אוטומטי ("allow only buy")**, עם הטרנד. "Below yellow line it is a sell", כשהקו הצהוב = BB אמצעי = MA200 | ‏@ForexMechanicEA ‏2026-01-20, ‏2026-04-22, ‏2026-06-24 |
| M4 | **בחוץ לפני FOMC/NFP** ("even if you run full auto you need to be out of market"). ‏PAUSE שעה לפני ושעה אחרי חדשות אדומות | ‏@ForexMechanicEA ‏2025-12-30, ‏2026-06-18, ‏2026-07-29 |
| M5 | בלי פוזיציות בסוף שבוע; ‏BTC בלי סשן אסיה (8–20) | ‏@ForexMechanicEA ‏2026-01-17, ‏2026-07-31, ‏2026-08-28; ‏@Jens_P_B ‏2026-04-10 |
| M6 | **Equity stop על גרף נפרד:** ‏15% (‏@Golden_CasperIT ‏2026-03-11, ‏2026-06-10), ‏10–20% בחשבון גדול (רמיל ‏2026-04-22) | ‏@ForexMechanicEA ‏2026-06-10, ‏2026-08-04 |
| M7 | חיתוך אחרי 3 רמות ("after 3 levels you will have to think of cutting all") | ‏@ForexMechanicEA ‏2026-06-30, ‏2026-07-23 |
| M8 | משיכת רווחים קבועה ("Always withdraw profits") | ‏@ForexMechanicEA ‏2026-06-24, ‏2026-07-14 |
| M9 | עצירה יומית ב-max DD, וסגירת הכול בלילה (22:00) | ‏@Jens_P_B ‏2026-04-28, ‏2026-08-07 |

### שיקול דעת (לא ניתן לבדיקה מכנית כמו שהוא)
- חיתוך כש-WAT מחליף צבע, או כשהנקודות/הנרות מתהפכים ("I don't use a SL I cut when market changes", ‏2026-08-08). WAT ו-Turncoat הם אינדיקטורים קנייניים.
- "Do not sell near support". ‏PAUSE ליד התנגדות. "too unsure now let's stop".
- הכניסות של רמיל ידניות (‏NEW CYCLE אדום). התוצאות שלו לא מייצגות BD אוטומטי.

## 3. מה עשו ב-7–8.2026 ובימי קריסה אחרים
- **29.7 (FOMC):** רמיל סגר בהפסד קטן כש-WAT התהפך ויצא לפני ההודעה ("Ok we are done now FOMC will probably cause a lot of volatility!"). ערב: "I have warned this morning about upcoming FOMC". אותו יום: ‏@FxHoudini "BD blown my 3k".
- **31.7:** "I think we are done for July, not worth it to risk more money!!". גם: "market has changed especially in gold with this war in Iran".
- **5–7.8 (גאופוליטיקה ואז NFP):**
  - 5.8, רמיל: "will not trade until after news".
  - 6.8, רמיל: "WAT paint green we should consider cutting… I close all"; "I took one last one too near support… cost me a huge stop". לפי ה-OCR: כ-‎−$10.8k.
  - 7.8, רמיל: "Be careful NFP today!", ואז "Done for the week".
  - **כל דמו ה-Hamster** של ‏@tradewithhappie התרסקו: "its due to geo political news from 5th aug it carrying dd, and today nfp finally blown".
  - ‏@guenther_huber: חשבון Trend Catcher התרסק.
- **10.8:** ה-copy trading של Ultima (EA החדשות של רמיל) קיבל margin call.
- **18.8 / 26–28.8:** חיתוכים ידניים, כ-‎−$3.4k ו-‎−$11.9k (OCR).
- **11.9:** רמיל: "I cut ouch!… Lots of damage, we will recover". כ-‎−$16.6k ביום אחד, כ-70% מרווח של חודש וחצי. ‏12.9: ‏@tradewithhappie "All profiles blown up".
- **הדפוס:** מי ששרד חתך באותו יום (ידנית) או לא החזיק פוזיציות לתוך FOMC/NFP. מי שהתרסק החזיק DD לתוך חדשות או סוף שבוע, או סחר נגד הטרנד (‏@davidsolomon100k ‏24.7: "I broke the rules… more than 7 Martingale levels… 70% drawdown").

## 4. משיכות
- רמיל חוזר על "Always withdraw profits" (‏24.6, ‏14.7, ‏30.7).
- ‏@tradewithhappie: משך את ההפקדה באותו יום (‏11.6).
- ‏@Golden_CasperIT: משיכת עודפים יומית/שבועית מותנית בגודל החשבון מול ה-DD הממוצע (‏17.6).
- ‏Lars (2025): חשבונות שמאופסים כל חודש עם משיכה.
- **אין נתוני משיכה מאומתים של אף אחד.**

## 5. מי שרד שנה ויותר
- **אף חבר לא הציג חשבון אמיתי מאומת של BD אוטומטי ששרד ≥12 חודשים**, כולל 7–9.2026.
- ‏@didikurnia: "Black Dragon - 1 Year" על **דמו** (‏27.4.2026), לפני הקריסות.
- רמיל: "EA Black Dragon still works well and is in the market for many years now. As you say it all depends on the trader's management!" (‏21.7). זו טענה בלי חשבון.
- הוותיקים (‏@Jens_P_B, ‏@Andre666666666, ‏@T_J1983) פעילים 10–11 חודשים. ‏Jens עבד עם SL, סגירה לילית ובלי סוף שבוע, ודיווח על פגיעות SL ו"overall still profit". ‏Andre: ‏equity protector ("6k dd are normal and for higher the equitity protector jumps in").
- ‏Lars: ‏myfxbook אמיתי 6–8.2025 בלבד (DD 47%). אין עדכון.
- **הערכה:** הדאטה תומך ב"שרידות = ניהול", לא ב"שרידות של סט".

## 6. השיקול שלי: המועמד הכי טוב לשיפור, ואיך לבדוק בלי כוונון על 2026
**מועמד 1 (מומלץ): M4, להיות בחוץ לפני FOMC/NFP**, ובגרסה הצרה: לא לפתוח סל חדש מ-X שעות לפני ההודעה, ולסגור/להשהות סלים פתוחים ב-T−1h.
- **למה הוא:**
  - (א) אפס או כמעט אפס פרמטרים. לוח שנה חיצוני, ו-1h הוא המספר של רמיל עצמו.
  - (ב) הסט החי (‏Lars, ‏Flag_Use_News=false) לא מכסה את זה. ‏base17 כן כולל מסנן חדשות, כך שזה פער ממשי בקובץ החי.
  - (ג) הקריסות הבולטות של 7–9.2026 בקבוצה קשורות לחדשות: ‏29.7 FOMC, ‏5–7.8 NFP וגאופוליטיקה, ‏11.9.
  - (ד) לא דורש אינדיקטור קנייני.
- **אזהרה:** ידוע לי מראש שהקריסות של 2026 הן ימי חדשות. לכן ההכרעה רק על holdout, ו-2026 לא משמש לבחירת הפרמטר.

**מועמד 2: M3, כיוון לפי צד MA200 ב-H4** (קנייה רק מעל, מכירה רק מתחת, לפתיחת סל חדש בלבד). זה הכלל המרכזי של רמיל ("Gold can kill any size account if you are against trend"). יש בו פרמטר (TF ו-MA), ולכן ‏MA200/H4 מקובע לפי הציטוט, בלי חיפוש.
**לא מומלצים לבדיקה ראשונה:**
- ‏M6 (equity stop): כבר קיים, ההגנה החיצונית של 15%.
- ‏M7 (חיתוך ב-3 רמות): משנה מהותית את הפרופיל, ונבדק בעקיפין ב-MaxPositions.
- ‏M1 (לוט): זו החלטת הקצאה של נדב, לא שיפור לוגיקה.

**תכנון הבדיקה (רישום נפרד לכל כלל, לפני ריצה):**
1. **ההגדרה קפואה מראש**, מתוך הציטוט:
   - FOMC/NFP מ-ForexFactory ההיסטורי, אירועי "high" של USD מסוג FOMC Statement / NFP בלבד.
   - חסימת פתיחה מ-T−60m עד T+60m. סלים פתוחים ב-T−60m: גרסה a = מושהים (PAUSE), גרסה b = נסגרים. שתיהן מוצהרות מראש ומדווחות שתיהן.
2. **DEV: ‏RF 2019–2023**, ‏base = הקובץ החי (‏bd_3digit_cal). משמש רק לאימות המימוש ולבחירה בין a ל-b לפי כלל שנכתב מראש: הגרסה עם CAGR/MDD טוב יותר ב-DEV.
3. **Holdout, פעם אחת:** ‏RF 2024–2025 + ‏EGlobal 11.2025–11.2026.
   - **עובר:** ‏MDD ב-holdout יורד ב-≥20% יחסי, הרווח לא יורד ביותר מ-10% יחסי, ומספר ימי ≤−8% לא עולה. זה נכון בשני חלקי ה-holdout בנפרד.
   - **נכשל:** כל השאר. בלי ניסיון שני עם פרמטר אחר.
4. **בקרת מזל:** אותו מספר שעות חסימה בזמנים אקראיים (‏placebo, ‏200 הגרלות). הכלל צריך להיות מעל אחוזון 95.
5. דורש טסטר. זה בתחום של Claude ובאישור נדב. לא שיניתי כלום ולא הרצתי.

אין המלצת מסחר. ההחלטה של נדב.
