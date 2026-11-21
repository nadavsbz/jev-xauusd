# t313: מנועי תשואה בינוניים בלי averaging (Grok -> Claude)
נכתב 20.11.2026 (שעון ישראל). מסלול: מחקר לקריאה בלבד. לא היו התחברויות, לא follow, לא subscribe ולא רכישות.

## הקשר ותנאי הסינון
- המטרה: 2–4% בחודש בכנות, equity DD של 25% לכל היותר. בלי grid, בלי martingale ובלי averaging. hard SL על כל עסקה, median hold של 15 דקות לפחות, עד ~3 עסקאות ביום, ובנטו מעלויות RoboForex ECN לפחות 10bp לעסקה בזהב או 4–5 pips ב-FX. בלי קורלציה ל-C1 (crypto trend H6) או ל-I2 (Nasdaq open momentum).
- לא חוזר על t307 או t307b. multi-asset TSMOM דרך ETF כבר הופיע ב-t307 #4. כאן נבדק רק ה-sleeve של FX ב-CFD (M7), והראיה שלו שלילית.
- תגיות: **VERIFIED** = קראתי את המספר במקור עצמו. **OBSERVED** = נגזר ישירות ממספרים במקור (חישוב פשוט שלי, והחישוב מוצג). **ASSUMED** = הנחה או הערכה שלי. **UNKNOWN** = לא נמצא.
- דילגתי על paywalls. לא המצאתי אף מספר. במקום שאין מספר כתוב UNKNOWN.

## שורה תחתונה (לקרוא קודם)
1. **[OBSERVED] בכל מקור שקראתי, אף כלל trend/breakout על מכשיר יחיד (זהב או זוג FX) עם hard SL לא מגיע ל-2–4% בחודש תחת DD של 25%.** במבחנים שפורסמו, יחס התשואה השנתית ל-maxDD יוצא בערך 0.3–1.2 (חישובים בכל פריט). ב-DD של 25% זה שווה בערך 0.6–2% בחודש. היוצא מן הכלל היחיד הוא M1 (Donchian H1 על זהב), ורק בחלון של שנתיים (2024–2026) שהיה קיצוני במגמות ובתנודתיות.
2. **[VERIFIED] SL פוגע ב-trend על זהב:** ב-golden cross H1 על זהב, בלי stop התוצאה הייתה ‎+646R, ועם stop או target הגרסה הטובה ביותר הגיעה ל-‎+88R. ב-EMA 9/20 H1, ‎+610R בלי stop מול ‎+529R עם stop (ripbacktest). במילים אחרות, ה-edge של trend בזהב יושב בזנב הימני, ו-SL הדוק חותך אותו.
3. **[VERIFIED] swap הוא הרוצח השקט:** ה-swap הנוכחי ב-IC Markets ללונג זהב (‎−$0.563 לאונקיה ללילה) מוריד את EMA 9/20 H1 long-only מ-‎+610R ל-‎+29R, ואת Supertrend מ-‎+547R ל-‎+7.2R. **[ASSUMED]** ב-RoboForex ה-swap ללונג בזהב גם הוא שלילי (צריך לבדוק בטרמינל). לכן כל מנוע trend בזהב שמחזיק לילות צריך להיבדק עם swap אמיתי, או בגרסה intraday שנסגרת לפני ה-rollover.
4. **[VERIFIED] ה-short בזהב מפסיד כמעט תמיד:** ב-72 מתוך 79 גרסאות שיכלו למכור בחסר, ה-shorts הפסידו אחרי עלויות (ripbacktest, 2004–2026).
5. **[OBSERVED] ההוכחה החיה היחידה שמצאתי לגישה הזו היא תיק מגוון של breakouts (Darwinex SUG):** 8 שנים, ‎+18.97% בשנה, בנרמול סיכון של Darwinex (VaR חודשי 6.5%). כלומר הדרך ל-2–4% בחודש עוברת כנראה דרך **תיק של 5–10 מנועי breakout לא-מתואמים** עם hard SL, ולא דרך מנוע בודד [ASSUMED].

