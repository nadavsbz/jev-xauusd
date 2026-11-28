# t319: הגנה על שני המנועים שעובדים (I2 ו-C1) – מחקר שולחני בלבד

- הוכן: 20.11.2026 (שעון ישראל), Grok (המאסטרו). **מחקר שולחני בלבד**: בלי backtest ובלי MT5. הרצתי רק סימולציית CUSUM סינתטית (סעיף 4, קובץ `cusum_sim.py` לצד המסמך) ושני חישובי סטיית-תקן של Sharpe לפי Lo (2002).
- תגיות: **VERIFIED** = קראתי בעצמי במקור הראשוני (PDF/קוד/עמוד). **OBSERVED** = מקור משני/תקציר/תוצאת חיפוש, לא אומת בגוף. **ASSUMED** = הנחה שלי. **UNKNOWN** = לא נמצא או חסום.
- כלל: אף מספר לא הומצא. לכל מספר יש URL. מה שחסום או בתשלום מסומן UNKNOWN (לא רכשתי כלום).
- הקשר: מבוסס על `/workspace/t318/t318_map.md`. אין המלצת מסחר, ההחלטה של נדב.

## 0. תקציר מנהלים

1. **גישה לעבודה המלאה של Delgado (SSRN 7323419): נחסמה.** SSRN מחזיר 403 "Content Blocked" מה-box (גם עמוד ה-abstract וגם Delivery.cfm); ResearchGate 403; r.jina.ai דורש אימות; scholar.archive.org דורש session. מה שכן נקרא במלואו: ה-abstract המלא (דרך חיפוש + thequant.space) – ובו שתי תשובות ישירות לשאלה "במה השכפולים שונים" (סעיף 1.1). גוף העבודה (23 עמודים, טבלאות לפי חודש/שעה/VIX): **UNKNOWN**.
2. **קוד PazSheimy נקרא במלואו** (git clone, commit `32fd5a31e793fefae4deae0fb65fc2e4585a7b01`, 15.08.2026) וגם ה-PDF של המאמר שלו (12 עמודים). הטבלה השנתית והסבר המנגנון בסעיף 1.2.
3. **ממצא חדש וחשוב: ה-Sep 2025 FAQ של Concretum עצמם (Q24) מראה 2025 שלילית ב-05–08** (מאי −2.1, יוני −2.0, יולי −2.0, אוגוסט −2.9, YTD 1.0%). זה תואם את החודשים החלשים של I2 (05–07.2025). **כלומר החולשה הזו משותפת לכל המשפחה, לא באג ב-I2** [VERIFIED, https://concretumgroup.com/wp-content/uploads/2026/02/Beat-the-Market.pdf, Q24].
4. **ממצא מנוגד שחשוב ל-I2 דווקא:** על SPY ו-ES המנוע נדחס ל-Sharpe≈0 מאז 2025 (brusco, סעיף 1.4), אבל על **Nasdaq (NQ, סשן ניו יורק)** שני בדיקות בלתי תלויות מצאו אותו חי: ripbacktest (חיובי בכל שנה 2020–2026, כולל 2025 ו-2026) ו-EdgeLab (רק צד Long אמיתי; Short "מראז'"). זה מתיישב עם I2 של Claude (+30.6k, 9/12 חודשים חיוביים) ועם הפער מול SPY. סימני אזהרה: הולדאוט של ripbacktest כבר נוצל, ו-ES לא עבר שם.
5. **C1:** שכפולים בלתי תלויים משחזרים את הבסיס (Sharpe 1.4–1.58 עד 03.2025), אבל **אחרי סוף נתוני המאמר (04.2025) האנסמבל שטוח: Sharpe 0.05** בבדיקה אחת, ו-Sharpe 0.51–0.53 ל-5 שנים אחרונות (לעומת 1.49 מ-2015). ה-BTC נפל ~53% מהשיא (אוקטובר 2025 עד יוני 2026) והאנסמבל הפסיד לכל היותר 15% – כלומר **הגנת ה-DD עבדה, התשואה לא**. [סעיף 2]
6. **פרוטוקול התרעה מוקדמת:** `t319_early_warning_PROTOCOL_DRAFT.md`. עיקרון: Sharpe מתגלגל של 60/120 ימים רועש מדי כדי להיות טריגר (SE שנתי ≈2.05 ו-1.45, חישוב שלי לפי Lo), לכן הוא "צהוב" בלבד. הטריגר הממשי: **CUSUM כיול ב-ARL0≈750 ימי מסחר, עם עיכוב חציוני ≈150–200 יום לזיהוי "הקצה נעלם"** (סימולציה שלי), ועוד פער Live-מול-Tester.

---

## 1. I2 – כל פרט אפשרי

### 1.1 מה שונה בין השכפולים (VWAP, אישור VWAP, Noise band, sizing, checkpoints, עלויות)

| רכיב | המאמר המקורי (Concretum, גרסה 22.09.2025) | קוד Concretum הציבורי | Delgado | PazSheimy | Brusco / Chris-ZZX | מקור |
|---|---|---|---|---|---|---|
| **VWAP** | מחושב רק משעות מסחר רגילות [VERIFIED] | **Typical price** = (H+L+C)/3 ×volume, מצטבר [VERIFIED] | "typical-price VWAP" הוא אחד משני הפרטים ש"פירטו מול קוד הייחוס" כדי להגיע ל-1,989% [VERIFIED מה-abstract] | typical price (HLC3) [VERIFIED בקוד] | HLC3 [VERIFIED/OBSERVED] | https://concretumgroup.com/backtesting-7-years-of-free-data-beat-the-market-an-effective-intraday-momentum-strategy-for-the-sp500-etf-spy/ ; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7323419 |
| **אישור VWAP בכניסה** | כניסה בפריצת band; יציאה (stop) ב-max(VWAP, UB) ללונג / min(VWAP, LB) לשורט [VERIFIED] | התנאי המשולב: close>UB **וגם** close>VWAP [VERIFIED] | "VWAP confirmation at entry" = הפרט השני שאומת מול הקוד [VERIFIED מה-abstract] | תנאי משולב בכל נקודת החלטה (מקביל לפי טענתם) [VERIFIED] | אותו דבר | Beat-the-Market.pdf עמ' ~12; קוד Paz שורות 150–153 |
| **Noise area / band** | σ(HH:MM)=ממוצע |close/open−1| על 14 הימים הקודמים באותה דקה; UB=max(Open, Close[t−1])·(1+σ), LB=min(…)·(1−σ); מכפיל 1 [VERIFIED] | זהה; ב-Paper: rolling 14, min_periods 13, shift(1) [VERIFIED בקוד Paz] | לא ידוע (UNKNOWN) | **ללא התאמת דיבידנד** ל-Close[t−1] (המקור מתאם) – הם מעריכים השפעה זניחה [VERIFIED מהמאמר שלהם] | ER/shock-control הם הרחבות שלהם, לא ליבה | Paz paper §2; FAQ Q6 במקור |
| **פרמטרי ליבה (FAQ של המחברים)** | lookback אופטימלי 90 יום: Sharpe 1.50 (מול 1.35 ב-14); multiplier 1.5: Sharpe 1.55 [VERIFIED Q14]. טבלת lookback 5–90: Sharpe 1.23–1.50 [VERIFIED Q6] | | | | | Beat-the-Market.pdf Q6, Q14 |
| **Sizing** | 2% daily vol target, σ=סטיית תקן 14 ימי תשואה, Shares=AUM/Open·min(0.02/σ, 4) [VERIFIED] | נ"ל | לא ידוע | זהה [VERIFIED] | זהה (Chris-ZZX: "previous 14 completed raw daily returns") | Paz קוד שורות 156–163. **I2 שלנו: TargetVol 0.15 – מקבילה לא ידועה לי (UNKNOWN: איך 0.15 מתורגם ל-2% יומי; Claude יודע)** |
| **Checkpoints** | החלטה כל 30 דקות; סגירה בסוף יום [VERIFIED] | `min_from_open % 30 == 0`; החלטה בסגירה, ביצוע אחרי נר [VERIFIED] | לא ידוע | זהה [VERIFIED] | ripbacktest: "close of checkpoint minute, fill at open of next minute", עד 30 דק' לפני סגירה [VERIFIED] | https://ripbacktest.com/posts/noise-area-breakout-nq/ |
| **עלויות** | $0.0035/מניה + slippage $0.001/מניה (נמדד ממסחר אמיתי: ממוצע ≈$0.001, חציון נמוך יותר) [VERIFIED §4.6] | נ"ל | לא ידוע | זהה | Brusco: 0 slippage בבסיס; Sharpe 1.02 גם ב-$0.005 [VERIFIED]; NQ: $15.76 הלוך-חזור (ripbacktest) | Beat-the-Market.pdf §4.6; brusco reports/validation.md |

**משמעות ל-I2 שלנו (ASSUMED, לבדיקה אצל Claude):** (א) אם ב-I2 ה-VWAP מחושב על close ולא על HLC3 – זה אחד משני הפרטים ש-Delgado מצא כ"מהותיים" לשכפול; ב-MT5 קשה לקבל HLC3 מצטבר-נפח (volume של CFD הוא tick volume). (ב) אם הכניסה אינה דורשת אישור VWAP – גם זה. (ג) DstFix מתייחס כנראה לשעון השרת (UNKNOWN מה בדיוק), וההבדל בין DST ארה"ב לאירופה (שבועות במרץ ובאוקטובר–נובמבר) יכול להזיז את חלון ה-RTH. **לא ביצעתי בדיקה, רק מסמן.**

### 1.2 PazSheimy: קוד וניתוח (VERIFIED, https://github.com/PazSheimy/spy-intraday-momentum-oos)

- נתונים: IQFeed 1-דק' SPY, 02.01.2015–31.03.2026, 1,101,234 נרות, 2,827 ימים; IS עד 30.04.2024 (2,333 ימים), OOS מ-01.05.2024 (480 ימים).
- IS: Sharpe 1.34, 19.8% שנתי, MDD 26.2%. OOS: Sharpe **0.39**, 4.8% שנתי, MDD 18.5%, מול SPY B&H 29.5% מצטבר (9.4% לאסטרטגיה). הקצה הממוצע היומי OOS 0.023% (t=0.54, p=0.59): לא מובהק מ-0.
- **Hit ratio נשאר ~45% (44.8 → 45.0). הירידה היא ביחס רווח-מול-הפסד לעסקה, לא בתדירות ניצחונות.** חשוב למעקב (סעיף 3).
- טבלה שנתית (אסטרטגיה, %): 2016 −13.4; 2017 −8.8; 2018 +60.5; 2019 +8.4; 2020 +26.2; 2021 +32.8; 2022 +23.7; 2023 +37.8; 2024 +30.1; **2025 −2.7 (Sharpe −0.10)**; **2026 (עד מרץ) −3.1 (Sharpe −0.99)**.
- המנגנונים שהם מציעים: 0-DTE (Rosa 2022 מתעד ירידה בחיזוי מומנטום תוך-יומי מאז 2013), צפיפות מסחר (crowding), "regime": חזק בשוק תנודתי עם טרנדים (2018, 2020, 2022), חלש בשוק שקט שעולה בהדרגה (2016–2017, 2025). הם עצמם אומרים: **480 יום OOS "suggestive but not conclusive"**; ה-Welch לא דוחה שוויון ממוצעים (p=0.255).
- ה-SSRN שלהם: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7290621 (OBSERVED, תקציר).

### 1.3 מה נמצא על Delgado (SSRN 7323419) – מה כן ידוע מה-abstract (VERIFIED)

- 2.6 מיליון נרות דקה SPY מ-TradeStation, 01.2000–08.2026. שחזור: 1,989% ו-Sharpe 1.317 בחלון המאמר (05.2007–04.2024).
- שחזר את עדכון ספטמבר 2025 של Concretum: 2024 = 31.8% (לעומת 32.2% שלהם), ינואר–אוגוסט 2025 = 1.4% (לעומת 1.0%).
- פוסט-פרסום: 05.2024–29.08.2025 = **+19.3%, Sharpe 1.057** (או +23.3%, Sharpe 1.284 מהיום הראשון אחרי 10.05.2024); **02.09.2025–14.08.2026 = −8.1%, Sharpe −0.461**. Sharpe מצרפי 05.2024–08.2026 = 0.35.
- אחרי חיפוש מתאמים: 129 ניסויים ב-ledger, PBO 38.49% / 40.87%, DSR (N=80) 99.999987%; ה-spec הסופי "frozen": Sharpe 1.274, MDD −14.8%, 2,110.6% – **אבל המחבר עצמו מצהיר שאין אימות פרוספקטיבי** ("the correct next experiment is the passage of time with frozen parameters").
- קטגוריות ההרחבות שנבדקו (בלי פרמטרים – UNKNOWN): asymmetric short filters, relative-volume sizing, volatility overlays, persistence filters, profit locks, breakeven rules, trade caps, daily loss limits, VWAP-dominance rules, intraday decay, regime overlays, performance-based overlays.
- מקורות: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7323419 ; https://thequant.space/flowcharts/beat-the-market-revisited-an-independent-replication-and-statistical-audit-of/
- **שים לב:** 02.09.2025–14.08.2026 של Delgado (SPY −8.1%) מול חלון Claude 09.2025–08.2026 על Nasdaq (+30.6k, 9/12 חיוביים): אותו חלון, תוצאה הפוכה. זה אומר שהחולשה אינה אוניברסלית בין אינדקסים (OBSERVED).

### 1.4 באיזה חלק מהיום ובאיזה VIX המנוע מפסיד מאז 2025

**VIX (SPY 2020-07 עד 2026-07, גרסת "final" = המקורית, Brusco, נתוני Alpaca-IEX עם VWAP מקורב) [VERIFIED, https://github.com/giovannibrusco/zarattini-2024-momentum-spy, reports/validation.md]:**

| VIX | תשואה כוללת | Sharpe | ימים |
|---|---|---|---|
| <15 | +34.6% | 2.37 | 262 |
| 15–20 | +16.6% | **0.50** | 636 |
| 20–30 | +48.1% | 1.35 | 515 |
| 30–40 | −0.3% | −0.01 | 74 |
| >40 | +3.4% | 9.14 | 5 (מדגם זעיר, אין מסקנות) |

- 2025: −4.9% (Sharpe −0.27); 2026 עד 07: −12.9% (Sharpe −1.91). על ES (נתוני CME מלאים) אותה תוצאה, מתאם יומי 0.97 → **לא עניין של feed או עלויות** (עלות ≈0.4 bps להלוך-חזור מול תוחלת −0.6 bps לעסקה) [VERIFIED reports/validation_es.md].
- ES final 2024-05-30 עד 2026-07: Sharpe **−0.07**, CAGR −2.1%; ES base (יציאה ב-band בלבד, ללא VWAP-final) Sharpe 0.52. הבסיס עדיף על final ב-2024–26 (Sharpe ~0.7 מול ~0) – **post-hoc, ואסור לבחור בו בדיעבד** לפי ה-CONCLUSIONS שלהם.
- **FAQ של המחברים Q19/Q20: אין קשר מובהק בין VIX לרווחיות שורטים** (p=0.91 ל-beta) [VERIFIED]. כלומר VIX כמסנן "ברור" אינו מוכח. **אבל** Q-regression על RSI(5): beta = −3.25 bps לכל נקודת RSI, p=0.001 (RSI גבוה של SPY ביום הקודם → תוחלת נמוכה יותר; הסבר gamma של דילרים) [VERIFIED, Beat-the-Market.pdf §4.5].
- Concretum כותבים ש"intraday trend-following profits have not disappeared, but weakened during certain parts of the session", וש"בעבר השעה האחרונה הניבה ~60% מהרווחים; מאז 2023 יש יותר היפוכים בסוף היום" (מתוך כותרת המאמר 07.08.2026 ותקציר-חיפוש) [OBSERVED]. **הגוף בתשלום ($80), לא נרכש: UNKNOWN אילו חצאי-שעה בדיוק.** המסמך המקורי (Q18) מציג עלייה 10:00–12:00, הפסקה בצהריים, וחזרה חזקה 14:00–סגירה (זה הדפוס ההיסטורי, לפני השינוי) [VERIFIED].
- חלק-יום ספציפי לאחר 2025 עבור SPY/Nasdaq: **UNKNOWN** (לא נמצא מקור חופשי). **המלצה: Claude מחשב זאת מה-trade log של I2 עצמו (בלי הרצה חדשה)**, ראו פרוטוקול R7.
- חודשים: הטבלה הרשמית של Concretum (Q24, עדכון 22.09.2025): 2025 – ינו −1.2, פבר 7.6, מרץ −0.2, אפר 4.3, מאי −2.1, יוני −2.0, יולי −2.0, אוג −2.9; סה"כ 1.0 [VERIFIED]. 2024: ינו 8.8, פבר −1.5, מרץ −0.4, אפר 5.8, מאי −4.3, יוני 1.6, יולי 8.2, אוג −2.8, ספט 4.1, אוק 6.7, נוב −2.6, דצמ 5.7, סה"כ 32.2. ב-2016–2017 (שנתיים שליליות −12.8%, −6.9%) הייתה אותה חולשה, ואחריה התאוששות (2018: +61.1%) [VERIFIED].

### 1.5 עבודות על Nasdaq/QQQ אחרי 2024

| מקור | מה בדק | תוצאה | תגית |
|---|---|---|---|
| ripbacktest.com (NQ, 1-דק', NinjaTrader back-adjusted, 01.2020–25.09.2026; פיתוח 2020–2023, ולידציה 01.2024–03.2025, הולדאוט 04.2025–09.2026 [**נוצל כבר**]; $15.76 הלוך-חזור) https://ripbacktest.com/posts/noise-area-breakout-nq/ | הכלל ללא שינוי, 1 חוזה | **NY LS: +$231,557, 1,504 עסקאות, +$153.96/עסקה, PF 1.28, Sharpe לא דווח. Long-only: +$152,227, 747 עסקאות, PF 1.43. חיובי בכל שנה: 2025 LS +$22,410 (217 עסקאות), L +$23,959; 2026 עד 09: LS +$34,256, L +$18,773.** Asia ו-London נכשלו (London הפסיד −$91,278). **ES לא עבר** (t=1.91, הולדאוט שלילי); YM לא עבר. 18 וריאנטים נוסו (t≥2.5 נדרש). | VERIFIED |
| EdgeLab (NQ, Databento 2010–2026, פרמטרים נעולים ב-2010–2017) https://edgelabtrading.com/blog/zarattini-intraday-momentum-nasdaq/ | פיצול Long/Short | **Long: Sharpe 0.90 IS / 0.68 OOS; Short: −0.21 IS / 1.22 OOS ("מראז'": הרווח בעיקר 2018 ו-2022); Both: 0.43 / 1.39.** Long-only: ~+88% ב-16 שנה, DD −11%, "soft patch since 2024 peak". עלות מודל 0.01% הלוך-חזור. | VERIFIED (דף), המחבר פרסם 24.07.2026 |
| OrderBlock.net/nq (5-דק', NQ, 2015–07.2025, עלות + tick) https://orderblock.net/nq | גרסה עם stop 0.24σ, יעד 1.5σ, מגבלה 58.5 נק' | ~28% שנתי בסיכון 1%/עסקה, DD ~46%; ~14%/26% בחצי סיכון. 2016, 2017, 2019 שטוחות/שליליות. ~2/3 מהרווח משלוש שנים (2018, 2022, 2023). לא אותו כלל בדיוק. | OBSERVED |
| POB-CL-DT PR #13 (SPY ו-QQQ, SIP מ-2016, slippage $0.01 ו-$0.02) https://github.com/patrickobirmingham-eng/POB-CL-DT/pull/13 | שחזור SPY/QQQ | תוצאות מספריות: לא נקראו (UNKNOWN) | OBSERVED |
| Chris-ZZX/spy-intraday-momentum (SPY, 2022–04.2024 test) https://github.com/Chris-ZZX/spy-intraday-momentum | הרחבות ML ו-shock control | Sharpe 2.015 בסיס עם vol sizing; shock control מעלה ל-2.287; "period-dependent". נקודת קצה 04.2024 – לא רלוונטי לשחיקה | OBSERVED |
| Concretum: "Where To Trade Intraday Trends" 19.08.2026 (49 ETFs, walk-forward) | רוחב נכסים | Top-4: Sharpe ≈1.2, CAGR 12%, MDD 13% (ללא מינוף) – מתוך תקציר | OBSERVED, מאמר בתשלום |

**מסקנה ל-I2 (OBSERVED + ASSUMED):** Nasdaq נראה עמיד יותר מ-SPY/ES בחלון 2025–2026 – שתי עבודות נפרדות; ההסבר המוצע שלי (ASSUMED, לא נבדק): תנודתיות תוך-יומית גבוהה יותר ב-Nasdaq מייצרת יותר "ימי טרנד" יחסית ל-band. **שני אזהרות:** (1) Short ב-Nasdaq אינו מוכח (EdgeLab); (2) I2 הוא CFD ב-RoboForex ECN, לא NQ futures: spreads/swap/DST שונים (UNKNOWN).

---

## 2. C1 – שכפולים בלתי תלויים אחרי הפרסום

**המאמר:** Zarattini, Pagani, Barbon, "Catching Crypto Trends", גרסה 09.04.2025. אנסמבל Donchian עם lookbacks 5/10/20/30/60/90/150/250/360 יום, vol target 25% שנתי על סטיית תקן 90 יום, תקרת הקצאה 200% [VERIFIED], BTC 01.2015–03.2025: Combo CAGR 30%, vol 17%, Sharpe 1.58, Sortino 2.03, MDD 19%, alpha 14% (לפני עלויות); Top-20 rotational Sharpe מעל 1.5 נטו, alpha 10.8% מול BTC; עלויות 0/10/25/50 bps + רף איזון מחדש 20% [VERIFIED, https://concretumgroup.com/wp-content/uploads/2026/02/Catching-Crypto-Trends.pdf].

| מקור | תקופה | תוצאה | תגית |
|---|---|---|---|
| AlgoEdge Research (live backtest, מתעדכן יומית; BTC+ETH, 9 מודלים, עלות 0.10%) https://algoedgeresearch.com/live/crypto-trend | 2015 עד 19.11.2026 | **מאז 2015: 25.6% שנתי, Sharpe 1.49, DD −19.7% (BTC B&H: 64.5%, Sharpe 1.09, DD −83.4%). 5 שנים אחרונות: 6.3% שנתי, Sharpe 0.53, DD −15.3%.** מצב נוכחי: **0 מתוך 9 מודלים ארוכים** (מזומן). שוחזרו הנתונים שלהם: BTC Sharpe 1.46 מול 1.45 בגיליון, DD −19.7% מול −20.0% | VERIFIED (דף); אופן החישוב שלהם: OBSERVED |
| AlgoEdge Insights (Beehiiv) https://algoedgeinsights.beehiiv.com/p/catching-crypto-trends-the-nine-model-strategy-that-cut-bitcoin-s-worst-crash-from-83-to-20 | BTC 12.2015–10.2026 | Sharpe 1.45, DD −20% (B&H 1.07 / −83%). ETH: 1.04 מול 0.90, DD −16% מול −79%. **פיצול: 2015–2021 Sharpe 1.96; 2022–03.2025: 0.84 (מול 0.60 B&H); מאז 04.2025: Sharpe 0.05 ("flat").** BTC נסגר בשיא ~$125,000 באוקטובר 2025, ירד 53% עד יוני 2026; הפסד מקסימלי של האסטרטגיה בתקופה: −15%. חשיפה ממוצעת ~21% ב-vol 25%; מול 62% שנתי של החזקה. Sharpe נשאר 1.27 גם בעלות 0.5% לעסקה. פלסבו (ערבוב תזמון 1,000 פעמים): חציון Sharpe 0.75 (אף ריצה לא הגיעה לאמיתי). | VERIFIED (קראתי את העמוד), מחבר אנונימי |
| 1nve.st (Jaewon Jung) https://www.1nve.st/p/catching-crypto-trends | 9 שנים | CAGR 31.5%, DD 15.9%, Sharpe 1.4 – תואם למאמר | OBSERVED (תאריך הפרסום לא נבדק) |
| Delphic Alpha "The Replicator" (67 מטבעות) https://delphicalpha.substack.com/p/the-replicator-catching-crypto-trends | 24.03.2026 | בתשלום: UNKNOWN | OBSERVED |
| QuantConnect (embedded backtest) | – | היסטורי בלבד, אינו מוכיח ביצוע חי: UNKNOWN | OBSERVED |
| GitHub / Reddit / X | – | **לא נמצא שכפול משמעותי אחר ב-GitHub; Reddit/X: לא נמצא ציטוט מדוד אחרי 2025** (חיפוש אחד בכל כיוון; X MCP לא הופעל כאן – UNKNOWN) | UNKNOWN |

**דפוס שחיקה (OBSERVED):** כל הנתונים החיוביים משתייכים ל-2015–2021 (Sharpe 1.96), ויורדים ל-0.84 ב-2022–03.2025 ול-0.05 מאז 04.2025. זו תבנית של "Sharpe decay", אבל מדגם ה-18 חודשים קצר; מקור הנתונים (Yahoo, BTC+ETH בלבד) שונה מהמאמר (CoinMarketCap, Top-20). עבור **C1 שלנו**: איזה יקום, vol target, בורסה, עלויות – UNKNOWN (לא ראיתי את ה-spec של C1; Claude יודע).
**מה "חי" בניגוד לפרשנות מכשילה:** האנסמבל לא הפסיד (≈שטוח) בזמן ש-BTC ירד 53%. זו הגנה (DD), לא תשואה. מבחינת מטרת נדב (עשרות אחוזים בחודש, מינוף, ללא ימי קריסה) – ארבעה אחוזים בשנה ל-vol 25% אינם מנוע צמיחה אלא "כרית" (ASSUMED).

---

## 3. פערים ו-UNKNOWN שנשארו

1. גוף העבודה של Delgado (טבלאות חודשיות/שעתיות/VIX של 2025–2026): **חסום**. נדרש מישהו עם גישה (נדב/Claude בדפדפן), או מייל למחבר (לא נשלח).
2. מאמרי Concretum בתשלום (Seasonality $80, "Can VIX Improve…", "Improving the ORB"): לא נרכשו. הם היו עונים על "איזה חלק יום" ו"אילו חוקי VIX". **החלטה לנדב, אין רכישה בלי אישור.**
3. התרגום של TargetVol 0.15 ב-I2 ו-DstFix: UNKNOWN (לא ראיתי קוד I2).
4. C1 על 2025–2026 עם יקום Top-20: UNKNOWN.

אין המלצת מסחר, ההחלטה של נדב.
