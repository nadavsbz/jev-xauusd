# PREREG t318-B: מגמה תוך-יומית (Noise Area) על סל ETF/CFD עם בחירת שווקים walk-forward

**STATUS: PROPOSED (טיוטה, לא FROZEN).** ממתין לביקורת של Claude. לא הורץ כלום ולא נפתח holdout.
- נכתב: 20.11.2026, Grok (המאסטרו), סבב t318.
- **מקורות:** מנוע Noise Area מ-"Beat the Market" (SSRN 4824172), PDF מלא: https://concretumgroup.com/wp-content/uploads/2026/02/Beat-the-Market.pdf [VERIFIED]. רעיון הבחירה בין שווקים מ-"Where To Trade Intraday Trends" (Concretum, 19.08.2026): https://concretumgroup.com/where-to-trade-intraday-trends/. המאמר הזה ב-Premium, ולכן **כלל הבחירה המדויק שלו UNKNOWN**. מה שידוע מהתקציר הציבורי: 49 ETFs, walk-forward momentum ranking, Top-4: Sharpe בערך 1.2, CAGR 12%, MDD 13% [OBSERVED].

## 0. למה זה B
- המנוע (P5) הוא בסיס I2, והוא משוחזר באופן עצמאי [VERIFIED: Delgado SSRN 7323419, PazSheimy]. **אבל ב-SPY יש שחיקה:** 02.09.2025 עד 14.08.2026: ‎-8.1%, Sharpe ‎-0.461 [VERIFIED, abstract של Delgado]. השאלה המעשית לחברה: האם ה-edge תלוי בשוק הספציפי, ואפשר לשמר אותו על ידי פיזור על שווקים לא מתואמים (זהב, אג"ח, אנרגיה, שווקים מתעוררים), או שהוא נשחק בכל מקום.
- החוקים פומביים ומאומתים, ואפשר לבדוק בחינם (Alpaca 1m ETFs). במקביל אפשר לבדוק על מכשירי RoboForex ECN (XAUUSD, US500, NAS100, GER40, XTIUSD וכו').
- נדחו: VIX-ETN (כ-1% לחודש, MDD 31% ב-S4, סיכון crash-day [VERIFIED/ASSUMED]), ORB-QQQ (מתואם ל-I2 ונקודת האיזון סביב 2¢ [VERIFIED clockout]), VWAP-TT (בלי slippage, עסקאות קצרות), Sector-MR ו-Overnight (החוקים בתשלום).

## 1. השערה
- **H1:** מנוע Noise Area, עם החוקים המדויקים של P5, המיושם על כל אחד מ-N שווקים נזילים, ועם בחירה חודשית walk-forward של Top-4 שווקים לפי ביצועי המנוע ב-12 החודשים הקודמים, מניב **תיק עם Sharpe נטו ≥1.0 ו-MDD ≤25%**, כולל בתקופה שבה ב-SPY לבדו המנוע נשחק (09.2025–10.2026).
- **H0:** Top-4 לא עדיף על בחירה אקראית של 4 שווקים (permutation), או Sharpe נטו <1.0.

## 2. חוקי המנוע (לכל שוק בנפרד) [VERIFIED מ-P5]
1. move(t−i, HH:MM) = |Close(t−i, HH:MM)/Open(t−i, 09:30) − 1| ו-σ(HH:MM) = ממוצע על i=1..14.
2. UB = max(Open_t, Close_{t−1}) × (1+σ). LB = min(Open_t, Close_{t−1}) × (1−σ). Close_{t−1} מותאם לדיבידנד (לפי ההערה של Delgado על הקוד של המחברים [VERIFIED abstract]).
3. החלטות רק ב-HH:00 וב-HH:30. לונג אם Close>UB **וגם** Close>VWAP. שורט אם Close<LB **וגם** Close<VWAP (VWAP confirmation, לפי Delgado ו-QC [VERIFIED]). VWAP מחושב כ-typical price (לפי Delgado [VERIFIED abstract]).
4. Trailing stop (נבדק רק בנקודות ההחלטה, כמו במאמר [VERIFIED]): לונג נסגר אם Close < max(UB, VWAP), שורט נסגר אם Close > min(LB, VWAP).
5. סגירה כפויה ב-15:59/16:00. אין פוזיציות לילה.
6. **סטופ קשיח נוסף (דרישת החברה, לא במאמר, ASSUMED):** סטופ חירום רציף ברמה של entry ∓ 2×σ(HH:MM של הכניסה)×entry, כדי שיהיה SL פיזי אצל הברוקר. נספר כחלק מהספק, לא כווריאנט.
7. **גודל:** vol target יומי 2% לפי σ של 14 ימים של השוק, מינוף מקסימלי 4x לשוק [VERIFIED P5]. בתיק: חלוקה שווה בסיכון בין 4 השווקים שנבחרו (משקל 1/4 מיעד הסיכון לכל אחד), מינוף ברוטו בתיק ≤4x [ASSUMED].

## 3. יקום (מוגדר מראש, 16 שווקים) [ASSUMED: הרשימה של Concretum עם 49 ה-ETFs לא פורסמה בחינם]
- **Alpaca (ETFs):** SPY, QQQ, IWM, DIA, GLD, SLV, TLT, IEF, USO, XLE, XLF, XLK, EEM, EFA, FXI, UNG.
- **RoboForex ECN (מקבילה, בדיקה משנית בלבד):** US500, NAS100, US2000, XAUUSD, XAGUSD, XTIUSD, GER40, JP225. נתונים מהמסוף בקריאה בלבד, **ורק כשהמסופים פנויים** (לא נוגעים ב-t301b ו-T286_1..3).
- מקור נתונים: Alpaca SIP 1m מ-2016 [VERIFIED כזמינות]. בדיקות איכות נתונים כמו ב-PREREG A §3.

## 4. כלל בחירה (walk-forward, מוגדר מראש) [ASSUMED]
- ביום המסחר הראשון בכל חודש מדרגים את 16 השווקים לפי **Sharpe נטו של המנוע לבדו** ב-252 ימי המסחר הקודמים, ובוחרים Top-4. אין שימוש במידע עתידי.
- וריאנטים מוגדרים מראש (K=4): Top-k ∈ {4, 6} × חלון דירוג ∈ {126, 252} ימים. **Primary = Top-4/252.**
- **ביקורת:** (a) כל 16 השווקים במשקל שווה, ו-(b) SPY לבדו (שווה ל-I2). (a) ו-(b) הם השוואות בלבד ולא נספרים כניסוי להחלטה.

## 5. עלויות
- ETFs: $0.0035 למניה לכל צד ו-SEC/TAF על מכירות (כמו ב-A), ו-**slippage של 1¢ למניה לכל צד** (פי 10 מה-$0.001 של המאמר [VERIFIED P5]). רגישות: 0.1, 1, 2¢.
- CFD של RoboForex: ספרד בפועל מה-tick history, עמלת ECN לפי מפרט החשבון (UNKNOWN עד שנקרא בקריאה בלבד) ו-swap = 0 (אין החזקה בלילה).

## 6. תקופות
- **DEV:** 04.01.2016 עד 31.12.2022 (ההרצה מתחילה ב-2017 בגלל חלון הדירוג של 252 ימים).
- **VAL:** 03.01.2023 עד 30.04.2024 (עד תום תקופת המאמר).
- **HOLDOUT (לא נגוע):** 01.05.2024 עד 23.10.2026. כולל את חלון השחיקה ב-SPY (09.2025–08.2026).
- **Forward:** מ-27.10.2026, Paper ב-Alpaca.

## 7. שערים (עלויות 1¢)
| שער | DEV | VAL | HOLDOUT |
|---|---|---|---|
| G1 Sharpe שנתי נטו של התיק | ≥1.2 | ≥1.0 | ≥1.0 |
| G2 ממוצע גיאומטרי חודשי נטו (במינוף שנקבע ב-DEV כך ש-MDD_DEV ≤20%) | ≥3.5% | ≥2.0% | ≥2.0% |
| G3 MDD | ≤25% | ≤25% | ≤25% |
| G4 Top-4 מול 4 אקראיים (5,000 permutations), Sharpe | p<0.05 | — | p<0.10 |
| G5 Top-4 מול SPY בלבד (I2) בחלון 09.2025–10.2026 | — | — | Sharpe Top-4 > Sharpe SPY ו->0 |
| G6 DSR עם N מצטבר חברתי (UNKNOWN, Claude ימלא) | ≥0.95 | — | ≥0.90 |
| G7 Holm על K=4 | עובר | — | — |
| G8 Worst day | ≥ ‎-4% | ≥ ‎-4% | ≥ ‎-4% |
| G9 Median hold | ≥15 דק' (מובנה: החלטות כל 30 דק') | | |
| G10 מתאם יומי ל-I2 ול-C1 | ≤0.6 | — | ≤0.6 |
- הערה ל-G2: Top-4 של Concretum מדווח CAGR 12% (כ-0.95% לחודש) ו-MDD 13% [OBSERVED]. כדי להגיע ל-3.5% לחודש צריך מינוף של פי 3 או יותר, ואז ה-MDD כנראה יעבור 25% [ASSUMED]. **ייתכן ש-G2 ייכשל גם אם ה-edge אמיתי.** במקרה כזה מדווחים "רכיב עם Sharpe", לא PASS.

## 8. Kill-criterion
- **KILL:** Sharpe נטו של Primary ב-DEV <0.8, **או** G4 עם p≥0.20 (הבחירה לא מוסיפה כלום).
- **KILL ב-holdout:** Sharpe של holdout <0.5, או MDD >25%. **אסור** לכוונן אחרי הפתיחה.
- תקציב: 4 ניסויים.

## 9. ה-iteration הבאה מוגדרת מראש
- אם B נכשל על G4 (הבחירה חסרת ערך) אבל כל 16 השווקים במשקל שווה עוברים את G1: **t318-B2** = תיק שווה-משקל עם ה-overlay של Fast-Alpha (P14: עיכוב כניסה ויציאה עד נר 5m נגדי [VERIFIED]). PREREG חדש ונספר במונה.
- אם B נכשל כי המנוע נשחק בכל השווקים מ-2025: מדווחים מיד ל-I2 (סיכון למנוע הקיים) ומציעים PREREG של בדיקת regime מתוך "The Intraday Seasonality of Market Trends" (יותר היפוכים בסוף היום מאז 2023 [OBSERVED]).

אין המלצת מסחר, ההחלטה של נדב.