## טבלת סיכום
| # | מועמד | מקור | נכס/TF | תשואה ו-DD מדווחים | עובר סינון? | ציון |
|---|---|---|---|---|---|---|
| M1 | Donchian 20/10 H1 (stop = ערוץ היציאה) | XAUUSD Global, 30.10.2026 | XAUUSD (GC=F) H1 | ‎+$2,588 לאונקיה, maxDD (סגור) $498, PF 1.53, 285 עסקאות, 10.2024–10.2026 [VERIFIED] | חלקית: יחס תשואה/DD מספיק, אבל רק שנתיים, בלי swap, ו-DD על עסקאות סגורות בלבד | **3** |
| M2 | 20-bar breakout H4, SL 2ATR / TP 4ATR | QuantStone, 2026 | XAUUSD H4 | ‎+33.9% ב-08.2022–09.2026 ב-1% סיכון, DD 12.4%, OOS ‎+19.3% [VERIFIED] | עובר עלות, hard SL, תדירות. **לא עובר יעד:** כ-1.1% בחודש ב-DD 25% [OBSERVED] | **3** |
| M3 | Turtle System 2 (55/20, 2N stop), 1 unit | ripbacktest, 2026 (חוקי Turtle 1983) | XAUUSD D1 | ‎+64R ב-2004–2026, DD ‎−8.5R, PF 2.18 [VERIFIED] | תשואה נמוכה (כ-0.6% בחודש ב-DD 25%), swap, שביר | **2** |
| M4 | EMA 9/20 H1 long-only, stop 1R | ripbacktest, 2026 | XAUUSD H1 | ‎+529R, DD ‎−55.9R, 2,865 עסקאות [VERIFIED]. עם swap נוכחי: ‎+40R [VERIFIED] | נכשל ב-swap ובוולידציה (PF 1.07) | **2** |
| M5 | Donchian 20 + SMA200, SL 2ATR, TP 2R | WickCheck, 2016–2026 | XAUUSD D1 | ‎+34% ב-1% סיכון, DD 9.6%, PF 1.68, 82 עסקאות [VERIFIED] | מעט מדי עסקאות. כ-0.6% בחודש ב-DD 25% [OBSERVED] | **2** |
| M6 | London breakout (טווח אסיה) על זוגות JPY | BacktestingMax, 2020–2025 | USDJPY / EURJPY M5–M15 | USDJPY M5: ‎+43.0%, DD 16.2%. EURJPY M5: ‎+36.3%, DD 19.4% (ב-1% סיכון) [VERIFIED] | נכשל: כ-0.5% בחודש, ו-pips לעסקה נמוך מ-4–5 [ASSUMED] | **2** |
| M7 | FX time-series momentum (G10) | Moskowitz/Ooi/Pedersen 2012. post-pub: Hutchinson et al. 2022, Chernov/Dahlquist/Lochstoer 2024 | G10 FX | Sharpe מחוץ למדגם ירד מ-‎+0.39 ל-‎−0.32 [VERIFIED, Hutchinson] | נכשל: דעך אחרי הפרסום | **1** |
| M8 | Volatility scaling כרכיב (לא מנוע) | Kim, Tse, Wald 2016, JFM | כל נכס | חלק גדול מה-alpha של TSMOM מגיע מנרמול לתנודתיות [VERIFIED, abstract] | רכיב sizing למנועים M1/M2 | **2** (רכיב) |
| M9 | Opening-range / noise-area breakout על XAUUSD | ripbacktest, 2026 (Zarattini/Aziz/Barbon 2024 הותאם לזהב) | XAUUSD M1 | ORB: ‎+4,774R ברוטו, ‎−2,003R נטו, 52,616 עסקאות. Noise area: ‎−$0.34 עד ‎+$0.12 לאונקיה לעסקה [VERIFIED] | נכשל בעלות | **1** |
| M10 | First half-hour momentum בזהב | Liquidity Hunters, 2026 (מבחן ל-Gao et al. 2018) | XAUUSD M1 | t בין ‎−0.15 ל-1.44. מפסיד כבר ב-1bp [VERIFIED] | נכשל | **1** |
| M11 | **LIVE: Darwinex SUG** (bendex) | darwinex.com/invest/SUG | FX, מדדים, סחורות; breakouts H1–D1 | ‎+301.39% ב-8 שנים, ‎+18.97% בשנה (DARWIN). 24,833 עסקאות, משך ממוצע 10H58M, 41.97% מנצחות [VERIFIED]. maxDD: UNKNOWN | ראיה חיה ל"תיק breakouts עם SL". החוקים פרטיים | **3** (benchmark) |
| M12 | **LIVE: Darwinex IME** (blaynmarshall) | darwinex.com/invest/IME | FX, מדדים, סחורות; multi-strategy | ‎+74.19% ב-3 שנים, ‎+20.32% בשנה (DARWIN), investable מ-17.07.2023 [VERIFIED]. DD: UNKNOWN | hard stops [VERIFIED, בלוג Darwinex]. סגנון האסטרטגיה UNKNOWN | **2** |
| R1 | נדחה: Myfxbook "Market Trend Follower" | myfxbook 10745819 | ידני, bossaFX, PLN | ‎+196.37%, DD 20.17%, מ-12.2023, עודכן לאחרונה 26.12.2025 [VERIFIED] | ידני, לא משוכפל, avg loss גדול מ-avg win, Sharpe 0.14, מעודכן ל-12.2025 בלבד | **1** |

## בחירות מובילות (PREREG מוצע, לא מחייב)
1. **M1 + M2: Donchian/breakout על XAUUSD ב-H1/H4 עם hard SL ו-sizing לפי ATR (M8).** לבדוק על ticks של RoboForex ב-2015–2021 (ה-screen של ה-pipeline), בשתי גרסאות: (א) כמו במקור; (ב) intraday-flat, כלומר סגירה לפני rollover 17:00 NY, כדי לנטרל swap. לדווח long ו-short בנפרד. **סף כישלון מוצע:** PF נמוך מ-1.2 ב-2015–2020, או יחס תשואה שנתית ל-maxDD (כולל עסקאות פתוחות) נמוך מ-1.0.
2. **תיק breakouts (בהשראת M11):** אותו כלל Donchian H1/H4 על 5–8 מכשירים בעלויות נמוכות (XAUUSD, USDJPY, EURJPY, ועוד) בסיכון שווה לפי ATR, ולמדוד קורלציה בין המכשירים ומול C1 ו-I2. **[ASSUMED]** רק דרך הגיוון אפשר לדחוף את יחס התשואה ל-DD מעבר ל-1.5, וזה מה שנדרש ל-2–4% בחודש.
3. לא לבזבז בדיקות על M7, M9 או M10. יש עליהם ראיה שלילית ישירה.

---

## M1. Donchian 20/10 H1 על זהב, ציון 3
- **מקור:** XAUUSD Global, "Donchian Channels on Gold: Turtle-Style Breakouts Tested on XAUUSD", פורסם 30.10.2026 ועודכן 02.11.2026. https://www.xauusdglobal.com/blog/donchian-channels-gold/ . האתר מציין "Drafted with AI" [VERIFIED], ולכן אמינות בינונית.
- **חוקים [VERIFIED]:** long כשה-close שובר את ה-high הגבוה של 20 הנרות הקודמים, short כשהוא שובר את ה-low הנמוך שלהם. יציאה מ-long ב-close מתחת ל-low של 10 נרות (ולהפך ב-short). כניסה ב-open של הנר הבא. עלות $0.30 לאונקיה לעסקה. ההצעה של האתר: ה-stop הוא ערוץ היציאה.
- **תוצאות [VERIFIED]:** GC=F H1 מ-30.10.2024 עד 30.10.2026: ‏285 עסקאות, win 43.9%, ממוצע ‎+$9.08, PF 1.53, נטו ‎+$2,588, maxDD (equity של עסקאות סגורות) $498. שנה 1: ‎+$1,049, שנה 2: ‎+$1,539. longs ‎+$1,848, shorts ‎+$741. ב-D1 מ-2015: כל ההגדרות הפסידו ב-2015–2020.
- **חישוב [OBSERVED]:** יחס שנתי ל-DD = (2,588/2)/498 = 2.6. ב-DD של 25% זה שווה בערך 65% בשנה, כ-4% בחודש לא מורכב. **אבל** ה-DD הוא על עסקאות סגורות בלבד (ה-DD הצף גבוה יותר), החלון קצר, ו-ATR(14) הממוצע היה $17.49, משטר תנודתיות חריג.
- **סינון:** עלות [OBSERVED]: ‎+$9.08 לאונקיה במחיר $3,000–3,600 הם בערך 25–30bp נטו, ולכן עובר את ה-10bp. hold: H1, עובר. תדירות: כ-0.6 עסקאות ביום, עובר. swap: לא נכלל, UNKNOWN.
- **ראיה אחרי פרסום:** אין (המבחן מ-10.2026). ב-ripbacktest, Turtle D1 על זהב שביר (M3) ו-ORB/intraday נכשל (M9).
- **מקור נתונים לבדיקה:** ticks או M1 של RoboForex ECN XAUUSD ב-2015–2021 (screen), ואחר כך holdout.
- **סיכון דעיכה:** גבוה. התוצאה תלויה במשטר המגמה של 2024–2026, והגרסה היומית הפסידה ב-2015–2020.

## M2. 20-bar breakout H4 עם SL 2ATR ו-TP 4ATR על זהב, ציון 3
- **מקור:** QuantStone Backtest Lab, "Gold (XAUUSD) 20-bar breakout on H4", 2026. https://quantstone.net/en/tools/backtest-lab/strategies/gold-xauusd-20-bar-breakout/
- **חוקים [VERIFIED]:** כניסה ב-close מעל ה-high של 20 נרות H4 (או מתחת ל-low שלהם). SL של 2×ATR(14), TP של 4×ATR(14), 1% סיכון לעסקה. עלויות: spread אמיתי לפי שעה וחצי spread של slippage על stops. בלי commission ובלי swap.
- **תוצאות [VERIFIED]:** 01.08.2022–25.09.2026: ‏‎+33.9%, ‏239 עסקאות, DD 12.4%, win 38.1%, רצף של 12 הפסדים. Design ‎+12.2%, OOS (06.2025–09.2026) ‎+19.3%. כל אורכי הטווח מ-10 עד 40 רווחיים (‎+29.0% עד ‎+89.1%). longs ‎+56.8%, shorts ‎−14.6%. אותו כלל על EURUSD: ‎−15.6%, GBPUSD ‎−6.6%, USDJPY ‎+0.2%.
- **חישוב [OBSERVED]:** בערך 7.3% בשנה ב-DD 12.4%. כפול 2 (2% סיכון) נותן כ-15% בשנה, כ-1.2% בחודש, ב-DD של כ-25%. **מתחת ליעד 2–4%.**
- **סינון:** hard SL כן, תדירות 58 בשנה, עלות 0.01R לעסקה [VERIFIED]. swap: לא נכלל.
- **ראיה אחרי פרסום:** OOS פנימי בלבד. **סיכון דעיכה:** גבוה. האתר עצמו כותב שהתוצאה "carried by gold's rally" (זהב עלה 143.2% בתקופה) [VERIFIED].

## M3. Turtle System 2 על זהב D1, ציון 2
- **מקור:** ripbacktest, "Turtle Trading Backtest: Daily Gold, 2004 to 2026", הוקפא 09.10.2026. https://ripbacktest.com/posts/turtle-trading-gold-daily/ . החוקים המקוריים של Dennis מ-1983.
- **חוקים [VERIFIED]:** N = ATR של 20 יום. כניסה בשבירה של high או low של 55 יום, יציאה ב-extreme ההפוך של 20 יום, stop של 2N. גרסה של יחידה אחת, בלי pyramiding (pyramiding הוא מעין averaging ב-winners, ולכן נשאר מחוץ לסינון).
- **תוצאות [VERIFIED]:** TT-S2-1U: ‏103 עסקאות, ‎+64R, PF 2.18, DD ‎−8.5R (כולל פתוחות), 43 ימי החזקה בממוצע. חיובי בכל תקופה: dev ‎+29R, val ‎+5R, holdout ‎+29R. בלי 10 העסקאות הטובות: ‎−14.7R. longs ‎+75.3R, shorts ‎−11.6R. על EURUSD אותו כלל: ‎+15R, DD ‎−22.9R, ו-holdout שלילי.
- **חישוב [OBSERVED]:** בערך 2.9R בשנה מול DD של 8.5R, יחס 0.34. ב-DD של 25% זה כ-8.5% בשנה, כ-0.7% בחודש.
- **swap [VERIFIED]:** בגרסת 4U ה-swap הנוכחי מוריד את ‎+225R ל-‎+75R. **סיכון דעיכה:** בינוני. מבנה Turtle ותיק, אבל ה-edge בזהב הוא בעיקר ה-long בשוק עולה.

## M4. EMA 9/20 H1 long-only עם stop 1R על זהב, ציון 2
- **מקור:** ripbacktest, "EMA 9/20 crossover gold", 2026. https://ripbacktest.com/posts/ema-9-20-crossover-gold/
- **חוקים [VERIFIED]:** golden cross של EMA(9) ו-EMA(20) על close של נר H1 פותח long, death cross סוגר. ‏1R = 1.5×ATR(14), stop ב-1R. החזקה גם בסופי שבוע.
- **תוצאות [VERIFIED]:** H1-L-S: ‏2,865 עסקאות, ‎+529R, PF 1.29, DD ‎−55.9R. PF בוולידציה 1.07 (נכשל). ב-swap נוכחי של IC (‎−$0.563 לאונקיה ללילה ללונג): ‎+40R, t 0.32. במימון של 3% בשנה: ‎+446R.
- **חישוב [OBSERVED]:** בערך 24R בשנה מול DD של 56R, יחס 0.43, כלומר כ-0.9% בחודש ב-DD 25%, וזה לפני swap.
- **סיכון דעיכה:** גבוה, ותלוי swap. רעיון נגזר: גרסה intraday-flat שלא נבדקה (UNKNOWN).

## M5. Donchian 20 + פילטר SMA200, SL 2ATR, TP 2R, על זהב D1, ציון 2
- **מקור:** WickCheck, "20-day breakout (Donchian) backtest", עודכן 20.11.2026. https://wickcheck.com/backtests/donchian-breakout/
- **חוקים [VERIFIED]:** long ב-close מעל high של 20 יום וגם מעל SMA200, short בהיפוך. stop של 2×ATR(14), target של 2R, 1% סיכון. נתונים מ-Yahoo.
- **תוצאות [VERIFIED]:** 20.11.2016–20.11.2026: ‏82 עסקאות, win 46%, PF 1.68, ‎+0.37R לעסקה, DD ‎−9.6%, ‎+34.0%. 2017 ‎−7.4R, 2021 ‎−5.0R, 2025 ‎+13.0R.
- **חישוב [OBSERVED]:** בערך 3% בשנה ב-DD 9.6%, כלומר כ-0.65% בחודש ב-DD 25%. 8 עסקאות בשנה, מעט מדי. **סיכון דעיכה:** בינוני-גבוה.

## M6. London breakout על זוגות JPY, ציון 2
- **מקור:** BacktestingMax, "London breakout strategy backtest on forex and gold", 26.10.2026. https://www.backtestingmax.com/backtests/london-breakout
- **חוקים [VERIFIED]:** טווח אסיה 00:00–07:00 לונדון. מ-07:00 עד 10:00 כניסה ב-close של נר מחוץ לטווח. SL בצד השני של הטווח, TP של 2R, סגירה ב-16:00. סיכון של 1%.
- **תוצאות [VERIFIED]:** 13 מתוך 18 מבחנים הפסידו. USDJPY M5: ‏1,049 עסקאות, PF 1.09, ‎+43.0%, DD ‎−16.2%. EURJPY M5: ‏1,236 עסקאות, PF 1.07, ‎+36.3%, DD ‎−19.4%. GBPUSD M5 ‎−39.5%. זהב M5 ‎+2%. רוב הרווח ב-JPY הגיע מ-buys בזמן שה-yen נחלש.
- **חישוב [OBSERVED/ASSUMED]:** בערך 6% בשנה ב-DD 16%. כ-0.03R לעסקה, ועל טווח EURJPY ממוצע של 45.8 pips [VERIFIED] זה כ-1.4 pips לעסקה [ASSUMED], מתחת לסף 4–5 pips. נכשל. **סיכון דעיכה:** גבוה, כי זו מגמת yen.

## M7. FX time-series momentum (G10), ציון 1
- **מקור:** Moskowitz, Ooi, Pedersen 2012 (JFE). Post-publication: Hutchinson et al. 2022, IRFA, "Are carry, momentum and value still there in currencies?" https://pureadmin.qub.ac.uk/ws/files/359418115/1_s2.0_S1057521922002058_main.pdf . Chernov, Dahlquist, Lochstoer, NBER w32900.
- **ראיה [VERIFIED]:** Hutchinson et al.: ה-Sharpe הממוצע מחוץ למדגם ירד מ-‎+0.39 ל-‎−0.32, ו-"currency excess returns do not exhibit autocorrelation". FinzData (תשעה currency futures, 2009–2026): ‎−1.28% בשנה, Sharpe ‎−0.12, DD ‎−41.32%. Chernov et al.: הביצועים של G10 "started to level off in the mid 2000s".
- **מסקנה:** נכשל. לא לבדוק.

## M8. Volatility scaling כרכיב, ציון 2 (רכיב בלבד)
- **מקור:** Kim, Tse, Wald 2016, JFM 30:103–124, doi 10.1016/j.finmar.2016.05.003.
- **ראיה [VERIFIED, abstract]:** התוצאות של MOP 2012 "largely driven by volatility-scaling returns... rather than by time series momentum". בלי scaling, TSMOM ו-buy-and-hold מניבים תשואה מצטברת דומה.
- **שימוש:** sizing לפי ATR או vol ב-M1/M2 ובתיק (פריט 2 בבחירות המובילות). זה לא מנוע תשואה בפני עצמו.

## M9. ORB ו-noise-area breakout על XAUUSD, ציון 1
- **מקור:** ripbacktest, https://ripbacktest.com/posts/gold-opening-range-breakout/ ו-https://ripbacktest.com/posts/noise-area-breakout-gold/
- **ראיה [VERIFIED]:** ORB של 30 דקות בסשנים אסיה, לונדון וניו יורק, 12 גרסאות: ‎+4,774R ברוטו ו-‎−2,003R נטו על 52,616 עסקאות. כל הגרסאות רווחיות לפני עלויות, ואף אחת לא עברה את כל השערים. Noise area (Zarattini/Aziz/Barbon) בשש גרסאות: ‎−$0.34 עד ‎+$0.12 לאונקיה לעסקה נטו. **נכשל בעלות. לא לבדוק.**

## M10. First half-hour momentum בזהב, ציון 1
- **מקור:** Liquidity Hunters, "Gold trading sessions 2015-2026". https://liquidityhunters.cl/en/studies/gold-trading-sessions/
- **ראיה [VERIFIED]:** ‏β בין ‎−0.001 ל-0.054, t בין ‎−0.15 ל-1.44. בעלות של 1bp: ‎−1.7% עד ‎−2.4% בשנה. נכשל.

## M11. LIVE: Darwinex SUG (bendex), ציון 3 כ-benchmark
- **מקור:** https://www.darwinex.com/invest/SUG (נקרא 20.11.2026, דף ציבורי). תיאור הסוחר: https://www.trade2win.com/threads/darwin-sug-by-endo77-bendex.238524/ ובלוג Darwinex 13.06.2024.
- **מאפיינים [VERIFIED]:** "A collection of fully automated breakout strategies H1 to D1... No martingale or grids... All trades always have a reasonable SL and TP". המקור הוא Donchian breakout משנת 2012. בשנים האחרונות נוספו גם mean reversions. ה-strategies מוחלפות לאורך הזמן.
- **מספרים [VERIFIED]:** ‎+301.39% ב-8 שנים, ‎+18.97% בשנה, investable מ-17.12.2018, ‏24,833 עסקאות, משך ממוצע 10H58M, 41.97% מנצחות, ‏280 משקיעים. אלה תשואות ברוטו של DARWIN, מנורמלות ל-VaR חודשי של 6.5%. maxDD: UNKNOWN (נטען ב-JS).
- **פרשנות [OBSERVED/ASSUMED]:** ‎+18.97% בשנה הם כ-1.45% בחודש בנרמול סיכון בינוני. ב-2–3 פעמים יותר סיכון זה 3–4% בחודש, וה-DD יגדל בהתאם (UNKNOWN). כ-12 עסקאות ליום על פני תיק של הרבה סימבולים. לסימבול בודד זה כנראה פחות מ-3 ביום [ASSUMED].
- **שימוש:** לא להעתיק (אסור subscribe). זה benchmark ארכיטקטוני ל"תיק breakouts עם SL". **סיכון דעיכה:** בינוני. בספטמבר 2020 הייתה ירידה של כ-6% [VERIFIED, פורום], וב-2021 הסוחר כתב על קורלציה בין אסטרטגיות בזמן מהומה.

## M12. LIVE: Darwinex IME (blaynmarshall), ציון 2
- **מקור:** https://www.darwinex.com/invest/IME ובלוג Darwinex "The IME Journey" מ-30.06.2025.
- **[VERIFIED]:** ‎+74.19% ב-3 שנים, ‎+20.32% בשנה (DARWIN, VaR 6.5%), investable מ-17.07.2023. "every system includes hard stops". מדובר ב-multi-strategy. סוג האסטרטגיות (trend או לא), DD ו-holding time: UNKNOWN.

## R1. נדחה: Myfxbook "Market Trend Follower"
- https://www.myfxbook.com/members/Profit_Investing/market-trend-follower/10745819 . [VERIFIED] ידני, bossaFX, ‏1:20, custom start ב-14.12.2023, ‎+196.37%, DD 20.17%, ‏120 עסקאות, avg win PLN 2,943 מול avg loss PLN 3,272, Sharpe 0.14, עדכון אחרון 26.12.2025. ידני, לא ניתן לשכפול, ומעודכן רק עד 12.2025. נדחה.

## קורלציה מול C1 ו-I2
- **[ASSUMED]** M1, M2 ו-M11 הם trend/breakout. מול C1 (crypto trend H6) יש סיכון לקורלציה של "משטר" (שניהם מרוויחים במגמות חזקות ומפסידים ב-chop), גם אם הנכסים שונים. צריך למדוד קורלציה יומית ב-2021–2026 לפני כל שילוב. מול I2 (Nasdaq open) הקורלציה צפויה נמוכה, כי הנכס והחלון שונים. M6 (לונדון 07:00–10:00) לא חופף ל-I2.

## הערות integrity
- כל מספר VERIFIED הועתק מהמקור. החישובים שלי מסומנים OBSERVED, והנוסחה מוצגת לידם.
- רוב הבקטסטים הם של אתרי מתרגלים מ-2026 (ripbacktest, QuantStone, WickCheck, BacktestingMax, XAUUSD Global), לא מאמרים שעברו ביקורת עמיתים. ripbacktest מקפיא חוקים מראש ומפרסם קוד, ולכן אמינות גבוהה יחסית. XAUUSD Global מציין "Drafted with AI".
- לא מצאתי אות MQL5 עם trend, hard SL, בלי averaging ותיעוד חי של 18 חודשים ומעלה שהצלחתי לאמת מדף ציבורי. מוצרי MQL5 Market שעלו בחיפוש (Gold Nexus Prime, TrendForge Gold, Forex Anvil Breakout) הם פרסומות עם תיעוד קצר. לא נכללו.
- ה-maxDD של DARWINs נטען דינמית ולא נקרא: UNKNOWN.
- עותקי מקור שמורים בתיבה: /workspace/t313/src/.
